import enum
import time
import pygame
from consts import *
import shared

class WeaponState(enum.Enum):
    READY = 1
    FIRING = 2
    RELOADING = 3
    
class NPCState(enum.Enum):
    IDLE = 1
    WALKING = 1
    HUNTING = 2
    FIRING = 3
    DEAD = 4
    

# Player class
class Player:
    def __init__(self, x, y, radius, speed, view_angle, rotation_speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.view_angle = view_angle
        self.rotation_speed = rotation_speed
       
class Weapon:
    def __init__(self, damage, range, fire_rate, accuracy, ammo, state, name):
        self.damage = damage
        self.range = range
        self.fire_rate = fire_rate
        self.accuracy = accuracy
        self.ammo = ammo
        self.state = state
        self.name = name
        self.spriteset = None
        self.current_sprite = None
        self.timer = 0
        self.frame = 0
        self.lastframe = 0
        
    def update(self):
        pass
    def draw(self):
        pass
    def fire(self):
        pass
    def reload(self):
        pass
    def ready(self):
        pass
    def loadSpriteset(self):
        pass
        
class Shotgun(Weapon):
    def __init__(self, damage = 10, range = 100, fire_rate = 1, accuracy = 1, ammo = 30, state = WeaponState.READY, name = "Shotgun"):
        super().__init__(damage, range, fire_rate, accuracy, ammo, state, name)
        self.loadSpriteset()     
        
    def loadSpriteset(self):
        self.spriteset = {
            "idle": [pygame.image.load("assets/weapons/shotgun/idle/SHTGA0-KEY.png").convert(),
                     pygame.image.load("assets/weapons/shotgun/idle/SHTGB0-KEY.png").convert()
                     ], #use convert() if file is  color key, if not convert_alpha
            "firing": [pygame.image.load("assets/weapons/shotgun/firing/SHTFA0-KEY.png").convert(),
                        # pygame.image.load("assets/weapons/shotgun/firing/SHTFB0-KEY.png").convert()
                        ],
            "reloading": [pygame.image.load("assets/weapons/shotgun/reloading/SHTGB0-KEY.png").convert(),
                          pygame.image.load("assets/weapons/shotgun/reloading/SHTGC0-KEY.png").convert(),
                          pygame.image.load("assets/weapons/shotgun/reloading/SHTGD0-KEY.png").convert()],
        }
        
        # iterate over sprite set and scale each sprite value by 2 both in width and height
        for key, value in self.spriteset.items():
           for index, sprite in enumerate(value):

                # scale sprite, done once so doesnt affect runtime performance 
                scale = 1.5
                self.spriteset[key][index] = pygame.transform.scale(sprite, (sprite.get_width() * scale, sprite.get_height() * scale))
                
                # set transparency if not included in image alpha already. a legacy technique
                # slightly faster than using image alpha (PNG), requires images with color key 
                self.spriteset[key][index].set_colorkey(TRANSPARENT_COLOR_KEY)
                      
                # create a surface from the current sprite, surface to surface blitting 'should' be faster
                # but it is not improving fps, on the contrary, so it is disabled for now
                #new_surface = pygame.Surface((self.spriteset[key][index].get_width(), self.spriteset[key][index].get_height()), pygame.SRCALPHA)
                #new_surface.blit(self.spriteset[key][index], (0, 0))
                #self.spriteset[key][index] = new_surface
            
        
    def draw(self, screen):
                  
        texture_rect = self.current_sprite.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - self.current_sprite.get_height()/2))
        # This transparent blitting operation is very slow on Pygame, the bigger the area, the slower it is
        screen.blit(self.current_sprite, (texture_rect),area = None,special_flags=pygame.BLEND_ALPHA_SDL2)
        
    def fire(self):
        self.state = WeaponState.FIRING
        
        self.timer = pygame.time.get_ticks() - FRAME_DELAY # this skips the delay in the update function
        self.frame = 0
        
        # Play shotgun sound
        shared.weapon_channel.play(shared.shotgun_firing)
        
        # Not used, Schedule the reload timer event to trigger after some time 
        #pygame.time.set_timer(WEAPON_RELOAD_EVENT, 400 , 1)
        
    
    def reload(self):
        self.state = WeaponState.RELOADING
       
        # reset timer and frame for the animation for the update function 
        self.timer = pygame.time.get_ticks()
        self.frame = 0
        
    def ready(self):
        self.state = WeaponState.READY
        self.frame = 0
        
    def update(self):
        
        current_time = pygame.time.get_ticks()
        
        # run the animation only if the timer is ready (prevent running continuously)
        nextframe_ready = current_time - self.timer >= FRAME_DELAY
                
        if nextframe_ready == True:
                
            if self.state == WeaponState.READY:
                
                total_frames = self.spriteset["idle"].__len__() #might be slow
                if self.frame >= total_frames: #loop the animation
                    self.frame = 0

                self.current_sprite = self.spriteset["idle"][self.frame]
                self.frame += 1 #increment current frame for the set
                
            elif self.state == WeaponState.FIRING:
                
                total_frames = self.spriteset["firing"].__len__()
                if self.frame >= total_frames:
                    self.frame = 0
                    # switch to reloading state, exit/skip animation set loop
                    self.reload()

                self.current_sprite = self.spriteset["firing"][self.frame]
                self.frame += 1
                
            elif self.state == WeaponState.RELOADING:
                
                total_frames = self.spriteset["reloading"].__len__()
                if self.frame >= total_frames:
                    self.frame = 0
                    self.ready()

                self.current_sprite = self.spriteset["reloading"][self.frame]
                self.frame += 1
        
            # reset timer (after manual even was triggered)
            self.timer = pygame.time.get_ticks()
              
