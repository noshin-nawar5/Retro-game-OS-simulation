from apps.ui import (C_BG, C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_RED, C_BLUE, C_WHITE, C_GREY, C_AMBER)

_BG   = (4, 6, 14)
_LINE = (18, 28, 55)


class Pong:

    def __init__(self, os_api):
        self.os = os_api
        self._reset()

    def _reset(self):
        self.ball_x      = 80.0
        self.ball_y      = 77.0
        self.dx          = 1.6
        self.dy          = 1.0
        self.paddle_y    = 57
        self.enemy_y     = 57
        self.score       = 0
        self.enemy_score = 0

    def update(self):
        keys = self.os.get_input()
        if keys.get("ESC") or keys.get("B"):
            self.os.exit_process()
            return

        if keys["UP"]   and self.paddle_y > 11:  self.paddle_y -= 2
        if keys["DOWN"] and self.paddle_y < 120: self.paddle_y += 2

        # AI with lag
        c = self.enemy_y + 12
        if   self.ball_y > c + 2: self.enemy_y = min(120, self.enemy_y + 2)
        elif self.ball_y < c - 2: self.enemy_y = max(11,  self.enemy_y - 2)

        self.ball_x += self.dx
        self.ball_y += self.dy

        # Wall bounce
        if self.ball_y <= 11 or self.ball_y >= 141:
            self.dy *= -1

        # Player paddle hit
        if 7 <= self.ball_x <= 12:
            if self.paddle_y <= self.ball_y <= self.paddle_y + 24:
                self.dx  = abs(self.dx)
                off      = (self.ball_y - (self.paddle_y + 12)) / 12.0
                self.dy  = off * 1.5

        # AI paddle hit
        if 147 <= self.ball_x <= 152:
            if self.enemy_y <= self.ball_y <= self.enemy_y + 24:
                self.dx = -abs(self.dx)

        if self.ball_x < 0:
            self.enemy_score += 1; self._reset()
        if self.ball_x > 159:
            self.score += 1;       self._reset()

        self._draw()

    def _draw(self):
        self.os.draw_rect(0, 0, 160, 144, _BG)

        # HUD
        self.os.draw_rect(0, 0, 160, 10, C_PANEL)
        self.os.draw_rect(0, 9, 160, 1, C_BORDER_DIM)
        self.os.draw_text(3,   2, "YOU " + str(self.score),       color=C_BLUE)
        self.os.draw_text(66,  2, "PONG",                         color=C_WHITE)
        self.os.draw_text(110, 2, "CPU " + str(self.enemy_score), color=C_RED)
        self.os.draw_text(48,  2, "ESC=QUIT",                     color=(25,35,60))

        # Dashed centre line
        for y in range(11, 144, 5):
            self.os.draw_rect(79, y, 2, 3, _LINE)

        # Player paddle (blue with highlight + shadow)
        self.os.draw_rect(7, self.paddle_y,      4, 24, C_BLUE)
        self.os.draw_rect(7, self.paddle_y,      4,  2, (170, 210, 255))
        self.os.draw_rect(7, self.paddle_y + 22, 4,  2, (30,  70, 160))

        # AI paddle (red)
        self.os.draw_rect(149, self.enemy_y,      4, 24, C_RED)
        self.os.draw_rect(149, self.enemy_y,      4,  2, (255, 140, 140))
        self.os.draw_rect(149, self.enemy_y + 22, 4,  2, (100,  20,  20))

        # Ball glow + core
        bx, by = int(self.ball_x), int(self.ball_y)
        self.os.draw_rect(bx-1, by-1, 4, 4, (50, 70, 110))
        self.os.draw_rect(bx,   by,   2, 2, C_WHITE)

        # Score bars
        self.os.draw_rect(11, 11, self.score * 3, 2,       C_BLUE)
        self.os.draw_rect(148 - self.enemy_score*3, 11,
                          self.enemy_score * 3, 2, C_RED)