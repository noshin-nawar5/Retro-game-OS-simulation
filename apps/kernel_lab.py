import random
from apps.ui import (
    C_PANEL, C_BORDER, C_BORDER_DIM,
    C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
    C_AMBER, C_RED, C_BLUE, C_CYAN, C_CYAN_DIM,
    C_WHITE, C_GREY, C_GREY_DIM,
    pid_color, draw_progress_bar
)
from kernel.process import Process

W, H     = 160, 144
_BG      = (4,   6,  10)
_PANEL   = (7,  11,  18)
_HDR     = (10, 16,  30)
_ROW_A   = (9,  13,  22)
_ROW_B   = (7,  10,  17)


class KERNAL:

    MAX_LOG = 10

    def __init__(self, os_api):
        self.os         = os_api
        self._frame     = 0
        self._log       = []
        self._prev_ctx  = 0
        self._prev_pids = set()
        self._sim_timer = 0

    # ─────────────────────────────────────────────────────────────────
    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        self._frame += 1
        sched = self.os.scheduler

        # Detect context switches → log
        if sched.context_switches != self._prev_ctx:
            self._prev_ctx = sched.context_switches
            fg = sched.foreground_process
            self._push("CTX SWITCH  PID " + str(fg.pid if fg else "?"), C_AMBER)

        # Detect process births / deaths → log
        cur = {p.pid for p in sched.get_all_processes()}
        for pid in sorted(cur - self._prev_pids):
            self._push("PID " + str(pid) + " ADMITTED", C_GREEN)
        for pid in sorted(self._prev_pids - cur):
            self._push("PID " + str(pid) + " TERMINATED", C_RED)
        self._prev_pids = cur

        # Simulate random I/O blocks on background processes
        self._sim_timer += 1
        if self._sim_timer > 180 + random.randint(0, 90):
            self._sim_timer = 0
            bg = [p for p in sched.get_all_processes()
                  if p is not sched.foreground_process and p.state == "READY"]
            if bg:
                p            = random.choice(bg)
                p.state      = "WAITING"
                p.wait_timer = random.randint(25, 60)
                self._push("PID " + str(p.pid) + " I/O BLOCK", C_CYAN)

        self._draw(sched)

    # ─────────────────────────────────────────────────────────────────
    def _draw(self, sched):
        self.os.draw_rect(0, 0, W, H, _BG)
        self._title(sched)
        self._cpu_panel(sched)
        self._scheduler_panel(sched)
        self._process_table(sched)
        self._log_strip()

    # ── TITLE BAR  y 0-8 ─────────────────────────────────────────────
    def _title(self, sched):
        self.os.draw_rect(0, 0, W, 9, _HDR)
        self.os.draw_rect(0, 8, W, 1, C_BORDER)
        # Coloured left accent
        self.os.draw_rect(0, 0, 3, 9, C_GREEN)
        self.os.draw_text(5,  2, "KERNEL LAB", color=C_GREEN)
        # Tick counter top-right
        self.os.draw_text(100, 2,
            "TICK " + str(sched.tick % 99999), color=C_GREEN_DARK)

    # ── CPU PANEL  x 0-78  y 9-55 ────────────────────────────────────
    def _cpu_panel(self, sched):
        x, y, w, h = 0, 9, 79, 47

        # Panel shell
        self.os.draw_rect(x, y, w, h, _PANEL)
        self.os.draw_border(x, y, w, h, C_BORDER)

        # Header bar — flashes AMBER on context switch
        hdr_col = C_AMBER if sched.ctx_flash > 0 else (12, 28, 12)
        self.os.draw_rect(x+1, y+1, w-2, 8, hdr_col)
        self.os.draw_text(x+3, y+2, "CPU", color=C_GREEN)

        # Flash indicator dot on right of header
        dot = C_AMBER if sched.ctx_flash > 0 else (20, 30, 20)
        self.os.draw_rect(x+w-9, y+2, 6, 5, dot)

        fg    = sched.foreground_process
        pid   = fg.pid  if fg else 0
        pc    = pid_color(pid) if fg else C_GREY
        state = fg.state if fg else "IDLE"

        # ── Running process ──────────────────────────────────────────
        # Label
        self.os.draw_rect(x+1, y+10, w-2, 1, C_BORDER_DIM)
        self.os.draw_text(x+3, y+12, "RUNNING PROCESS", color=C_GREY)

        # PID badge — coloured box
        self.os.draw_rect(x+3,  y+20, 22, 9, (14, 20, 35))
        self.os.draw_border(x+3, y+20, 22, 9, pc)
        self.os.draw_text(x+5,  y+22, "P" + str(pid).zfill(2), color=pc)

        # State text
        state_col = (C_GREEN  if state == "RUNNING" else
                     C_CYAN   if state == "WAITING" else C_AMBER)
        self.os.draw_text(x+28, y+22, state[:7], color=state_col)

        # ── Load bar ─────────────────────────────────────────────────
        self.os.draw_rect(x+1, y+31, w-2, 1, C_BORDER_DIM)
        self.os.draw_text(x+3, y+33, "LOAD", color=C_GREY)
        # Bar track + fill
        self.os.draw_rect(x+28, y+33, w-31, 6, (12, 18, 28))
        filled = int((w-31) * sched.cpu_load / 100)
        if filled:
            # Colour shifts: green<50% amber<80% red>=80%
            bar_col = (C_GREEN  if sched.cpu_load < 50 else
                       C_AMBER  if sched.cpu_load < 80 else C_RED)
            self.os.draw_rect(x+28, y+33, filled, 6, bar_col)
        # Percentage label
        pct_str = str(sched.cpu_load) + "%"
        self.os.draw_text(x+3, y+41, pct_str, color=C_GREEN_DIM)

        # ── CTX flash legend ─────────────────────────────────────────
        self.os.draw_text(x+28, y+41,
            "CTX " + str(sched.context_switches), color=C_GREY_DIM)

    # ── SCHEDULER PANEL  x 81-159  y 9-55 ───────────────────────────
    def _scheduler_panel(self, sched):
        x, y, w, h = 81, 9, 79, 47

        self.os.draw_rect(x, y, w, h, _PANEL)
        self.os.draw_border(x, y, w, h, C_BORDER)
        self.os.draw_rect(x+1, y+1, w-2, 8, (22, 17, 6))
        self.os.draw_text(x+3, y+2, "SCHEDULER", color=C_AMBER)

        # ── Round-robin quantum bar ──────────────────────────────────
        self.os.draw_rect(x+1, y+10, w-2, 1, C_BORDER_DIM)
        self.os.draw_text(x+3, y+12, "QUANTUM (time slice)", color=C_GREY)

        q_max = sched.time_quantum
        q_rem = max(0, sched._bg_quantum)
        # Track
        self.os.draw_rect(x+3, y+20, w-6, 6, (18, 14, 5))
        # Fill — shrinks as quantum ticks down
        q_fill = int((w-6) * q_rem / max(q_max, 1))
        if q_fill:
            self.os.draw_rect(x+3, y+20, q_fill, 6, C_AMBER)
        # Tick marks every quantum/5
        for i in range(1, 5):
            mx2 = x + 3 + int((w-6) * i / 5)
            self.os.draw_rect(mx2, y+20, 1, 6, (30, 22, 8))

        self.os.draw_text(x+3, y+28,
            str(q_rem) + "/" + str(q_max) + " TICKS LEFT", color=C_AMBER)

        # ── Ready queue ──────────────────────────────────────────────
        self.os.draw_rect(x+1, y+35, w-2, 1, C_BORDER_DIM)
        self.os.draw_text(x+3, y+37, "READY QUEUE  (next->)", color=C_GREY)

        rq = sched.get_ready_queue()
        # Show up to 5 slots
        SLOTS  = 5
        SLOT_W = 14
        for i in range(SLOTS):
            sx2 = x + 3 + i * (SLOT_W + 1)
            sy2 = y + 46
            if i < len(rq):
                p   = rq[i]
                pc2 = pid_color(p.pid)
                self.os.draw_rect(sx2, sy2, SLOT_W, 8, (16, 20, 32))
                self.os.draw_border(sx2, sy2, SLOT_W, 8, pc2)
                self.os.draw_text(sx2+2, sy2+2,
                    "P" + str(p.pid), color=pc2)
            else:
                # Empty slot — dim box
                self.os.draw_rect(sx2, sy2, SLOT_W, 8, (9, 11, 18))
                self.os.draw_border(sx2, sy2, SLOT_W, 8, C_BORDER_DIM)
                # Dashes inside
                self.os.draw_text(sx2+3, sy2+2, "--", color=C_GREY_DIM)

        # Arrow showing direction of execution
        ax = x + 3 + SLOTS * (SLOT_W + 1) + 2
        self.os.draw_text(ax, y + 48, ">CPU", color=C_GREEN_DARK)

    # ── PROCESS TABLE  y 56-127 ──────────────────────────────────────
    def _process_table(self, sched):
        processes = sched.get_all_processes()
        tx, ty, tw, th = 0, 56, W, 72

        self.os.draw_rect(tx, ty, tw, th, _PANEL)
        self.os.draw_border(tx, ty, tw, th, C_BORDER)

        # Header strip
        self.os.draw_rect(tx+1, ty+1, tw-2, 8, (14, 10, 26))
        self.os.draw_text(tx+3, ty+2, "PROCESS TABLE", color=C_BLUE)

        # Column header row
        hy = ty + 10
        self.os.draw_rect(tx+1, hy, tw-2, 8, (10, 13, 24))
        self.os.draw_rect(tx+1, hy+8, tw-2, 1, C_BORDER)
        hc = (55, 75, 140)
        # Columns: PID(16) | NAME(46) | STATE(28) | MEM(18) | CPU BAR(rest)
        self.os.draw_text(tx+4,   hy+1, "PID",   color=hc)
        self.os.draw_text(tx+22,  hy+1, "NAME",  color=hc)
        self.os.draw_text(tx+70,  hy+1, "STATE", color=hc)
        self.os.draw_text(tx+102, hy+1, "MEM",   color=hc)
        self.os.draw_text(tx+120, hy+1, "  CPU%", color=hc)

        # Process rows — 11px each
        ROW_H   = 11
        start_y = hy + 9
        max_cpu = max((p.cpu_time for p in processes), default=1)

        for i, p in enumerate(processes):
            ry = start_y + i * ROW_H
            if ry + ROW_H > ty + th - 1:
                break

            # Alternating row background
            self.os.draw_rect(tx+1, ry, tw-2, ROW_H, _ROW_A if i%2==0 else _ROW_B)

            # ── State determines stripe + text colour ────────────────
            if p.state == "RUNNING":
                stripe, tc = C_GREEN, C_GREEN
            elif p.state == "WAITING":
                stripe, tc = C_CYAN,  C_CYAN
            elif p.state == "READY":
                stripe, tc = C_AMBER, C_AMBER
            else:
                stripe, tc = C_GREY,  C_GREY

            # 3px left stripe = visual state indicator
            self.os.draw_rect(tx+1, ry, 3, ROW_H, stripe)

            # Foreground = bright top edge
            if p is sched.foreground_process:
                self.os.draw_rect(tx+1, ry, tw-2, 1, (35, 55, 110))

            pc = pid_color(p.pid)

            # PID: coloured square dot + number
            self.os.draw_rect(tx+5, ry+3, 4, 5, pc)
            self.os.draw_text(tx+11, ry+3, str(p.pid), color=pc)

            # Name
            self.os.draw_text(tx+22, ry+3,
                p.app.__class__.__name__[:7], color=tc)

            # State label — coloured, easy to read
            st_lbl = {"RUNNING": "RUN", "READY": "RDY",
                      "WAITING": "WAIT", "TERMINATED": "END"}.get(p.state, p.state[:4])
            self.os.draw_text(tx+70, ry+3, st_lbl, color=stripe)

            # Waiting countdown bar (only when WAITING)
            if p.state == "WAITING":
                self.os.draw_rect(tx+88, ry+4, 12, 3, (10, 25, 28))
                wfill = int(12 * p.wait_timer / 60)
                if wfill:
                    self.os.draw_rect(tx+88, ry+4, wfill, 3, C_CYAN)

            # Memory blocks
            self.os.draw_text(tx+102, ry+3, str(p.memory_needed), color=C_GREEN_DIM)

            # CPU usage bar (proportional to cpu_time)
            bar_x = tx + 120
            bar_w = tw - 122
            self.os.draw_rect(bar_x, ry+3, bar_w, 5, (10, 14, 22))
            cpu_fill = int(bar_w * p.cpu_time / max_cpu)
            if cpu_fill:
                self.os.draw_rect(bar_x, ry+3, cpu_fill, 5, pc)
            # CPU time number at end
            self.os.draw_text(bar_x + bar_w - 12, ry+3,
                str(p.cpu_time)[-3:], color=C_GREY_DIM)

            # Divider
            self.os.draw_rect(tx+1, ry+ROW_H-1, tw-2, 1, C_BORDER_DIM)

    # ── LOG STRIP  y 128-135 ─────────────────────────────────────────
    def _log_strip(self):
        self.os.draw_rect(0, 128, W, 8, (6, 8, 14))
        self.os.draw_rect(0, 128, W, 1, C_BORDER_DIM)
        self.os.draw_text(2, 130, "LOG:", color=C_GREY_DIM)
        if self._log:
            txt, col = self._log[-1]
            self.os.draw_text(24, 130, txt[:22], color=col)

    # ── HELPER ───────────────────────────────────────────────────────
    def _push(self, text, col=None):
        self._log.append((text, col or C_GREEN_DIM))
        if len(self._log) > self.MAX_LOG:
            self._log = self._log[-self.MAX_LOG:]