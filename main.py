from random import * # Import random for screen shakes
from settings import * # Import all constants from settings
from sprites import * # Import all sprite classes
from map import Map, Camera # Import Map and Camera classes
from utils import * # Import A* pathfinding function
from os import path # Import path for file handling
from math import cos, sin # Import trigonometric functions for fireworks
import sys # Import sys for exiting the game

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
        self.lives = 3  # Player lives
        self.life_loss_timer = 0.0  # Timer for the life lost animation
        self.collision_timer = 0  # Timer for collision particle effect
        self.screen_shake = 0 # Timer for screen shake effect
        self.paused = False  # Pause state for the game
        self.state = 'home'  # Game state: 'home', 'playing', 'game_over'
        self.time_left = 100.0  # Time remaining for the whole game
        self.level_time_limit = 120.0  # Time limit for the current game session
        self.home_time_input = "120"  # Time input shown on the home screen
        self.level_start_time = None  # Start time for the timer
        self.game_over_reason = None  # Reason for game over: 'enemy' or 'timeout'
        self.love_timer = 0.0  # Timer for playing love sound every 30 seconds
        pg.mixer.init()
        self.audio_dir = path.join(self.game_folder, 'audio')  # Directory containing audio files
        self.theme_sound = pg.mixer.Sound(path.join(self.audio_dir, 'theme_music (2).wav')) # Load background music
        self.theme_sound.set_volume(0.5) # Set music volume
        self.theme_sound.play(-1) # Play music in a loop
        self.game_over_sound = pg.mixer.Sound(path.join(self.audio_dir, 'game_over.wav')) # Load game over sound
        self.game_over_sound.set_volume(0.7) # Set game over sound volume
        self.coin_sound = pg.mixer.Sound(path.join(self.audio_dir, 'coin.wav')) # Load coin pickup sound
        self.coin_sound.set_volume(0.7) # Set coin sound volume
        self.victory_sound = pg.mixer.Sound(path.join(self.audio_dir, 'rap.wav')) # Load victory rap sound
        self.victory_sound.set_volume(0.7) # Set victory sound volume
        self.lose_sound = pg.mixer.Sound(path.join(self.audio_dir, 'lose.wav')) # Load lose life sound
        self.lose_sound.set_volume(0.7) # Set lose sound volume
        self.love_sound = pg.mixer.Sound(path.join(self.audio_dir, 'love.wav')) # Load love sound
        self.love_sound.set_volume(0.7) # Set love sound volume
    def handle_home_input(self, event):
        if event.key == pg.K_BACKSPACE: # Handle backspace to delete last character 
            self.home_time_input = self.home_time_input[:-1]
            return
        elif event.unicode.isdigit():  # handle numeric input for time limit
            if len(self.home_time_input) < 4: # Limit the input to 4 units
                self.home_time_input = (self.home_time_input + event.unicode).lstrip('0') or event.unicode # This is to add new inputs
        elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER: # Start the game when enter is pressed
            self.start_game()
            return
        difficulties = ["EASY", "NORMAL", "HARD"]
        speeds = {"EASY": 0.7, "NORMAL": 1.0, "HARD": 1.5}
        if event.key in (pg.K_LEFT, pg.K_UP):
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index - 1) % len(difficulties)]
            self.enemy_mult = speeds[self.difficulty]
            return
        if event.key in (pg.K_RIGHT, pg.K_DOWN):
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + 1) % len(difficulties)]
            self.enemy_mult = speeds[self.difficulty]
            return
        if event.key == pg.K_SPACE:
            self.start_game()
