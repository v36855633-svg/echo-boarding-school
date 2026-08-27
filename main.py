"""
Главный файл игры «Интернат Эхо» (Pygame)
"""

import pygame
import sys

from game_config import *
from game_manager import GameManager, GameState, DayPhase
from player import Player
from enemy import Enemy
from level import Level
from noise_system import NoiseSystem
from ui import UI

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Интернат Эхо")
    clock = pygame.time.Clock()

    # Инициализация систем
    gm = GameManager()
    level = Level()
    player = Player()
    enemy = Enemy()
    noise_system = NoiseSystem()
    ui = UI()

    # Связывание
    gm.player = player
    gm.enemy = enemy
    gm.level = level
    gm.noise_system = noise_system
    gm.ui = ui

    player.level = level
    player.enemy = enemy
    player.noise_system = noise_system
    player.ui = ui
    player.gm = gm

    enemy.set_player(player)
    enemy.set_level(level)
    enemy.set_noise_system(noise_system)
    enemy.set_ui(ui)
    enemy.gm = gm

    noise_system.set_enemy(enemy)

    ui.gm = gm

    gm.start_new_game()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if gm.state in (GameState.GAME_OVER, GameState.VICTORY):
                        gm.start_new_game()
                elif event.key == pygame.K_e:
                    if gm.state == GameState.PLAYING:
                        player.try_interact()
                elif event.key == pygame.K_SPACE:
                    if gm.state == GameState.PLAYING:
                        player.try_hide()
                elif event.key == pygame.K_g:
                    if gm.state == GameState.PLAYING:
                        player.use_gramophone()

        keys = pygame.key.get_pressed()
        if gm.state == GameState.PLAYING:
            # обновление
            gm.update(dt)
            player.update(dt, keys)
            enemy.update(dt)
            noise_system.update(dt)
            ui.update(dt)

        # отрисовка
        screen.fill(COLOR_FLOOR)
        level.draw(screen)
        noise_system.draw(screen)
        for item in level.items:
            item.draw(screen)
        player.draw(screen)
        enemy.draw(screen)
        ui.draw(screen)

        if gm.state == GameState.GAME_OVER:
            # затемнение
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,128))
            screen.blit(overlay, (0,0))
            # текст
            font = pygame.font.SysFont(None, 36)
            text = font.render("ИГРА ОКОНЧЕНА", True, (255,0,0))
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            text2 = pygame.font.SysFont(None, 24).render("Нажмите R для перезапуска", True, (255,255,255))
            screen.blit(text2, (WINDOW_WIDTH//2 - text2.get_width()//2, WINDOW_HEIGHT//2))
        elif gm.state == GameState.VICTORY:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,128))
            screen.blit(overlay, (0,0))
            font = pygame.font.SysFont(None, 36)
            text = font.render("ПОБЕДА!", True, (0,255,0))
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, WINDOW_HEIGHT//2 - 50))
            text2 = pygame.font.SysFont(None, 24).render("Нажмите R для новой игры", True, (255,255,255))
            screen.blit(text2, (WINDOW_WIDTH//2 - text2.get_width()//2, WINDOW_HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
