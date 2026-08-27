"""
Класс игрока — движение, шум, стамина, укрытия (Pygame)
"""

import pygame
import math

from game_config import *
from game_manager import GameManager

class Player:
    def __init__(self):
        self.gm = GameManager()
        self.pos = [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]
        self.radius = PLAYER_RADIUS

        self.speed_multiplier = 1.0
        self.is_crouching = False
        self.is_running = False
        self.is_hiding = False
        self.stamina = STAMINA_MAX
        self.alive = True
        self.has_voice = True

        self.last_noise_time = 0.0
        self.noise_cooldown = 0.5

        self.level = None
        self.enemy = None
        self.noise_system = None
        self.ui = None

    def update(self, dt, keys):
        if not self.alive:
            return

        # Определение скорости
        speed = PLAYER_SPEED
        if self.is_crouching:
            speed *= CROUCH_SPEED_MULTIPLIER
            self.is_running = False
        if self.is_running and not self.is_crouching:
            if self.stamina > 0:
                speed *= 1.6
                self.stamina -= STAMINA_DRAIN_RUN * dt
                if self.stamina <= 0:
                    self.stamina = 0
                    self.is_running = False
            else:
                self.is_running = False
        else:
            if not self.is_running:
                self.stamina = min(STAMINA_MAX, self.stamina + STAMINA_REGEN * dt)

        # Движение
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy = 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy = -1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx = 1

        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707

        new_x = self.pos[0] + dx * speed * dt
        new_y = self.pos[1] + dy * speed * dt

        if self.level and self.level.can_move_to(new_x, new_y, self.radius):
            self.pos = [new_x, new_y]

        # Генерация шума
        if (dx != 0 or dy != 0) and not self.is_hiding:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time - self.last_noise_time > self.noise_cooldown:
                self.last_noise_time = current_time
                noise_radius = NOISE_RADIUS_WALK
                if self.is_running:
                    noise_radius = NOISE_RADIUS_RUN
                elif self.is_crouching:
                    noise_radius = NOISE_RADIUS_CROUCH

                if self.noise_system:
                    self.noise_system.create_noise(
                        self.pos[0] + self.radius,
                        self.pos[1] + self.radius,
                        noise_radius,
                        'player'
                    )
                    self.gm.add_noise(noise_radius * 0.1)

    def try_interact(self):
        if self.level:
            self.level.interact_near(self.pos[0] + self.radius,
                                     self.pos[1] + self.radius)

    def try_hide(self):
        if self.level:
            hiding_spot = self.level.find_hiding_spot_near(
                self.pos[0] + self.radius,
                self.pos[1] + self.radius
            )
            if hiding_spot:
                self.is_hiding = not self.is_hiding
                if self.is_hiding:
                    self.pos = list(hiding_spot)
                    if self.ui:
                        self.ui.show_message("Вы спрятались", 1.0)
                else:
                    if self.ui:
                        self.ui.show_message("Вы вышли из укрытия", 1.0)

    def use_gramophone(self):
        if not self.has_voice:
            if self.ui:
                self.ui.show_message("Вы не можете использовать голос", 1.5)
            return
        if 'gramophone' in [item['type'] for item in self.gm.collected_items]:
            if self.noise_system:
                self.noise_system.create_noise(
                    self.pos[0] + self.radius,
                    self.pos[1] + self.radius,
                    200,
                    'gramophone'
                )
                if self.enemy:
                    self.enemy.hear_gramophone(
                        self.pos[0] + self.radius,
                        self.pos[1] + self.radius
                    )
                if self.ui:
                    self.ui.show_message("Граммофон играет!", 2.0)

    def reset_position(self):
        self.pos = [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]
        self.stamina = STAMINA_MAX
        self.is_hiding = False

    def lose_voice(self):
        self.has_voice = False
        if self.ui:
            self.ui.show_message("Смотрительница забрала ваш голос!", 3.0)

    def set_ui(self, ui):
        self.ui = ui

    def draw(self, screen):
        pygame.draw.circle(screen, COLOR_PLAYER,
                           (int(self.pos[0] + self.radius), int(self.pos[1] + self.radius)),
                           self.radius)
        # направление взгляда (просто линия вправо)
        end_x = int(self.pos[0] + self.radius + self.radius)
        end_y = int(self.pos[1] + self.radius)
        pygame.draw.line(screen, (255, 255, 255),
                         (int(self.pos[0] + self.radius), int(self.pos[1] + self.radius)),
                         (end_x, end_y), 2)
