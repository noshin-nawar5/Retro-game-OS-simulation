import pygame

class InputDevice:
    def __init__(self):
        self.keys       = {}
        self._prev_keys = {}

    def update(self):
        self._prev_keys = dict(self.keys)
        p = pygame.key.get_pressed()
        self.keys = {
            "LEFT":  p[pygame.K_LEFT],
            "RIGHT": p[pygame.K_RIGHT],
            "UP":    p[pygame.K_UP],
            "DOWN":  p[pygame.K_DOWN],
            "A":     p[pygame.K_z],
            "B":     p[pygame.K_x],
            "START": p[pygame.K_RETURN],
            "ESC":   p[pygame.K_ESCAPE],
        }

    def get_keys(self):
        return self.keys