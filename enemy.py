"""
ИИ Смотрительницы — патрулирование, обнаружение, погоня (Pygame)
"""

import pygame
import math
import random

from game_config import *
from game_manager import GameManager

class EnemyState:
    PATROL = "patrol"
    INVESTIGATE = "investigate"
    CHASE = "chase"
    SEARCH = "search"
    TRANS = "trans"

class Enemy:
    def __init__(self):
        self.gm = GameManager()
        self.pos = [WINDOW_WIDTH * 0.7, WINDOW_HEIGHT * 0.7]
        self.radius = TILE_SIZE * 0.35

        self.state = EnemyState.PATROL
        self.state_timer = 0.0
        self.anger_meter = 0.0
        self.memory_timer = 0.0
        self.last_known_player_pos = None
        self.investigation_target = None
        self.patrol_points = []
        self.current_patrol_index = 0
        self.night_mode = False

        self.hearing_radius = ENEMY_HEARING_RADIUS
        self.vision_radius = ENEMY_VISION_RADIUS
        self.vision_angle = ENEMY_VISION_ANGLE

        self.player = None
        self.level = None
        self.noise_system = None
        self.ui = None

        self.trans_timer = 0.0
        self.trans_duration = 20.0

    def set_player(self, player):
        self.player = player

    def set_level(self, level):
        self.level = level

    def set_noise_system(self, noise_system):
        self.noise_system = noise_system

    def set_ui(self, ui):
        self.ui = ui

    def reset_for_chapter(self, chapter):
        self.state = EnemyState.PATROL
        self.anger_meter = 0.0
        self.memory_timer = 0.0
        self.last_known_player_pos = None
        self.investigation_target = None
        self.trans_timer = 0.0

        difficulty = self.gm.difficulty_multiplier
        self.hearing_radius = ENEMY_HEARING_RADIUS * difficulty
        self.vision_radius = ENEMY_VISION_RADIUS * difficulty
        self.night_mode = False

        self._generate_patrol_points()

        if self.level:
            spawn = self.level.get_enemy_spawn(chapter)
            if spawn:
                self.pos = list(spawn)

    def set_night_mode(self, active):
        self.night_mode = active
        if active:
            self.hearing_radius *= 1.3
            self.vision_radius *= 1.2
        else:
            self.hearing_radius = ENEMY_HEARING_RADIUS * self.gm.difficulty_multiplier
            self.vision_radius = ENEMY_VISION_RADIUS * self.gm.difficulty_multiplier

    def _generate_patrol_points(self):
        self.patrol_points = []
        if not self.level:
            return
        rooms = self.level.rooms
        for _ in range(5):
            if rooms:
                room = random.choice(rooms)
                rx, ry, rw, rh = room
                px = random.uniform(rx + 30, rx + rw - 30)
                py = random.uniform(ry + 30, ry + rh - 30)
                self.patrol_points.append((px, py))
        if not self.patrol_points:
            self.patrol_points = [(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)]
        self.current_patrol_index = 0

    def update(self, dt):
        if self.gm.state != GameManager().state.__class__.PLAYING:
            return

        self.state_timer += dt
        self.memory_timer -= dt

        if self.state == EnemyState.TRANS:
            self.trans_timer -= dt
            if self.trans_timer <= 0:
                self.state = EnemyState.SEARCH
                self.state_timer = 0.0
            return

        if self.player and self.player.alive and not self.player.is_hiding:
            self._check_detection(dt)

        if self.state == EnemyState.PATROL:
            self._update_patrol(dt)
        elif self.state == EnemyState.INVESTIGATE:
            self._update_investigate(dt)
        elif self.state == EnemyState.CHASE:
            self._update_chase(dt)
        elif self.state == EnemyState.SEARCH:
            self._update_search(dt)

        if self.state != EnemyState.CHASE:
            self.anger_meter = max(0, self.anger_meter - ENEMY_ANGER_DECAY * dt)

        if self.state == EnemyState.CHASE and self.memory_timer <= 0:
            self.state = EnemyState.SEARCH
            self.state_timer = 0.0
            self.last_known_player_pos = None

    def _check_detection(self, dt):
        if not self.player:
            return
        px = self.player.pos[0] + PLAYER_RADIUS
        py = self.player.pos[1] + PLAYER_RADIUS
        ex = self.pos[0] + self.radius
        ey = self.pos[1] + self.radius

        dx = px - ex
        dy = py - ey
        distance = math.sqrt(dx*dx + dy*dy)

        if distance <= self.hearing_radius:
            self.anger_meter += 30 * dt
            if self.anger_meter > ENEMY_ANGER_THRESHOLD:
                self._start_chase(px, py)
                return

        if distance <= self.vision_radius:
            # упрощённо: считаем, что враг смотрит по направлению к игроку
            # если нет стены между ними
            if self.level and self.level.has_line_of_sight(ex, ey, px, py):
                self.anger_meter = ENEMY_ANGER_THRESHOLD + 10
                self._start_chase(px, py)

    def _start_chase(self, px, py):
        self.state = EnemyState.CHASE
        self.state_timer = 0.0
        self.memory_timer = ENEMY_MEMORY_TIME
        self.last_known_player_pos = (px, py)
        if self.ui:
            self.ui.show_message("Смотрительница вас заметила!", 1.5)

    def hear_gramophone(self, px, py):
        self.state = EnemyState.TRANS
        self.trans_timer = self.trans_duration
        self.investigation_target = None
        if self.ui:
            self.ui.show_message("Смотрительница в трансе!", 2.0)

    def _update_patrol(self, dt):
        if not self.patrol_points:
            return
        target = self.patrol_points[self.current_patrol_index]
        self._move_towards(target, ENEMY_SPEED_PATROL, dt)

        ex = self.pos[0] + self.radius
        ey = self.pos[1] + self.radius
        if math.sqrt((target[0]-ex)**2 + (target[1]-ey)**2) < 10:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
            self.state_timer = 0.0
            if random.random() < 0.3:
                self.state_timer = -random.uniform(1.0, 3.0)

    def _update_investigate(self, dt):
        if self.investigation_target is None:
            self.state = EnemyState.PATROL
            return
        self._move_towards(self.investigation_target, ENEMY_SPEED_INVESTIGATE, dt)
        ex = self.pos[0] + self.radius
        ey = self.pos[1] + self.radius
        if math.sqrt((self.investigation_target[0]-ex)**2 +
                     (self.investigation_target[1]-ey)**2) < 15:
            self.state_timer = 0.0
            self.state = EnemyState.SEARCH
            self.investigation_target = None

    def _update_chase(self, dt):
        if not self.player or not self.player.alive:
            self.state = EnemyState.PATROL
            return
        target = (self.player.pos[0] + PLAYER_RADIUS,
                  self.player.pos[1] + PLAYER_RADIUS)
        if self.player.is_hiding:
            self.memory_timer = 0
            return
        self._move_towards(target, ENEMY_SPEED_CHASE, dt)
        self.last_known_player_pos = target
        self.memory_timer = ENEMY_MEMORY_TIME

        ex = self.pos[0] + self.radius
        ey = self.pos[1] + self.radius
        px = self.player.pos[0] + PLAYER_RADIUS
        py = self.player.pos[1] + PLAYER_RADIUS
        if math.sqrt((px-ex)**2 + (py-ey)**2) < 15:
            self.gm.game_over("Вас поймала Смотрительница")

    def _update_search(self, dt):
        if self.last_known_player_pos:
            self._move_towards(self.last_known_player_pos, ENEMY_SPEED_INVESTIGATE, dt)
            ex = self.pos[0] + self.radius
            ey = self.pos[1] + self.radius
            if math.sqrt((self.last_known_player_pos[0]-ex)**2 +
                         (self.last_known_player_pos[1]-ey)**2) < 15:
                self.last_known_player_pos = None
                self.state_timer = 0.0
                if self.state_timer > 2.0:
                    self.state = EnemyState.PATROL
        else:
            if self.state_timer > 3.0:
                self.state = EnemyState.PATROL
                self.state_timer = 0.0
            else:
                if random.random() < 0.1:
                    self._move_towards(
                        (random.uniform(0, WINDOW_WIDTH),
                         random.uniform(0, WINDOW_HEIGHT)),
                        ENEMY_SPEED_INVESTIGATE * 0.5, dt)

    def _move_towards(self, target, speed, dt):
        if not self.level:
            return
        ex = self.pos[0] + self.radius
        ey = self.pos[1] + self.radius
        dx = target[0] - ex
        dy = target[1] - ey
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 1:
            return
        dx /= distance
        dy /= distance

        new_x = self.pos[0] + dx * speed * dt
        new_y = self.pos[1] + dy * speed * dt

        enemy_radius = self.radius
        if self.level.can_move_to(new_x, new_y, enemy_radius):
            self.pos = [new_x, new_y]
        else:
            if self.level.can_move_to(new_x, self.pos[1], enemy_radius):
                self.pos[0] = new_x
            elif self.level.can_move_to(self.pos[0], new_y, enemy_radius):
                self.pos[1] = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, COLOR_ENEMY,
                           (int(self.pos[0] + self.radius), int(self.pos[1] + self.radius)),
                           int(self.radius))
        # индикатор состояния
        if self.state == EnemyState.CHASE:
            color = (255, 128, 0)
        elif self.state == EnemyState.INVESTIGATE:
            color = (255, 255, 0)
        elif self.state == EnemyState.TRANS:
            color = (128, 128, 255)
        else:
            color = (180, 180, 180)
        pygame.draw.circle(screen, color,
                           (int(self.pos[0] + self.radius), int(self.pos[1] + self.radius)),
                           int(self.radius * 0.5), 2)
