import pygame as pg                     # Import pygame library for graphics, input, sprites
from pygame.sprite import Sprite        # Import Sprite base class to create game objects
from settings import * 
                 # Import all constants 
from utils import *# Importing Utils
from os import path
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
        self.spritesheet = Spritesheet(path.join(self.game.img_dir, "sprite_sheet.png")) # Sets up spritesheet and getting image from sprite sheet
        self.load_images()# loads the images

        # Create player square image
        self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(WHITE)  # fill player with white color
        self.image = self.spritesheet.get_image(0,0,TILESIZE,TILESIZE)
        self.image.set_colorkey(BLACK)
        # Rectangle used for drawing and positioning
        self.rect = self.image.get_rect()

        # Velocity vector 
        self.vel = vec(0,0)
        # Position stored as vector for precise movement
        self.pos = vec(x,y) * TILESIZE
        # Hit rectangle used for collision 
        self.hit_rect = PLAYER_HIT_RECT 
        # 4 properties are important (logic check example)
        self.jumping = False
        self.walking = False
        self.last_update = 0
        self.current_frame = 0
    def get_keys(self):
        # Reset velocity every frame before checking input
        self.vel = vec(0,0)
        keys = pg.key.get_pressed()
        if keys[pg.K_f]:
            print('fired projectile')
            p = Projectile(self.game, self.pos.x, self.pos.y) 
        # Get all keyboard key states and check for movement keys
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

    def load_images(self):
       # Changed my sprite_sheet (llama:6 total image frames): Used Piskel library
        self.standing_frames = [self.spritesheet.get_image(0,0,TILESIZE,TILESIZE),
                                self.spritesheet.get_image(0,TILESIZE,TILESIZE,TILESIZE)]# This is to get the images from the sprite and is done to place it on the player.
        self.moving_frames = [self.spritesheet.get_image(TILESIZE*2,0,TILESIZE, TILESIZE),
                                self.spritesheet.get_image(TILESIZE*3, 0,TILESIZE,TILESIZE)]# helps sets
        for frame in self.standing_frames: # Load different frames: open sprite sheet to open it in a graphing editor
            frame.set_colorkey(BLACK)# Color key set for black pixels
        for frame in self.moving_frames:
            frame.set_colorkey(BLACK)

    def animate(self):
        now = pg.time.get_ticks() #gets current time
        if not self.jumping and not self.walking: #only while static: this needs to update self.walking and self.jumping
            if now - self.last_update > 350: #cooldown for sprite update 350 milliseconds per frame
                self.last_update = now #updates now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames) #this line iterates through all frames, and if you are on the last one, it goes back to the beginning
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame] #sets the current image to be that frame
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        elif self.jumping: 
            if now - self.last_update > 350:  # faster animation for jump
                self.last_update = now #updates now
                self.current_frame = (self.current_frame + 1) % len(self.jumping_frames) #this line iterates through all frames, and if you are on the last one, it goes back to the beginning
                bottom = self.rect.bottom

                bottom = self.rect.bottom
                self.image = self.jumping_frames[self.current_frame]# sets the current image to be that frame
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
    def state_check(self):
        if self.vel != vec(0,0):
            self.moving = True
        else: 
            self.moving = False

    def update(self):
        self.animate() # Animates the sprite and updates it to the player so the player looks animated.
        # Get keyboard input and update velocity
        self.get_keys()
        self.state_check() # making sure that animation updating
        # Update rectangle center to match position
        self.rect.center = self.pos

        # Move player based on velocity and delta time
        # dt (delta time) makes movement framerate independent
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
        #self.image = pg.Surface((TILESIZE, TILESIZE))
        #self.image.fill(GREEN)  # wall is green
        
        self.image = pg.image.load(os.path.join(script_dir, "images", "Wall.png")).convert_alpha()

        self.rect = self.image.get_rect()

        # Walls don’t move
        self.vel = vec(0,0) 

        # Position vector
        self.pos = vec(x,y) * TILESIZE

        # Set rectangle position
        self.rect.center = self.pos


    def update(self):
        pass  # walls don’t need updating



    class Projectile(Sprite):
        def __init__(self, game, x, y):
            self.groups = game.all_sprites, game.all_projectiles #group
            Sprite.__init__(self, self.groups)
            self.game = game
            self.image = pg.Surface((TILESIZE, TILESIZE))
            self.image.fill(RED) #only difference from player, the color
            self.rect = self.image.get_rect()
            self.vel = vec(1,0)
            self.pos = vec(x,y) * TILESIZE
            
 
        def update(self):
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False) # check for collision with walls
            print(hits)
            self.pos += self.vel * self.speed # move projectile
            self.rect.center = self.pos # update rectangle position

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

    