import pygame as pg
from settings import *

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites # Add player to all_sprites group for rendering and updates
        pg.sprite.Sprite.__init__(self, self.groups) # Initialize the sprite and add it to different groups
        self.game = game
        self.image = pg.Surface((TILESIZE - 4, TILESIZE - 4)) # Create a surface for the player sprite
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.x, self.y = x * TILESIZE, y * TILESIZE # Set initial position based on tile coordinates
        self.vx, self.vy = 0, 0
        self.health = PLAYER_HEALTH
        self.last_dash = 0
        self.is_dashing = False

    def get_keys(self):
        self.vx, self.vy = 0, 0
        keys = pg.key.get_pressed()
        if keys[pg.K_a]: self.vx = -PLAYER_SPEED
        if keys[pg.K_d]: self.vx = PLAYER_SPEED
        if keys[pg.K_w]: self.vy = -PLAYER_SPEED
        if keys[pg.K_s]: self.vy = PLAYER_SPEED

        # Dash logic
        now = pg.time.get_ticks()
        if keys[pg.K_SPACE] and now - self.last_dash > DASH_COOLDOWN:
            self.is_dashing = True
            self.last_dash = now
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vx > 0: self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0: self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.walls, False)
            if hits:
                if self.vy > 0: self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0: self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y
    def update(self):
        self.get_keys()
        speed_mult = 3 if self.is_dashing and pg.time.get_ticks() - self.last_dash < DASH_DURATION else 1 # If dashing and within dash duration then increase speed; otherwise normal speed
        if speed_mult == 1: self.is_dashing = False # End dash after duration

        self.x += self.vx * self.game.dt * speed_mult
        self.rect.x = self.x
        self.collide_with_walls('x')
        
        self.y += self.vy * self.game.dt * speed_mult
        self.rect.y = self.y
        self.collide_with_walls('y')