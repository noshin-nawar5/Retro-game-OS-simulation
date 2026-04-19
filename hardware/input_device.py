import pygame

class InputDevice:
    def __init__(self):
        self.keys       = {}
        self._prev_keys = {}

    def update(self):
        self._prev_keys = dict(self.keys)
        p = pygame.key.get_pressed()
        self.keys = {
            "LEFT":  p[pygame.K_LEFT] or p[pygame.K_a],
            "RIGHT": p[pygame.K_RIGHT] or p[pygame.K_d],
            "UP":    p[pygame.K_UP] or p[pygame.K_w],
            "DOWN":  p[pygame.K_DOWN] or p[pygame.K_s],
            "A":     p[pygame.K_z],
            "B":     p[pygame.K_x],
            "START": p[pygame.K_RETURN],
            "ESC":   p[pygame.K_ESCAPE],
        }

    def get_keys(self):
        return self.keys