from apps.ui import (C_PANEL, C_BORDER, C_BORDER_DIM, C_BORDER_LIT,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_AMBER, C_BLUE, C_CYAN, C_WHITE, C_GREY,
                     pid_color)


class SystemDashboard:

    def __init__(self, os_api):
        self.os = os_api

    def update(self):
        pass  # called directly via draw_overlay() from main loop

    def draw_overlay(self):
        sched     = self.os.scheduler
        memory    = sched.memory_manager.get_memory_snapshot()
        processes = sched.get_all_processes()

        # current_process is always set by scheduler.schedule()
        fg = sched.current_process

        # ── TOP-RIGHT STATS BOX ──────────────────────────────────────
        bx, by, bw, bh = 88, 0, 72, 28

        # Background
        self.os.draw_rect(bx, by, bw, bh, (8, 12, 20))
        # Coloured title bar
        self.os.draw_rect(bx + 1, by, bw - 1, 9, (18, 30, 60))
        # Borders
        self.os.draw_border(bx, by, bw, bh, C_BORDER)
        # Bright top edge
        self.os.draw_rect(bx, by, bw, 1, C_BORDER_LIT)

        # Title text
        self.os.draw_text(bx + 3, by + 2, "KERNEL", color=C_BLUE)
        self.os.draw_text(bx + 45, by + 2, "STATS", color=C_CYAN)

        # Vertical divider
        for yy in range(by + 10, by + bh - 1):
            self.os.draw_pixel(bx + 36, yy, C_BORDER_DIM)

        # Left: CPU
        cpu_val = "PID" + str(fg.pid) if fg else "IDLE"
        cpu_col = pid_color(fg.pid) if fg else C_GREY
        self.os.draw_text(bx + 2,  by + 11, "CPU",   color=C_GREEN_DIM)
        self.os.draw_text(bx + 2,  by + 19, cpu_val, color=cpu_col)

        # Right: counters
        r = sum(1 for p in processes if p.state == "RUNNING")
        q = sum(1 for p in processes if p.state == "READY")
        self.os.draw_text(bx + 39, by + 11,
                          "R" + str(r) + " Q" + str(q), color=C_GREEN_DIM)
        self.os.draw_text(bx + 39, by + 19,
                          "T" + str(sched.tick % 9999),  color=C_AMBER)

        # ── MEMORY BAR — bottom strip ────────────────────────────────
        bar_y = 137
        self.os.draw_rect(0, bar_y, 160, 7, (8, 12, 20))
        self.os.draw_rect(0, bar_y, 160, 1, C_BORDER_DIM)

        # "MEM" label
        self.os.draw_text(2, bar_y + 1, "MEM", color=C_GREEN_DARK)

        # Bar track
        bx2, bw2 = 22, 126
        self.os.draw_rect(bx2, bar_y + 1, bw2, 5, (15, 20, 30))

        # Per-PID coloured segments
        pmap = {p.pid: pid_color(p.pid) for p in processes}
        for i in range(bw2):
            idx = int(i * 256 / bw2)
            pid_val = memory[idx] if idx < 256 else 0
            col = pmap.get(pid_val, (20, 28, 40)) if pid_val else (20, 28, 40)
            self.os.draw_rect(bx2 + i, bar_y + 2, 1, 3, col)

        # Usage %
        used = sum(1 for c in memory if c != 0)
        pct  = used * 100 // 256
        self.os.draw_text(bx2 + bw2 + 2, bar_y + 1,
                          str(pct) + "%", color=C_GREEN_DIM)