import random
from apps.ui import (C_BG, C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_RED, C_WHITE, C_GREY, draw_hud)

_FOOD_COL   = (255,  70,  70)
_HEAD_COL   = (0,   255, 120)
_BODY_A     = (0,   180,  80)
_BODY_B     = (0,   150,  65)
_BORDER_COL = (30,  100, 200)
_BG_COL     = (5,    8,  14)


class Snake:
    CELL = 4
    COLS = 38
    ROWS = 32
    OX   = 1
    OY   = 11

    def __init__(self, os_api):
        self.os = os_api
        self._reset()

    def _reset(self):
        cx, cy         = self.COLS // 2, self.ROWS // 2
        self.snake     = [(cx, cy), (cx-1, cy), (cx-2, cy)]
        self.direction = (1, 0)
        self._next_dir = (1, 0)
        self.score     = 0
        self.dead      = False
        self._frame    = 0
        self._speed    = 6
        self._place_food()

    def _place_food(self):
        while True:
            f = (random.randint(0, self.COLS-1), random.randint(0, self.ROWS-1))
            if f not in self.snake:
                self.food = f
                break

    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        if self.dead:
            if keys.get("START"):
                self._reset()
            self._draw_death()
            return

        d = self.direction
        if keys["UP"]    and d != (0,  1): self._next_dir = (0, -1)
        if keys["DOWN"]  and d != (0, -1): self._next_dir = (0,  1)
        if keys["LEFT"]  and d != (1,  0): self._next_dir = (-1, 0)
        if keys["RIGHT"] and d != (-1, 0): self._next_dir = (1,  0)

        self._frame += 1
        if self._frame >= self._speed:
            self._frame = 0
            self._step()
        self._draw()

    def _step(self):
        self.direction = self._next_dir
        hx, hy   = self.snake[0]
        dx, dy   = self.direction
        nh       = (hx + dx, hy + dy)
        if not (0 <= nh[0] < self.COLS and 0 <= nh[1] < self.ROWS):
            self.dead = True; return
        if nh in self.snake:
            self.dead = True; return
        self.snake.insert(0, nh)
        if nh == self.food:
            self.score += 1
            self._speed = max(2, 6 - self.score // 5)
            self._place_food()
        else:
            self.snake.pop()

    def _draw(self):
        C = self.CELL
        # Background
        self.os.draw_rect(0, 0, 160, 144, _BG_COL)
        # HUD
        draw_hud(self.os, "SNAKE  SCORE " + str(self.score),
                 right_text="ESC=QUIT", left_color=C_GREEN)
        # Play area border (blue glow)
        self.os.draw_border(self.OX-1, self.OY-1,
                            self.COLS*C+2, self.ROWS*C+2, _BORDER_COL)
        # Food
        fx, fy = self.food
        self.os.draw_rect(self.OX+fx*C, self.OY+fy*C, C-1, C-1, _FOOD_COL)
        # Snake
        for i, (sx, sy) in enumerate(self.snake):
            col = _HEAD_COL if i == 0 else (_BODY_A if i%2==0 else _BODY_B)
            self.os.draw_rect(self.OX+sx*C, self.OY+sy*C, C-1, C-1, col)
        # Score progress bar
        bw = min(154, self.score * 5)
        self.os.draw_rect(3, 142, 154, 2, C_GREEN_DARK)
        if bw:
            self.os.draw_rect(3, 142, bw, 2, C_GREEN)

    def _draw_death(self):
        self._draw()
        # Popup
        self.os.draw_rect(22, 50, 116, 50, (8, 8, 16))
        self.os.draw_border(22, 50, 116, 50, C_RED)
        self.os.draw_rect(23, 51, 114, 10, (40, 10, 20))
        self.os.draw_text(32,  53, "GAME  OVER",           color=C_RED)
        self.os.draw_text(38,  65, "SCORE  " + str(self.score), color=C_WHITE)
        self.os.draw_text(26,  77, "ENTER=RETRY",           color=C_GREEN_DIM)
        self.os.draw_text(26,  87, "ESC=QUIT",              color=C_GREY)