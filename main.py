# Need to add a home page to pick different difficulties and levels.
import pygame as pg # Import pygame for game development
import sys # Import sys for exiting the game
from random import * # Import random for screen shakes
from settings import * # Import all constants from settings
from sprites import * # Import all sprite classes
from map import Map, Camera # Import Map and Camera classes
from utils import * # Import A* pathfinding function
from os import path # Import path for file handling

class Game:
    def __init__(self):
        pg.init() # Initialize all imported pygame modules
        self.screen = pg.display.set_mode((WIDTH, HEIGHT)) # Set up the game window
        self.clock = pg.time.Clock() # Clock to manage frame rate
        self.game_folder = path.dirname(__file__)  # Get the directory of the game script
        self.img_dir = path.join(self.game_folder, 'images')  # Directory containing images
        self.level_index = 0
        self.difficulty = "NORMAL" # Default difficulty
        self.enemy_mult = 1.0 # Multiplier for enemy speed 
        self.collision_timer = 0  # Timer for collision particle effect
        self.screen_shake = 0 # Timer for screen shake effect
        self.paused = False  # Pause state for the game
        self.state = 'home'  # Game state: 'home', 'playing', 'game_over'
    def handle_home_input(self, event):
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
            self.state = 'playing'
            self.load_level()
# This home screen was a reference from the Kids Can Code tutorial on making a platformer, but I heavily modified it to fit the theme of Neon Escape.
    def show_home_screen(self):
        self.screen.fill(MAGENTA) 
        
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

    def draw_text_centered(self, text, size, color, y):
        font = pg.font.SysFont('Times New Roman', size, bold=True)
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(WIDTH // 2, y))
        self.screen.blit(surf, rect)

    def load_level(self):
        self.all_sprites = pg.sprite.Group()# Group to hold all sprites for easy updating and drawing
        self.walls = pg.sprite.Group() # Group to hold wall sprites for collision detection
        self.enemies = pg.sprite.Group() # Group to hold enemy sprites for collision detection
        self.cores = pg.sprite.Group() # Group to hold energy core sprites for collection
        self.portals = pg.sprite.Group() # Group to hold portal sprites for level exit
        self.teleporters = pg.sprite.Group() # Group to hold blue teleport portals
        self.collision_timer = 0  # Reset collision timer
        # Added a background image for the levls for a better design.
        self.background = pg.image.load(path.join(self.img_dir, 'background.png')).convert() # Load background image for the level
        
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
                if tile == 'B': TeleportPortal(self, col, row) # Create blue teleport portal here
        
        # Link blue portals in pairs so they teleport to each other
        teleporters = list(self.teleporters)
        for i in range(0, len(teleporters), 2):
            if i + 1 < len(teleporters):
                teleporters[i].dest = teleporters[i + 1] # Link portals in pairs
                teleporters[i + 1].dest = teleporters[i] # Link portals in pairs 

        self.camera = Camera(self.map.width, self.map.height) # Initialize camera with map size to follow player

    def update(self):
        # Skip update if game is paused
        if self.paused:
            return
        
        self.all_sprites.update()
        self.camera.update(self.player)# Update camera to follow player

        # Handle blue teleport portals
        if self.player.teleport_timer <= 0:
            hit = pg.sprite.spritecollideany(self.player, self.teleporters)
            if hit and hit.dest:
                dest = hit.dest
                self.player.pos = pg.math.Vector2(dest.rect.centerx, dest.rect.centery)
                self.player.rect.center = self.player.pos
                self.player.vel = pg.math.Vector2(0, 0)
                self.player.teleport_timer = 0.3
        else:
            self.player.teleport_timer = max(self.player.teleport_timer - self.dt, 0)
        
        # Handle timers
        if self.collision_timer > 0:
            self.collision_timer -= self.dt * 1000  # Decrease timer
            if self.collision_timer <= 0:
                self.load_level()  # Reset level after particle effect
        
        # Collisions
        if pg.sprite.spritecollide(self.player, self.cores, True): # Collect core and remove it from the game
            pass 
            
        if pg.sprite.spritecollide(self.player, self.enemies, False) and self.collision_timer <= 0: # If player hits an enemy and not in collision 
            # Game over on contact with enemy
            self.state = 'game_over'
            # Create game over particles
            self.all_sprites = pg.sprite.Group()  # Clear sprites for game over animation
            return

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
        # Scale background image to fit screen and draw it
        scaled_bg = pg.transform.scale(self.background, (WIDTH, HEIGHT))
        self.screen.blit(scaled_bg, (0, 0))
        
        # Draw all sprites on top of the background
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        
        # User Interface
        self.draw_text(f"LEVEL {self.level_index + 1}", 20, WHITE, 10, 10) # Level indicator
        self.draw_text(f"CORES: {len(self.cores)}", 20, WHITE, 10, 35) # Cores remaining
        self.draw_text(f"MODE: {self.difficulty}", 20, WHITE, WIDTH - 150, 10) # Difficulty indicator
        
        # Draw dash cooldown timer at the top center
        self.draw_cooldown_timer()
        
        # Draw pause screen overlay
        if self.paused:
            # Semi-transparent overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0)) # This is to draw the overlay on the screen when press p
            
            # Pause text
            self.draw_text_centered("PAUSED", 60, GREEN, HEIGHT // 2 - 40)
            self.draw_text_centered("Press P to Resume", 24, WHITE, HEIGHT // 2 + 40)
        
        pg.display.flip()

    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # Create game over particles for animation if not already created
        if not hasattr(self, 'game_over_started'):
            self.game_over_started = True
            self.all_sprites = pg.sprite.Group()  # Clear sprites for game over animation
            for _ in range(50):  # More particles for dramatic effect
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                Particle(self, x, y, RED)
        
        # Update and draw particles
        self.all_sprites.update()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y)) # Draw the particles with their own positions for the explosion effect
        
        # Game Over text
        self.draw_text_centered("GAME OVER", 80, RED, HEIGHT // 3)
        self.draw_text_centered("You were caught by the enemy!", 24, RED, HEIGHT // 3 + 60) # This is an additional message when caught by the enemy 
        
        # Restart instruction
        alpha = 150 + (105 * (pg.time.get_ticks() % 1000 > 500))  # This is to flash the particles
        restart_color = (alpha, alpha, alpha)
        self.draw_text_centered("PRESS R TO RETURN TO MENU", 24, restart_color, HEIGHT - 100) # Instruction to return to menu
        
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.SysFont('Times New Roman', size, bold=True)
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y)) # Draw text at a specific position

    def draw_cooldown_timer(self):
        # Calculate cooldown progress
        now = pg.time.get_ticks()
        time_since_dash = now - self.player.last_dash
        cooldown_remaining = max(0, DASH_COOLDOWN - time_since_dash) # Time remaining on cooldown
        cooldown_progress = 1 - (cooldown_remaining / DASH_COOLDOWN)  # 0 = on cooldown, 1 = ready
        
        # Timer bar dimensions
        bar_width = 200
        bar_height = 20
        bar_x = (WIDTH // 2) - (bar_width // 2)
        bar_y = 10
        
        # Draw background bar (cooldown state)
        bg_color = RED if cooldown_remaining > 0 else CYAN # This shows when the bar ready to speed up.
        pg.draw.rect(self.screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), 2) # The border for the cooldown bar.
        
        # Draw cooldown progress bar
        filled_width = int(bar_width * cooldown_progress)
        if cooldown_remaining > 0:
            pg.draw.rect(self.screen, YELLOW, (bar_x, bar_y, filled_width, bar_height)) # This is the cooldown progress bar that fills up as the dash becomes ready.
        else:
            pg.draw.rect(self.screen, CYAN, (bar_x, bar_y, bar_width, bar_height)) # This fills the bar completely when the dash is ready to use.
        
        # Draw border
        pg.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2) # This is the white border around the cooldown bar for a pixelated like effect.
        
        # Draw cooldown text
        seconds_remaining = cooldown_remaining / 1000.0
        if cooldown_remaining > 0:
            timer_text = f"COOLDOWN: {seconds_remaining:.1f}s"
            color = YELLOW
        else:
            timer_text = "READY!"
            color = CYAN
        
        font = pg.font.SysFont('Times New Roman', 14, bold=True)
        surf = font.render(timer_text, True, color)
        text_rect = surf.get_rect(center=(WIDTH // 2, bar_y + bar_height // 2 + 1))
        self.screen.blit(surf, text_rect)

    def run(self):
        while True:
            self.dt = self.clock.tick(FPS) / 1000.0 # Delta time for consistent movement.
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    pg.quit()
                    sys.exit()
                if event.type == pg.KEYDOWN:
                    if self.state == 'home':
                        self.handle_home_input(event) # Handle input for home screen
                    elif self.state == 'playing':
                        if event.key == pg.K_p:  # Toggle pause on 'P' key press
                            self.paused = not self.paused
                    elif self.state == 'game_over':
                        if event.key == pg.K_r:
                            self.state = 'home'
                            if hasattr(self, 'game_over_started'): # This is to reset the particles 
                                delattr(self, 'game_over_started') # This is made to allow particles ot be created again.
            if self.state == 'home': # Show home screen in the home state.
                self.show_home_screen()
            elif self.state == 'playing':
                self.update() # Update game Logic 
                self.draw() # Draw everything on the screen
            elif self.state == 'game_over':
                self.draw_game_over()

if __name__ == "__main__":
    g = Game()
    g.run()