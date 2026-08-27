"""
Генерация уровня, столкновения, линия видимости, укрытия (Pygame)
"""

import random
import math
import pygame

from game_config import *

class Level:
    def __init__(self):
        self.tiles = []
        self.rooms = []
        self.doors = []
        self.items = []
        self.hiding_spots = []
        self.enemy_spawns = {}
        self.generate(1)

    def generate(self, chapter):
        self.tiles = [[1 for _ in range(LEVEL_WIDTH)] for _ in range(LEVEL_HEIGHT)]
        self.rooms = []
        self.doors = []
        self.items = []
        self.hiding_spots = []

        for _ in range(NUM_ROOMS):
            self._create_room()

        self._connect_rooms()
        self._place_doors()
        self._place_items(chapter)
        self._place_hiding_spots()
        self.enemy_spawns[chapter] = self._get_random_room_center()

    def _create_room(self):
        w = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        h = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        x = random.randint(1, LEVEL_WIDTH - w - 1)
        y = random.randint(1, LEVEL_HEIGHT - h - 1)

        for (rx, ry, rw, rh) in self.rooms:
            if (x < rx + rw + 1 and x + w + 1 > rx and
                y < ry + rh + 1 and y + h + 1 > ry):
                return

        for i in range(x, x + w):
            for j in range(y, y + h):
                self.tiles[j][i] = 0

        self.rooms.append((x * TILE_SIZE, y * TILE_SIZE,
                           w * TILE_SIZE, h * TILE_SIZE))

    def _connect_rooms(self):
        if len(self.rooms) < 2:
            return
        for i in range(len(self.rooms) - 1):
            r1 = self.rooms[i]
            r2 = self.rooms[i + 1]
            cx1 = int((r1[0] + r1[2]/2) / TILE_SIZE)
            cy1 = int((r1[1] + r1[3]/2) / TILE_SIZE)
            cx2 = int((r2[0] + r2[2]/2) / TILE_SIZE)
            cy2 = int((r2[1] + r2[3]/2) / TILE_SIZE)

            for x in range(min(cx1, cx2), max(cx1, cx2) + 1):
                self.tiles[cy1][x] = 0
            for y in range(min(cy1, cy2), max(cy1, cy2) + 1):
                self.tiles[y][cx2] = 0

    def _place_doors(self):
        for _ in range(NUM_DOORS):
            x = random.randint(1, LEVEL_WIDTH - 2)
            y = random.randint(1, LEVEL_HEIGHT - 2)
            if self.tiles[y][x] == 0:
                self.doors.append((x * TILE_SIZE, y * TILE_SIZE))

    def _place_items(self, chapter):
        from items import Item
        types = ITEM_TYPES
        for _ in range(NUM_ITEMS):
            pos = self._get_random_floor_tile()
            if pos:
                item_type = random.choice(types)
                item = Item(item_type=item_type, pos=pos)
                self.items.append(item)

    def _place_hiding_spots(self):
        for _ in range(6):
            pos = self._get_random_floor_tile()
            if pos:
                self.hiding_spots.append(pos)

    def _get_random_floor_tile(self):
        for _ in range(50):
            x = random.randint(1, LEVEL_WIDTH - 2)
            y = random.randint(1, LEVEL_HEIGHT - 2)
            if self.tiles[y][x] == 0:
                return (x * TILE_SIZE, y * TILE_SIZE)
        return None

    def _get_random_room_center(self):
        if not self.rooms:
            return (WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        room = random.choice(self.rooms)
        return (room[0] + room[2]/2 - TILE_SIZE/2,
                room[1] + room[3]/2 - TILE_SIZE/2)

    def can_move_to(self, x, y, radius):
        points = [
            (x, y),
            (x + radius*2, y),
            (x, y + radius*2),
            (x + radius*2, y + radius*2),
            (x + radius, y + radius)
        ]
        for px, py in points:
            tile_x = int(px / TILE_SIZE)
            tile_y = int(py / TILE_SIZE)
            if tile_x < 0 or tile_x >= LEVEL_WIDTH or tile_y < 0 or tile_y >= LEVEL_HEIGHT:
                return False
            if self.tiles[tile_y][tile_x] == 1:
                return False
        return True

    def has_line_of_sight(self, x1, y1, x2, y2):
        x1 = int(x1 / TILE_SIZE)
        y1 = int(y1 / TILE_SIZE)
        x2 = int(x2 / TILE_SIZE)
        y2 = int(y2 / TILE_SIZE)

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            if x1 < 0 or x1 >= LEVEL_WIDTH or y1 < 0 or y1 >= LEVEL_HEIGHT:
                return False
            if self.tiles[y1][x1] == 1:
                return False
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return True

    def interact_near(self, x, y):
        for item in self.items[:]:
            if not item.collected:
                dx = item.pos[0] + item.size[0]/2 - x
                dy = item.pos[1] + item.size[1]/2 - y
                if math.sqrt(dx*dx + dy*dy) < 30:
                    item.collect()
                    self.items.remove(item)
                    break

    def find_hiding_spot_near(self, x, y):
        for spot in self.hiding_spots:
            dx = spot[0] + TILE_SIZE/2 - x
            dy = spot[1] + TILE_SIZE/2 - y
            if math.sqrt(dx*dx + dy*dy) < 40:
                return spot
        return None

    def get_enemy_spawn(self, chapter):
        return self.enemy_spawns.get(chapter, (WINDOW_WIDTH*0.7, WINDOW_HEIGHT*0.7))

    def draw(self, screen):
        # пол
        screen.fill(COLOR_FLOOR)
        # стены
        for y in range(LEVEL_HEIGHT):
            for x in range(LEVEL_WIDTH):
                if self.tiles[y][x] == 1:
                    rect = pygame.Rect(x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, COLOR_WALL, rect)
        # двери
        for door in self.doors:
            rect = pygame.Rect(door[0], door[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_DOOR, rect)
        # укрытия
        for spot in self.hiding_spots:
            rect = pygame.Rect(spot[0], spot[1], TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLOR_HIDING, rect)
