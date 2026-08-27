"""
Предметы на уровне (Pygame)
"""

import pygame
from game_config import *
from game_manager import GameManager

class Item:
    def __init__(self, item_type='key', pos=(0,0)):
        self.item_type = item_type
        self.size = (TILE_SIZE * 0.5, TILE_SIZE * 0.5)
        self.pos = list(pos)
        self.collected = False
        self.gm = GameManager()

    def collect(self):
        if not self.collected:
            self.collected = True
            self.gm.collect_item(self.item_type, id(self))

    def draw(self, screen):
        if self.collected:
            return
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        pygame.draw.rect(screen, COLOR_ITEM, rect)
        # небольшая вариация по типу
        if self.item_type == 'gramophone':
            pygame.draw.circle(screen, (255,255,255),
                               (int(self.pos[0]+self.size[0]/2), int(self.pos[1]+self.size[1]/2)),
                               int(self.size[0]/2))
        elif self.item_type == 'medkit':
            pygame.draw.rect(screen, (255,0,0), rect, 2)
