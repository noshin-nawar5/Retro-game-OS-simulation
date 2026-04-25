from kernel.process import Process


class OS_API:
    def __init__(self, display, scheduler, input_device):
        self.display      = display
        self.scheduler    = scheduler
        self.input_device = input_device
        # Shared kernel event bus — games write here, OS Monitor reads here
        self._event_log  = []
        self._MAX_EVENTS = 20

    def draw_pixel(self, x, y, color):
        self.display.draw_pixel(x, y, color)

    def draw_text(self, x, y, text, color=(255, 255, 255)):
        self.display.draw_text(x, y, text, color)

    def draw_rect(self, x, y, w, h, color):
        self.display.draw_rect(x, y, w, h, color)

    def draw_border(self, x, y, w, h, color):
        self.display.draw_border(x, y, w, h, color)

    def clear_screen(self):
        self.display.clear()

    def get_input(self):
        return self.input_device.get_keys()

    def log_event(self, text, color=(0, 180, 80)):
  
        pid = self.get_pid()
        full = ("PID" + str(pid) + " " + text) if pid else text
        self._event_log.append((full, color))
        if len(self._event_log) > self._MAX_EVENTS:
            self._event_log = self._event_log[-self._MAX_EVENTS:]

    def exit_process(self):
        p = self.scheduler.current_process
        if p:
            p.state = "TERMINATED"

    def get_pid(self):
        p = self.scheduler.current_process
        return p.pid if p else None

    def create_process(self, app_class, memory_needed=10):
        pid     = self.scheduler.generate_pid()
        app     = app_class(self)
        process = Process(pid, app, memory_needed)
        if self.scheduler.add_process(process):
            self.scheduler.foreground_process = process

    def kill_foreground(self):
        self.scheduler.kill_foreground()

    def block_process(self, ticks=30):
        p = self.scheduler.current_process
        if p:
            p.state      = "WAITING"
            p.wait_timer = ticks