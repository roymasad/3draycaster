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
    def __init__(self, x, y, radius, speed, view_angle, rotation_speed, health, damage, name, fire_rate, state, accuracy):
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
        self.loadSpriteset()
        
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
    def __init__(self, x, y, radius = 5, speed = 30, view_angle = 0, rotation_speed = 1, health = 20, damage = 10, name = "Shotgun Guy", fire_rate = 1, state = NPCState.IDLE, accuracy = 1):
        super().__init__(x, y, radius, speed, view_angle, rotation_speed, health, damage, name, fire_rate, state, accuracy)
  