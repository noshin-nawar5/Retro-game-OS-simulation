import pygame
from apps.pong           import Pong
from apps.snake          import Snake
from apps.breakout       import Breakout
from apps.system_monitor import SystemMonitor
from apps.memory_viewer  import MemoryViewer
from apps.ui import (C_PANEL, C_PANEL_ALT, C_BORDER, C_BORDER_DIM, C_BORDER_LIT,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_BLUE, C_CYAN, C_AMBER, C_WHITE, C_GREY,
                     C_RED, C_PURPLE, C_BG)

# Colour tag per menu entry (icon bg colour, text colour)
ENTRY_COLORS = [
    ((20, 30, 80),  (80,  160, 255)),   # PONG     — blue
    ((10, 40, 20),  (0,   220, 100)),   # SNAKE    — green
    ((40, 15, 50),  (170,  90, 240)),   # BREAKOUT — purple
    ((10, 40, 40),  (60,  210, 210)),   # SYS MON  — cyan
    ((40, 30, 10),  (255, 185,  40)),   # MEM VIEW — amber
    ((40, 10, 10),  (220,  55,  55)),   # SHUTDOWN — red
]
MENU = [
    ("PONG",           "P", Pong,          10),
    ("SNAKE",          "S", Snake,         10),
    ("BREAKOUT",       "B", Breakout,      10),
    ("SYSTEM MONITOR", "M", SystemMonitor,  8),
    ("MEMORY VIEWER",  "V", MemoryViewer,   8),
    ("SHUTDOWN",       "X", None,           0),
]


class Launcher:

    def __init__(self, os_api):
        self.os         = os_api
        self.selected   = 0
        self.up_last    = False
        self.down_last  = False
        self.start_last = False
        self._frame     = 0

    def update(self):
        keys = self.os.get_input()
        self._frame += 1

        if keys["UP"] and not self.up_last:
            self.selected = (self.selected - 1) % len(MENU)
        if keys["DOWN"] and not self.down_last:
            self.selected = (self.selected + 1) % len(MENU)
        if keys["START"] and not self.start_last:
            _, _, app_class, mem = MENU[self.selected]
            if app_class is None:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            else:
                self.os.create_process(app_class, memory_needed=mem)

        self.up_last    = keys["UP"]
        self.down_last  = keys["DOWN"]
        self.start_last = keys["START"]
        self._draw()

    def _draw(self):
        W, H    = 160, 144
        ITEM_H  = 18
        START_Y = 22

        # Background
        self.os.draw_rect(0, 0, W, H, C_BG)

        # ── HEADER ──────────────────────────────────────────────────
        self.os.draw_rect(0, 0, W, 20, C_PANEL)
        self.os.draw_rect(0, 19, W, 1, C_BORDER)
        # Coloured accent bar on left
        self.os.draw_rect(0, 0, 3, 20, C_BLUE)
        self.os.draw_text(6,  3,  "RETROCORE", color=C_BLUE)
        self.os.draw_text(6,  12, "OS  V1.0",  color=C_CYAN)
        # Divider + hints on right
        self.os.draw_rect(105, 2, 1, 16, C_BORDER_DIM)
        self.os.draw_text(108,  3, "ENTER=RUN", color=C_GREY)
        self.os.draw_text(108, 12, "UP/DN=MOVE", color=C_GREY)

        # ── MENU ITEMS ───────────────────────────────────────────────
        for i, (label, icon, _, _) in enumerate(MENU):
            y           = START_Y + i * ITEM_H
            bg_col, fg_col = ENTRY_COLORS[i]
            is_sel      = (i == self.selected)

            if is_sel:
                # Highlighted row fill
                self.os.draw_rect(2, y, W - 4, ITEM_H - 2, bg_col)
                self.os.draw_border(2, y, W - 4, ITEM_H - 2,
                                    tuple(min(255, c + 80) for c in bg_col))
                # Left accent stripe
                self.os.draw_rect(2, y, 3, ITEM_H - 2, fg_col)
                # Blinking cursor
                if (self._frame // 18) % 2 == 0:
                    self.os.draw_text(8, y + 5, ">", color=fg_col)
                self.os.draw_text(18, y + 5, label, color=fg_col)
                # Icon badge
                bx = W - 18
                self.os.draw_rect(bx, y + 2, 13, 13, bg_col)
                self.os.draw_border(bx, y + 2, 13, 13, fg_col)
                self.os.draw_text(bx + 3, y + 5, icon, color=fg_col)
            else:
                # Dim unselected row
                self.os.draw_rect(2, y, W - 4, ITEM_H - 2, (10, 12, 16))
                self.os.draw_rect(2, y, 3, ITEM_H - 2, (30, 35, 45))
                self.os.draw_text(18, y + 5, label, color=C_GREY)
                bx = W - 18
                self.os.draw_rect(bx, y + 2, 13, 13, (12, 14, 18))
                self.os.draw_border(bx, y + 2, 13, 13, (30, 35, 45))
                self.os.draw_text(bx + 3, y + 5, icon, color=C_GREY)

            # Row divider (skip last)
            if i < len(MENU) - 1:
                self.os.draw_rect(5, y + ITEM_H - 2, W - 10, 1, C_BORDER_DIM)

        # ── FOOTER ───────────────────────────────────────────────────
        fy = H - 9
        self.os.draw_rect(0, fy, W, 9, C_PANEL)
        self.os.draw_rect(0, fy, W, 1, C_BORDER_DIM)
        item_label = MENU[self.selected][0]
        self.os.draw_text(4, fy + 2, "SELECTED: " + item_label, color=C_BORDER)