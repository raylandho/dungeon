import pygame
import sys
from settings import TILE_SIZE, FPS
from player import Player
from projectile import Projectile
from enemy import Enemy
from dungeon import Dungeon
from inventory import Inventory  # Import the Inventory class

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
    
    info = pygame.display.Info()
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.NOFRAME)
    
    current_mode = "borderless"
    pygame.display.set_caption('Dungeon Crawler')
    clock = pygame.time.Clock()

    dungeon_width_in_tiles = 100
    dungeon_height_in_tiles = 100
    dungeon = Dungeon(dungeon_width_in_tiles, dungeon_height_in_tiles)
    
    player_start_x, player_start_y = dungeon.get_random_open_position()
    player = Player(player_start_x, player_start_y)
    
    dungeon.clear_spawn_area(dungeon.layout, player_start_x // TILE_SIZE, player_start_y // TILE_SIZE)

    # Initialize enemies with valid spawn positions
    enemies = [Enemy(*dungeon.get_random_open_position()) for _ in range(5)]

    projectiles = []

    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)

    game_started = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen, current_mode = toggle_fullscreen(current_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                if event.key == pygame.K_SPACE and not game_started:
                    game_started = True
                if event.key == pygame.K_SPACE and not inventory.is_open:
                    player.melee_attack(enemies)
                if event.key == pygame.K_r and not inventory.is_open:
                    player.ranged_attack(projectiles, dungeon_width_in_tiles * TILE_SIZE, dungeon_height_in_tiles * TILE_SIZE)
                if event.key == pygame.K_i:
                    inventory.toggle()
                if event.key == pygame.K_t and not inventory.is_open:  # Assuming 'T' is the key to teleport
                    player.teleport(screen, camera_offset, dungeon.get_walls(), dungeon.tiles_x, dungeon.tiles_y, dungeon, SCREEN_WIDTH, SCREEN_HEIGHT, enemies, projectiles)
                if inventory.is_open:
                    if event.key == pygame.K_UP:
                        inventory.move_selection_up()
                    elif event.key == pygame.K_DOWN:
                        inventory.move_selection_down()
                    elif event.key == pygame.K_RETURN:  # Unlock selected attack or upgrade
                        inventory.unlock_attack(player)

        if inventory.is_open:
            inventory.draw(screen, player)  # Pass the player to access points directly
            continue
        
        if not game_started:
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 74)
            text_surface = font.render("Space to Start", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        keys = pygame.key.get_pressed()
        player.handle_movement(keys, dungeon.get_walls(), dungeon.tiles_x, dungeon.tiles_y)
        player.update_aim_direction(keys)

        camera_offset_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_offset_y = player.rect.centery - SCREEN_HEIGHT // 2

        camera_offset_x = max(0, min(camera_offset_x, dungeon.tiles_x * TILE_SIZE - SCREEN_WIDTH))
        camera_offset_y = max(0, min(camera_offset_y, dungeon.tiles_y * TILE_SIZE - SCREEN_HEIGHT))

        camera_offset = (camera_offset_x, camera_offset_y)

        screen.fill((0, 0, 0))

        dungeon.draw(screen, camera_offset)

        for projectile in projectiles[:]:
            if not projectile.move(dungeon.get_walls()):  # Pass walls to move method
                projectiles.remove(projectile)
            elif projectile.is_off_screen():
                projectiles.remove(projectile)
            else:
                projectile_screen_x = projectile.rect.x - camera_offset_x
                projectile_screen_y = projectile.rect.y - camera_offset_y
                screen.blit(projectile.image, (projectile_screen_x, projectile_screen_y))

                for enemy in enemies[:]:
                    if projectile.rect.colliderect(enemy.rect):
                        if enemy.take_damage(projectile.damage):
                            enemies.remove(enemy)
                            player.gain_xp(50)
                        projectiles.remove(projectile)
                        break

        for enemy in enemies:
            enemy.move_towards_player(player.rect, dungeon.get_walls())
            enemy.update()

        for enemy in enemies:
            enemy.draw(screen, camera_offset)

        player.draw(screen, camera_offset)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
