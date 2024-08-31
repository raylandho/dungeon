# enemy.py

import pygame
from settings import TILE_SIZE, PLAYER_SIZE

class Enemy:
    def __init__(self, x, y):
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((255, 0, 0))  # Red enemy
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 50  # Enemy health

    def move_towards_player(self, player_rect, walls):
        """Simple AI to move the enemy towards the player."""
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y

        if abs(dx) > abs(dy):
            new_pos = (self.rect.x + (5 if dx > 0 else -5), self.rect.y)
        else:
            new_pos = (self.rect.x, self.rect.y + (5 if dy > 0 else -5))

        if not self.check_collision(new_pos, walls):
            self.rect.topleft = new_pos

    def check_collision(self, new_pos, walls):
        future_rect = pygame.Rect(new_pos, (PLAYER_SIZE, PLAYER_SIZE))
        for wall in walls:
            if future_rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

    def take_damage(self, amount):
        """Reduce the enemy's health by a specified amount and check if they die."""
        self.health = max(0, self.health - amount)
        if self.health == 0:
            return True  # Return True if the enemy dies
        return False
