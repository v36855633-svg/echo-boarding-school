"""
Интерфейс — HUD и сообщения (Pygame)
"""

import pygame
from game_config import *
from game_manager import GameManager, GameState, DayPhase

class UI:
    def __init__(self):
        self.gm = GameManager()
        self.font = pygame.font.SysFont(None, 24)
        self.message = ""
        self.message_timer = 0.0

    def show_message(self, text, duration=2.0):
        self.message = text
        self.message_timer = duration

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, screen):
        # сообщение внизу слева
        if self.message:
            text_surf = self.font.render(self.message, True, COLOR_TEXT)
            screen.blit(text_surf, (10, WINDOW_HEIGHT - 30))

        # HUD
        chapter_text = f"Глава: {self.gm.current_chapter}"
        chapter_surf = self.font.render(chapter_text, True, COLOR_TEXT)
        screen.blit(chapter_surf, (WINDOW_WIDTH - 150, WINDOW_HEIGHT - 30))

        phase = "Ночь" if self.gm.day_phase == DayPhase.NIGHT else "День"
        phase_text = f"Фаза: {phase}"
        phase_surf = self.font.render(phase_text, True, COLOR_TEXT)
        screen.blit(phase_surf, (WINDOW_WIDTH - 150, WINDOW_HEIGHT - 60))

        if self.gm.player:
            stamina_text = f"Стамина: {int(self.gm.player.stamina)}"
            stamina_surf = self.font.render(stamina_text, True, COLOR_TEXT)
            screen.blit(stamina_surf, (10, WINDOW_HEIGHT - 60))

    def show_game_over(self, reason):
        # в main.py будет отдельный экран, здесь просто установим сообщение
        self.message = f"ИГРА ОКОНЧЕНА: {reason}. Нажмите R для перезапуска"
        self.message_timer = 999  # держим до перезапуска

    def show_victory(self):
        self.message = "ПОБЕДА! Вы спасли брата. Нажмите R для новой игры"
        self.message_timer = 999