class NPC:
    def __init__(self, x, y, radius, speed, view_angle, rotation_speed, health, damage, name, fire_rate, state, accuracy, width, height, normalized_height, vertical_offset):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.view_angle = view_angle
        self.rotation_speed = rotation_speed
        self.health = health
        self.damage = damage
        self.name = name
        self.fire_rate = fire_rate
        self.state = state
        self.accuracy = accuracy
        self.spriteset = None
        self.current_sprite = None
        self.timer = 0
        self.frame = 0
        self.lastframe = 0
        self.width = width
        self.height = height
        self.normalized_height = normalized_height
        self.vertical_offset = vertical_offset

        
    def update(self):
        pass
    def draw(self):
        pass
    def fire(self):
        pass
    def die(self):
        pass
    def loadSpriteset(self):
        pass
        
class ShotgunGuy(NPC):
    def __init__(self, x = 500, y = 500, radius = 5, speed = 30, view_angle = 0, rotation_speed = 1, 
                 health = 20, damage = 10, name = "Shotgun Guy", fire_rate = 1, state = NPCState.IDLE, 
                 accuracy = 1 , width = 35, height = 55, normalized_height = 60, vertical_offset = 0.2):
        super().__init__(x, y, radius, speed, view_angle, rotation_speed, health, damage, name, fire_rate, state, accuracy, width, height, normalized_height, vertical_offset)   
        self.loadSpriteset()
        
    def loadSpriteset(self):
        
        self.spriteset = {
            "idle_front": [
                            pygame.image.load("assets/npc/shotgunguy/idle/front/SHIDA1-KEY.png").convert(),
                            pygame.image.load("assets/npc/shotgunguy/idle/front/SHIDB1-KEY.png").convert()
                     ], 
            "firing_front": [
                            pygame.image.load("assets/npc/shotgunguy/firing/front/SPOSE1-KEY.png").convert(),
                            pygame.image.load("assets/npc/shotgunguy/firing/front/SPOSF1-KEY.png").convert()
                        ],
            "walking_front": [
                            pygame.image.load("assets/npc/shotgunguy/walking/front/SPOSA1-KEY.png").convert(),
                            pygame.image.load("assets/npc/shotgunguy/walking/front/SPOSB1-KEY.png").convert(),
                            pygame.image.load("assets/npc/shotgunguy/walking/front/SPOSC1-KEY.png").convert(),
                            pygame.image.load("assets/npc/shotgunguy/walking/front/SPOSD1-KEY.png").convert()
                          ],
        }
        

        # iterate over sprite set and set color key
        for key, value in self.spriteset.items():
           for index, sprite in enumerate(value):

                self.spriteset[key][index].set_colorkey(TRANSPARENT_COLOR_KEY)
        
        
    def draw(self, screen, player):

        # Get distance between sprite and player
        distance = math.sqrt((player.x - self.x)**2 + (player.y - self.y)**2)
        
        # Dynamically inversly scale sprite size based on distance
        scale = 100 / distance 

        # Calculate npc screen projected x position, based on player vs npc positions, no matrix math
        # based on, which used degrees instead of radians to calculate small steps
        # https://wynnliam.github.io/raycaster/news/tutorial/2019/04/03/raycaster-part-02.html
        # TODO seems inaccurate in alignement with FOV as is, to investigate why or replace algo/fix FOV
        
        # Get relative vector difference between player and npc
        h_x = self.x - player.x
        h_y = self.y - player.y
        
        # Get angle difference
        p = math.degrees(math.atan2(h_y, h_x))
        
        if (p > 360):
            p -= 360
        if (p < 0):
            p += 360
            
        # To speed up calculate, i wont use the FOV as variable but instead precalculate it
        # FOV as defined in consts.py is 80, but 120 seems to 'align' better the NPC and walls
        # TODO investigate why 120 is better than 80? is FOV misconfigured or something?
        # HALF FOV = 60, this is required in the formula
        #q = ((math.degrees(player.view_angle) + FOV/2) - p)
        q = ((math.degrees(player.view_angle) + 60) - p)
        
        # projected x position
        # prebake screen width / FOV, assuming width of 800, then it is 6.66
        #screen_x =  q * (SCREEN_WIDTH / 120)
        screen_x =  q * (6.66)
        
        # invert screen_x on the vertical axis
        # TODO this is a workaround, it is best calculate x correctly instead above (tan?)
        screen_x = int(SCREEN_WIDTH - screen_x)

        # Draw only when projected x is within FOV/Screen
        if screen_x >= 0 and screen_x < (SCREEN_WIDTH-1):
            
            self.current_sprite = pygame.transform.scale(self.current_sprite, (self.width * scale, self.height * scale))
     
            texture_rect = self.current_sprite.get_rect(center=(screen_x, SCREEN_HEIGHT/2 + self.current_sprite.get_height() * self.vertical_offset )) 
        
            # if sprite doesnt have a wall in the way, draw it
            # TODO BUG here or in storing the depth buffer:
            # on some view angles the sprites draw infront of closer walls, maybe quadrant related
            # TODO enhancement, this should occlude per column of a sprite and not the entire sprite
            if distance < shared.depth_buffer_1d[screen_x] :
                screen.blit(self.current_sprite, (texture_rect),area = None,special_flags=pygame.BLEND_ALPHA_SDL2)
            
        
    
    def update(self):
        
        current_time = pygame.time.get_ticks()
        
        # run the animation only if the timer is ready (prevent running continuously)
        nextframe_ready = current_time - self.timer >= FRAME_DELAY_SHORT
                
        if nextframe_ready == True:
                
            if self.state == NPCState.IDLE:
                
                total_frames = self.spriteset["idle_front"].__len__() #might be slow
                if self.frame >= total_frames: #loop the animation
                    self.frame = 0

                self.current_sprite = self.spriteset["idle_front"][self.frame]
                self.frame += 1 #increment current frame for the set
                
            elif self.state == NPCState.FIRING:
                
                total_frames = self.spriteset["firing_front"].__len__()
                if self.frame >= total_frames:
                    self.frame = 0
                    # switch to reloading state, exit/skip animation set loop
                    self.reload()

                self.current_sprite = self.spriteset["firing_front"][self.frame]
                self.frame += 1
                
            elif self.state == NPCState.WALKING:
                
                total_frames = self.spriteset["walking_front"].__len__()
                if self.frame >= total_frames:
                    self.frame = 0
                    self.ready()

                self.current_sprite = self.spriteset["walking_front"][self.frame]
                self.frame += 1
        
            # reset timer (after manual even was triggered)
            self.timer = pygame.time.get_ticks()
    
    def fire(self):
        pass
    def die(self):
        pass
  