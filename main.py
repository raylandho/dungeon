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
    dungeon = Dungeon(SCREEN_WIDTH, SCREEN_HEIGHT)
    player_start_x, player_start_y = dungeon.get_random_open_position()
    
    # Ensure the player's spawn area is clear of walls
    dungeon.clear_spawn_area(dungeon.layout, player_start_x // TILE_SIZE, player_start_y // TILE_SIZE)
    
    player = Player(player_start_x, player_start_y)

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

        # Check for player collision with exits
        for exit_pos in dungeon.get_exit_positions():
            exit_rect = pygame.Rect(exit_pos[0], exit_pos[1], TILE_SIZE * 2, TILE_SIZE)
            if player.rect.colliderect(exit_rect):
                # Determine the spawn position based on the exit used
                if exit_pos[1] == 0:  # Top exit
                    player.rect.y = SCREEN_HEIGHT - TILE_SIZE * 3  # Ensure the player is not in the wall
                    player.rect.x = exit_pos[0]
                elif exit_pos[1] == SCREEN_HEIGHT - TILE_SIZE:  # Bottom exit
                    player.rect.y = SCREEN_HEIGHT - TILE_SIZE * 2  # Spawn one tile above the bottom wall
                    player.rect.x = exit_pos[0]
                elif exit_pos[0] == 0:  # Left exit
                    player.rect.x = SCREEN_WIDTH - TILE_SIZE * 3  # Ensure the player is not in the wall
                    player.rect.y = exit_pos[1]
                elif exit_pos[0] == SCREEN_WIDTH - TILE_SIZE * 2:  # Right exit
                    player.rect.x = TILE_SIZE
                    player.rect.y = exit_pos[1]

                # Generate a new dungeon after teleporting
                previous_exit = (exit_pos[0] // TILE_SIZE, exit_pos[1] // TILE_SIZE)
                dungeon = Dungeon(SCREEN_WIDTH, SCREEN_HEIGHT)

                # Fill the gap left by the previous exit with a wall or another exit
                if previous_exit[1] == 0 or previous_exit[1] == (SCREEN_HEIGHT // TILE_SIZE) - 1:  # Top or bottom
                    dungeon.layout[previous_exit[1]][previous_exit[0]] = '1'  # Wall
                elif previous_exit[0] == 0 or previous_exit[0] == (SCREEN_WIDTH // TILE_SIZE) - 1:  # Left or right
                    dungeon.layout[previous_exit[1]][previous_exit[0]] = '1'  # Wall

                dungeon.clear_spawn_area(dungeon.layout, player.rect.x // TILE_SIZE, player.rect.y // TILE_SIZE)
                break

        # Melee attack (Spacebar)
        if keys[pygame.K_SPACE]:
            player.melee_attack(enemies)

        # Ranged attack (R key)
        if keys[pygame.K_r]:
            current_time = pygame.time.get_ticks()
            if current_time - player.last_attack_time >= player.attack_cooldown:
                projectile = Projectile(player.rect.centerx, player.rect.centery, player.aim_direction, SCREEN_WIDTH, SCREEN_HEIGHT)
                projectiles.append(projectile)
                player.use_mana(projectile.mana_cost)
                player.last_attack_time = current_time

        # Move the enemies towards the player if they are still alive
        for enemy in enemies:
            enemy.move_towards_player(player.rect, dungeon.get_walls())
            enemy.update()  # Update enemy state (including flash effect)

        # Clear the screen first
        screen.fill((0, 0, 0))  # Clear screen with black

        # Draw the dungeon (background)
        dungeon.draw(screen)

        # Draw the projectiles next
        for projectile in projectiles[:]:
            projectile.move()
            if projectile.is_off_screen():
                projectiles.remove(projectile)
            else:
                projectile.draw(screen)
                # Check collision with each enemy
                for enemy in enemies[:]:
                    if projectile.rect.colliderect(enemy.rect):
                        if enemy.take_damage(projectile.damage):  # Use projectile's damage
                            print("Enemy has died")
                            player.gain_xp(50)  # Award XP for killing the enemy
                            enemies.remove(enemy)  # Remove the dead enemy from the list
                        projectiles.remove(projectile)
                        break  # Stop checking other enemies for this projectile

        # Draw each enemy if still alive
        for enemy in enemies:
            enemy.draw(screen)

        # Draw the player last
        player.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
