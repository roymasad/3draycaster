
import math
from consts import *
from termcolor import colored
import shared

# Cast a ray from the player's position at a given angle and return the distance, coordinates and meta data(color) to the nearest HIT wall
# POV_xRange is the range of columns to scan for the ray, it is used per scan limit of the screen width/POV by the caller of this function
# ignore_debug is used to debug only top view direct rays, ignoring 2d fov and 3d horizonal raycasts
def cast_ray(player, ray_angle, level, POV_xRange, ignore_debug = False):
    
    # Wrap the angle to 0-2pi for consistency
    ray_angle = ray_angle % (2 * math.pi)
    
    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print(colored("\n\n==SENDING RAY using DDA sub Steps==", "green"))  
    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("Player X: {}   Player Y: {}  Player Angle: {:.3f} Ray Angle: {:.3f}".format(int(player.x), int(player.y), player.view_angle, ray_angle))
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print("View column scan from X : " + str(POV_xRange))
    
    # Pre calculate the ray direction values in cos and sin (useful for right triangle calculations)
    cos_angle = math.cos(ray_angle)  
    sin_angle = math.sin(ray_angle)  
    tan_angle = math.tan(ray_angle)
    atan_angle = math.atan(ray_angle)

    # Calculate the internal delta x and y of the player position inside the current block
    offset_px = player.x % BLOCK_SIZE
    offset_py = player.y % BLOCK_SIZE
    # Normalize to use normalized formulas
    normalized_offset_px = offset_px / BLOCK_SIZE
    normalized_offset_py = offset_py / BLOCK_SIZE
    
    # Calculate the origin block x and y of the ray position for debugging
    initial_grid_x = int(player.x / BLOCK_SIZE)
    initial_grid_y = int(player.y / BLOCK_SIZE)
    
    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("Initial Grid X: " + str(initial_grid_x) + "   Grid Y: " + str(initial_grid_y))
    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("Cos Angle: {:.3f}   Sin Angle: {:.3f}  Tan Angle: {:.3f}   aTan Angle: {:.3f}".format(cos_angle, sin_angle, tan_angle, atan_angle))
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print(f"Offset X: {offset_px:.3f}, Offset Y: {offset_py:.3f}")
    
    """
    This section is the DDA algorithm for raycasting
    It is a more efficient way to step through the grid
    Based on the ray direction and the current position of the ray,
    it calculates the next potential hit location on the grid line in a fast way
    """
    
    # ./doc folder pix credit to the excellent DDA explainer youtube video by fahlrile https://www.youtube.com/watch?v=IDmWuSrEkow
    # Kindly note the Y axis direction is different between the video/picture and the code in python
    # You can use the 'Image Preview' VS Code plugin from the marketplace to see image previews in comment lines below
        
    # Shared variables
    
    # Steps trackers for the vertical and horizontal hits, i prefer variables to be descriptive and declared explicitly in python
    steps = 0 
    steps_v = 0
    steps_h = 0
    
    # Distance variables for the vertical and horizontal hits
    distance_v = 0
    distance_h = 0

    # We need the sign of the cos and sin to know if we are going to add or subtract the offset per axis
    x_sign = int(math.copysign(1, cos_angle))
    y_sign = int(math.copysign(1, sin_angle))
    
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print("X Sign: " + str(x_sign) + "   Y Sign: " + str(y_sign))
    
    # Final results variables
    next_rayhit_x_h = 0
    next_rayhit_y_h = 0
    next_rayhit_x_v = 0
    next_rayhit_y_v = 0
    
    # TLDR: DDA Algorithm
    # We are going to do 2 main calculations, one with X locked on grid lines and Y as incremental (vertical intersections)
    # Then we are going to do one with Y locked on grid lines and X as incremental (horizontal intersections)
    # And then select the one that yields the shortest distance to optimial traversal (frontface vs backface of the wall)
    # Reference: ./doc/dda-overview.png
    # Referecece: ./doc/overlapped-shortest.png
    # Note the code accounts for both +/i axis scanning unlike the reference image that only accounts for positive axis scanning

    #############################################################
    # Calculate the next potential hit on the Vertical grid lines
    #############################################################
    # X locked to Grid, Y incremental, Vertical Intersections
    # Check if the ray is facing right/left based on cos of angle so we now if we are going to add or subtract the offset also 
    # (Also check python cos/sin range/quadrants and axis direction)
    
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print (colored("\n==VERTICAL RAY SCANNING==","blue"))
    
    # Initialize the deltas to 0
    delta_xi = 0
    delta_yi = 0
    delta_xe = 0
    delta_ye = 0
    
    # texture "x" indexing needed for fake 3d walls rending in caller function (normalized)
    texture_x_h = 0
    texture_x_v = 0
    texture_x = 0
    
    # Ray is facing right
    if cos_angle > 0:
        delta_xi = (1 - normalized_offset_px) # use normalized values
    # Ray is facing left
    elif cos_angle < 0:
        delta_xi = normalized_offset_px
    # This is parallel, and will not hit anything, so we set the distance to a high value to avoid being selected as the shortest distance
    else:
        delta_xi = 0
        distance_v = 1000000 # Set to a high value to avoid being selected as the shortest distance

    if delta_xi != 0:
        # Calculate the Y value based on angle as defined by the right triangle rules
        # Reference, check ./doc/vertical-intersections-step1.png   
                
        # Calculate the internal delta y side length value as defined by the right triangle rules
        # (We denormalize by multiplying by BLOCK_SIZE)
        
        delta_xi = BLOCK_SIZE - offset_px if x_sign == 1 else -offset_px
        delta_yi = delta_xi * tan_angle 
        
        # Required to correctly select grid_x index backwards(ray pointing backward to x axis) by offsetting the x value slightly negatively
        # ex, if x = 16 then x = 15.99 -> grid_x = 0 since grid_0 is (0 to 15). This is not required for positive vertical scanning 
        if x_sign == -1:
            delta_xi += -EPSILON 

        # External delta y
        # Reference, check ./doc/vertical-intersections-step2.png
        delta_ye = abs(tan_angle * BLOCK_SIZE) * y_sign
        delta_xe = BLOCK_SIZE * x_sign

        # Starting position (player position + nearest inline grid intersection)
        ray_x = player.x + delta_xi
        ray_y = player.y + delta_yi
        
        if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "delta_xi: " + str(int(delta_xi)) + "   delta_yi: " + str(int(delta_yi)))
        if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "delta_xe: " + str(int(delta_xe)) + "   delta_ye: " + str(int(delta_ye)))
        if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "start X: " + str(int(ray_x)) + "   start Y: " + str(int(ray_y)))  

        # Step through the level grid until a wall is hit (Level designed to be closed, or limit max steps to avoid infinite loop on open levels or bugs) 

        # Loop until finding a wall or timing out
        while True: # TODO remove
            
            # Increment the steps for counting
            steps_v += 1

            # If the ray has taken too many steps, quit or else we get stuck in an infinite loop
            # It is imposible for the steps to be higher than 2 times the map size (accurate 'enough' but fast)
            if steps_v > MAP_SIZE_X * 2:
                print(colored("Error: Raycast took too many steps", 'red'))
                quit()  
            
            # Clamp to level boundraies in case of ray increment slightly overshooting the edges of level boundaries
            if ray_x < 0 : 
                ray_x = 0
            if ray_x >= MAP_SIZE_X * BLOCK_SIZE : 
                ray_x = MAP_SIZE_X * BLOCK_SIZE - 1
            if ray_y < 0 : 
                ray_y = 0
            if ray_y >= MAP_SIZE_Y * BLOCK_SIZE : 
                ray_y = MAP_SIZE_Y * BLOCK_SIZE - 1
            
            # Calculate the grid cell the ray is in
            grid_x = int(ray_x / BLOCK_SIZE)
            grid_y = int(ray_y / BLOCK_SIZE)
            
            if (shared.DEBUG_LEVEL >= 3 and not ignore_debug): print ( colored("\n-Step : " + str(steps_v),"yellow"))
            if (shared.DEBUG_LEVEL >= 3 and not ignore_debug): print ( "grid_x: " + str(grid_x) + "   grid_y: " + str(grid_y))
            if (shared.DEBUG_LEVEL >= 3 and not ignore_debug): print ( "ray_x: " + str(int(ray_x)) + "   ray_y: " + str(int(ray_y)))
            
            # Check for out of bounds errors
            if grid_x < 0 or grid_x >= MAP_SIZE_X or grid_y < 0 or grid_y >= MAP_SIZE_Y:
                print(colored("Error: Raycast referenced out of bounds Grid X Y", 'red'))
                quit()
            
            # If we hit a wall, break the loop
            if level[grid_y][grid_x] > 0:
                
                # Assign the final vertical values  
                next_rayhit_x_v = ray_x
                next_rayhit_y_v = ray_y
                
                # Save this value for wall texture mapping from delta_yi/tan on vertical scans        
                texture_x_v = (next_rayhit_y_v % BLOCK_SIZE) / BLOCK_SIZE
                
                # Calculate the distance of these 2 points using math.hypot  
                distance_v = math.hypot(player.x - next_rayhit_x_v, player.y - next_rayhit_y_v)
                
                if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print (colored("\n==VERTICAL HIT==",'red'))
                if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "Distance : " + str(int(distance_v)))        
                break
            
            # Move in external delta increments
            ray_x += delta_xe
            ray_y += delta_ye
            
  
    ####################################################################
    # Next, calculate the next potential hit on the horizontal grid line
    ####################################################################
    
    # Y locked to Grid, X incremental, Horizontal Intersections
    # Check if the ray is facing down/up based on sin of angle so we now if we are going to add or subtract the offset
    # Reference, check ./doc/horizontal-intersections-step1.png   
    
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print (colored("\n==HORIZONTAL RAY SCANNING==", "blue"))
        
    # Reset the deltas
    delta_xi = 0
    delta_yi = 0
    delta_xe = 0
    delta_ye = 0
    
    # Ray is facing down
    if sin_angle > 0:
        delta_yi = (1 - normalized_offset_py)
    # Ray is facing up
    elif sin_angle < 0:
        delta_yi = normalized_offset_py
    # This is parallel, and will not hit anything, so we set the distance to a high value to avoid being selected as the shortest distance
    else:
        delta_yi = 0
        distance_h = 1000000 # Set to a high value to avoid being selected as the shortest distance
    
    if delta_yi != 0:
        
        # Calculate internal X delta_xi side length value as defined by the right triangle rules
        # Reference: ./doc/horizontal-intersections-step1.png    
        delta_yi = BLOCK_SIZE - offset_py if y_sign == 1 else -offset_py
        delta_xi = delta_yi * (1/tan_angle) 
 
        # Required to correctly select grid_y index backwards(ray pointing backward to y axis) by offsetting the y value slightly negatively
        if y_sign == -1:
           delta_yi += -EPSILON 
        
        # External delta x 
        # Reference: check ./doc/horizontal-intersections-step2.png

        delta_ye = BLOCK_SIZE * y_sign
        delta_xe = abs(1/tan_angle * BLOCK_SIZE) * x_sign
        
        # For below, same comments as the vertical loop above, omitting for brevity
        
        ray_x = player.x + delta_xi
        ray_y = player.y + delta_yi 
  
        if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "delta_xi: " + str(int(delta_xi)) + "   delta_yi: " + str(int(delta_yi)))
        if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "delta_xe: " + str(int(delta_xe)) + "   delta_ye: " + str(int(delta_ye)))
        if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "start X: " + str(int(ray_x)) + "   start Y: " + str(int(ray_y))) 

        while True:
            
            steps_h += 1
            
            if steps_h > MAP_SIZE_X * 2:
                print(colored("Error: Raycast took too many steps", 'red'))
                quit()
            
            if ray_x < 0 : 
                ray_x = 0
            if ray_x >= MAP_SIZE_X * BLOCK_SIZE : 
                ray_x = MAP_SIZE_X * BLOCK_SIZE - 1
            if ray_y < 0 : 
                ray_y = 0
            if ray_y >= MAP_SIZE_Y * BLOCK_SIZE : 
                ray_y = MAP_SIZE_Y * BLOCK_SIZE - 1
            
            grid_x = int(ray_x / BLOCK_SIZE)
            grid_y = int(ray_y / BLOCK_SIZE)      
            
            if (shared.DEBUG_LEVEL >= 3 and not ignore_debug): print ( colored("\n-Step : " + str(steps_h),"yellow"))
            if (shared.DEBUG_LEVEL >= 3 and not ignore_debug): print ( "grid_x: " + str(grid_x) + "   grid_y: " + str(grid_y))
            if (shared.DEBUG_LEVEL >= 3 and not ignore_debug): print ( "ray_x: " + str(int(ray_x)) + "   ray_y: " + str(int(ray_y)))
            
            if grid_x < 0 or grid_x >= MAP_SIZE_X or grid_y < 0 or grid_y >= MAP_SIZE_Y:
                print(colored("Error: Raycast referenced out of bounds Grid X Y", 'red'))
                quit()
            
            # TODO, Investigate Above here, remove
            if level[grid_y][grid_x] > 0:
                    
                next_rayhit_x_h = ray_x
                next_rayhit_y_h = ray_y
                
                # Save this value for wall texture mapping from delta_yi/tan on vertical scans        
                texture_x_h = (next_rayhit_x_h % BLOCK_SIZE) / BLOCK_SIZE
                
                distance_h = math.hypot(player.x - next_rayhit_x_h, player.y - next_rayhit_y_h)
                
                if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print (colored("\n==HORIZONTAL HIT==","red"))
                if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print ( "Distance : " + str(int(distance_h)))           
                break
            
            ray_x += delta_xe 
            ray_y += delta_ye    
                
        
    
    # Init final distance and ray hit values
    distance_direct = 0

    # Init ray hit values
    ray_x = 0
    ray_y = 0

    # Choose the steps of the shorter distance between vertical and horizontal hit
    
    if shared.scanmode == "vertical": # For debugging, space bar key
        if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print(colored("\n==SCAN MODE: VERTICAL OVERRIDE==","green"))
        ray_x = next_rayhit_x_v
        ray_y = next_rayhit_y_v    
        distance_direct = distance_v
        steps = steps_v
        texture_x = texture_x_v
    elif shared.scanmode == "horizontal":
        if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print(colored("\n==SCAN MODE: HORIZONTAL OVERRIDE==","green"))
        ray_x = next_rayhit_x_h
        ray_y = next_rayhit_y_h    
        distance_direct = distance_h
        steps = steps_h
        texture_x = texture_x_h
    else:
        if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print(colored("\n==SCAN MODE: SHORTEST AUTO==","green"))
        if distance_h < distance_v:
            ray_x = next_rayhit_x_h
            ray_y = next_rayhit_y_h
            distance_direct = distance_h
            steps = steps_h
            texture_x = texture_x_h
            if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("HORIZONTAL HIT IS SHORTER")
        # If the vertical hit is shorter or equal, we select it
        else:
            ray_x = next_rayhit_x_v
            ray_y = next_rayhit_y_v    
            distance_direct = distance_v
            steps = steps_v
            texture_x = texture_x_v
            if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("VERTICAL HIT IS SHORTER")
    
    # Return the optimize distance and meta data to the nearest wall
    
    # Fish eye correction, uses perpendicular distance, required, so this is what we return instead
    distance_perdendicular = distance_direct * math.cos(player.view_angle - ray_angle) 
    
    # Calculate the grid cell the ray is in
    grid_x = int(ray_x / BLOCK_SIZE)
    grid_y = int(ray_y / BLOCK_SIZE)
    
    # Assuming level stores color information, read color from map value >0
    wall_color = level[grid_y][grid_x]  

    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print(colored("\n==FINAL HIT DATA==","red"))   
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print("Hit_x : {:.3f}   Hit_y: {:.3f}".format(ray_x, ray_y))
    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("Grid X: " + str(grid_x) + "   Grid Y: " + str(grid_y))
    if (shared.DEBUG_LEVEL >= 1 and not ignore_debug): print("Steps " + str(steps))
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print("Distance Perdendicular: " + str(int(distance_perdendicular)))
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print("Distance: " + str(int(distance_direct)))
    if (shared.DEBUG_LEVEL >= 2 and not ignore_debug): print("Wall Color: " + str(wall_color) + "\n\n")
    
    #quit() #enable for 1 frame log debugging
    return distance_perdendicular, wall_color, ray_x, ray_y, steps, initial_grid_x, initial_grid_y, grid_x, grid_y, texture_x
