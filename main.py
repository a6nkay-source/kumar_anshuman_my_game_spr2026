# Need to add a home page to pick different difficulties and levels.
import pygame as pg # Import pygame for game development
import sys # Import sys for exiting the game
import random # Import random for screen shake
from settings import * # Import all constants from settings
from sprites import * # Import all sprite classes
from map import Map, Camera # Import Map and Camera classes

class Game:
    def __init__(self):
        pg.init() # Initialize all imported pygame modules
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) # Set up the game window
        self.clock = pg.time.Clock() # Clock to manage frame rate
        self.level_index = 0
        self.difficulty = "NORMAL" # Default difficulty
        self.enemy_mult = 1.0 # Multiplier for enemy speed
        self.collision_timer = 0  # Timer for collision particle effect
        self.invincibility_timer = 0  # Timer for invincibility after respawn
        self.screen_shake = 0 # Timer for screen shake effect
        self.show_home_screen() # Show the selection menu before starting
# This home screen was a reference from the Kids Can Code tutorial on making a platformer, but I heavily modified it to fit the theme of Neon Escape.
    def show_home_screen(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS) 
            self.screen.fill(BGCOLOR)
            
            self.draw_text_centered("NEON ESCAPE", 80, BLACK, HEIGHT // 4)
            self.draw_text_centered("Presented by Anshuman Kumar", 24 , DARK_GRAY, HEIGHT // 4 + 60)
            
            
            y_offset = HEIGHT // 2
            
            # Difficulty Logic Visuals
            diff_color = GREEN if self.difficulty == "EASY" else (YELLOW if self.difficulty == "NORMAL" else RED)
            self.draw_text_centered(f"SELECT DIFFICULTY", 20, WHITE, y_offset) # Prompt to select difficulty
            self.draw_text_centered(f" {self.difficulty} ", 35, diff_color, y_offset + 40) # Highlight selected difficulty
            self.draw_text_centered("1 EASY  2 NORMAL  3 HARD", 16, DARK_GRAY, y_offset + 80) # Instructions for difficulty selection

            # Level Visulas
            self.draw_text_centered(f"STARTING LEVEL: {self.level_index + 1}", 20, WHITE, y_offset + 140)
            self.draw_text_centered("USE UP / DOWN KEYS", 16, DARK_GRAY, y_offset + 170)
            
            # Start Text
            alpha = 150 + (105 * (pg.time.get_ticks() % 1000 > 500)) 
            start_color = (alpha, alpha, alpha)
            self.draw_text_centered("PRESS SPACE TO START", 24, start_color, HEIGHT - 100)
            
            pg.display.flip()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_1:
                        self.difficulty = "EASY" # Set difficulty to easy and apply enemy speed multiplier
                        self.enemy_mult = 0.7
                    if event.key == pg.K_2:
                        self.difficulty = "NORMAL"# Set difficulty to normal and apply enemy speed multiplier
                        self.enemy_mult = 1.0
                    if event.key == pg.K_3:
                        self.difficulty = "HARD"# Set difficulty to hard and apply enemy speed multiplier
                        self.enemy_mult = 1.5
                    if event.key == pg.K_UP:
                        self.level_index = (self.level_index + 1) % len(MAPS)
                    if event.key == pg.K_DOWN:
                        self.level_index = (self.level_index - 1) % len(MAPS)
                    if event.key == pg.K_SPACE:
                        waiting = False

    def draw_text_centered(self, text, size, color, y):
        font = pg.font.SysFont('Courier', size, bold=True)
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(surf, rect)

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
                if tile == 'M': 
                    m = Enemy(self, col, row) # Create enemy here
                    m.speed = ENEMY_SPEED * self.enemy_mult # Apply difficulty multiplier
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
            
        if pg.sprite.spritecollide(self.player, self.enemies, False) and self.collision_timer <= 0 and self.invincibility_timer <= 0: # If player hits an enemy and not in collision 
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
        self.draw_text(f"CORES: {len(self.cores)}", 20, WHITE, 10, 35) # Cores remaining
        self.draw_text(f"MODE: {self.difficulty}", 20, WHITE, WIDTH - 150, 10) # Difficulty indicator
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