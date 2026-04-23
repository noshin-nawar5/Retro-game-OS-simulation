from apps.ui import (C_BG, C_PANEL, C_BORDER, C_BORDER_DIM,
                     C_RED, C_BLUE, C_WHITE, C_GREY, C_AMBER,
                     C_GREEN, C_GREEN_DIM)

_BG   = (4, 6, 14)
_LINE = (18, 28, 55)
MAX_LIVES = 3

_EV_GREEN = (0,   180,  80)
_EV_AMBER = (255, 185,  40)
_EV_RED   = (220,  55,  55)
_EV_CYAN  = (60,  210, 210)


class Pong:

    def __init__(self, os_api):
        self.os = os_api
        self._full_reset()
        self.os.log_event("PONG STARTED", _EV_GREEN)

    def _full_reset(self):
        self.lives       = MAX_LIVES
        self.score       = 0
        self.enemy_score = 0
        self.dead        = False
        self._ball_reset()

    def _ball_reset(self):
        self.ball_x   = 80.0
        self.ball_y   = 77.0
        self.dx       = 1.6
        self.dy       = 1.0
        self.paddle_y = 57
        self.enemy_y  = 57

    def update(self):
        keys = self.os.get_input()

        if keys.get("ESC") or keys.get("B"):
            self.os.log_event("PONG EXIT", _EV_AMBER)
            self.os.exit_process()
            return

        if self.dead:
            if keys.get("START"):
                self._full_reset()
                self.os.log_event("PONG RESTART", _EV_AMBER)
            self._draw_gameover()
            return

        if keys["UP"]   and self.paddle_y > 11:  self.paddle_y -= 2
        if keys["DOWN"] and self.paddle_y < 120: self.paddle_y += 2

        c = self.enemy_y + 12
        if   self.ball_y > c + 2: self.enemy_y = min(120, self.enemy_y + 2)
        elif self.ball_y < c - 2: self.enemy_y = max(11,  self.enemy_y - 2)

        self.ball_x += self.dx
        self.ball_y += self.dy

        if self.ball_y <= 11 or self.ball_y >= 141:
            self.dy *= -1

        if 7 <= self.ball_x <= 12:
            if self.paddle_y <= self.ball_y <= self.paddle_y + 24:
                self.dx = abs(self.dx)
                off     = (self.ball_y - (self.paddle_y + 12)) / 12.0
                self.dy = off * 1.5
                # Real event: paddle hit = I/O syscall (display update)
                self.os.log_event("PADDLE HIT DRAW", _EV_CYAN)

        if 147 <= self.ball_x <= 152:
            if self.enemy_y <= self.ball_y <= self.enemy_y + 24:
                self.dx = -abs(self.dx)

        if self.ball_x < 0:
            self.lives -= 1
            self.enemy_score += 1
            if self.lives <= 0:
                self.dead = True
                self.os.log_event("GAME OVER L=0", _EV_RED)
            else:
                self.os.log_event("MISS LIFE=" + str(self.lives), _EV_RED)
                self._ball_reset()

        if self.ball_x > 159:
            self.score += 1
            self.os.log_event("POINT S=" + str(self.score), _EV_GREEN)
            self._ball_reset()

        self._draw()

    def _draw(self):
        self.os.draw_rect(0, 0, 160, 144, _BG)
        self.os.draw_rect(0, 0, 160, 10, C_PANEL)
        self.os.draw_rect(0, 9, 160, 1, C_BORDER_DIM)
        self.os.draw_text(3,   2, "YOU " + str(self.score),       color=C_BLUE)
        self.os.draw_text(66,  2, "PONG",                         color=C_WHITE)
        self.os.draw_text(110, 2, "BOT " + str(self.enemy_score), color=C_RED)
        for i in range(self.lives):
            self.os.draw_rect(148 - i * 7, 2, 5, 5, C_GREEN)
        for y in range(11, 144, 5):
            self.os.draw_rect(79, y, 2, 3, _LINE)
        self.os.draw_rect(7, self.paddle_y,      4, 24, C_BLUE)
        self.os.draw_rect(7, self.paddle_y,      4,  2, (170, 210, 255))
        self.os.draw_rect(7, self.paddle_y + 22, 4,  2, (30,  70, 160))
        self.os.draw_rect(149, self.enemy_y,      4, 24, C_RED)
        self.os.draw_rect(149, self.enemy_y,      4,  2, (255, 140, 140))
        self.os.draw_rect(149, self.enemy_y + 22, 4,  2, (100,  20,  20))
        bx, by = int(self.ball_x), int(self.ball_y)
        self.os.draw_rect(bx-1, by-1, 4, 4, (50, 70, 110))
        self.os.draw_rect(bx,   by,   2, 2, C_WHITE)
        self.os.draw_rect(11, 11, min(60, self.score * 3),       2, C_BLUE)
        self.os.draw_rect(89, 11, min(60, self.enemy_score * 3), 2, C_RED)

    def _draw_gameover(self):
        self._draw_court()
        self.os.draw_rect(22, 48, 116, 56, (6, 6, 14))
        self.os.draw_border(22, 48, 116, 56, C_RED)
        self.os.draw_rect(23, 49, 114, 11, (40, 10, 20))
        self.os.draw_text(34,  51, "GAME  OVER",                        color=C_RED)
        self.os.draw_text(28,  64, "YOUR SCORE  " + str(self.score),    color=C_WHITE)
        self.os.draw_text(28,  74, "BOT  SCORE  " + str(self.enemy_score), color=C_GREY)
        self.os.draw_text(28,  86, "ENTER = RETRY",                     color=C_GREEN_DIM)
        self.os.draw_text(28,  96, "ESC = QUIT",                        color=C_GREY)

    def _draw_court(self):
        self.os.draw_rect(0, 0, 160, 144, _BG)
        self.os.draw_rect(0, 0, 160, 10, C_PANEL)
        self.os.draw_rect(0, 9, 160, 1, C_BORDER_DIM)
        self.os.draw_text(3,  2, "YOU " + str(self.score),       color=C_BLUE)
        self.os.draw_text(66, 2, "PONG",                         color=C_WHITE)
        self.os.draw_text(110,2, "BOT " + str(self.enemy_score), color=C_RED)
        for y in range(11, 144, 5):
            self.os.draw_rect(79, y, 2, 3, _LINE)
        self.os.draw_rect(7,   self.paddle_y, 4, 24, C_BLUE)
        self.os.draw_rect(149, self.enemy_y,  4, 24, C_RED)