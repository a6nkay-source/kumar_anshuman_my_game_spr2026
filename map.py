import pygame as pg
from settings import *

class Map:
    # Load map from text file and store it as a list of strings
    def __init__(self, filename):
        self.data = [] 
        with open(filename, 'rt') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comment lines
                if line and not line.startswith('#'):
                    self.data.append(line)
        
        # Ensure all rows have the same width by padding or truncating
        if self.data:
            self.tilewidth = len(self.data[0])  # Width of first row
            # Validate all rows have the same width
            for i, row in enumerate(self.data):
                if len(row) != self.tilewidth:
                    # Pad shorter rows or truncate longer ones
                    if len(row) < self.tilewidth:
                        self.data[i] = row + '1' * (self.tilewidth - len(row))
                    else:
                        self.data[i] = row[:self.tilewidth]
        else:
            self.tilewidth = 0
        
        self.tileheight = len(self.data)  # Number of rows in the map
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class Camera: # Sets the view of the game 
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
        # Limit scrolling to map boundaries
        x = min(0, x) 
        y = min(0, y)
        x = max(-(self.width - WIDTH), x) # These imit scrolling to map boundaries
        y = max(-(self.height - HEIGHT), y) # These limit scrolling to map boundaries
        self.camera = pg.Rect(x, y, self.width, self.height)