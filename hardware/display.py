import pygame
import numpy as np
from hardware.font import FONT


class Display:

    def __init__(self, width=160, height=144, scale=4):
        self.width   = width
        self.height  = height
        self.scale   = scale

        pygame.init()
        pygame.display.set_caption("RetroCore OS")

        self.screen = pygame.display.set_mode(
            (width * scale, height * scale),
               pygame.DOUBLEBUF
            )

        # numpy framebuffer — shape (H, W, 3), cleared with one slice op
        self.framebuffer = np.zeros((height, width, 3), dtype=np.uint8)

        # Pre-allocated surface — NEVER recreated, just overwritten each frame
        self._surf = pygame.Surface((width, height))

    def clear(self, color=(0, 0, 0)):
        self.framebuffer[:] = color

    def draw_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.framebuffer[y, x] = color

    def draw_rect(self, x, y, w, h, color):
        x1 = max(0, x);          y1 = max(0, y)
        x2 = min(self.width, x + w); y2 = min(self.height, y + h)
        if x1 < x2 and y1 < y2:
            self.framebuffer[y1:y2, x1:x2] = color

    def draw_border(self, x, y, w, h, color):
        self.draw_rect(x,         y,         w, 1, color)
        self.draw_rect(x,         y + h - 1, w, 1, color)
        self.draw_rect(x,         y,         1, h, color)
        self.draw_rect(x + w - 1, y,         1, h, color)

    def draw_text(self, x, y, text, color=(255, 255, 255)):
        cx = x
        for ch in text:
            ch = ch.upper()
            if ch not in FONT:
                cx += 6
                continue
            for row, bits in enumerate(FONT[ch]):
                for col, b in enumerate(bits):
                    if b == "1":
                        self.draw_pixel(cx + col, y + row, color)
            cx += 6

    def render(self):
        # Write numpy array into pre-allocated surface — zero allocations
        pygame.surfarray.blit_array(self._surf, self.framebuffer.transpose(1, 0, 2))

        scaled = pygame.transform.scale(
    self._surf,
    (self.width * self.scale, self.height * self.scale)
)

        self.screen.blit(scaled, (0, 0))
    
        pygame.display.flip()