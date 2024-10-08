import pygame
import sys
import os
import random
from settings import TILE_SIZE, FPS
from player import Player
from projectile import Projectile, Fireball, EnemyProjectile  # Import EnemyProjectile
from enemy import RangedEnemy, Enemy, BossMeleeEnemy  # Import both RangedEnemy and Enemy (melee enemies)
from dungeon import Dungeon
from inventory import Inventory  # Import the Inventory class

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


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
    
    pygame.mixer.init()
    pygame.mixer.music.load(resource_path('assets/movement.mp3')) 
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)  # 50% volume
    
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

     # Round-related variables
    current_round = 1
    enemies_per_round = 5  # Start with 5 enemies in round 1
    enemies = []  # Empty list of enemies that will be populated at the start of each round
    enemies_defeated = 0  # Keep track of how many enemies have been defeated

    projectiles = []
    enemy_projectiles = []  # New list to hold enemy projectiles

    inventory = Inventory(SCREEN_WIDTH, SCREEN_HEIGHT)

    game_started = False
    game_over = False
    
    lightning_in_progress = False
    lightning_move_cooldown = 35  # Cooldown in milliseconds (adjust as needed)
    last_lightning_move_time = 0

    def spawn_enemies():
        """Spawn enemies based on the current round."""
        nonlocal enemies, enemies_per_round
        # Increase difficulty each round by adding more enemies
        num_ranged = random.randint(1, current_round // 2 + 1)
        #num_ranged = 0
        num_melee = random.randint(2, current_round + 2)
        #num_melee = 0
        num_boss = 1 + current_round // 3 # Add a boss enemy every 3 rounds
        #num_boss = 3

        ranged_enemies = [RangedEnemy(*dungeon.get_random_open_position(), SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(num_ranged)]
        melee_enemies = [Enemy(*dungeon.get_random_open_position()) for _ in range(num_melee)]
        boss_melee_enemies = [BossMeleeEnemy(*dungeon.get_random_open_position()) for _ in range(num_boss)]
        enemies = ranged_enemies + melee_enemies + boss_melee_enemies

    def check_for_next_round():
        """Check if all enemies are defeated and advance to the next round."""
        nonlocal current_round, enemies_per_round, enemies_defeated
        if not enemies:
            current_round += 1  # Move to the next round
            enemies_defeated = 0
            spawn_enemies()
    
    spawn_enemies()

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
                    current_round = 1
                    enemies_defeated = 0
                    spawn_enemies()
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
                        if player.mana >= 30:  # Ensure player has enough mana (adjust mana cost as needed)
                            player.start_lightning_strike(dungeon_width_in_tiles * TILE_SIZE, dungeon_height_in_tiles * TILE_SIZE)
                            lightning_in_progress = True
                            last_lightning_move_time = current_time  # Reset cooldown
                        else:
                            print("Not enough mana for lightning strike!")  # Notify player of insufficient mana
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
                    player.confirm_lightning_strike(enemies, screen, camera_offset)
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
        
        check_for_next_round()

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
                            if isinstance(enemy, BossMeleeEnemy):
                                player.gain_xp(150)
                            else:
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
                if isinstance(enemy, BossMeleeEnemy):
                    player.gain_xp(150)  # Bosses drop 150 XP
                else:
                    player.gain_xp(50)  # Regular enemies drop 50 XP
                enemies.remove(enemy)  # Remove enemy from the list

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
        player.update()
        player.draw(screen, camera_offset)
        
        # Draw round number on the top right corner
        font = pygame.font.SysFont(None, 48)
        round_text = font.render(f"Round: {current_round}", True, (0, 0, 0))
        screen.blit(round_text, (SCREEN_WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()