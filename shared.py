#shares between modules

from consts import *

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