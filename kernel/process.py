class Process:

    HISTORY_LEN = 30

    def __init__(self, pid, app, memory_needed):
        self.pid           = pid
        self.app           = app
        self.memory_needed = memory_needed
        self.state         = "NEW"
        self.memory_base   = None
        self.cpu_time      = 0
        self.wait_timer    = 0
        self.cpu_history   = [0] * self.HISTORY_LEN
        self._h_idx        = 0

    def record_active(self, active: bool):
        self.cpu_history[self._h_idx] = 1 if active else 0
        self._h_idx = (self._h_idx + 1) % self.HISTORY_LEN

    def run_for_tick(self, background=False):
        if self.state == "TERMINATED":
            return
        if not background:
            self.app.update()
            self.record_active(True)
        else:
            if hasattr(self.app, "background_update"):
                self.app.background_update()
            self.record_active(False)