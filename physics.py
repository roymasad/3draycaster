
from consts import *

# Check collision with level walls, use proposed_player to check for collision and update player position if it is valid
# disallow_clipping is a flag to avoid clipping through the wall, it does so by checking if the player is at least 1 block away from surrounding walls
def check_level_collision(player, proposed_x, proposed_y, level, player_body_buffer = 5):

    # Add the player body size buffer (radius) to the proposed position
    # this way the play body does not clip through the walls
    
    proposed_x_buffer = player.x
    proposed_y_buffer = player.y
    
    if (proposed_x > player.x):
        proposed_x_buffer = player.x + player_body_buffer
        
    if (proposed_x < player.x):
        proposed_x_buffer = player.x - player_body_buffer
        
    if (proposed_y > player.y):
        proposed_y_buffer = player.y + player_body_buffer
    
    if (proposed_y < player.y):
        proposed_y_buffer = player.y - player_body_buffer
        

    # Proposed new grid location
    grid_x = int(proposed_x_buffer / BLOCK_SIZE)
    grid_y = int(proposed_y_buffer / BLOCK_SIZE)
     
    # # Wall clipping agrressivecheck, disabled by default (keep 1 grid distance from walls)
    # if disallow_clipping:
    #     # Calculate the grid coordinates of the cells around the player and use min/max to avoid out of bounds errors
    #     grid_x_left = max(0, grid_x - 1)
    #     grid_x_right = min(MAP_SIZE_X - 1, grid_x + 1)
    #     grid_y_up = max(0, grid_y - 1)
    #     grid_y_down = min(MAP_SIZE_Y - 1, grid_y + 1)

    #     # Check if any of the cells around the player contain a wall
    #     for x in range(grid_x_left, grid_x_right + 1):
    #         for y in range(grid_y_up, grid_y_down + 1):
    #             if level[y][x] > 0:
    #                 # There's a wall nearby, don't move the player, return without changing x,y
    #                 return player
    
    
    if level[grid_y][grid_x] > 0:
        # There's a wall nearby, don't move the player, return without changing x,y
        return player
    
    # If map grid is empty accept the move
    if level[grid_y][grid_x] == 0:
        player.x =  proposed_x
        player.y =  proposed_y
    
    # If move is not valid, return the original player with original x,y only
    # If valid, return with new x,y 
    return player
