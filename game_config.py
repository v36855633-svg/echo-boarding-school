"""
Конфигурация игры «Интернат Эхо»
Содержит глобальные настройки, константы и баланс
"""

# Размеры окна
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Размер тайла
TILE_SIZE = 40

# Цвета
COLOR_FLOOR = (0.12, 0.10, 0.14, 1)
COLOR_WALL = (0.25, 0.22, 0.28, 1)
COLOR_PLAYER = (0.2, 0.8, 0.4, 1)
COLOR_ENEMY = (0.9, 0.1, 0.1, 1)
COLOR_ITEM = (0.9, 0.8, 0.2, 1)
COLOR_DOOR = (0.6, 0.4, 0.2, 1)
COLOR_TEXT = (0.9, 0.9, 0.9, 1)
COLOR_UI_BG = (0, 0, 0, 0.7)
COLOR_HIDING = (0.3, 0.3, 0.5, 1)
COLOR_NOISE = (1, 0.8, 0, 0.5)

# Параметры игрока
PLAYER_SPEED = 120          # пикселей в секунду
PLAYER_RADIUS = 12
NOISE_RADIUS_RUN = 80       # радиус шума при беге
NOISE_RADIUS_WALK = 30      # радиус шума при ходьбе
NOISE_RADIUS_CROUCH = 5     # радиус шума при крадущемся шаге
CROUCH_SPEED_MULTIPLIER = 0.4  # множитель скорости при крадущемся шаге
STAMINA_MAX = 100
STAMINA_DRAIN_RUN = 20      # в секунду
STAMINA_REGEN = 15          # в секунду

# Параметры Смотрительницы
ENEMY_SPEED_PATROL = 40
ENEMY_SPEED_CHASE = 110
ENEMY_SPEED_INVESTIGATE = 70
ENEMY_HEARING_RADIUS = 150  # базовый радиус слуха
ENEMY_VISION_RADIUS = 200   # радиус зрения
ENEMY_VISION_ANGLE = 110    # угол обзора в градусах
ENEMY_ANGER_DECAY = 10      # скорость затухания подозрительности
ENEMY_ANGER_THRESHOLD = 70  # порог для начала погони
ENEMY_MEMORY_TIME = 5.0     # время помнить игрока после потери из виду

# Генерация уровня
LEVEL_WIDTH = 20            # в тайлах
LEVEL_HEIGHT = 15
MIN_ROOM_SIZE = 4
MAX_ROOM_SIZE = 7
NUM_ROOMS = 8
NUM_ITEMS = 10
NUM_DOORS = 12

# Предметы
ITEM_TYPES = ['key', 'note', 'gramophone', 'cameron_fragment', 'medkit']

# Сохранение
SAVE_DIR = 'saves'
SAVE_FILE = 'echo_save.json'

# Геймплейные параметры
DAY_DURATION = 120          # секунд в игровом дне
NIGHT_DURATION = 180        # секунд в игровой ночи
CHAPTERS = 4

FPS = 60
