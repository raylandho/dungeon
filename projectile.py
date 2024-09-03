import pygame
from settings import PLAYER_SIZE

class Projectile:
    def __init__(self, x, y, direction, screen_width, screen_height, speed=5, size=None):
        if size is None:
            size = PLAYER_SIZE // 2  # Default size
        self.size = size
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 255, 0))  # Default yellow color for projectiles
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction.normalize()  # Ensure the direction vector is normalized
        self.speed = speed
        self.damage = 25  # Damage dealt by the projectile
        self.mana_cost = 10  # Mana cost for shooting the projectile
        self.screen_width = screen_width  # Store screen width
        self.screen_height = screen_height  # Store screen height

    def move(self, walls):
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check for collision with walls
        if self.check_collision(walls):
            return False  # Return False if collision occurs

        return True  # Return True if no collision occurs

    def check_collision(self, walls):
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def is_off_screen(self):
        return not (0 <= self.rect.x <= self.screen_width and 0 <= self.rect.y <= self.screen_height)

class MeleeAttack:
    def __init__(self, player_rect, attack_range=50, damage=50):
        self.rect = player_rect.copy()
        self.rect.inflate_ip(attack_range, attack_range)  # Increase the size of the rect to represent the attack range
        self.damage = damage

    def check_collision(self, enemies):
        """Check if the melee attack collides with any enemies and apply damage."""
        kills = 0
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                if enemy.take_damage(self.damage):
                    enemies.remove(enemy)
                    kills += 1
        return kills
