import pygame as pg
import os
# Settings
WIDTH = 800
HEIGHT = 600
TITLE = "MY Cool Game" # Title
FPS = 60 # Frames per second
CAMERA_RADIUS = 200 # Radius of the camera's circular mask
TILESIZE = 32 # Avergae Pixel size


script_dir = os.path.dirname(__file__)

# Player Values
PLAYER_SPEED = 280
PLAYER_HIT_RECT = pg.Rect(0, 0, TILESIZE, TILESIZE) # Player Hitbox

# color values
# tuple storing RGB values
BLUE = (0, 0, 255)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
WALL_COLOR = (100, 100, 100)
YELLOW = (255, 255, 0)

