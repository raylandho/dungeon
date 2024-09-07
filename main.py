import pygame
import sys
from settings import TILE_SIZE, FPS
from player import Player
from projectile import Projectile, Fireball, EnemyProjectile  # Import EnemyProjectile
from enemy import RangedEnemy, Enemy, BossMeleeEnemy  # Import both RangedEnemy and Enemy (melee enemies)
from dungeon import Dungeon
from inventory import Inventory  # Import the Inventory class

def toggle_fullscreen(current_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    if current_mode is None:
        return screen, current_mode
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

    # Initialize 10 ranged and 10 melee enemies with valid spawn positions
    ranged_enemies = [RangedEnemy(*dungeon.get_random_open_position(), SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(3)]
    melee_enemies = [Enemy(*dungeon.get_random_open_position()) for _ in range(10)]
    boss_melee_enemies = [BossMeleeEnemy(*dungeon.get_random_open_position()) for _ in range(2)]
    enemies = ranged_enemies + melee_enemies + boss_melee_enemies # Combine both lists into the main enemies list

    projectiles = []
    enemy_projectiles = []  # New list to hold enemy projectiles

    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)

    game_started = False
    game_over = False
    
    lightning_in_progress = False
    lightning_move_cooldown = 35  # Cooldown in milliseconds (adjust as needed)
    last_lightning_move_time = 0

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Restart the game
                    player.reset(player_start_x, player_start_y, inventory)  # Pass inventory to reset
                    ranged_enemies = [RangedEnemy(*dungeon.get_random_open_position(), SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(3)]
                    melee_enemies = [Enemy(*dungeon.get_random_open_position()) for _ in range(10)]
                    boss_melee_enemies = [BossMeleeEnemy(*dungeon.get_random_open_position()) for _ in range(2)]
                    enemies = ranged_enemies + melee_enemies + boss_melee_enemies  # Respawn 10 ranged and 10 melee enemies
                    projectiles.clear()  # Clear all projectiles
                    enemy_projectiles.clear()  # Clear enemy projectiles
                    game_over = False
                    game_started = True
                    print("Game restarted!")
                continue 

            if not lightning_in_progress:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        screen, current_mode = toggle_fullscreen(current_mode, screen, SCREEN_WIDTH, SCREEN_HEIGHT)
                    if event.key == pygame.K_SPACE and not game_started:
                        game_started = True
                    if event.key == inventory.keybindings["Melee Attack"] and not inventory.is_open:
                        player.melee_attack(enemies)
                    if event.key == inventory.keybindings["Ranged Attack"] and not inventory.is_open:
                        player.ranged_attack(projectiles, dungeon_width_in_tiles * TILE_SIZE, dungeon_height_in_tiles * TILE_SIZE)
                    if event.key == inventory.keybindings["Fireball"] and not inventory.is_open and player.fireball_unlocked:
                        player.fireball_attack(projectiles, dungeon_width_in_tiles * TILE_SIZE, dungeon_height_in_tiles * TILE_SIZE)
                    if event.key == pygame.K_i:
                        inventory.toggle()
                    if event.key == inventory.keybindings["Teleport"] and not inventory.is_open:
                        if player.teleport_attack_unlocked:
                            player.teleport_attack(screen, camera_offset, dungeon.get_walls(), dungeon.tiles_x, dungeon.tiles_y, dungeon, SCREEN_WIDTH, SCREEN_HEIGHT, enemies, projectiles)
                        else:
                            player.teleport(screen, camera_offset, dungeon.get_walls(), dungeon.tiles_x, dungeon.tiles_y, dungeon, SCREEN_WIDTH, SCREEN_HEIGHT, enemies, projectiles)
                    if event.key == inventory.keybindings["Lightning Strike"] and not inventory.is_open and player.lightning_unlocked:
                        player.start_lightning_strike(dungeon_width_in_tiles * TILE_SIZE, dungeon_height_in_tiles * TILE_SIZE)
                        lightning_in_progress = True
                        last_lightning_move_time = current_time  # Reset cooldown

                    if inventory.is_open:
                        if inventory.rebinding_mode:
                            inventory.process_keybinding(event)
                        elif event.key == pygame.K_UP:
                            inventory.move_selection_up()
                        elif event.key == pygame.K_DOWN:
                            inventory.move_selection_down()
                        elif event.key == pygame.K_RETURN:
                            inventory.select(player)

        if lightning_in_progress:
            keys = pygame.key.get_pressed()
            if current_time - last_lightning_move_time >= lightning_move_cooldown:
                if keys[pygame.K_LEFT]:
                    player.move_lightning_strike_target("left")
                    last_lightning_move_time = current_time
                if keys[pygame.K_RIGHT]:
                    player.move_lightning_strike_target("right")
                    last_lightning_move_time = current_time
                if keys[pygame.K_UP]:
                    player.move_lightning_strike_target("up")
                    last_lightning_move_time = current_time
                if keys[pygame.K_DOWN]:
                    player.move_lightning_strike_target("down")
                    last_lightning_move_time = current_time
                if keys[pygame.K_RETURN]:  # Confirm lightning strike
                    player.confirm_lightning_strike(enemies)
                    lightning_in_progress = False
        
        if player.is_dead:
            game_over = True

        if game_over:
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont(None, 74)
            text_surface = font.render("You Died! Press Space to Restart", True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            pygame.display.flip()
            clock.tick(FPS)
            continue

        if inventory.is_open:
            inventory.draw(screen, player)
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

        if not lightning_in_progress:
            keys = pygame.key.get_pressed()
            player.handle_movement(keys, dungeon.get_walls(), dungeon.tiles_x, dungeon.tiles_y, enemies)  # Pass enemies to prevent overlap
            player.update_aim_direction(keys)

        camera_offset_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_offset_y = player.rect.centery - SCREEN_HEIGHT // 2

        camera_offset_x = max(0, min(camera_offset_x, dungeon.tiles_x * TILE_SIZE - SCREEN_WIDTH))
        camera_offset_y = max(0, min(camera_offset_y, dungeon.tiles_y * TILE_SIZE - SCREEN_HEIGHT))

        camera_offset = (camera_offset_x, camera_offset_y)

        screen.fill((0, 0, 0))

        dungeon.draw(screen, camera_offset)

        # Update and draw player projectiles
        for projectile in projectiles[:]:  # Iterate over a copy of the list
            projectile_removed = False  # Flag to track if projectile has been removed

            if isinstance(projectile, Fireball):
                if not projectile.move(dungeon.get_walls(), enemies, player):  # Fireball with walls and enemies
                    projectiles.remove(projectile)
                    projectile_removed = True  # Mark projectile as removed
                else:
                    projectile.draw(screen, camera_offset)
                    continue

            elif not projectile_removed and not projectile.move(dungeon.get_walls()):  # Regular projectile with walls only
                projectiles.remove(projectile)
                projectile_removed = True

            if not projectile_removed:
                for enemy in enemies[:]:  # Check collisions with enemies
                    if projectile.rect.colliderect(enemy.rect):
                        if enemy.take_damage(projectile.damage):
                            enemies.remove(enemy)
                            player.gain_xp(50)
                        projectiles.remove(projectile)
                        projectile_removed = True
                        break  # Exit loop after removing projectile

            if not projectile_removed and projectile.is_off_screen(camera_offset):  # Check off-screen with camera offset
                projectiles.remove(projectile)
                projectile_removed = True

            if not projectile_removed:
                projectile.draw(screen, camera_offset)  # Draw with camera offset

        # Update all enemies (ranged enemies shoot projectiles)
        for enemy in enemies[:]:
            enemy.update(player, dungeon.get_walls(), camera_offset, enemies)  # Pass the enemies list to prevent overlaps
            
            # Only handle projectiles for ranged enemies
            if isinstance(enemy, RangedEnemy):
                # Collect enemy projectiles into the enemy_projectiles list
                for projectile in enemy.projectiles:
                    enemy_projectiles.append(projectile)
                enemy.projectiles = []  # Clear the enemy's own projectile list to prevent duplicates

            # Remove enemy if dead
            if enemy.is_dead():
                player.gain_xp(50)
                enemies.remove(enemy)

        # Update and draw enemy projectiles
        for e_projectile in enemy_projectiles[:]:
            if not e_projectile.move(dungeon.get_walls()):  # Move the projectile and check for wall collisions
                enemy_projectiles.remove(e_projectile)
                continue

            # Check if the projectile hits the player
            if e_projectile.rect.colliderect(player.rect):
                player.take_damage(e_projectile.damage)
                enemy_projectiles.remove(e_projectile)
                continue

            # Remove projectile if it's off the screen
            if e_projectile.is_off_screen(camera_offset):
                enemy_projectiles.remove(e_projectile)
                continue

            # Draw the projectile
            e_projectile.draw(screen, camera_offset)

        # Draw all enemies
        for enemy in enemies:
            enemy.draw(screen, camera_offset)

        player.draw(screen, camera_offset)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
