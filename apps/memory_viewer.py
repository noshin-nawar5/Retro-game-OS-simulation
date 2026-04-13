from apps.ui import (C_BG, C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_CYAN, C_WHITE, C_GREY, C_GREY_DIM,
                     pid_color)


class MemoryViewer:
    FREE  = (14, 20, 30)
    CELL  = 4
    COLS  = 32
    ROWS  = 8
    OX    = 14
    OY    = 14

    def __init__(self, os_api):
        self.os = os_api

    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        memory    = self.os.scheduler.memory_manager.get_memory_snapshot()
        processes = self.os.scheduler.get_all_processes()
        pmap  = {p.pid: pid_color(p.pid) for p in processes}
        pname = {p.pid: p.app.__class__.__name__[:6] for p in processes}

        # Background
        self.os.draw_rect(0, 0, 160, 144, (5, 7, 12))

        # Title bar
        self.os.draw_rect(0, 0, 160, 11, (10, 15, 26))
        self.os.draw_rect(0, 10, 160, 1, C_BORDER)
        self.os.draw_rect(0,  0,  3, 11, C_CYAN)
        self.os.draw_text(6,  2, "MEMORY VIEWER", color=C_CYAN)
        self.os.draw_text(112, 2, "ESC=BACK",      color=(25, 40, 70))

        # Grid border
        gw = self.COLS * self.CELL + 2
        gh = self.ROWS * self.CELL + 2
        self.os.draw_border(self.OX-1, self.OY-1, gw, gh, C_BORDER)

        # Grid cells
        for idx in range(256):
            col = idx % self.COLS
            row = idx // self.COLS
            x   = self.OX + col * self.CELL
            y   = self.OY + row * self.CELL
            pid = memory[idx]
            if pid:
                c = pmap.get(pid, C_GREEN_DIM)
                self.os.draw_rect(x, y, self.CELL-1, self.CELL-1, c)
                # Highlight pixel
                self.os.draw_pixel(x, y, tuple(min(255, v+60) for v in c))
            else:
                self.os.draw_rect(x, y, self.CELL-1, self.CELL-1, self.FREE)

        # Right stats panel
        px = self.OX + self.COLS * self.CELL + 4
        pw = 160 - px
        self.os.draw_rect(px-1, self.OY-1, pw+1, gh, (8, 12, 20))
        self.os.draw_border(px-1, self.OY-1, pw+1, gh, C_BORDER_DIM)

        used = sum(1 for c in memory if c != 0)
        free = 256 - used
        pct  = used * 100 // 256

        self.os.draw_text(px+1, self.OY+2,  "USED", color=(40, 70, 120))
        self.os.draw_text(px+1, self.OY+10, str(used), color=C_GREEN)
        self.os.draw_text(px+1, self.OY+20, "FREE", color=(40, 70, 120))
        self.os.draw_text(px+1, self.OY+28, str(free), color=C_GREEN)
        self.os.draw_text(px+1, self.OY+38, str(pct)+"%", color=C_GREEN_DIM)

        # Vertical usage bar
        bx  = px + 5
        by  = self.OY + 50
        bh  = gh - 56
        fil = max(0, int(bh * used / 256))
        self.os.draw_rect(bx, by, 6, bh, (12, 18, 28))
        self.os.draw_border(bx, by, 6, bh, C_BORDER_DIM)
        if fil:
            self.os.draw_rect(bx+1, by+bh-fil, 4, fil, C_GREEN)

        # Legend strip
        ly = self.OY + gh + 3
        self.os.draw_rect(0, ly, 160, 144-ly, (8, 12, 20))
        self.os.draw_rect(0, ly, 160, 1, C_BORDER_DIM)
        # Free swatch
        self.os.draw_rect(3, ly+3, 6, 5, self.FREE)
        self.os.draw_border(3, ly+3, 6, 5, C_BORDER_DIM)
        self.os.draw_text(11, ly+3, "FREE", color=(30, 50, 80))
        lx = 42
        for p in processes:
            c = pmap[p.pid]
            self.os.draw_rect(lx, ly+3, 6, 5, c)
            nm = pname[p.pid]
            self.os.draw_text(lx+8, ly+3, nm, color=c)
            lx += 8 + len(nm)*6 + 4
            if lx > 148:
                break