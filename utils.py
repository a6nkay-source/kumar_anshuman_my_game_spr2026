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

        self.tilewidth = len(self.data[0])  # number of columns in the map
        # height of the map is number of rows, not the length of the first row
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class Spritesheet:
    def __init__(self, filename):# Initializes sprite_sheet property
        self.spritesheet = pg.image.load(filename).convert()# Will load image and utalize it
        
        # Does something called Blit which creates the image. Load into memory and creates a new image.
        # Process and return with parameters that are given 
    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0,0), (x,y, width, height))
        new_image = pg.transform.scale(image, (width, height))
        image = new_image #DO not want scaling and not scaling stuff but using images in true image form.  
        return image
    
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
class Camera: # Camera Class so the camera can follow the player
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        # Width and height of the map for camera
        self.width = width
        self.height = height
 
    def apply(self, entity): # Applies camera offest
        return entity.rect.move(self.camera.topleft)
 
    def apply_rect(self, rect): # Applies camera offest to rec
        return rect.move(self.camera.topleft)
 
    def update(self, target): # Makes camera follow the player
 
        # center camera on target
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)
 
        # limit moving to the map size
        x = min(0, x)
        x = max(-(self.width - WIDTH), x)
        y = min(0, y)
        y = max(-(self.height - HEIGHT), y)
 
        self.camera = pg.Rect(x, y, self.width, self.height) # Update camera based on dcord
       