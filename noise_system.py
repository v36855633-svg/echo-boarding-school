"""
Система шума — визуализация звуковых волн (Pygame)
"""

import pygame
import math

from game_config import *

class NoiseSystem:
    def __init__(self):
        self.noises = []
        self.enemy = None

    def set_enemy(self, enemy):
        self.enemy = enemy

    def create_noise(self, x, y, radius, source='player'):
        self.noises.append({
            'pos': (x, y),
            'radius': 0,
            'max_radius': radius,
            'alpha': 0.6,
            'source': source
        })
        if self.enemy and source in ('player', 'gramophone'):
            self.enemy.hear_noise(x, y, radius, source)

    def update(self, dt):
        for noise in self.noises[:]:
            noise['radius'] += 30 * dt
            noise['alpha'] -= 0.5 * dt
            if noise['alpha'] <= 0 or noise['radius'] >= noise['max_radius']:
                self.noises.remove(noise)

    def draw(self, screen):
        for noise in self.noises:
            # рисуем окружность с прозрачностью
            surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            color = (255, 255, 0, int(noise['alpha'] * 255))
            pygame.draw.circle(surf, color,
                               (int(noise['pos'][0]), int(noise['pos'][1])),
                               int(noise['radius']), 1)
            screen.blit(surf, (0,0))
