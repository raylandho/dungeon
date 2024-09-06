import pygame
import random
from settings import TILE_SIZE, PLAYER_SIZE

class Enemy:
    def __init__(self, x, y):
        self.size = 40  # Example size, adjust as needed
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 0, 0))  # Red enemy
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 50  # Example health value
        self.speed = 2  # Example speed value
        self.attack_range = 50  # Range within which enemy can attack the player
        self.attack_cooldown = 1000  # Time in milliseconds between attacks
        self.last_attack_time = 0  # Last time the enemy attacked
        self.damage = 10  # Damage the enemy deals per attack
        self.is_flashing = False
        self.flash_duration = 100  # Duration of the flash effect in milliseconds
        self.original_color = (255, 0, 0)
    
    def get_valid_spawn_position(self, dungeon, enemies):
        """Get a valid spawn position that doesn't overlap with other enemies or walls."""
        while True:
            x = random.randint(0, dungeon.tiles_x - 1) * TILE_SIZE
            y = random.randint(0, dungeon.tiles_y - 1) * TILE_SIZE
            if dungeon.layout[y // TILE_SIZE][x // TILE_SIZE] != 1 and not self.overlaps_with_enemies(x, y, enemies):
                return (x, y)

    def overlaps_with_enemies(self, x, y, enemies):
        """Check if the given position overlaps with any existing enemies."""
        temp_rect = pygame.Rect(x, y, self.size, self.size)
        for enemy in enemies:
            if temp_rect.colliderect(enemy.rect):
                return True
        return False

    def move_towards_player(self, player_rect, walls, enemies):
        """Simple AI to move the enemy towards the player without overlapping other enemies."""
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y

        if abs(dx) > abs(dy):
            new_pos = (self.rect.x + (self.speed if dx > 0 else -self.speed), self.rect.y)
        else:
            new_pos = (self.rect.x, self.rect.y + (self.speed if dy > 0 else -self.speed))

        if not self.check_collision(new_pos, walls, enemies):
            self.rect.topleft = new_pos

    def check_collision(self, new_pos, walls, enemies):
        future_rect = pygame.Rect(new_pos, (self.size, self.size))
        
        # Check collision with walls
        for wall in walls:
            if future_rect.colliderect(wall):
                return True
        
        # Check collision with other enemies
        for enemy in enemies:
            if enemy != self and future_rect.colliderect(enemy.rect):
                return True
        
        return False

    def melee_attack(self, player):
        """Attack the player if within range and if cooldown allows."""
        current_time = pygame.time.get_ticks()
        if self.rect.colliderect(player.rect) and current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            player.take_damage(self.damage)  # Call player's take_damage function
            print(f"Enemy attacks player for {self.damage} damage!")

    def draw(self, screen, camera_offset):
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))

    def take_damage(self, amount):
        """Reduce the enemy's health by a specified amount and trigger the flash effect."""
        self.health = max(0, self.health - amount)
        self.start_flash()
        print(f"Enemy took {amount} damage, remaining health: {self.health}")
        if self.health == 0:
            return True  # Return True if the enemy dies
        return False

    def start_flash(self):
        """Start the flash effect by changing the color to white."""
        self.is_flashing = True
        self.image.fill((255, 255, 255))  # Change color to white
        self.flash_start_time = pygame.time.get_ticks()  # Record the time when the flash starts

    def update(self):
        """Update the enemy's state, including the flash effect."""
        if self.is_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start_time >= self.flash_duration:
                self.image.fill(self.original_color)  # Revert to the original color
                self.is_flashing = False
