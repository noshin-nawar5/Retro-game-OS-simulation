from apps.ui import (C_BG, C_PANEL, C_PANEL_ALT, C_BORDER, C_BORDER_DIM,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_AMBER, C_RED, C_BLUE, C_CYAN, C_WHITE, C_GREY,
                     draw_progress_bar, pid_color)


class SystemMonitor:

    def __init__(self, os_api):
        self.os = os_api

    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        sched     = self.os.scheduler
        processes = sched.get_all_processes()

        # Background
        self.os.draw_rect(0, 0, 160, 144, (5, 7, 11))

        # ── TITLE BAR ────────────────────────────────────────────────
        self.os.draw_rect(0, 0, 160, 11, (12, 18, 32))
        self.os.draw_rect(0, 10, 160, 1, C_BORDER)
        self.os.draw_rect(0,  0,   3, 11, C_CYAN)
        self.os.draw_text(6,  2, "SYSTEM MONITOR", color=C_CYAN)
        self.os.draw_text(112, 2, "ESC=BACK",       color=(30, 50, 90))

        # ── KERNEL STATS ROW ─────────────────────────────────────────
        ky = 13
        self.os.draw_rect(0, ky, 160, 12, C_PANEL)
        self.os.draw_rect(0, ky+11, 160, 1, C_BORDER_DIM)

        self.os.draw_text(3,  ky+3, "TICK",  color=(40, 60, 100))
        self.os.draw_text(27, ky+3, str(sched.tick), color=C_BLUE)

        self.os.draw_text(60,  ky+3, "CTX",  color=(40, 60, 100))
        self.os.draw_text(84,  ky+3, str(sched.context_switches), color=C_AMBER)

        used = sched.memory_manager.get_used()
        self.os.draw_text(112, ky+3, "MEM",  color=(40, 60, 100))
        self.os.draw_text(130, ky+3, str(used) + "/256", color=C_GREEN)

        # ── COLUMN HEADERS ───────────────────────────────────────────
        hy = 27
        self.os.draw_rect(0, hy, 160, 9, (14, 20, 36))
        self.os.draw_rect(0, hy+8, 160, 1, C_BORDER)
        hdr_col = (50, 80, 140)
        self.os.draw_text(4,   hy+2, "PID",      color=hdr_col)
        self.os.draw_text(22,  hy+2, "PROCESS",  color=hdr_col)
        self.os.draw_text(76,  hy+2, "STATE",    color=hdr_col)
        self.os.draw_text(110, hy+2, "MEM",      color=hdr_col)
        self.os.draw_text(128, hy+2, "CPU",      color=hdr_col)

        # ── PROCESS ROWS ─────────────────────────────────────────────
        ROW_H   = 16
        START_Y = 37
        max_cpu = max((p.cpu_time for p in processes), default=1)

        for i, p in enumerate(processes):
            ry = START_Y + i * ROW_H
            if ry + ROW_H > 134:
                break

            bg = (10, 15, 24) if i % 2 == 0 else (8, 12, 20)
            self.os.draw_rect(0, ry, 160, ROW_H-1, bg)

            # State indicator stripe on left
            if p.state == "RUNNING":
                stripe = C_GREEN;  row_col = C_GREEN
            elif p.state == "READY":
                stripe = C_AMBER;  row_col = C_AMBER
            else:
                stripe = C_GREY;   row_col = C_GREY
            self.os.draw_rect(0, ry, 3, ROW_H-1, stripe)

            # PID colour dot
            pc = pid_color(p.pid)
            self.os.draw_rect(6, ry+4, 4, 5, pc)
            self.os.draw_text(13, ry+4, str(p.pid), color=row_col)

            # App name
            self.os.draw_text(22, ry+4, p.app.__class__.__name__[:9], color=row_col)

            # State badge
            if p.state == "RUNNING":
                bb, bc = (0, 40, 20),  C_GREEN
            elif p.state == "READY":
                bb, bc = (50, 35, 0),  C_AMBER
            else:
                bb, bc = (40, 10, 10), C_RED
            self.os.draw_rect(76,  ry+2, 30, 9, bb)
            self.os.draw_border(76, ry+2, 30, 9, bc)
            self.os.draw_text(78, ry+4, p.state[:5], color=bc)

            # Memory
            self.os.draw_text(110, ry+4, str(p.memory_needed), color=C_GREEN_DIM)

            # CPU time + bar
            self.os.draw_text(128, ry+4, str(p.cpu_time), color=C_GREEN_DIM)
            draw_progress_bar(self.os, 128, ry+11, 28, 2, p.cpu_time, max_cpu, pc)

            self.os.draw_rect(0, ry+ROW_H-1, 160, 1, C_BORDER_DIM)

        # ── FOOTER ───────────────────────────────────────────────────
        self.os.draw_rect(0, 134, 160, 10, C_PANEL)
        self.os.draw_rect(0, 134, 160,  1, C_BORDER_DIM)
        self.os.draw_text(4, 137,
            str(len(processes)) + " PROCS   Q=" + str(sched.time_quantum),
            color=(35, 55, 95))