import pygame as pg                     # Import pygame library for graphics, input, sprites, etc.
from pygame.sprite import Sprite        # Import Sprite base class to create game objects
from settings import *                  # Import all constants 

vec = pg.math.Vector2                   # Shortcut name for pygame’s vector class 


def collide_hit_rect(one, two):  # Function that checks collision using hit rectangles instead of sprite rect
    # one.hit_rect = custom collision box for sprite one
    # two.rect = regular rectangle for sprite two
    return one.hit_rect.colliderect(two.rect)  # returns True if rectangles overlap
    
# This function looks for x and y collision in sequence and sets x and y position
def collide_with_walls(sprite, group, dir):
    # sprite = object moving
    # group = group of walls to check collision with
    # dir = direction of movement 
    
    if dir == 'x':  # Only checking horizontal collisions
        # spritecollide checks if sprite hits any sprite in group
        # False = don't delete walls if collision happens
        # collide_hit_rect = custom collision detection function
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            #print("collided with wall from x dir")
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2 # Checks if hits the rectangle for horizontal collisions 
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':  # Only checking vertical collisions
        # spritecollide checks if sprite hits any sprite in group
        # False = don't delete walls if collision happens
        # collide_hit_rect = custom collision detection function
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            print("collided with wall from y dir")
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.width / 2 # Checks if hits the rectangle for vertical collisions
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.width / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Player(Sprite):
    def __init__(self, game, x, y):
        # Add player to sprite group that contains all sprites
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)

        self.game = game  # reference to main game object

        # Create player square image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(WHITE)  # fill player with white color

        # Rectangle used for drawing and positioning
        self.rect = self.image.get_rect()

        # Velocity vector 
        self.vel = vec(0,0)

        # Position stored as vector for precise movement
        self.pos = vec(x,y) * TILESIZE

        # Hit rectangle used for collision 
        self.hit_rect = PLAYER_HIT_RECT 


    def get_keys(self):
        # Reset velocity every frame before checking input
        self.vel = vec(0,0)

        # Get all keyboard key states
        keys = pg.key.get_pressed()

        # Horizontal movement
        if keys[pg.K_a]:            # if A pressed: move left
            self.vel.x = -PLAYER_SPEED
        if keys[pg.K_d]:            # if D pressed: move right
            self.vel.x = PLAYER_SPEED

        # Vertical movement
        if keys[pg.K_w]:            # if W pressed: move up
            self.vel.y = -PLAYER_SPEED
        if keys[pg.K_s]:            # if S pressed: move down
            self.vel.y = PLAYER_SPEED

        # If moving diagonally, reduce speed so diagonal isn’t faster
        if self.vel.x != 0 and self.vel.y != 0:
            self.vel *= 0.7071      # normalize diagonal speed


    def update(self):
        # Called every frame automatically

        # Get keyboard input and update velocity
        self.get_keys()

        # Update rectangle center to match position
        self.rect.center = self.pos

        # Move player based on velocity and delta time
        # dt makes movement framerate independent
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.all_walls, 'x') # Calls function to check horizontal collisions
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.all_walls, 'y')# Calls function to check vertical collisions
        self.rect.center = self.hit_rect.center

class Mob(Sprite):
    def __init__(self, game, x, y):
        # Add mob to all_sprites group
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)

        self.game = game

        # Create mob square image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(RED)  # mob is red

        self.rect = self.image.get_rect()

        # Velocity direction vector 
        self.vel = vec(1,0)

        # Position stored as vector
        self.pos = vec(x,y) * TILESIZE

        # Movement speed
        self.speed = 10


    def update(self):
        # Check collision with walls
        # True = delete wall if collision occurs
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)

        if hits:
            print("collided")  # debug message
            self.speed = -self.speed    # increase speed after hitting wall
            

        # If mob goes off screen horizontally
        if self.rect.x > WIDTH or self.rect.x < 0:
            self.speed *= -1      # reverse direction
            self.pos.y += TILESIZE  # move down one row

        # Move mob based on speed and direction
        self.pos += self.speed * self.vel

        # Update rectangle position
        self.rect.center = self.pos

class Wall(Sprite):
    def __init__(self, game, x, y):
        # Add wall to both all_sprites and all_walls groups
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)

        self.game = game

        # Create wall square
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)  # wall is green

        self.rect = self.image.get_rect()

        # Walls don’t move
        self.vel = vec(0,0) 

        # Position vector
        self.pos = vec(x,y) * TILESIZE

        # Set rectangle position
        self.rect.center = self.pos


    def update(self):
        pass  # walls don’t need updating

class Coin(Sprite):
    def __init__(self, game, x, y):
        # Add coin to all sprites group
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)

        self.game = game

        # Create coin square
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)  # coin is yellow

        self.rect = self.image.get_rect()

        # Coins don’t move
        self.vel = vec(0,0)

        # Position vector
        self.pos = vec(x,y) * TILESIZE


    def update(self):
        pass  # coin currently does nothing
