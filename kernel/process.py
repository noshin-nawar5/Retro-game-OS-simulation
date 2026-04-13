class Process:
    def __init__(self, pid, app, memory_needed):
        self.pid           = pid
        self.app           = app
        self.memory_needed = memory_needed
        self.state         = "NEW"
        self.memory_base   = None
        self.cpu_time      = 0

    def run_for_tick(self, background=False):
        if self.state == "TERMINATED":
            return
        if not background:
            self.app.update()
        elif hasattr(self.app, "background_update"):
            self.app.background_update()