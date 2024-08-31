import pygame
import sys
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from player import Player, Projectile
from enemy import Enemy
from dungeon import Dungeon

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Dungeon Crawler')
    clock = pygame.time.Clock()

    # Initialize game objects
    dungeon = Dungeon()
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

        keys = pygame.key.get_pressed()
        player.handle_movement(keys, walls)
        player.update_aim_direction(keys)

        # Melee attack (Spacebar)
        if keys[pygame.K_SPACE]:
            player.melee_attack(enemies)

        # Ranged attack (R key)
        if keys[pygame.K_r]:
            player.ranged_attack(projectiles)

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
                        if enemy.take_damage(20):  # Deal damage and check if the enemy dies
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
