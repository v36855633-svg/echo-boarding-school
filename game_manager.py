"""
Менеджер игры — управление состояниями, циклами дня/ночи, главами (Pygame)
"""

from enum import Enum
import json
import os

from game_config import *

class GameState(Enum):
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class DayPhase(Enum):
    DAY = "day"
    NIGHT = "night"
    TRANSITION = "transition"

class GameManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized:
            return
        self.initialized = True

        self.state = GameState.PLAYING
        self.day_phase = DayPhase.DAY

        self.current_chapter = 1
        self.max_chapter = CHAPTERS

        self.day_timer = 0.0
        self.night_timer = 0.0
        self.transition_timer = 0.0

        self.brother_found = False
        self.player_voice = True
        self.collected_items = []
        self.discovered_memories = []
        self.total_noise_made = 0.0

        self.player = None
        self.enemy = None
        self.level = None
        self.noise_system = None
        self.ui = None

        self.difficulty_multiplier = 1.0

    def start_new_game(self):
        self.current_chapter = 1
        self.brother_found = False
        self.player_voice = True
        self.collected_items = []
        self.discovered_memories = []
        self.total_noise_made = 0.0
        self.difficulty_multiplier = 1.0
        self.state = GameState.PLAYING
        self.day_phase = DayPhase.DAY
        self.day_timer = 0.0
        self.night_timer = 0.0

        if self.level:
            self.level.generate(self.current_chapter)
        if self.player:
            self.player.reset_position()
        if self.enemy:
            self.enemy.reset_for_chapter(self.current_chapter)
        if self.ui:
            self.ui.show_message("Глава 1: Поиск брата", 3.0)

    def update(self, dt):
        if self.state != GameState.PLAYING:
            return

        if self.day_phase == DayPhase.DAY:
            self.day_timer += dt
            if self.day_timer >= DAY_DURATION:
                self.switch_to_night()
        elif self.day_phase == DayPhase.NIGHT:
            self.night_timer += dt
            if self.night_timer >= NIGHT_DURATION:
                self.switch_to_day()
        elif self.day_phase == DayPhase.TRANSITION:
            self.transition_timer += dt
            if self.transition_timer >= 3.0:
                if self.day_timer >= DAY_DURATION:
                    self.day_phase = DayPhase.NIGHT
                    self.night_timer = 0.0
                else:
                    self.day_phase = DayPhase.DAY
                    self.day_timer = 0.0

    def switch_to_night(self):
        self.day_phase = DayPhase.TRANSITION
        self.transition_timer = 0.0
        if self.enemy:
            self.enemy.set_night_mode(True)
        if self.ui:
            self.ui.show_message("Наступает ночь...", 2.0)

    def switch_to_day(self):
        self.day_phase = DayPhase.TRANSITION
        self.transition_timer = 0.0
        if self.enemy:
            self.enemy.set_night_mode(False)
        if self.ui:
            self.ui.show_message("Рассвет...", 2.0)

    def add_noise(self, amount):
        self.total_noise_made += amount
        self.difficulty_multiplier = 1.0 + (self.total_noise_made / 1000.0) * 0.5

    def collect_item(self, item_type, item_id):
        self.collected_items.append({
            'type': item_type,
            'id': item_id,
            'chapter': self.current_chapter
        })
        if self.ui:
            self.ui.show_message(f"Найдено: {item_type}", 1.5)

    def discover_memory(self, memory_id):
        self.discovered_memories.append(memory_id)
        if self.ui:
            self.ui.show_message("Воспоминание восстановлено", 2.0)

    def complete_chapter(self):
        if self.current_chapter < self.max_chapter:
            self.current_chapter += 1
            self.day_phase = DayPhase.DAY
            self.day_timer = 0.0
            self.night_timer = 0.0
            if self.level:
                self.level.generate(self.current_chapter)
            if self.enemy:
                self.enemy.reset_for_chapter(self.current_chapter)
            if self.player:
                self.player.reset_position()
            if self.ui:
                self.ui.show_message(f"Глава {self.current_chapter}: начинается", 3.0)
        else:
            self.state = GameState.VICTORY
            if self.ui:
                self.ui.show_victory()

    def game_over(self, reason="Вы пойманы"):
        self.state = GameState.GAME_OVER
        if self.ui:
            self.ui.show_game_over(reason)

    def get_save_data(self):
        return {
            'chapter': self.current_chapter,
            'brother_found': self.brother_found,
            'player_voice': self.player_voice,
            'collected_items': self.collected_items,
            'discovered_memories': self.discovered_memories,
            'total_noise_made': self.total_noise_made,
            'difficulty': self.difficulty_multiplier,
            'player_pos': list(self.player.pos) if self.player else [0, 0]
        }
