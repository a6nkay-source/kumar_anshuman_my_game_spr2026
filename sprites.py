from random import *
import pygame as pg
from settings import *

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
        self.image = pg.Surface((28, 28)) # Slightly smaller than tile for better collision
        self.image.set_colorkey((0,0,0))
        draw_pixel_rect(self.image, CYAN, self.image.get_rect()) # Draw player with pixelated style
        self.rect = self.image.get_rect()
        # Center the player on the tile
        self.pos = pg.math.Vector2(x * TILESIZE + TILESIZE // 2, y * TILESIZE + TILESIZE // 2)
        self.rect.center = self.pos
        self.vel = pg.math.Vector2(0, 0)
        self.last_dash = -DASH_COOLDOWN
        self.health = PLAYER_HEALTH

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
        self.image = pg.Surface((26, 26))
        draw_pixel_rect(self.image, RED, self.image.get_rect())
        self.rect = self.image.get_rect()
        # Center the enemy on the tile
        self.pos = pg.math.Vector2(x * TILESIZE + TILESIZE // 2, y * TILESIZE + TILESIZE // 2)
        self.rect.center = self.pos
        self.vel = pg.math.Vector2(0, 0)
        self.speed = ENEMY_SPEED  # Default speed, modified by difficulty

    def update(self):
        dir = (self.game.player.pos - self.pos)
        if dir.length() > 0:
            self.vel = dir.normalize() * self.speed
        else:
            self.vel = pg.math.Vector2(0, 0)
        
        # Move in x direction and check for wall collisions
        self.pos.x += self.vel.x * self.game.dt
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        
        # Move in y direction and check for wall collisions
        self.pos.y += self.vel.y * self.game.dt
        self.rect.y = self.pos.y
        self.collide_with_walls('y')

    def collide_with_walls(self, dir):
        hits = pg.sprite.spritecollide(self, self.game.walls, False)
        if hits:
            if dir == 'x':  # Horizontal collision
                if self.vel.x > 0: self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0: self.pos.x = hits[0].rect.right
                self.rect.x = self.pos.x
            if dir == 'y':  # Vertical collision
                if self.vel.y > 0: self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0: self.pos.y = hits[0].rect.bottom
                self.rect.y = self.pos.y

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

class Portal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.portals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(MAGENTA) # Portal background
        pg.draw.rect(self.image, BLACK, [4, 4, 24, 24], 2) # Portal with a black border
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE # Position portal based on tile coordinates

# Want to add this for particle affects when colliding with enemies or getting cores
class Particle(pg.sprite.Sprite):
    def __init__(self, game, x, y, color):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(5, 25) # Random size for particles for a nice look
        self.image = pg.Surface((size, size)) # Create a small surface 
        self.image.fill(color) # Particles will be a specific color. 
        self.rect = self.image.get_rect() # Rect: Used as the position is needed to be found.
        self.pos = pg.math.Vector2(x, y) 

        # Random burst direction
        self.vel = pg.math.Vector2(uniform(-1, 1), uniform(-1, 1)) * 100
        self.life = 255 # Opacity/Life timer

    def update(self):
        self.life -= 15 # This will make the particles fade over time
        if self.life <= 0: # Remove the particle when it goes away.
            self.kill()
        else:
            self.pos += self.vel * self.game.dt
            self.rect.center = self.pos
            self.image.set_alpha(self.life)