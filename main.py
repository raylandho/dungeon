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

    # Initialize game objects
    dungeon = Dungeon(SCREEN_WIDTH, SCREEN_HEIGHT)
    player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    walls = dungeon.get_walls()

    # Initialize enemies list
    enemies = [
        Enemy(200, 200),
        Enemy(100, 100)
    ]
    
    # Initialize projectiles list
    projectiles = []

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

        keys = pygame.key.get_pressed()
        player.handle_movement(keys, walls)
        player.update_aim_direction(keys)

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
            enemy.move_towards_player(player.rect, walls)

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
