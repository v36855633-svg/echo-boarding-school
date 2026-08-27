"""
Система сохранения и загрузки
"""

import json
import os
from game_config import SAVE_DIR, SAVE_FILE

def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def save_game(data):
    ensure_save_dir()
    path = os.path.join(SAVE_DIR, SAVE_FILE)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_game():
    path = os.path.join(SAVE_DIR, SAVE_FILE)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def delete_save():
    path = os.path.join(SAVE_DIR, SAVE_FILE)
    if os.path.exists(path):
        os.remove(path)
