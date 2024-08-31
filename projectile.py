# projectile.py

import pygame
from settings import PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Projectile:
    def __init__(self, x, y, direction, speed=5, size=None):
        if size is None:
            size = PLAYER_SIZE // 2  # Default size
        self.size = size
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 0))  # Default yellow color for projectiles
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed

    def move(self):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def is_off_screen(self):
        return not (0 <= self.rect.x <= SCREEN_WIDTH and 0 <= self.rect.y <= SCREEN_HEIGHT)

class MeleeAttack(Projectile):
    def __init__(self, player_rect):
        super().__init__(player_rect.centerx, player_rect.centery, pygame.math.Vector2(0, 0), speed=0)
        self.rect = player_rect.copy()  # The melee attack area is the same as the player's rect
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill((255, 0, 0))  # Red for melee attack

    def move(self):
        # Melee attacks don't move, so we override move to do nothing
        pass

    def check_collision(self, enemies):
        """Check if the melee attack collides with any enemies and return the number of kills."""
        kills = 0
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                print("Enemy killed by melee attack")
                enemies.remove(enemy)  # Instantly remove the enemy
                kills += 1
        return kills
