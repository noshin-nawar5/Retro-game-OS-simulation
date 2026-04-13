class RoundRobinScheduler:
    """
    Foreground process runs EVERY frame — never preempted.
    Background processes share CPU via round-robin (no drawing).
    current_process always points to the foreground process so
    dashboard and syscalls can read it safely.
    """

    def __init__(self, time_quantum, memory_manager):
        self.time_quantum       = time_quantum
        self.memory_manager     = memory_manager
        self.process_table      = []
        self.pid_counter        = 1
        self.foreground_process = None
        self.current_process    = None   # always = foreground (for dashboard)
        self.tick               = 0
        self.context_switches   = 0
        self._bg_queue          = []
        self._bg_current        = None
        self._bg_quantum        = 0

    def generate_pid(self):
        pid = self.pid_counter
        self.pid_counter += 1
        return pid

    def add_process(self, process):
        base = self.memory_manager.allocate(process.pid, process.memory_needed)
        if base is None:
            print(f"[Scheduler] OOM — cannot admit PID {process.pid}")
            return False
        process.memory_base = base
        process.state       = "READY"
        self.process_table.append(process)
        print(f"[Scheduler] PID {process.pid} ({process.app.__class__.__name__}) admitted")
        return True

    def kill_foreground(self):
        if self.foreground_process:
            self.foreground_process.state = "TERMINATED"

    def schedule(self):
        self.tick += 1

        # 1. Clean up terminated processes
        for p in [x for x in self.process_table if x.state == "TERMINATED"]:
            self.memory_manager.free(p.pid)
            print(f"[Scheduler] PID {p.pid} freed")
            if self.foreground_process is p:
                # Restore to PID 1 (launcher)
                self.foreground_process = next(
                    (x for x in self.process_table if x.pid == 1), None
                )
            if self._bg_current is p:
                self._bg_current = None
            self._bg_queue = [x for x in self._bg_queue if x is not p]
        self.process_table = [p for p in self.process_table if p.state != "TERMINATED"]

        if not self.process_table:
            self.current_process = None
            return

        # 2. Ensure foreground is valid
        if self.foreground_process not in self.process_table:
            self.foreground_process = self.process_table[0]

        # 3. Run foreground every frame — no exceptions, no preemption
        fg = self.foreground_process
        fg.state = "RUNNING"
        fg.run_for_tick(background=False)
        fg.cpu_time      += 1
        self.current_process = fg   # keep attribute in sync for dashboard

        # 4. Background round-robin (no drawing, invisible to screen)
        bg_list = [p for p in self.process_table if p is not fg]
        for p in bg_list:
            if p.state == "RUNNING":
                p.state = "READY"

        # Sync bg queue
        in_queue = {p.pid for p in self._bg_queue}
        for p in bg_list:
            if p.pid not in in_queue:
                self._bg_queue.append(p)
        self._bg_queue = [p for p in self._bg_queue if p in bg_list]

        if self._bg_queue:
            if self._bg_current is None or self._bg_quantum <= 0:
                if self._bg_current is not None:
                    self._bg_queue.append(self._bg_current)
                self._bg_current = self._bg_queue.pop(0)
                self._bg_quantum = self.time_quantum
                self.context_switches += 1
            self._bg_current.run_for_tick(background=True)
            self._bg_current.cpu_time += 1
            self._bg_quantum -= 1

    def get_all_processes(self):
        return self.process_table

    def get_memory_used(self):
        return sum(p.memory_needed for p in self.process_table)