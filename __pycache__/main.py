import pygame as pg
import sys
from settings import *
from sprites import *
from map import Map, Camera

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Neon Escape") # Set window title
        self.clock = pg.time.Clock()
        self.load_data()

    def load_data(self):
        self.map = Map('map/level1.txt')

    def new(self):
        # Initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.core = pg.sprite.Group()
        self.cores = pg.sprite.Group()
        self.portals = pg.sprite.Group()

        # Parse map data and create sprites
        for row, tiles in enumerate(self.map.data):
            # Iterate through each tile in the row and create corresponding sprites
            for col, tile in enumerate(tiles):
                if tile == '1': Wall(self, col, row)
                if tile == 'P': self.player = Player(self, col, row)
                if tile == 'M': Enemy(self, col, row)
                if tile == 'C': EnergyCore(self, col, row)
                if tile == 'E': self.portal = Portal(self, col, row)
                
        self.camera = Camera(self.map.width, self.map.height) # Initialize camera with map dimensions
        self.score = 0 # Start score at 0
        self.run() # Start the game loop 

    def run(self):
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update() # Update game state
            self.draw() # Draw everything after updating

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player) # Update camera to follow player
        self.player.pos = pg.math.Vector2(self.player.rect.center) # Update player position for collision detection

        # Core Collection
        hits = pg.sprite.spritecollide(self.player, self.cores, True)
        for hit in hits: # Player collects core
            self.score += 1 # Update score

        # Enemy Collision
        if pg.sprite.spritecollide(self.player, self.enemies, False):
            self.player.health -= 1 # Reduce player health on collision
            if self.player.health <= 0: # Check for game over
                self.playing = False #Restart Level

        # Exit Portal
        if len(self.cores) == 0: # Check if all cores are collected
            if pg.sprite.spritecollide(self.player, self.portals, False):
                print("Level Complete!") # Print score on level completion
                self.playing = False # Proceed to next level or end game
    def draw(self):
        self.screen.fill(BGCOLOR) # Clear screen with black background
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite)) # Draw sprites with camera offset
        
        # Draw HUD
        self.draw_text(f'Score: {self.score}', 22, WHITE, 10, 10) # Display score
        pg.display.flip() # Update the display

    def draw_text(self, text, size, color, x, y):
        font = pg.font.SysFont('Arial', size)
        surface = font.render(text, True, color)
        self.screen.blit(surface, (x, y))

if __name__ == "__main__":
    g = Game()
    while True:
        g.new()
