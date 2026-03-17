import pygame as pg
from settings import *

# Add missing constants to fix NameError
DASH_COOLDOWN = 1000  # 1 second cooldown for dash
DASH_DURATION = 200   # 0.2 seconds duration for dash

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE - 4, TILESIZE - 4))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.x, self.y = x * TILESIZE, y * TILESIZE
        self.pos = pg.math.Vector2(self.x, self.y)  # Added pos attribute
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
        hits = pg.sprite.spritecollide(self, self.game.walls, False)
        if dir == 'x':
            if hits:
                if self.vx > 0: self.x = hits[0].rect.left - self.rect.width
                if self.vx < 0: self.x = hits[0].rect.right
                self.vx = 0
                self.rect.x = self.x
        if dir == 'y':
            if hits:
                if self.vy > 0: self.y = hits[0].rect.top - self.rect.height
                if self.vy < 0: self.y = hits[0].rect.bottom
                self.vy = 0
                self.rect.y = self.y

    def update(self):
        self.get_keys()
        speed_mult = 3 if self.is_dashing and pg.time.get_ticks() - self.last_dash < DASH_DURATION else 1
        if speed_mult == 1: self.is_dashing = False

        self.x += self.vx * self.game.dt * speed_mult
        self.rect.x = self.x
        self.collide_with_walls('x')
        
        self.y += self.vy * self.game.dt * speed_mult
        self.rect.y = self.y
        self.collide_with_walls('y')
        
        self.pos = pg.math.Vector2(self.x, self.y)  # Update pos after movement

class Enemy(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.enemies
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE - 4, TILESIZE - 4))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.pos = pg.math.Vector2(x, y) * TILESIZE

    def update(self):
        # Simple tracking AI
        dir = (self.game.player.pos - self.pos)
        if dir.length_squared() > 0:
            dir = dir.normalize()
            self.pos += dir * ENEMY_SPEED * self.game.dt
        self.rect.topleft = self.pos

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE

class EnergyCore(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.cores
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE//2, TILESIZE//2))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x * TILESIZE + TILESIZE//2, y * TILESIZE + TILESIZE//2)

class Portal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.portals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(MAGENTA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE