import math

# Game frame settings
FPS = 60

# Set the width and height of the screen [width, height]
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 550

# Define the man size in x and y, set to 32 blocks by default
MAP_SIZE_X = 32
MAP_SIZE_Y = 32

# Define the block size for the uniform cells in map, same on X width and Y height for raycast tilemaps
BLOCK_SIZE = 32

MAX_WALL_HEIGHT = BLOCK_SIZE
FOCAL_LENGTH = SCREEN_HEIGHT / 2
FOV = 80 #doesnt seem to do much

# Starting position of the player

PLAYER_INITIAL_X = 100
PLAYER_INITIAL_Y = 150
PLAYER_RADIUS = 15
PLAYER_SPEED = 70
PLAYER_VIEW_ANGLE = math.pi /2 - 0.6
PLAYER_ROTATION_SPEED = 2
PLAYER_RUNNING_SPEED = 140
PLAYER_HEALTH = 100

PLAYER_INITIAL_X = 373
PLAYER_INITIAL_Y = 229
PLAYER_VIEW_ANGLE = 0.472

MOUSE_SENSITIVITY = 1.7

# Define a small epsilon value to help avoid division by zero if needed
EPSILON = 1e-10

# Wall textures should be uniform in size, 64x64 pixels for example
TEXTURE_SIZE = 64

# Define colors, can be used anywhere
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0) 
BLUE = (0, 0, 255)
GREY = (128, 128, 128)
GREEN = (0, 255, 0)
LIGHT_GREY = (190, 190, 190)
LIGHT_GREY_EXTRA = (230, 230, 230)
DARK_GREY = (50, 50, 50)

SKY_BLUE = (135, 206, 235)
GROUND_BROWN = (139, 69, 19)
GROUND_GREY = (128, 128, 128)

# WALL COLORS and TEXTURES index values used in map grid array # TODO json file loading to be implemented by will use the same values

WHITE_EMPTY_SPACE = 0
BLUE_SOLID_WALL = 1
GREY_SOLID_WALL = 2
GREEN_SOLID_WALL = 3
RED_SOLID_WALL = 4
BLUE_TEXTURE_WALL = 5
GREY_TEXTURE_STONEWALL = 6

MINIMAP_SCALE_FACTOR = 0.5
MINIMAP_OFFSET_X = 144
MINIMAP_OFFSET_Y = 44

# CYAN, used instead of loading PNGs with alpha, this color is the default that is used with doom
# Double important when using Pygame which is very slow blitting with alpha (pngs/surfaces)
TRANSPARENT_COLOR_KEY = (0, 255, 255)

# Animation frame delay in ms
FRAME_DELAY = 150
# Shorter constant for when you want to update/draw faster
FRAME_DELAY_SHORT = 100

# EVENTS (ASYNC)
DEFAULT_EVENT = -100
CANCEL_EVENT = -1
WEAPON_FIRE_EVENT = 0
WEAPON_RELOAD_EVENT = 1
WEAPON_READY_EVENT = 2