# This home screen was a reference from the Kids Can Code tutorial on making a platformer, but I heavily modified it to fit the theme of Neon Escape.
    def show_home_screen(self):
        self.screen.fill(MAGENTA) 
        
        self.draw_text_centered("NEON ESCAPE", 80, BLACK, HEIGHT // 4)
        self.draw_text_centered("Presented by Anshuman Kumar", 24 , DARK_GRAY, HEIGHT // 4 + 60) 
        
        
        y_offset = HEIGHT // 2 - 30
        
        # Difficulty Logic Visuals
        diff_color = GREEN if self.difficulty == "EASY" else (YELLOW if self.difficulty == "NORMAL" else RED)
        self.draw_text_centered("SELECT DIFFICULTY", 20, WHITE, y_offset)
        self.draw_text_centered(f" {self.difficulty} ", 35, diff_color, y_offset + 45)
        self.draw_text_centered("USE ARROW KEYS TO CHANGE DIFFICULTY", 16, DARK_GRAY, y_offset + 90)

        # Level Visuals
        self.draw_text_centered("STARTING LEVEL: 1", 20, WHITE, y_offset + 150)
        self.draw_text_centered(f"COMPLETE ALL LEVELS IN {self.home_time_input or '120'}s", 16, DARK_GRAY, y_offset + 185)
        input_text = f"{self.home_time_input or '120'}s"
        input_font = pg.font.SysFont('Copperplate Gothic', 28, bold=True)
        input_surf = input_font.render(input_text, True, WHITE)
        input_rect = input_surf.get_rect(center=(WIDTH // 2, y_offset + 270))
        pg.draw.rect(self.screen, RED, input_rect.inflate(32, 22), border_radius=8)
        self.screen.blit(input_surf, input_rect)
        self.draw_text_centered("TYPE THE TIME YOU WANT", 18, DARK_GRAY, y_offset + 315)
        
        # Start Text
        alpha = 150 + (105 * (pg.time.get_ticks() % 1000 > 500))
        start_color = (alpha, alpha, alpha)
        self.draw_text_centered("PRESS SPACE TO START", 24, start_color, HEIGHT - 120)
        
        pg.display.flip()

    def draw_text_centered(self, text, size, color, y):
        font = pg.font.SysFont('Copperplate Gothic', size, bold=True)
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
        self.screen_shake = 1500  # Screen shake duration in milliseconds when player enters
        # Added a background image for the levls for a better design
        level_images = ['background.png', 'bg_2.png', 'bg_3.png']  # One image for each level
        self.background = pg.image.load(path.join(self.img_dir, level_images[self.level_index])).convert() # Load background image for the level
        
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

    def start_game(self):
        self.state = 'playing'
        self.level_index = 0
        self.lives = 3
        self.load_level()
        self.level_start_time = pg.time.get_ticks()
        try: # If the input of user invalid set it to 120 as default value
            self.level_time_limit = max(1.0, float(self.home_time_input or '120'))
        except ValueError:
            self.level_time_limit = 120.0
        self.time_left = self.level_time_limit

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
        if self.screen_shake > 0:
            self.screen_shake -= self.dt * 1000  # Decrease screen shake timer
        
        if self.collision_timer > 0:
            self.collision_timer -= self.dt * 1000  # Decrease timer
            if self.collision_timer <= 0:
                self.load_level()  # Reset level after particle effect
                self.camera.update(self.player)  # Update camera to follow player position

        if self.life_loss_timer > 0:
            self.life_loss_timer = max(0, self.life_loss_timer - self.dt) # Decrease the life loss timer
        
        # Game timer countdown
        if self.level_start_time is not None:
            elapsed = (pg.time.get_ticks() - self.level_start_time) / 1000.0
            self.time_left = max(0, self.level_time_limit - elapsed)
            if self.time_left <= 0:
                self.state = 'game_over'
                self.game_over_reason = 'timeout'
                self.theme_sound.stop()
                self.game_over_sound.play()
                self.all_sprites = pg.sprite.Group()
                return
        
        # Love sound timer
        self.love_timer += self.dt
        if self.love_timer >= 30.0:
            self.love_sound.play()
            self.love_timer = 0.0
        
        # Collisions
        if pg.sprite.spritecollide(self.player, self.cores, True): # Collect core and remove it from the game
            self.coin_sound.play()

        if pg.sprite.spritecollide(self.player, self.enemies, False) and self.collision_timer <= 0: # If player hits an enemy and not in collision 
            self.lose_sound.play() # Play the lose life sound effect
            self.lives -= 1
            self.life_loss_timer = 1.8 # This starts the loss life animation
            if self.lives <= 0:
                self.state = 'game_over' # Set the game start over
                self.game_over_reason = 'enemy' # Set the reason 
                self.theme_sound.stop()  # Stop the background music
                self.game_over_sound.play()  # Play the game over sound
                self.all_sprites = pg.sprite.Group()  # Clear sprites for game over animation
                return
            else:
                self.load_level()  # Restart the current level with remaining time
                self.camera.update(self.player)  # Update camera to follow new player position
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
                    self.camera.update(self.player)  # Update camera to follow new player position
                else:
                    # Victory! All levels completed
                    self.state = 'victory'
                    self.theme_sound.stop()  # Stop the background music
                    self.victory_sound.play()  # Play the victory rap sound

    def draw(self):
        # Used AI to help with the screen shake effect: I used Gemini to come up with the code
        # I used the prompt: For the game Neon Escape, I want to add a screen shake effect when the player enters a level. 
        # Apply screen shake offset
        shake_offset = (0, 0)
        if self.screen_shake > 0:
            shake_offset = (randint(-5, 5), randint(-5, 5))  # Random shake offset
        
        # Scale background image to fit screen and draw it
        scaled_bg = pg.transform.scale(self.background, (WIDTH, HEIGHT)) # Scale background
        self.screen.blit(scaled_bg, shake_offset) # Draw the background with shake offset for a dynamic effect
        
        # Draw all sprites on top of the background
        for sprite in self.all_sprites:
            sprite_pos = self.camera.apply(sprite)
            self.screen.blit(sprite.image, (sprite_pos.x + shake_offset[0], sprite_pos.y + shake_offset[1]))
        
        # Apply flashlight effect for level 3 (index 2)
        if self.level_index == 2:
            self.draw_flashlight(shake_offset)
        
        # User Interface
        self.draw_text(f"LEVEL {self.level_index + 1}", 20, WHITE, 10 + shake_offset[0], 10 + shake_offset[1]) # Level indicator
        self.draw_text(f"CORES: {len(self.cores)}", 20, WHITE, 10 + shake_offset[0], 35 + shake_offset[1]) # Cores remaining
        self.draw_text(f"TIME: {self.time_left:.1f}s", 20, WHITE, WIDTH // 4 - 70 + shake_offset[0], 10 + shake_offset[1]) # Timer indicator
        self.draw_text(f"MODE: {self.difficulty}", 20, WHITE, WIDTH - 150 + shake_offset[0], 35 + shake_offset[1]) # Difficulty indicator
        self.draw_text(f"LIVES: {' '.join(['X'] * self.lives)}", 20, RED, WIDTH - 220 + shake_offset[0], HEIGHT - 35 + shake_offset[1])

        if self.life_loss_timer > 0:
            self.draw_life_loss_animation(shake_offset)
        
        # Draw dash cooldown timer at the top center
        self.draw_cooldown_timer(shake_offset)
        
        # Draw pause screen overlay
        if self.paused:
            # Semi-transparent overlay
            overlay = pg.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0)) # This is to draw the overlay on the screen when press p
            
            # Pause text
            self.draw_text_centered("PAUSED", 60, GREEN, HEIGHT // 2 - 40)
            self.draw_text_centered("Press P to Resume", 24, WHITE, HEIGHT // 2 + 40) # This is the button to resume the game.
        
        pg.display.flip()

    def draw_flashlight(self, shake_offset=(0, 0)):
        # Get player position on screen (account for camera)
        player_screen_pos = self.camera.apply(self.player)
        flashlight_x = int(player_screen_pos.x + shake_offset[0]) # This is to calculate the flashlight center(x coordinate).
        flashlight_y = int(player_screen_pos.y + shake_offset[1])# This is to calculate the flashlight center(y coordinate).
        
        # Create dark overlay surface with per-pixel alpha
        dark_overlay = pg.Surface((WIDTH, HEIGHT), pg.SRCALPHA)
        
        # Fill with kinda transparent dark shade
        dark_overlay.fill((0, 0, 0, 230))
        
        # Draw radial gradient for flashlight: reveals the scene underneath 
        flashlight_radius = 180
        for radius in range(flashlight_radius, 0, -4):
            # Fade from transparent to opaque from center outward
            alpha = int((1 - radius / flashlight_radius) ** 2 * 230)
            pg.draw.circle(dark_overlay, (0, 0, 0, alpha), (flashlight_x, flashlight_y), radius)
        
        # Blit the dark overlay with the flashlight cutout
        self.screen.blit(dark_overlay, (0, 0))

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
        if self.game_over_reason == 'timeout':
            self.draw_text_centered("Time has run out!", 24, RED, HEIGHT // 3 + 60)
        else:
            self.draw_text_centered("You were caught by the enemy!", 24, RED, HEIGHT // 3 + 60) # This is an additional message when caught by the enemy 
        
        # Restart instruction
        alpha = 150 + (105 * (pg.time.get_ticks() % 1000 > 500))  # This is to flash the particles
        restart_color = (alpha, alpha, alpha)
        if self.game_over_reason == 'timeout':
            self.draw_text_centered("PRESS R TO RETURN TO MENU", 24, restart_color, HEIGHT - 100)
        else:
            self.draw_text_centered("PRESS R TO RESTART LEVEL", 24, restart_color, HEIGHT - 100)
        
        pg.display.flip()

    def draw_victory(self):
        self.screen.fill(BLACK)
        
        # Initialize victory animation if not already started
        if not hasattr(self, 'victory_start_time'): # This is to make the vitory animation
            self.victory_start_time = pg.time.get_ticks()
            self.all_sprites = pg.sprite.Group()  # Clear sprites for victory animation
            self.last_firework_time = 0  # Track when last firework was created
            self.firework_colors = [RED, MAGENTA, CYAN, YELLOW]  # Colorful fireworks
        
        # Calculate elapsed time in seconds
        current_time = pg.time.get_ticks() # Current time
        elapsed_time = (current_time - self.victory_start_time) / 1000.0
        time_since_last_firework = (current_time - self.victory_start_time) - (self.last_firework_time * 1000)
        
        # Create fireworks every 400ms for 10 seconds (25 fireworks total)
        if elapsed_time < 10 and time_since_last_firework > 400:
            # Create a firework burst at a random position
            firework_x = random.randint(WIDTH // 4, 3 * WIDTH // 4)  # Random X in middle 50% of screen
            firework_y = random.randint(HEIGHT // 4, 3 * HEIGHT // 4)  # Random Y in middle 50% of screen
            firework_color = random.choice(self.firework_colors)  # Random color
            
            # Create particles radiating outward from center point
            for _ in range(50):  # 50 particles per firework burst
                particle = Particle(self, firework_x, firework_y, firework_color)
                # Create radial explosion pattern
                angle = random.uniform(0, 2 * 3.14159)  # Random angle in full circle
                speed = random.uniform(200, 400)  # Variable speed for natural spread
                particle.vel = pg.math.Vector2(speed * cos(angle), speed * sin(angle)) # This sets the velocity based on the angle of the particles
            
            self.last_firework_time = elapsed_time # Update the last firework time
        
        # Update and draw particles
        self.all_sprites.update()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, (sprite.rect.x, sprite.rect.y)) # Draw the particles with their own positions for the explosion effect.
        
        # Draw victory text
        self.draw_text_centered("GAME OVER", 80, RED, HEIGHT // 3) 
        self.draw_text_centered("Congrats! You Have Passed All 3 Levels!!!!", 28, MAGENTA, HEIGHT // 3 + 70)
        
        # Return instruction (flashing after animation completes)
        if elapsed_time >= 10:
            alpha = 150 + (105 * (pg.time.get_ticks() % 1000 > 500))
            return_color = (alpha, alpha, alpha)
            self.draw_text_centered("PRESS R TO RETURN TO MENU", 24, return_color, HEIGHT - 100) 
        
        pg.display.flip()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.SysFont('Copperplate Gothic', size, bold=True) # This creates a font object 
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y)) # Draw text at a specific position

    def draw_life_loss_animation(self, shake_offset=(0, 0)):
        alpha = int(255 * (self.life_loss_timer / 1.8))
        message = "1 LIFE GONE"
        font = pg.font.SysFont('Copperplate Gothic', 24, bold=True) # This create a font for the text
        surf = font.render(message, True, YELLOW)
        surf.set_alpha(alpha)
        x = WIDTH // 2 - surf.get_width() // 2 + shake_offset[0] # Adjust teh x position
        y = HEIGHT // 2 - 80 - int((2 - self.life_loss_timer) * 30) # Adjust the y position
        self.screen.blit(surf, (x, y))

    def draw_cooldown_timer(self, shake_offset=(0, 0)): # This draws the dash cooldown timer.
        # Calculate cooldown progress
        now = pg.time.get_ticks()
        time_since_dash = now - self.player.last_dash
        cooldown_remaining = max(0, DASH_COOLDOWN - time_since_dash) # Time remaining on cooldown
        cooldown_progress = 1 - (cooldown_remaining / DASH_COOLDOWN)  # 0 = on cooldown, 1 = ready
        
        # Timer bar dimensions
        bar_width = 200 # Width of the cooldown bar
        bar_height = 20 # Height of the cooldown bar
        bar_x = (WIDTH // 2) - (bar_width // 2) + shake_offset[0] # Center teh bar at the top of the screen with shake offset
        bar_y = 10 + shake_offset[1]
        
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
            timer_text = f"COOLDOWN: {seconds_remaining:.1f}s" # This shows the cool down time
            color = YELLOW
        else:
            timer_text = "READY!"
            color = CYAN #shows when dash ready 
        
        font = pg.font.SysFont('Copperplate Gothic', 14, bold=True)
        surf = font.render(timer_text, True, color) # renders the cooldown text
        text_rect = surf.get_rect(center=(WIDTH // 2 + shake_offset[0], bar_y + bar_height // 2 + 1))
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
                            self.level_index = 0
                            self.lives = 3
                            self.time_left = 120.0
                            self.game_over_sound.stop()  # Stop the game over sound
                            self.theme_sound.play(-1)  # Play the theme music in a loop
                            self.game_over_reason = None
                            if hasattr(self, 'game_over_started'): # This is to reset the particles 
                                delattr(self, 'game_over_started') # This is made to allow particles ot be created again.
                    elif self.state == 'victory':
                        if event.key == pg.K_r:
                            self.state = 'home'
                            self.level_index = 0  # Reset level index for next playthrough
                            self.theme_sound.play(-1)  # Play the theme music in a loop
                            self.victory_sound.stop()  # Stop the victory rap sound
                            if hasattr(self, 'victory_start_time'): # This is to reset the victory particles
                                delattr(self, 'victory_start_time') # This is made to allow particles to be created again.
                            if hasattr(self, 'last_wave_time'):
                                delattr(self, 'last_wave_time')
            if self.state == 'home': # Show home screen in the home state.
                self.show_home_screen()
            elif self.state == 'playing':
                self.update() # Update game Logic 
                self.draw() # Draw everything on the screen
            elif self.state == 'game_over':
                self.draw_game_over()
            elif self.state == 'victory':
                self.draw_victory()

if __name__ == "__main__":
    g = Game()
    g.run()