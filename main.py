import pygame
import sys
from settings import TILE_SIZE, FPS
from player import Player
from projectile import Projectile
from enemy import Enemy
from dungeon import Dungeon

def toggle_fullscreen(current_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    if current_mode == "fullscreen":
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.NOFRAME)
        current_mode = "borderless"
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        current_mode = "fullscreen"
    return screen, current_mode

def main():
    pygame.init()
    
    # Set initial mode to fullscreen windowed mode and get screen dimensions
    info = pygame.display.Info()
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.NOFRAME)
    
    current_mode = "borderless"
    pygame.display.set_caption('Dungeon Crawler')
    clock = pygame.time.Clock()

    # Initialize the dungeon and player
    dungeon_width_in_tiles = 100  # Example large dungeon size
    dungeon_height_in_tiles = 100
    dungeon = Dungeon(dungeon_width_in_tiles, dungeon_height_in_tiles)
    
    player_start_x, player_start_y = dungeon.get_random_open_position()
    player = Player(player_start_x, player_start_y)
    
    # Ensure the player's spawn area is clear of walls
    dungeon.clear_spawn_area(dungeon.layout, player_start_x // TILE_SIZE, player_start_y // TILE_SIZE)

    # Initialize enemies list
    enemies = [Enemy(200, 200), Enemy(100, 100)]
    
    # Initialize projectiles list
    projectiles = []

    # Game state
    game_started = False

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Toggle between fullscreen and borderless fullscreen
                    screen, current_mode = toggle_fullscreen(current_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                if event.key == pygame.K_SPACE and not game_started:
                    # Start the game when space is pressed
                    game_started = True
                if event.key == pygame.K_r:  # Shoot projectile
                    current_time = pygame.time.get_ticks()
                    if current_time - player.last_attack_time >= player.attack_cooldown and player.mana >= 10:
                        # Offset the projectile's start position by the camera offset
                        start_x = player.rect.centerx + player.aim_direction.x * (player.size // 2)
                        start_y = player.rect.centery + player.aim_direction.y * (player.size // 2)
                        projectile = Projectile(start_x, start_y, player.aim_direction, dungeon_width_in_tiles * TILE_SIZE, dungeon_height_in_tiles * TILE_SIZE)
                        projectiles.append(projectile)
                        player.use_mana(projectile.mana_cost)
                        player.last_attack_time = current_time
                        print(f"Projectile launched at ({start_x}, {start_y}) in direction {player.aim_direction}")
                    else:
                        print("Not enough mana to shoot.")

        if not game_started:
            # Display start screen
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 74)
            text_surface = font.render("Space to Start", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        keys = pygame.key.get_pressed()
        player.handle_movement(keys, dungeon.get_walls())
        player.update_aim_direction(keys)

        # Calculate the camera offset
        camera_offset_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_offset_y = player.rect.centery - SCREEN_HEIGHT // 2

        # Ensure the camera doesn't show beyond the map edges
        camera_offset_x = max(0, min(camera_offset_x, dungeon.tiles_x * TILE_SIZE - SCREEN_WIDTH))
        camera_offset_y = max(0, min(camera_offset_y, dungeon.tiles_y * TILE_SIZE - SCREEN_HEIGHT))

        camera_offset = (camera_offset_x, camera_offset_y)

        # Clear the screen first
        screen.fill((0, 0, 0))  # Clear screen with black

        # Draw the dungeon (background)
        dungeon.draw(screen, camera_offset)

        # Move and draw each projectile
        for projectile in projectiles[:]:
            projectile.move()
            if projectile.is_off_screen():
                projectiles.remove(projectile)
            else:
                # Adjust the projectile position for the camera
                projectile_screen_x = projectile.rect.x - camera_offset_x
                projectile_screen_y = projectile.rect.y - camera_offset_y
                screen.blit(projectile.image, (projectile_screen_x, projectile_screen_y))

                # Check for collision with enemies
                for enemy in enemies[:]:
                    if projectile.rect.colliderect(enemy.rect):
                        if enemy.take_damage(projectile.damage):
                            enemies.remove(enemy)  # Remove enemy if it dies
                        projectiles.remove(projectile)  # Remove the projectile
                        break  # Stop checking other enemies for this projectile

        # Move the enemies towards the player if they are still alive
        for enemy in enemies:
            enemy.move_towards_player(player.rect, dungeon.get_walls())
            enemy.update()  # Update enemy state (including flash effect)

        # Draw each enemy
        for enemy in enemies:
            enemy.draw(screen, camera_offset)

        # Draw the player last
        player.draw(screen, camera_offset)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
