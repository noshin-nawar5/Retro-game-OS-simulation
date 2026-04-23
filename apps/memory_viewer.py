from apps.ui import (C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_AMBER, C_RED, C_CYAN, C_CYAN_DIM,
                     C_WHITE, C_GREY, C_GREY_DIM,
                     pid_color, draw_progress_bar)


class MemoryViewer:
    FREE = (11, 17, 27)
    CELL = 4
    COLS = 32
    ROWS = 8
    OX   = 1
    OY   = 13

    def __init__(self, os_api):
        self.os = os_api

    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        sched     = self.os.scheduler
        memory    = sched.memory_manager.get_memory_snapshot()
        change    = sched.memory_manager.change_age
        fade_max  = sched.memory_manager.FADE_TICKS
        processes = sched.get_all_processes()

        pmap  = {p.pid: pid_color(p.pid) for p in processes}
        pname = {p.pid: p.app.__class__.__name__[:7].upper() for p in processes}

        self.os.draw_rect(0, 0, 160, 144, (4, 6, 10))

        # ── TITLE BAR ─────────────────────────────
        self.os.draw_rect(0, 0, 160, 11, (8, 13, 23))
        self.os.draw_rect(0, 10, 160, 1, C_BORDER)
        self.os.draw_rect(0, 0, 3, 11, C_CYAN)

        self.os.draw_text(6, 2, "MEMORY GRID", color=C_CYAN)
        self.os.draw_text(112, 2, "ESC=BACK", color=(20, 36, 68))

        # ── GRID ──────────────────────────────────
        C  = self.CELL
        gw = self.COLS * C + 2
        gh = self.ROWS * C + 2

        self.os.draw_border(self.OX-1, self.OY-1, gw, gh, C_BORDER)

        for idx in range(256):
            col = idx % self.COLS
            row = idx // self.COLS

            cx = self.OX + col * C
            cy = self.OY + row * C

            pid = memory[idx]
            age = change[idx]

            if pid:
                base = pmap.get(pid, C_GREEN_DIM)

                if age > 0:
                    t = age / fade_max
                    draw_col = tuple(
                        int(base[k] + (255-base[k]) * t)
                        for k in range(3)
                    )
                else:
                    draw_col = base

                self.os.draw_rect(cx, cy, C-1, C-1, draw_col)
                self.os.draw_pixel(
                    cx, cy,
                    tuple(min(255, v+50) for v in draw_col)
                )

            else:
                if age > 0:
                    t = age / fade_max
                    draw_col = (int(88*t), int(12*t), int(12*t))
                else:
                    draw_col = self.FREE

                self.os.draw_rect(cx, cy, C-1, C-1, draw_col)

        # ── RIGHT STATS PANEL ─────────────────────
        px  = self.OX + self.COLS * C + 3
        pw  = max(20, 160 - px - 1)
        phy = self.OY - 1
        phh = gh

        self.os.draw_rect(px-1, phy, pw+1, phh, (7,11,19))
        self.os.draw_border(px-1, phy, pw+1, phh, C_BORDER_DIM)

        used = sched.memory_manager.get_used()
        free = 256 - used
        pct  = used * 100 // 256
        frag = sched.memory_manager.fragmentation()

        self.os.draw_text(px+1, phy+2,  "USED", color=C_GREY)
        self.os.draw_text(px+1, phy+10, str(used), color=C_GREEN)

        self.os.draw_text(px+1, phy+20, "FREE", color=C_GREY)
        self.os.draw_text(px+1, phy+28, str(free), color=C_GREEN)

        self.os.draw_text(px+1, phy+38, str(pct)+"%", color=C_GREEN_DIM)

        # Usage bar
        bx  = px + 5
        by  = phy + 50
        bh  = phh - 56
        fil = max(0, int(bh * used / 256))

        self.os.draw_rect(bx, by, 6, bh, (10,15,25))
        self.os.draw_border(bx, by, 6, bh, C_BORDER_DIM)

        if fil:
            self.os.draw_rect(bx+1, by+bh-fil, 4, fil, C_GREEN)

        # ── FRAGMENTATION BAR ─────────────────────
        fy = self.OY + gh + 2

        self.os.draw_text(self.OX, fy, "FRAG", color=C_GREY)

        frag_col = (
            C_GREEN if frag < 0.3
            else (C_AMBER if frag < 0.6 else C_RED)
        )

        draw_progress_bar(
            self.os,
            self.OX + 26,
            fy + 1,
            self.COLS * C - 26,
            4,
            int(frag * 100),
            100,
            frag_col
        )

        self.os.draw_text(
            self.OX + self.COLS * C - 20,
            fy,
            str(int(frag*100)) + "%",
            color=frag_col
        )

        # ── LEGEND (FIXED COLUMN STYLE) ───────────
        ly = fy + 9

        self.os.draw_rect(0, ly, 160, 144-ly, (7,10,17))
        self.os.draw_rect(0, ly, 160, 1, C_BORDER_DIM)

        # FREE item
        self.os.draw_rect(2, ly+3, 6, 6, self.FREE)
        self.os.draw_border(2, ly+3, 6, 6, C_BORDER_DIM)
        self.os.draw_text(10, ly+4, "FREE", color=C_GREY)

        # Process legend in columns
        col_x = 44
        item_y = ly + 3
        row_gap = 10
        max_y = 128

        for p in processes:
            c = pmap[p.pid]
            nm = pname[p.pid]

            self.os.draw_rect(col_x, item_y, 6, 6, c)

            bc = (
                tuple(min(255, v+80) for v in c)
                if p is sched.foreground_process
                else C_BORDER_DIM
            )

            self.os.draw_border(col_x, item_y, 6, 6, bc)

            self.os.draw_text(col_x+8, item_y+1, nm, color=c)

            item_y += row_gap

            if item_y > max_y:
                item_y = ly + 3
                col_x += 52

        # ── MEMORY MAP BAR ────────────────────────
        tl_y = 144 - 6

        self.os.draw_rect(0, tl_y, 160, 6, (6,9,15))
        self.os.draw_rect(0, tl_y, 160, 1, C_BORDER_DIM)

        self.os.draw_text(1, tl_y+1, "MAP", color=(22,36,62))

        for i in range(152):
            idx = int(i * 256 / 152)
            pv  = memory[idx]

            col_c = (
                pmap.get(pv, self.FREE)
                if pv else self.FREE
            )

            self.os.draw_rect(7+i, tl_y+2, 1, 3, col_c)