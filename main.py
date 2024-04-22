import math
import time
import pygame
import cProfile
import pstats
import os
#import pygame.surfarray as surfarray
#import numpy as np

# Game custom modules
from physics import *
from classes import *
from data import *
from graphics import *
from consts import *
import shared 

def main():
    
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Initialize Pygame
    pygame.init()
    
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    # Surface optimizations, don't seem to be improving performance, keeping for verbosity
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF # | pygame.FULLSCREEN
    
    screen = pygame.display.set_mode(size , flags=flags, vsync=True)

    # Set the title of the window
    pygame.display.set_caption("Wolfy Style DDA Raycasting 3D Demo")

    # Loop until the user clicks the close button
    running = True

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    
    # Define the view mode
    # top, 3d
    view_mode = 'top'
    
    
    # 32x32 grid representing the level
    # different values represent different wall types/colors
    level = level1

    player = Player(PLAYER_INITIAL_X, PLAYER_INITIAL_Y, PLAYER_RADIUS, PLAYER_SPEED, PLAYER_VIEW_ANGLE, PLAYER_ROTATION_SPEED)

    # Load the stone texture and convert it to a PixelArray array for better performance
    wall_texture_grey = pygame.image.load('assets/textures/wall-stone.png').convert() #rgb colors might be flipped otherwise
    #Load the texture into a PixelArray
    wall_texture_grey_array = pygame.PixelArray(wall_texture_grey)
    # Update the loaded texture array into the shared module for dynamic referencing
    shared.wall_colors_textures_list[GREY_TEXTURE_STONEWALL] = wall_texture_grey_array
    
    # Load the blue wall texture
    wall_texture_blue = pygame.image.load('assets/textures/wall-blue.png').convert()
    wall_textire_blue_array = pygame.PixelArray(wall_texture_blue)
    shared.wall_colors_textures_list[BLUE_TEXTURE_WALL] = wall_textire_blue_array
    
    # Load a skybox texture
    skybox_texture = pygame.image.load('assets/skyboxes/SNOSKY03.png').convert()
    #resize the skybox texture
    skybox_texture = pygame.transform.scale(skybox_texture, (skybox_texture.get_width(), SCREEN_HEIGHT/2))
    #skybox_array = pygame.PixelArray(skybox_texture)
    skybox_rect = skybox_texture.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))


    # Create a Font object
    font_30 = pygame.font.Font(None, 30)
    font_22 = pygame.font.Font(None, 18)
    
    # GUI counter
    ray_steps = 0
    
    # Delta time
    delta_time = 0
    current_time = 0
    previous_time = time.time()

    # Create new Shotgun weapon
    weapon = Shotgun()
    
    #  Game Loop
    while running:
        
        current_time = time.time()
        delta_time = current_time - previous_time
        
        # Initialize the proposed player movement with the current player position for this frame (to be valided by the collision detection)
        proposed_x = player.x
        proposed_y = player.y
        
        # Check for user input events (and custom game events)
        # Game control keys (quit, view mode, etc.)
        for event in pygame.event.get():
            
            # UI Events
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and view_mode == 'top':  # Left mouse button clicked
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_grid_x = int((mouse_pos[0] - MINIMAP_OFFSET_X) // (BLOCK_SIZE * MINIMAP_SCALE_FACTOR))
                    clicked_grid_y = int((mouse_pos[1] - MINIMAP_OFFSET_Y)  // (BLOCK_SIZE * MINIMAP_SCALE_FACTOR))
                    
                    if clicked_grid_x > 0 and clicked_grid_x < MAP_SIZE_X-1 and clicked_grid_y > 0 and clicked_grid_y < MAP_SIZE_Y-1:
                        level[clicked_grid_y][clicked_grid_x] = 5
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and view_mode == 'top':  # Left mouse button clicked
                    mouse_pos = pygame.mouse.get_pos()
                    clicked_grid_x = int((mouse_pos[0] - MINIMAP_OFFSET_X) // (BLOCK_SIZE * MINIMAP_SCALE_FACTOR))
                    clicked_grid_y = int((mouse_pos[1] - MINIMAP_OFFSET_Y)  // (BLOCK_SIZE * MINIMAP_SCALE_FACTOR))
                    if clicked_grid_x > 0 and clicked_grid_x < MAP_SIZE_X-1 and clicked_grid_y > 0 and clicked_grid_y < MAP_SIZE_Y-1:
                        level[clicked_grid_y][clicked_grid_x] = 0
            
            # weapon fired in 3d mode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and view_mode == '3d':
                weapon.fire()
                
            
            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_q:
                    running = False
                    quit()
                    
                if event.key == pygame.K_TAB:
                    view_mode = '3d' if view_mode == 'top' else 'top'
                    # Console log the change
                    if (shared.DEBUG_LEVEL >= 1): print('View mode: ', view_mode)
                if event.key == pygame.K_SPACE:
                    if shared.scanmode == "shortest":
                        shared.scanmode = "horizontal"
                    elif shared.scanmode == "horizontal":
                        shared.scanmode = "vertical"
                    else:
                        shared.scanmode = "shortest"
                if event.key == pygame.K_ESCAPE:
                    shared.paused = not shared.paused
                    if (shared.DEBUG_LEVEL >= 1): print ('Paused: ' + str(shared.paused))
                if event.key == pygame.K_0:
                    shared.DEBUG_LEVEL = 0
                if event.key == pygame.K_1:
                    shared.DEBUG_LEVEL = 1
                if event.key == pygame.K_2:
                    shared.DEBUG_LEVEL = 2
                if event.key == pygame.K_3:
                    shared.DEBUG_LEVEL = 3
            
            if event.type == pygame.MOUSEMOTION and view_mode == '3d' and not shared.paused:
                # Get the relative movement of the mouse
                rel_x, rel_y = event.rel
                
                # Check if the mouse is moving left or right
                if rel_x < 0:
                    # Mouse is moving left
                    player.view_angle -= player.rotation_speed * delta_time * MOUSE_SENSITIVITY
                elif rel_x > 0:
                    # Mouse is moving right
                    player.view_angle += player.rotation_speed * delta_time * MOUSE_SENSITIVITY
               
            # Custom game events     
            if event.type == DEFAULT_EVENT:
                pass
            
            # if event.type == WEAPON_RELOAD_EVENT:
            #     weapon.reload()
            
            # if event.type == WEAPON_READY_EVENT:
            #     weapon.ready()
                
        
        # Movement keys support multiple keys at once and diagonal movement with pressing and holding
        if not shared.paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]: 
                proposed_x += player.speed * math.cos(player.view_angle) * delta_time
                proposed_y += player.speed * math.sin(player.view_angle) * delta_time
               
                player = check_level_collision(player, proposed_x, player.y, level)
                player = check_level_collision(player, player.x, proposed_y, level)
                 
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: 
                proposed_x -= player.speed * math.cos(player.view_angle) * delta_time
                proposed_y -= player.speed * math.sin(player.view_angle) * delta_time
                
                player = check_level_collision(player, proposed_x, player.y, level)
                player = check_level_collision(player, player.x, proposed_y, level)

                
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.view_angle -= player.rotation_speed * delta_time
            
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.view_angle += player.rotation_speed * delta_time
                
            if keys[pygame.K_LSHIFT]:
                player.speed = PLAYER_RUNNING_SPEED
            else:
                player.speed = PLAYER_SPEED

        if player.view_angle < 0:
            player.view_angle = 2 * math.pi
        if player.view_angle > 2 * math.pi:
            player.view_angle = 0
                
        # Gameplay logic, check if paused or not
        if not shared.paused:
            
            # Raycasting Mode Drawing
            
            if view_mode == '3d':
                
                # Grab the mouse cursor
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
                
                # Screen clear
                screen.fill(BLACK)
                
                # Draw the sky and floor first
                #pygame.draw.rect(screen, SKY_BLUE, pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT / 2))
                pygame.draw.rect(screen, GROUND_GREY, pygame.Rect(0, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT / 2))

                # Draw the skybox
                # Scroll/clip it based on the player view angle
                skybox_rect.left = 0 - (skybox_texture.get_width() * player.view_angle ) /  (math.pi*2 )
                screen.blit(skybox_texture, skybox_rect)
                
                # Add the buffer looping image
                # PS: the 2 skyboxes are reset to initial positions by the player's wrapping angle
                skybox_rect.left = skybox_rect.left + skybox_texture.get_width()
                screen.blit(skybox_texture, skybox_rect)
                
                
                # For each vertical slice of the screen
                # render half the screen width interleaved => performance boost at neglightable visual loss
                for x in range(0,SCREEN_WIDTH, 2):
                    # Calculate the ray angle per vertical slice of the POV
                    ray_angle = player.view_angle + math.atan((x - SCREEN_WIDTH / 2) / FOCAL_LENGTH)

                    # Enable debug only for player angle(ignore debug for POV angles)
                    ray_debug = not (ray_angle == player.view_angle)
                        
                    # Cast the ray and find the distance to the nearest wall
                    ray_distance, wall_color, hit_x, hit_y, steps, intial_grid_x, initial_grid_y, grid_x, grid_y, texture_x \
                    = cast_ray(player, ray_angle, level, x, ray_debug)
                    
                    # disable GUI steps
                    ray_steps = 0

                    # Calculate the height of the wall slice
                    slice_height = int(MAX_WALL_HEIGHT * FOCAL_LENGTH / ray_distance )

                    if (wall_color == GREY_TEXTURE_STONEWALL or wall_color == BLUE_TEXTURE_WALL):
                
                        # Calculate the final texture x-coordinate, so denormallize to texture size
                        texture_x = int(texture_x * TEXTURE_SIZE)
                        
                        # Create a surface for the wall slice (1 pixel wide, TEXTURE pixels tall)
                        wall_slice_surface = pygame.Surface((1, TEXTURE_SIZE))

                        # Draw the wall slice with texture mapping from top to bottom on Y axis
                        # In the range of the Texture not to slice_height (then hardwarescaling it later to the slice_height)
                        # If you use slice_height, the y loop will take alot longer when the player moves close to the wall and will tank fps
                        for y in range(TEXTURE_SIZE):
                            
                            # Load the correct texture from the lookup table
                            if wall_color == GREY_TEXTURE_STONEWALL:
                                texture_color =   shared.wall_colors_textures_list[GREY_TEXTURE_STONEWALL][texture_x, y]
                            if wall_color == BLUE_TEXTURE_WALL:
                                texture_color =   shared.wall_colors_textures_list[BLUE_TEXTURE_WALL][texture_x, y]
                            
                            # Paint the texture pixel on the thin slice surface
                            wall_slice_surface.set_at((0, y), texture_color)
                                                
                        # Scale the wall slice surface to the size of final the wall slice height
                        # '2' is used as slice width here because the loop has a step of 2 (see above)
                        wall_slice_surface = pygame.transform.scale(wall_slice_surface, (2, slice_height))

                        # Get the texture y slice location on the screen (centered)
                        tex_location_y = int(SCREEN_HEIGHT / 2 - slice_height / 2)

                        # Blit the wall slice surface onto the screen
                        screen.blit(wall_slice_surface, (x, tex_location_y))
                        
                            
                    else:
                        # Calculate the color of the wall slice based on the distance and the wall color
                        
                        color_brightness = 255 - min(ray_distance/2, 255)
                        color_brightness = max(color_brightness, 30)  # Adjust the minimum brightness of distant walls
                        color_brightness_normalized = (color_brightness / 255)
                        
                        # texture or colored wall mode
                        if wall_color == GREY_TEXTURE_STONEWALL or wall_color == BLUE_TEXTURE_WALL: 
                            wall_color = LIGHT_GREY # placeholder color for minimap for textured walls
                        else:   
                            wall_color = shared.wall_colors_textures_list[wall_color]
                        
                        wall_color = (wall_color[0] * color_brightness_normalized, wall_color[1] * color_brightness_normalized, wall_color[2] * color_brightness_normalized)

                        # Draw the wall slice
                        pygame.draw.rect(screen, wall_color, pygame.Rect(x, SCREEN_HEIGHT / 2 - slice_height / 2, 2, slice_height))
                    
                    # Draw aiming reticle
                    pygame.draw.circle(screen, RED, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 3)
                    
                    # Draw selected weapon HUD
                    weapon.update()
                    weapon.draw(screen)

            # Top view map mode Drawing
            if view_mode == 'top':
                
                # Release the mouse cursor
                pygame.mouse.set_visible(True)
                pygame.event.set_grab(False)
    
                # Screen clear
                screen.fill(BLACK)
                
                # draw the level
                # i is the row number (y) and j is the column number (x)
                # wall color depends on the wall grid value
                for i in range(MAP_SIZE_Y):
                    for j in range(MAP_SIZE_X):

                        if level[i][j] in shared.wall_colors_textures_list:
                            if level[i][j] == GREY_TEXTURE_STONEWALL:
                                # Draw the wall texture
                                selected_color = LIGHT_GREY
                            elif level[i][j] == BLUE_TEXTURE_WALL:
                                selected_color = BLUE
                            else:
                                selected_color = shared.wall_colors_textures_list[level[i][j]]
                            
                            pygame.draw.rect(screen, selected_color, pygame.Rect(j * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, i * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y, BLOCK_SIZE * MINIMAP_SCALE_FACTOR, BLOCK_SIZE * MINIMAP_SCALE_FACTOR))                           

                # Draw the map grid based on the block size and map size          
                for i in range(MAP_SIZE_Y):
                    pygame.draw.line(screen, LIGHT_GREY_EXTRA, (0 + MINIMAP_OFFSET_X, i * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), (BLOCK_SIZE * MAP_SIZE_X * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, i * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), 1)
                for j in range(MAP_SIZE_X):
                    pygame.draw.line(screen, LIGHT_GREY_EXTRA, (j * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, 0 + MINIMAP_OFFSET_Y), (j * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, BLOCK_SIZE * MAP_SIZE_Y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), 1)
                
                # Draw the raytraced scanners
                ray_distance, wall_color, hit_x, hit_y, steps, intial_grid_x, initial_grid_y, grid_x, grid_y, texture_x \
                = cast_ray(player, player.view_angle, level, 0)
                
                # texture or color wall mode
                if wall_color == GREY_TEXTURE_STONEWALL or wall_color == BLUE_TEXTURE_WALL:
                    wall_color = LIGHT_GREY 
                else:   
                    wall_color = shared.wall_colors_textures_list[wall_color]
                
                # draw a gray transparent rectangle on initial grid position
                pygame.draw.rect(screen, LIGHT_GREY_EXTRA, pygame.Rect(intial_grid_x * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, initial_grid_y * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y, BLOCK_SIZE * MINIMAP_SCALE_FACTOR, BLOCK_SIZE * MINIMAP_SCALE_FACTOR))
                
                pygame.draw.rect(screen, RED, pygame.Rect(grid_x * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, grid_y * BLOCK_SIZE * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y, BLOCK_SIZE * MINIMAP_SCALE_FACTOR, BLOCK_SIZE * MINIMAP_SCALE_FACTOR))
            
                pygame.draw.line(screen, wall_color, (player.x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, player.y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), (hit_x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, hit_y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), 2)
                ray_steps = steps
                
                # Draw the player pin
                pygame.draw.circle(screen, RED, (player.x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, player.y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), player.radius * MINIMAP_SCALE_FACTOR, 1)
                # Draw the player view angle
                end_x = (player.x + player.radius * 1 * math.cos(player.view_angle))
                end_y = (player.y + player.radius * 1 * math.sin(player.view_angle))
                pygame.draw.line(screen, BLACK, (player.x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, player.y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), (end_x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, end_y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), 3) 
                
                        
                # # with POV
                ray_angle = player.view_angle + math.atan(-(SCREEN_WIDTH / 2) / FOCAL_LENGTH)
                ray_distance, wall_color, hit_x, hit_y, steps, intial_grid_x, initial_grid_y, grid_x, grid_y, texture_x \
                = cast_ray(player, ray_angle, level, 0, True)
                pygame.draw.line(screen, LIGHT_GREY, (player.x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, player.y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), (hit_x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, hit_y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), 1)
                
                ray_angle = player.view_angle + math.atan((SCREEN_WIDTH / 2) / FOCAL_LENGTH)
                ray_distance, wall_color, hit_x, hit_y, steps, intial_grid_x, initial_grid_y, grid_x, grid_y, texture_x \
                = cast_ray(player, ray_angle, level, 0, True)
                pygame.draw.line(screen, LIGHT_GREY, (player.x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, player.y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), (hit_x * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_X, hit_y * MINIMAP_SCALE_FACTOR + MINIMAP_OFFSET_Y), 1)

            
            # Update the display
            
            
            # Calculate the FPS
            fps = clock.get_fps()

            # Render the FPS onto a Surface
            fps_text = font_30.render("FPS: {:.0f}".format(fps), True, WHITE)

            # Blit the FPS Surface onto the screen
            screen.blit(fps_text, (12, 20))
            
            steps_text = font_30.render("STEPS: {:.0f}".format(ray_steps), True, WHITE)
            screen.blit(steps_text, (12, 50))
            
            instructions_text = font_22.render("TAB: View Mode", True, WHITE)
            screen.blit(instructions_text, (660, 20))
            
            instructions_text = font_22.render("SHIFT: Hold to Run", True, WHITE)
            screen.blit(instructions_text, (660, 50))
            
            instructions_text = font_22.render("SPC: Toogle V/H Scan", True, WHITE)
            screen.blit(instructions_text, (660, 80))
            
            instructions_text = font_22.render("Mouse, A/D : Rotate", True, WHITE)
            screen.blit(instructions_text, (660, 110))
            
            instructions_text = font_22.render("W/S: Move", True, WHITE)
            screen.blit(instructions_text, (660, 140))
            
            instructions_text = font_22.render("0/1/2/3: Debug Logs", True, WHITE)
            screen.blit(instructions_text, (660, 170))
            
            instructions_text = font_22.render("Esc: Pause/Resume", True, WHITE)
            screen.blit(instructions_text, (660, 200))
            
            instructions_text = font_22.render("Click map LR: Add/Rem", True, WHITE)
            screen.blit(instructions_text, (660, 230))
            
            instructions_text = font_22.render("Q: Quit", True, WHITE)
            screen.blit(instructions_text, (660, 260))
                        
            # Flip frame buffer to draw screen 
            pygame.display.flip()

            # Limit to 30 frames per second
            clock.tick(FPS)
            
            # Update the previous time
            previous_time = current_time

    # Close the window and quit.
    pygame.quit()



# profiler = cProfile.Profile()
# profiler.enable()

main()

# profiler.disable()
# stats = pstats.Stats(profiler).sort_stats('cumulative')
# stats.print_stats()






