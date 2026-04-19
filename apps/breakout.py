import random
from apps.ui import (C_BG, C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_GREEN, C_GREEN_DIM, C_GREEN_DARK,
                     C_RED, C_BLUE, C_CYAN, C_WHITE, C_GREY, C_PURPLE)

BRICK_COLORS = [
    (220,  50,  50),  # red
    (230, 120,  35),  # orange
    (220, 200,  35),  # yellow
    (50,  200,  70),  # green
    (60,  140, 230),  # blue
    (160,  60, 230),  # purple
]
_BG = (4, 5, 12)


class Breakout:
    ROWS     = 5
    COLS     = 13
    BRICK_W  = 11
    BRICK_H  = 5
    BRICK_GAP = 1
    GRID_OX  = 3
    GRID_OY  = 14

    def __init__(self, os_api):
        self.os = os_api
        self._reset()

    def _reset(self):
        self.paddle_x = 60
        self.paddle_w = 24
        self.ball_x   = 80.0
        self.ball_y   = 108.0
        self.dx       = 0.8
        self.dy       = -1.0
        self.lives    = 3
        self.score    = 0
        self.dead     = False
        self.won      = False
        self.bricks   = [[True]*self.COLS for _ in range(self.ROWS)]

    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        if self.dead or self.won:
            if keys.get("START"):
                self._reset()
            self._draw_end()
            return

        if keys["LEFT"]  and self.paddle_x > 2:
            self.paddle_x -= 3
        if keys["RIGHT"] and self.paddle_x < 160 - self.paddle_w - 2:
            self.paddle_x += 3

        self.ball_x += self.dx
        self.ball_y += self.dy
        bx, by = int(self.ball_x), int(self.ball_y)

        # Wall bounces
        if self.ball_x <= 2:
            self.ball_x = 2.0;   self.dx = abs(self.dx)
        if self.ball_x >= 157:
            self.ball_x = 157.0; self.dx = -abs(self.dx)
        if self.ball_y <= 11:
            self.ball_y = 11.0;  self.dy = abs(self.dy)

        # Paddle collision
        py = 126
        if py <= by <= py + 4 and self.paddle_x-1 <= bx <= self.paddle_x+self.paddle_w+1:
            self.dy = -abs(self.dy)
            off     = (bx - (self.paddle_x + self.paddle_w/2)) / (self.paddle_w/2)
            self.dx = off * 1.2
            if abs(self.dx) < 0.5:
                self.dx = 0.5 if self.dx >= 0 else -0.5

        # Ball lost
        if self.ball_y > 135:
            self.lives -= 1
            if self.lives <= 0:
                self.dead = True
            else:
                self.ball_x = self.paddle_x + self.paddle_w/2
                self.ball_y = 108.0
                self.dx     = 0.8 * (1 if random.random() > 0.5 else -1)
                self.dy     = -1.0

        self._check_bricks()

        if all(not self.bricks[r][c]
               for r in range(self.ROWS) for c in range(self.COLS)):
            self.won = True

        self._draw()

    def _check_bricks(self):
        bx, by = int(self.ball_x), int(self.ball_y)
        for row in range(self.ROWS):
            col_c = BRICK_COLORS[row % len(BRICK_COLORS)]
            for col in range(self.COLS):
                if not self.bricks[row][col]:
                    continue
                rx = self.GRID_OX + col * (self.BRICK_W + self.BRICK_GAP)
                ry = self.GRID_OY + row * (self.BRICK_H + self.BRICK_GAP)
                if rx <= bx <= rx+self.BRICK_W and ry <= by <= ry+self.BRICK_H:
                    self.bricks[row][col] = False
                    self.score += (self.ROWS - row) * 10
                    if bx < rx or bx > rx+self.BRICK_W:
                        self.dx *= -1
                    else:
                        self.dy *= -1
                    return

    def _draw(self):
        self.os.draw_rect(0, 0, 160, 144, _BG)

        # HUD
        self.os.draw_rect(0, 0, 160, 11, C_PANEL)
        self.os.draw_rect(0, 10, 160, 1, C_BORDER_DIM)
        self.os.draw_text(2,  2, "BREAKOUT",          color=C_CYAN)
        self.os.draw_text(68, 2, "SCORE: " + str(self.score),     color=C_WHITE)
        #self.os.draw_text(96, 2, "LIVES",          color=(20,20,50))
        for i in range(self.lives):
            self.os.draw_rect(138 + i*7, 3, 5, 5, C_GREEN)

        # Play area border
        self.os.draw_border(1, 11, 158, 130, C_BORDER)

        # Bricks
        for row in range(self.ROWS):
            bc    = BRICK_COLORS[row % len(BRICK_COLORS)]
            hi    = tuple(min(255, c+70) for c in bc)
            shade = tuple(max(0,   c-70) for c in bc)
            for col in range(self.COLS):
                if not self.bricks[row][col]:
                    continue
                rx = self.GRID_OX + col * (self.BRICK_W + self.BRICK_GAP)
                ry = self.GRID_OY + row * (self.BRICK_H + self.BRICK_GAP)
                self.os.draw_rect(rx, ry,        self.BRICK_W, self.BRICK_H, bc)
                self.os.draw_rect(rx, ry,        self.BRICK_W, 1,            hi)
                self.os.draw_rect(rx, ry+self.BRICK_H-1, self.BRICK_W, 1, shade)

        # Paddle (blue with highlight)
        px, py = self.paddle_x, 126
        self.os.draw_rect(px,   py,   self.paddle_w, 5, C_BLUE)
        self.os.draw_rect(px,   py,   self.paddle_w, 1, (170, 210, 255))
        self.os.draw_rect(px,   py+4, self.paddle_w, 1, (30,  70, 160))
        self.os.draw_rect(px,   py,   3, 5, (160, 200, 255))
        self.os.draw_rect(px+self.paddle_w-3, py, 3, 5, (160, 200, 255))

        # Ball
        bx, by = int(self.ball_x), int(self.ball_y)
        self.os.draw_rect(bx-1, by-1, 4, 4, (40, 55, 100))
        self.os.draw_rect(bx,   by,   2, 2, C_WHITE)

        # Danger line
        self.os.draw_rect(2, 133, 156, 1, (35, 15, 15))

    def _draw_end(self):
        self._draw()
        col   = C_RED if self.dead else C_GREEN
        title = "GAME OVER" if self.dead else "YOU  WIN!"
        self.os.draw_rect(22, 52, 116, 48, (8, 8, 16))
        self.os.draw_border(22, 52, 116, 48, col)
        self.os.draw_rect(23, 53, 114, 10,
                          (38, 10, 20) if self.dead else (10, 38, 20))
        self.os.draw_text(38,  55, title,                      color=col)
        self.os.draw_text(28,  67, "SCORE " + str(self.score), color=C_WHITE)
        self.os.draw_text(28,  79, "ENTER = RETRY",              color=C_GREEN_DIM)
        self.os.draw_text(28,  89, "ESC = QUIT",                 color=C_GREY)