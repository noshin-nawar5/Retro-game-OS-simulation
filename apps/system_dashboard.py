from apps.ui import (C_BORDER_DIM, C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_AMBER, C_GREY_DIM, pid_color, draw_progress_bar)


class SystemDashboard:

    def __init__(self, os_api):
        self.os = os_api

    def update(self):
        pass

    def draw_overlay(self):
        sched     = self.os.scheduler
        memory    = sched.memory_manager.get_memory_snapshot()
        processes = sched.get_all_processes()

        bar_y = 137

        # Strip background
        self.os.draw_rect(0, bar_y, 160, 7, (7, 10, 17))
        self.os.draw_rect(0, bar_y, 160, 1, C_BORDER_DIM)

        # CPU load bar
        self.os.draw_text(1, bar_y+1, "CPU", color=C_GREEN_DARK)
        draw_progress_bar(self.os, 19, bar_y+2, 28, 3,
                          sched.cpu_load, 100, C_GREEN)

        # Context-switch flash dot
        dot_col = C_AMBER if sched.ctx_flash > 0 else (18, 24, 36)
        self.os.draw_rect(49, bar_y+1, 6, 5, dot_col)

        # MEM label
        self.os.draw_text(57, bar_y+1, "MEM", color=C_GREEN_DARK)

        # Per-PID memory bar
        bx2, bw2 = 70, 70
        self.os.draw_rect(bx2, bar_y+1, bw2, 5, (11, 17, 27))
        pmap = {p.pid: pid_color(p.pid) for p in processes}
        for i in range(bw2):
            idx    = int(i * 256 / bw2)
            pv     = memory[idx] if idx < 256 else 0
            col    = pmap.get(pv, (17, 24, 36)) if pv else (17, 24, 36)
            self.os.draw_rect(bx2+i, bar_y+2, 1, 3, col)

        # Usage %
        used = sum(1 for c in memory if c != 0)
        pct  = used * 100 // 256
        self.os.draw_text(bx2+bw2+2, bar_y+1, str(pct)+"%", color=C_GREEN_DIM)