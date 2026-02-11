import pygame as pg 
from settings import *

class Map:
    def __init__(self, filename):
        # Creating data for building for a map using a list
        self.data = []
        # opens a specific file 
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())# Self.strip strips any beginning and ending characters.

        self.tilewidth = len(self.data[0])# Colecting the length of the list
        self.tileheight = len(self.data[0])
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE
# This class creates a coutdown timer for a Cool Down
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        # Allows us to set property until time until cool down.
        self.time = time
    def start(self): # Counts the timer in milliseconds
        self.start_time = pg.time.get_ticks() # Return the number of milliseconds since pygame.init(). 

    def ready(self): # Starts the timer
        # sets current time to 
        current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if current_time - self.start_time >= self.time: # Sees how much time as passed
            return True
        return False