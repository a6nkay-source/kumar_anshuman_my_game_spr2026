import pygame as pg

# Game Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
TILESIZE = 32

# Colors (Neon Palette)
BGCOLOR = (0, 128, 0) # Change background "
DARK_GRAY = (40, 40, 50) # This is used for the Presented Title
WHITE = (220, 220, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
BLUE = (50, 150, 255)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)
DARK_GRAY = (40, 40, 50)
GREEN = (50, 255, 50)
BLACK = (0, 0, 0)

# Map Files
MAPS = ['level1.txt', 'level2.txt'] # Need to make more maps

# Player Settings
PLAYER_SPEED = 300
DASH_SPEED_MULT = 3
DASH_DURATION = 150000
DASH_COOLDOWN = 800

# Enemy Settings
ENEMY_SPEED = 400