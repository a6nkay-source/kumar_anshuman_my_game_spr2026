import pygame as pg

# Game Constants
TITLE = "Neon Escape"
WIDTH = 800
HEIGHT = 600
FPS = 60
TILESIZE = 32

# Colors (Neon Palette)
BGCOLOR = (5, 5, 15) # Dark background for neon contrast
WHITE = (220, 220, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)
DARK_GRAY = (40, 40, 50)

# Map Files
MAPS = ['level1.txt', 'level2.txt'] # Add more levels as needed

# Player Settings
PLAYER_SPEED = 250
PLAYER_HEALTH = 100
DASH_SPEED_MULT = 3
DASH_DURATION = 150
DASH_COOLDOWN = 800

# Enemy Settings
ENEMY_SPEED = 140