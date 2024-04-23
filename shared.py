#shares between modules

import pygame

from consts import *

clock = pygame.time.Clock()

# Scan modes for raycasting # useful for debugging
# shortest, horizontal, vertical
scanmode = "shortest"

# True, False
paused = False

# 0 none, 1 minimal, 2 moderate, 3 maximum
DEBUG_LEVEL = 0

# Lookup table for wall colors and textures used for rendering map grid walls
wall_colors_textures_list = {
    GREY_TEXTURE_STONEWALL: '',  # reference to loaded array of pixels for texture, linked on init, null by default
    BLUE_TEXTURE_WALL: '',  
    GREEN_SOLID_WALL: GREEN,  
    GREY_SOLID_WALL: GREY,  
    BLUE_SOLID_WALL: BLUE,  
    RED_SOLID_WALL: RED,  
    WHITE_EMPTY_SPACE: WHITE,
}


# Create an array for items andnpcs

items = []
npcs = []

# Initialize the audio mixer 
pygame.mixer.init() 
    
# Create channels for multiple sounds(weapon, player, npc, level)
weapon_channel = pygame.mixer.Channel(0)

# Load shotgun sound
shotgun_firing = pygame.mixer.Sound('assets/audio/fx/shotgun_firing.mp3')

# 1d depth buffer
depth_buffer_1d = [0] * SCREEN_WIDTH