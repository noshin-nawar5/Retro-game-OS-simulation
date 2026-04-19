# Backgrounds
C_BG         = (6,   8,  10)
C_PANEL      = (14,  18,  22)
C_PANEL_ALT  = (10,  14,  18)

# Borders
C_BORDER     = (40,  80, 140)
C_BORDER_DIM = (20,  40,  70)
C_BORDER_LIT = (80, 140, 220)

# Green (OS / system)
C_GREEN      = (0,  220, 100)
C_GREEN_DIM  = (0,  130,  60)
C_GREEN_DARK = (0,   50,  25)

# Accent colours
C_AMBER      = (255, 185,  40)
C_AMBER_DIM  = (130,  90,  15)
C_RED        = (220,  55,  55)
C_RED_DIM    = (110,  25,  25)
C_BLUE       = (80,  160, 255)
C_BLUE_DIM   = (30,   70, 160)
C_CYAN       = (60,  210, 210)
C_CYAN_DIM   = (20,  100, 100)
C_PURPLE     = (170,  90, 240)
C_WHITE      = (210, 215, 220)
C_GREY       = (90,   95, 100)
C_GREY_DIM   = (30,   35,  40)

# Per-PID colours — bright, distinct, readable on dark backgrounds
PID_COLORS = [
    (0,   220, 100),   # 1 — bright green
    (80,  160, 255),   # 2 — sky blue
    (255, 185,  40),   # 3 — amber
    (220,  80, 220),   # 4 — magenta
    (60,  210, 210),   # 5 — cyan
    (255, 100,  60),   # 6 — orange
]


def pid_color(pid):
    return PID_COLORS[(pid - 1) % len(PID_COLORS)]


def draw_panel(os_api, x, y, w, h, title=None):
    os_api.draw_rect(x, y, w, h, C_PANEL)
    os_api.draw_border(x, y, w, h, C_BORDER)
    if title:
        os_api.draw_rect(x + 1, y + 1, w - 2, 8, (20, 40, 80))
        os_api.draw_text(x + 3, y + 2, title, color=C_BLUE)


def draw_hud(os_api, left_text, right_text="ESC=BACK",
             left_color=None, right_color=None):
    if left_color  is None: left_color  = C_WHITE
    if right_color is None: right_color = C_GREY
    os_api.draw_rect(0, 0, 160, 9, C_PANEL)
    os_api.draw_rect(0, 8, 160, 1, C_BORDER_DIM)
    os_api.draw_text(2, 2, left_text, color=left_color)
    rx = 158 - len(right_text) * 6
    os_api.draw_text(max(rx, 2), 2, right_text, color=right_color)


def draw_progress_bar(os_api, x, y, w, h, value, max_value, color):
    os_api.draw_rect(x, y, w, h, C_GREY_DIM)
    filled = int(w * min(value, max_value) / max(max_value, 1))
    if filled > 0:
        os_api.draw_rect(x, y, filled, h, color)