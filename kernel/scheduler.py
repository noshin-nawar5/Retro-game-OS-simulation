class RoundRobinScheduler:

    CTX_FLASH_TICKS = 8

    def __init__(self, time_quantum, memory_manager):
        self.time_quantum       = time_quantum
        self.memory_manager     = memory_manager
        self.process_table      = []
        self.pid_counter        = 1
        self.foreground_process = None
        self.current_process    = None
        self.tick               = 0
        self.context_switches   = 0
        self.last_switch_tick   = 0
        self.ctx_flash          = 0
        self.ready_queue        = []
        self._bg_current        = None
        self._bg_quantum        = 0
        self._load_buf          = [0] * 60
        self._load_idx          = 0
        self.cpu_load           = 0

    def generate_pid(self):
        pid = self.pid_counter
        self.pid_counter += 1
        return pid

    def add_process(self, process):
        base = self.memory_manager.allocate(process.pid, process.memory_needed)
        if base is None:
            print(f"[Scheduler] OOM — PID {process.pid} rejected")
            return False
        process.memory_base = base
        process.state       = "READY"
        self.process_table.append(process)
        if process not in self.ready_queue:
            self.ready_queue.append(process)
        print(f"[Scheduler] PID {process.pid} ({process.app.__class__.__name__}) admitted")
        return True

    def kill_foreground(self):
        if self.foreground_process:
            self.foreground_process.state = "TERMINATED"

    def schedule(self):
        self.tick += 1
        self.memory_manager.tick()

        # ---- 1. Unblock WAITING processes when timer expires ----
        for p in self.process_table:
            if p.state == "WAITING":
                p.wait_timer -= 1
                if p.wait_timer <= 0:
                    p.state = "READY"
                    if p not in self.ready_queue:
                        self.ready_queue.append(p)

        # ---- 2. Clean up terminated ----
        for p in [x for x in self.process_table if x.state == "TERMINATED"]:
            self.memory_manager.free(p.pid)
            if self.foreground_process is p:
                self.foreground_process = next(
                    (x for x in self.process_table if x.pid == 1), None
                )
            if self._bg_current is p:
                self._bg_current = None
            self.ready_queue = [x for x in self.ready_queue if x is not p]
        self.process_table = [p for p in self.process_table
                              if p.state != "TERMINATED"]

        if not self.process_table:
            self.current_process = None
            self._update_load(False)
            return

        # ---- 3. Ensure valid foreground ----
        if self.foreground_process not in self.process_table:
            self.foreground_process = self.process_table[0]

        # ---- 4. Run foreground every frame — never preempted ----
        fg = self.foreground_process
        fg.state = "RUNNING"
        self.ready_queue = [p for p in self.ready_queue if p is not fg]
        fg.run_for_tick(background=False)
        fg.cpu_time      += 1
        self.current_process = fg
        self._update_load(True)

        # ---- 5. Background round-robin ----
        bg_list = [p for p in self.process_table
                   if p is not fg and p.state in ("READY", "RUNNING")]

        for p in bg_list:
            if p not in self.ready_queue:
                self.ready_queue.append(p)
        self.ready_queue = [p for p in self.ready_queue
                            if p in bg_list or p is fg]

        for p in bg_list:
            if p.state == "RUNNING":
                p.state = "READY"

        if bg_list:
            if (self._bg_current is None or
                    self._bg_current not in bg_list or
                    self._bg_quantum <= 0):
                next_bg = next(
                    (p for p in self.ready_queue if p in bg_list), None
                )
                if next_bg != self._bg_current:
                    self.context_switches += 1
                    self.last_switch_tick  = self.tick
                    self.ctx_flash         = self.CTX_FLASH_TICKS
                self._bg_current = next_bg
                self._bg_quantum = self.time_quantum

            if self._bg_current:
                self._bg_current.run_for_tick(background=True)
                self._bg_current.cpu_time += 1
                self._bg_quantum -= 1

        if self.ctx_flash > 0:
            self.ctx_flash -= 1

    def _update_load(self, active):
        self._load_buf[self._load_idx] = 1 if active else 0
        self._load_idx = (self._load_idx + 1) % 60
        self.cpu_load  = int(sum(self._load_buf) / 60 * 100)

    def get_all_processes(self):
        return self.process_table

    def get_ready_queue(self):
        return [p for p in self.ready_queue
                if p is not self.foreground_process]

    def get_memory_used(self):
        return sum(p.memory_needed for p in self.process_table)