from random import *
import pygame as pg
from settings import *
from utils import astar_pathfind # This is the A* pathfinding function
from math import cos, sin # Import trigonometric functions for particle physics 

# Make this to show borders bbetter for a better User Interface
# The user will have a better experience with this 
def draw_pixel_rect(surface, color, rect, border_size=2):

    pg.draw.rect(surface, color, rect)
    inner_rect = rect.inflate(-border_size*2, -border_size*2) # Create smaller rect for inner border
    pg.draw.rect(surface, (0, 0, 0), inner_rect, border_size) # Add inner black border for pixel effect

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((24, 24))
        self.image.set_colorkey((0,0,0))
        draw_pixel_rect(self.image, CYAN, self.image.get_rect()) # Draw player with pixelated style
        self.rect = self.image.get_rect()
        # Center the player on the tile
        self.pos = pg.math.Vector2(x * TILESIZE + TILESIZE // 2, y * TILESIZE + TILESIZE // 2)
        self.rect.center = self.pos
        self.vel = pg.math.Vector2(0, 0)
        self.last_dash = -DASH_COOLDOWN
        self.teleport_timer = 0

    def update(self):
        self.vel = pg.math.Vector2(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_a]: self.vel.x = -PLAYER_SPEED # Moves the Left
        if keys[pg.K_d]: self.vel.x = PLAYER_SPEED # Moves to the Right
        if keys[pg.K_w]: self.vel.y = -PLAYER_SPEED # Moves Upward
        if keys[pg.K_s]: self.vel.y = PLAYER_SPEED # Moves Downward

        now = pg.time.get_ticks()
        is_dashing = keys[pg.K_SPACE] and (now - self.last_dash < DASH_DURATION)
        if keys[pg.K_SPACE] and now - self.last_dash > DASH_COOLDOWN:
            self.last_dash = now
            if hasattr(self.game, 'blaze_sound'):
                self.game.blaze_sound.play()

        speed = PLAYER_SPEED * (DASH_SPEED_MULT if is_dashing else 1)

        if self.vel.length() > 0:
            self.vel = self.vel.normalize() * speed

        self.pos.x += self.vel.x * self.game.dt # Move the player based on velocity and delta time
        self.rect.x = self.pos.x # Update rect position for collision detection
        self.collide_with_walls('x')
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

        if self.vel.length() > 0 and is_dashing:
            # Create dash particles
            if random() > 0.5 or is_dashing: # Random chance to create a particle for a more dynamic effect
                Particle(self.game, self.rect.centerx, self.rect.centery, CYAN)
        if is_dashing:
            # Create a trail of particles while dashing
            for _ in range(3):
                Particle(self.game, self.rect.centerx, self.rect.centery, CYAN)


    def collide_with_walls(self, dir):
        hits = pg.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            if dir == 'x': # This is for horizontal collision
                if self.vel.x > 0: self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0: self.pos.x = hits[0].rect.right # Adjust position to prevent moving into wall
                self.rect.x = self.pos.x
            if dir == 'y': # This is for vertical collision
                if self.vel.y > 0: self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0: self.pos.y = hits[0].rect.bottom # Adjust position to prevent moving into wall
                self.rect.y = self.pos.y

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((24, 24))
        draw_pixel_rect(self.image, RED, self.image.get_rect()) # This is the enemy drawn pixelated
        self.rect = self.image.get_rect()
        # Center the enemy on the tile
        self.pos = pg.math.Vector2(x * TILESIZE + TILESIZE // 2, y * TILESIZE + TILESIZE // 2)
        self.rect.center = self.pos
        self.vel = pg.math.Vector2(0, 0)
        self.speed = ENEMY_SPEED  # Default speed, modified by difficulty
        
        # A* Pathfinding variables
        self.path = []  # Current path from A* algorithm
        self.path_index = 0  # Current waypoint in path
        self.path_recalc_timer = 0  # Timer for path recalculation
        self.path_recalc_interval = 0.25  # Recalculate path every 0.25 seconds for smoother chasing
        self.stuck_timer = 0  # Timer to detect if enemy is stuck
        self.last_pos = self.pos.copy()  # Track previous position
        self.stuck_threshold = 0.3  # If no movement for 0.3 seconds, consider stuck

    def update(self):
        # Always chase the player with A* pathfinding.
        # This prevents the enemy from stopping when the player moves far away.
        self.stuck_timer += self.game.dt
        if self.stuck_timer >= 0.1:  # Check every 0.1 seconds
            distance_moved = (self.pos - self.last_pos).length()
            if distance_moved < 5:  # If moved less than 5 pixels
                self.stuck_timer = 0
            else:
                self.stuck_timer = 0
                self.last_pos = self.pos.copy()

        # If there is no current path, or the current path is finished, recalculate immediately.
        if not self.path or self.path_index >= len(self.path):
            self.path = astar_pathfind(self.pos, self.game.player.pos, self.game.map.data)
            self.path_index = 0
            self.path_recalc_timer = 0
        else:
            # Recalculate path periodically while following a valid route.
            self.path_recalc_timer += self.game.dt
            if self.path_recalc_timer >= self.path_recalc_interval:
                self.path_recalc_timer = 0
                self.path = astar_pathfind(self.pos, self.game.player.pos, self.game.map.data)
                self.path_index = 0

        # Follow the calculated path if available.
        if self.path and self.path_index < len(self.path):
            waypoint = pg.math.Vector2(self.path[self.path_index])
            dir_to_waypoint = waypoint - self.pos

            if dir_to_waypoint.length() < self.speed * self.game.dt + 10:
                self.path_index += 1
            elif dir_to_waypoint.length() > 0:
                self.vel = dir_to_waypoint.normalize() * self.speed
            else:
                self.vel = pg.math.Vector2(0, 0)
        else:
            # Fallback: if no path is available, keep moving directly toward the player.
            dir_to_player = self.game.player.pos - self.pos
            if dir_to_player.length() > 0:
                self.vel = dir_to_player.normalize() * self.speed
            else:
                self.vel = pg.math.Vector2(0, 0)

        # Move in x direction and check for wall collisions
        self.pos.x += self.vel.x * self.game.dt
        self.rect.centerx = self.pos.x
        self.collide_with_walls('x')
        
        # Move in y direction and check for wall collisions
        self.pos.y += self.vel.y * self.game.dt
        self.rect.centery = self.pos.y
        self.collide_with_walls('y')

    def collide_with_walls(self, dir):
        hits = pg.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            if dir == 'x':  # Horizontal collision
                if self.vel.x > 0:  # Moving right
                    self.pos.x = hits[0].rect.left - self.rect.width // 2
                if self.vel.x < 0:  # Moving left
                    self.pos.x = hits[0].rect.right + self.rect.width // 2
                self.rect.centerx = self.pos.x
                self.vel.x = 0  # Stop horizontal movement
            if dir == 'y':  # Vertical collision
                if self.vel.y > 0:  # Moving down
                    self.pos.y = hits[0].rect.top - self.rect.height // 2
                if self.vel.y < 0:  # Moving up
                    self.pos.y = hits[0].rect.bottom + self.rect.height // 2
                self.rect.centery = self.pos.y
                self.vel.y = 0  # Stop vertical movement

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # Beveled pixel look
        self.image.fill(DARK_GRAY)
        pg.draw.rect(self.image, WHITE, [0, 0, TILESIZE, TILESIZE], 1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE

class EnergyCore(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.cores
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((16, 16))
        draw_pixel_rect(self.image, YELLOW, self.image.get_rect())
        self.rect = self.image.get_rect()
        self.rect.center = (x * TILESIZE + 16, y * TILESIZE + 16)

class Bomb(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.bombs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((20, 20), pg.SRCALPHA)
        draw_pixel_rect(self.image, RED, self.image.get_rect()) # Draw the bomb 
        pg.draw.circle(self.image, BLACK, (10, 10), 6, 2) # Added a circle on the bomb
        self.rect = self.image.get_rect() # center the bomb
        self.rect.center = (x * TILESIZE + TILESIZE // 2, y * TILESIZE + TILESIZE // 2) # Center the bomb

class Portal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.portals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(MAGENTA) # Portal background
        pg.draw.rect(self.image, BLACK, [4, 4, 24, 24], 2) # Portal with a black border
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE # Position portal based on tile coordinates

class TeleportPortal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.teleporters
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(BLUE)
        pg.draw.rect(self.image, WHITE, [4, 4, TILESIZE - 8, TILESIZE - 8], 2)
        pg.draw.circle(self.image, CYAN, (TILESIZE // 2, TILESIZE // 2), 8, 0)
        self.rect = self.image.get_rect(topleft=(x * TILESIZE, y * TILESIZE))
        self.dest = None

# Want to add this for particle affects when colliding with enemies or getting cores
class Particle(pg.sprite.Sprite): 
    def __init__(self, game, x, y, color):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(3, 15) # Random size for particles for a nice look
        self.image = pg.Surface((size, size)) # Create a small surface 
        self.image.fill(color) # Particles will be a specific color. 
        self.rect = self.image.get_rect() # Rect: Used as the position is needed to be found.
        self.pos = pg.math.Vector2(x, y) 

        # Random burst direction with variable speeds
        angle = uniform(0, 2 * 3.14159)  # Random angle in full circle
        speed = uniform(150, 400)  # Variable speed for natural spread
        self.vel = pg.math.Vector2(speed * cos(angle), speed * sin(angle))
        self.acc = pg.math.Vector2(0, 300)  # Gravity acceleration downward
        self.life = 255 # Opacity/Life timer
        self.max_life = 255

    def update(self):
        # Apply gravity/acceleration
        self.vel += self.acc * self.game.dt
        # Apply velocity to position
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        
        # Fade out over time
        self.life -= 12 # Faster fade for more dramatic effect
        if self.life <= 0: # Remove the particle when it goes away.
            self.kill()
        else:
            # Calculate alpha from remaining life
            alpha = int((self.life / self.max_life) * 255)
            self.image.set_alpha(alpha)

class ExplosionParticle(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.explosion_particles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(4, 12) # Randome size for the explosion particles
        self.image = pg.Surface((size, size), pg.SRCALPHA) # Create a small surface with alpha for explosion particle effects
        self.image.fill(RED) # Red fairy explosion effect
        self.rect = self.image.get_rect() # Rect Used as teh position is needed
        self.pos = pg.math.Vector2(x, y) # Center the explosion
        self.rect.center = self.pos # Set the rect center
        self.vel = pg.math.Vector2(uniform(-300, 300), uniform(-300, 300)) # Random velocity for the explosion
        self.life = 5.0 # Life timer for explosion particles, they will last longer
        self.max_life = 5.0 # Max life for explosion particles, used for fading out effect

    def update(self):
        self.pos += self.vel * self.game.dt # Move the explosion particle
        self.rect.center = self.pos
        self.life -= self.game.dt
        if self.life <= 0:
            self.kill()
        else:
            alpha = int((self.life / self.max_life) * 255)
            self.image.set_alpha(alpha) # fade out the explosion particle over time