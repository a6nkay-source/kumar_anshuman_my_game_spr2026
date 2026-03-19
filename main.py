# Need to add a home page to pick different difficulties and levels.
import pygame as pg # Import pygame for game development
import sys # Import sys for exiting the game
from settings import *  # Import all constants from settings
from sprites import *  # Import all sprite classes
from map import Map, Camera # Import Map and Camera classes

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) # Set up the game window
        self.clock = pg.time.Clock() # Clock to manage frame rate
        self.level_index = 0
        self.collision_timer = 0  # Timer for collision particle effect
        self.invincibility_timer = 0  # Timer for invincibility after respawn
        
    def load_level(self):
        self.all_sprites = pg.sprite.Group()# Group to hold all sprites for easy updating and drawing
        self.walls = pg.sprite.Group() # Group to hold wall sprites for collision detection
        self.enemies = pg.sprite.Group() # Group to hold enemy sprites for collision detection
        self.cores = pg.sprite.Group() # Group to hold energy core sprites for collection
        self.portals = pg.sprite.Group() # Group to hold portal sprites for level exit
        self.collision_timer = 0  # Reset collision timer
        self.invincibility_timer = 1000  # 1 second of invincibility after respawn
        
        self.map = Map(MAPS[self.level_index])
        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == '1': Wall(self, col, row) # Create wall here 
                if tile == 'P': self.player = Player(self, col, row) # Create player here
                if tile == 'M': Enemy(self, col, row) # Create enemy here
                if tile == 'C': EnergyCore(self, col, row) # Create energy core here
                if tile == 'E': self.exit_node = Portal(self, col, row) # Create portal here
        
        self.camera = Camera(self.map.width, self.map.height) # Initialize camera with map size to follow player

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)# Update camera to follow player
        
        # Handle timers
        if self.collision_timer > 0:
            self.collision_timer -= self.dt * 1000  # Decrease timer
            if self.collision_timer <= 0:
                self.load_level()  # Reset level after particle effect
                
        if self.invincibility_timer > 0:
            self.invincibility_timer -= self.dt * 1000  # Decrease invincibility timer
        
        # Collisions
        if pg.sprite.spritecollide(self.player, self.cores, True): # Collect core and remove it from the game
            pass 
            
        if pg.sprite.spritecollide(self.player, self.enemies, False) and self.collision_timer <= 0 and self.invincibility_timer <= 0: # If player hits an enemy and not in collision or invincibility state
            # Create collision particles
            for _ in range(10):  # Create multiple particles for collision effect
                Particle(self, self.player.rect.centerx, self.player.rect.centery, RED)
            self.collision_timer = 500  # Show particles for 500ms before resetting

        if len(self.cores) == 0: 
            # Change portal color to show it's active
            self.exit_node.image.fill(MAGENTA)
            
        # Check if player reaches the portal
        if pg.sprite.spritecollide(self.player, self.portals, False):
            if len(self.cores) == 0:  # Only allow passage if all cores collected
                self.level_index += 1
                if self.level_index < len(MAPS):
                    self.load_level()
                else:
                    print("Game Over - You Escaped!") # If all cores collected and portal reached, end game
                    pg.quit()
                    sys.exit()

    def draw(self):
        self.screen.fill(BGCOLOR)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        # User Interface
        self.draw_text(f"LEVEL {self.level_index + 1}", 20, WHITE, 10, 10) # Level indicator
        self.draw_text(f"CORES: {len(self.cores)}", 20, YELLOW, 10, 35) # Cores remaining
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.SysFont('Courier', size, bold=True)
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def run(self):
        self.load_level()
        while True:
            self.dt = self.clock.tick(FPS) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT: return
            self.update()
            self.draw()

if __name__ == "__main__":
    g = Game()
    g.run()