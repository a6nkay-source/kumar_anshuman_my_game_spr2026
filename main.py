# game engine using template from Chris Bradfield's "Making Games with Python & Pygame"
# I can push from vs code...
import pygame as pg
import sys
from os import path
# import game configuration values 
from settings import *
# import sprite classes 
from sprites import *
# import helper utilities
from utils import *
# shortcut for vector math
vec = pg.math.Vector2



# This class(Game) controls the entire game loop and logic
class Game:
    def __init__(self):
        # initialize pygame modules
        pg.init()

        # create game window using WIDTH and HEIGHT from settings.py
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        # set window title
        pg.display.set_caption(TITLE)
        # create clock object to control FPS
        self.clock = pg.time.Clock()
        # controls main program loop
        self.running = True
        # controls whether a round of the game is active
        self.playing = True
        # cooldown timer 5 seconds
        self.game_cooldown = Cooldown(5000)
    # Load external data 
    def load_data(self):
        # get folder where this script is located
        self.game_dir = path.dirname(__file__)
        self.img_dir = path.join(self.game_dir, 'images')# Goes to image folder
        self.wall_img = pg.image.load(path.join(self.img_dir, 'Wall.png')).convert_alpha()# Gets the wall texture from the image folder

        # load map file
        self.map = Map(path.join(self.game_dir, 'level1.txt'))

        print('data is loaded')
    
    # Start a new game round

    def new(self):
        # load assets and map
        self.load_data()
        # sprite groups 
        self.all_sprites = pg.sprite.Group()
        self.all_walls = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        # read map file and create objects
        for row, tiles in enumerate(self.map.data):
            for col, tile, in enumerate(tiles):

                # if tile is "1", create a wall at that position
                if tile == '1':
                    Wall(self, col, row)

                # if tile is "P", create player start position
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'M':
                    Mob(self, col, row ) # Setting the Mob
                if tile == 'C':
                    Coin(self, col, row)# Setting coins position
        # start game loop
        self.run()    
    # Main Game Loop
    # runs until self.running is False
    
    def run(self):
        while self.running:

            # delta time 
            self.dt = self.clock.tick(FPS) / 1000
            # handle input/events
            self.events()
            # update game logic
            self.update()
            # draw everything
            self.draw()
    # Handle events
    def events(self):
        for event in pg.event.get():

            # if window close button pressed
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False

            # mouse button released
            if event.type == pg.MOUSEBUTTONUP:
                print("i can get mouse input")
            # key pressed
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_k:
                    print("i can determine when keys are pressed")
            # key released
            if event.type == pg.KEYUP:
                if event.key == pg.K_k:
                    print("i can determine when keys are released")

    # Quit game 
    def quit(self):
        pass
    # Update all game objects
    def update(self):
        # call update() on every sprite
        self.all_sprites.update()

    
    # Draw everything to screen
    def draw(self):
        # fill background color
        self.screen.fill(BLUE)

        # draw debug text
        self.draw_text("Hello World", 24, WHITE, WIDTH/2, TILESIZE)
        # show delta time
        self.draw_text(str(self.dt), 24, WHITE, WIDTH/2, HEIGHT/4)
        # show cooldown ready state (True/False)
        self.draw_text(str(self.game_cooldown.ready()), 24, WHITE, WIDTH/2, HEIGHT/3)
        # show player position vector
        self.draw_text(str(self.player.pos), 24, WHITE, WIDTH/2, HEIGHT-TILESIZE*3)
        # draw all sprites to screen
        self.all_sprites.draw(self.screen)

        # update display
        pg.display.flip()


    
    # Function for drawing text to screen
    def draw_text(self, text, size, color, x, y):

        # find system font
        font_name = pg.font.match_font('arial')
        # create font object
        font = pg.font.Font(font_name, size)
        # render text surface
        text_surface = font.render(text, True, color)

        # get rectangle for positioning
        text_rect = text_surface.get_rect()
        # set position
        text_rect.midtop = (x,y)
        # draw text on screen
        self.screen.blit(text_surface, text_rect)

# Program Entry Point
# Game does not start until this is instantiated
if __name__ == "__main__":
    # create game object
    g = Game()# No arguement in here
# keep starting new game rounds while running
while g.running:
    g.new()
# quit pygame when done
pg.quit()
