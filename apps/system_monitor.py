from kernel.process import Process
from apps.ui import (C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_GREEN, C_GREEN_DIM,
                     C_AMBER, C_RED, C_BLUE, C_CYAN, C_CYAN_DIM,
                     C_WHITE, C_GREY, C_GREY_DIM,
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

        self.os.draw_rect(0, 0, 160, 144, (4, 6, 10))

        # ── TITLE ────────────────────────────────────────────────────
        self.os.draw_rect(0, 0, 160, 11, (9, 14, 26))
        self.os.draw_rect(0, 10, 160, 1, C_BORDER)
        self.os.draw_rect(0,  0,  3, 11, C_CYAN)
        self.os.draw_text(6,  2, "TASK CTRL", color=C_CYAN)
        self.os.draw_text(112, 2, "ESC=BACK",       color=(22, 36, 72))

        # ── KERNEL STATS ─────────────────────────────────────────────
        ky = 13
        self.os.draw_rect(0, ky, 160, 13, C_PANEL)
        self.os.draw_rect(0, ky+12, 160, 1, C_BORDER_DIM)

        self.os.draw_text(3,  ky+2, "TICK", color=C_GREY)
        self.os.draw_text(27, ky+2, str(sched.tick % 9999), color=C_BLUE)

        ctx_col = C_AMBER if sched.ctx_flash > 0 else C_GREEN_DIM
        self.os.draw_text(55, ky+2, "CTX", color=C_GREY)
        self.os.draw_text(75, ky+2, str(sched.context_switches), color=ctx_col)

        used = sched.memory_manager.get_used()
        self.os.draw_text(100, ky+2, "MEM", color=C_GREY)
        self.os.draw_text(118, ky+2, str(used)+"/256", color=C_GREEN)

        # CPU load bar
        self.os.draw_text(3,   ky+8, "CPU", color=C_GREY)
        draw_progress_bar(self.os, 22, ky+9, 100, 3,
                          sched.cpu_load, 100, C_GREEN)
        self.os.draw_text(124, ky+8, str(sched.cpu_load)+"%", color=C_GREEN_DIM)

        # ── COLUMN HEADERS ───────────────────────────────────────────
        hy = 28
        self.os.draw_rect(0, hy, 160, 9, (11, 17, 30))
        self.os.draw_rect(0, hy+8, 160, 1, C_BORDER)
        hc = (44, 72, 128)
        self.os.draw_text(4,   hy+2, "PID",      color=hc)
        self.os.draw_text(28,  hy+2, "PROCESS",  color=hc)
        self.os.draw_text(74,  hy+2, "STATE",    color=hc)
        self.os.draw_text(108, hy+2, "MEM",      color=hc)
        self.os.draw_text(128, hy+2, "CPU", color=hc)

        # ── PROCESS ROWS ─────────────────────────────────────────────
        ROW_H   = 16
        START_Y = 38
        max_cpu = max((p.cpu_time for p in processes), default=1)

        for i, p in enumerate(processes):
            ry = START_Y + i * ROW_H
            if ry + ROW_H > 130:
                break

            bg = (8, 13, 21) if i % 2 == 0 else (6, 10, 17)
            self.os.draw_rect(0, ry, 160, ROW_H-1, bg)

            if p is sched.foreground_process:
                self.os.draw_rect(0, ry, 160, 1, (28, 42, 80))

            if p.state == "RUNNING":
                stripe, rc = C_GREEN, C_GREEN
            elif p.state == "WAITING":
                stripe, rc = C_CYAN, C_CYAN
            elif p.state == "READY":
                stripe, rc = C_AMBER, C_AMBER
            else:
                stripe, rc = C_GREY, C_GREY
            self.os.draw_rect(0, ry, 3, ROW_H-1, stripe)

            pc = pid_color(p.pid)
            self.os.draw_rect(5, ry+4, 4, 5, pc)
            self.os.draw_text(12, ry+4, str(p.pid), color=rc)
            self.os.draw_text(22, ry+4, p.app.__class__.__name__[:9], color=rc)

            # State badge
            if p.state == "RUNNING":
                bb, bc = (0, 36, 17),  C_GREEN
            elif p.state == "WAITING":
                bb, bc = (0, 28, 36),  C_CYAN
            elif p.state == "READY":
                bb, bc = (46, 32, 0),  C_AMBER
            else:
                bb, bc = (36, 10, 10), C_RED
            self.os.draw_rect(74, ry+2, 30, 9, bb)
            self.os.draw_border(74, ry+2, 30, 9, bc)
            lbl = p.state[:4] if p.state != "WAITING" else "WAIT"
            self.os.draw_text(76, ry+4, lbl, color=bc)

            if p.state == "WAITING":
                draw_progress_bar(self.os, 74, ry+11, 30, 2,
                                  p.wait_timer, 60, C_CYAN_DIM)

            self.os.draw_text(108, ry+4, str(p.memory_needed), color=C_GREEN_DIM)

            # Sparkline (last 12 ticks)
            sx   = 124
            idx0 = (p._h_idx - 12) % Process.HISTORY_LEN
            for j in range(12):
                val = p.cpu_history[(idx0+j) % Process.HISTORY_LEN]
                sc  = pc if val else C_GREY_DIM
                bh  = 5 if val else 2
                self.os.draw_rect(sx + j*3, ry+3 + (6-bh), 2, bh, sc)

            self.os.draw_rect(0, ry+ROW_H-1, 160, 1, C_BORDER_DIM)

        # ── READY QUEUE STRIP ─────────────────────────────
        qy = 124
        self.os.draw_rect(0, qy, 160, 14, C_PANEL)
        self.os.draw_rect(0, qy, 160, 1, C_BORDER_DIM)

        self.os.draw_text(3, qy+4, "QUEUE", color=C_GREY)

        rq = sched.get_ready_queue()[:5]

        start_x = 38
        box_w = 18
        gap = 4

        for i, p in enumerate(rq):
            qx = start_x + i * (box_w + gap)

            pc = pid_color(p.pid)

            self.os.draw_rect(qx, qy+2, box_w, 9, (14,18,30))
            self.os.draw_border(qx, qy+2, box_w, 9, pc)

            label = str(p.pid)
            self.os.draw_text(qx+5, qy+4, label, color=pc)

        if not rq:
            self.os.draw_text(38, qy+4, "EMPTY", color=C_GREY_DIM)


