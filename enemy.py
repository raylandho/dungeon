import pygame
import random
from settings import TILE_SIZE
from projectile import EnemyProjectile

class Enemy:
    def __init__(self, x, y):
        self.size = 40  # Example size, adjust as needed
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((255, 0, 0))  # Red enemy for melee enemies
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 50  # Example health value
        self.speed = 2  # Example speed value
        self.is_flashing = False
        self.flash_duration = 100  # Duration of the flash effect in milliseconds
        self.flash_start_time = 0  # Track when the flash started
        self.original_color = (255, 0, 0)  # Default color is red for melee enemies
        self.melee_range = 50  # Melee attack range
        self.melee_damage = 10  # Damage dealt by melee attack
        self.attack_cooldown = 1000  # Cooldown between melee attacks in milliseconds
        self.last_attack_time = 0  # Track the last time the enemy attacked

    def take_damage(self, amount):
        """Reduce the enemy's health by a specified amount and trigger the flash effect."""
        self.health -= amount
        self.start_flash()  # Trigger the flash effect
        print(f"Enemy took {amount} damage, remaining health: {self.health}")
        if self.health <= 0:
            return True  # Return True if the enemy dies
        return False

    def start_flash(self):
        """Start the flash effect by changing the color to white."""
        self.is_flashing = True
        self.image.fill((255, 255, 255))  # Change color to white
        self.flash_start_time = pygame.time.get_ticks()  # Record the time when the flash starts

    def update(self, player, walls, camera_offset, enemies):
        """Update enemy state, including movement and flashing."""
        self.move_towards_player(player.rect, walls, enemies)
        self.melee_attack(player)

        if self.is_flashing:
            current_time = pygame.time.get_ticks()
            if current_time - self.flash_start_time >= self.flash_duration:
                self.image.fill(self.original_color)  # Revert to the original color
                self.is_flashing = False

    def move_towards_player(self, player_rect, walls, enemies):
        """Move the enemy towards the player without overlapping other enemies or the player."""
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y

        if abs(dx) > abs(dy):
            new_pos = (self.rect.x + (self.speed if dx > 0 else -self.speed), self.rect.y)
        else:
            new_pos = (self.rect.x, self.rect.y + (self.speed if dy > 0 else -self.speed))

        # Prevent overlapping with walls, other enemies, and the player
        if not self.check_collision(new_pos, walls, enemies) and not self.check_collision_with_player(new_pos, player_rect):
            self.rect.topleft = new_pos

    def check_collision(self, new_pos, walls, enemies):
        """Check for collision with walls and other enemies."""
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

    def check_collision_with_player(self, new_pos, player_rect):
        """Check for collision with the player's entire bounding box."""
        future_rect = pygame.Rect(new_pos, (self.size, self.size))
        return future_rect.colliderect(player_rect)

    def overlaps_with_other_enemies(self, new_pos, enemies):
        """Check if the enemy overlaps with any other enemies at the new position."""
        future_rect = pygame.Rect(new_pos, (self.size, self.size))
        
        # Check overlap with other enemies
        for other_enemy in enemies:
            if other_enemy != self and future_rect.colliderect(other_enemy.rect):
                return True
        return False

    def melee_attack(self, player):
        """Perform a melee attack on the player if within range and cooldown is over."""
        current_time = pygame.time.get_ticks()
        
        # Use pygame.Vector2 for distance calculation
        enemy_pos = pygame.math.Vector2(self.rect.center)
        player_pos = pygame.math.Vector2(player.rect.center)
        distance_to_player = enemy_pos.distance_to(player_pos)
        
        if distance_to_player <= self.melee_range and current_time - self.last_attack_time >= self.attack_cooldown:
            player.take_damage(self.melee_damage)  # Inflict damage to the player
            self.last_attack_time = current_time  # Update last attack time
            print(f"Enemy dealt {self.melee_damage} damage to the player!")

    def draw(self, screen, camera_offset):
        """Draw the enemy sprite."""
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))

    def is_dead(self):
        """Return True if the enemy's health is 0 or less."""
        return self.health <= 0

class RangedEnemy(Enemy):
    def __init__(self, x, y, screen_width, screen_height):
        super().__init__(x, y)
        self.image.fill((255, 165, 0))  # Orange color for ranged enemies
        self.original_color = (255, 165, 0)  # Original color is orange
        self.projectiles = []  # List to store enemy projectiles
        self.shoot_cooldown = 1500  # Cooldown between shots (milliseconds)
        self.last_shot_time = 0  # Track the last time the enemy shot
        self.screen_width = screen_width
        self.screen_height = screen_height

    def shoot(self, player):
        """Shoot a projectile towards the player."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shoot_cooldown:
            # Create a new projectile aimed at the player
            direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
            direction = direction.normalize()  # Normalize the direction vector
            
            # Initialize the projectile at the enemy's center
            new_projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, direction, self.screen_width, self.screen_height)
            self.projectiles.append(new_projectile)
            self.last_shot_time = current_time

    def update(self, player, walls, camera_offset, enemies):
        """Update enemy logic, including shooting."""
        super().update(player, walls, camera_offset, enemies)  # Pass the required arguments to the base update method
        self.shoot(player)  # Attempt to shoot at the player

    def draw(self, screen, camera_offset):
        """Draw the enemy sprite."""
        super().draw(screen, camera_offset)
        # Projectiles are drawn in the main loop

class BossMeleeEnemy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = 80  # Boss size is 2x2 tiles (assuming each tile is 40x40)
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((0, 0, 255))  # Blue for boss enemies
        self.original_color = (0, 0, 255)  # Original color is blue
        self.health = 200  # Higher health for the boss
        self.speed = 3  # Speed value for boss
        self.melee_damage = 25  # Stronger melee attacks
        self.melee_range = 70  # Melee attack range
        self.attack_cooldown = 800  # Cooldown between attacks
        self.rect = pygame.Rect(x, y, self.size, self.size) 

    def take_damage(self, amount):
        """Reduce the enemy's health by a specified amount and trigger the flash effect."""
        self.health -= amount
        self.start_flash()  # Trigger the flash effect
        print(f"Boss took {amount} damage, remaining health: {self.health}")
        if self.health <= 0:
            return True  # Return True if the boss dies
        return False

    def move_towards_player(self, player_rect, walls, enemies, gap=5):
        """Move the enemy towards the player without overlapping other enemies or the player, leaving a gap."""
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery

        if abs(dx) > abs(dy):
            # Move horizontally
            new_x = self.rect.x + (self.speed if dx > 0 else -self.speed)
            new_pos = (new_x, self.rect.y)

            # Ensure there is a gap between the boss and the player
            if abs(player_rect.centerx - (self.rect.centerx + (self.speed if dx > 0 else -self.speed))) < self.size // 2 + gap:
                new_pos = (self.rect.x, self.rect.y)  # Stop movement if within gap range
        else:
            # Move vertically
            new_y = self.rect.y + (self.speed if dy > 0 else -self.speed)
            new_pos = (self.rect.x, new_y)

            # Ensure there is a gap between the boss and the player
            if abs(player_rect.centery - (self.rect.centery + (self.speed if dy > 0 else -self.speed))) < self.size // 2 + gap:
                new_pos = (self.rect.x, self.rect.y)  # Stop movement if within gap range

        # Prevent overlapping with walls, other enemies, and the player
        if not self.check_collision(new_pos, walls, enemies) and not self.check_collision_with_player(player_rect, gap):
            self.rect.topleft = new_pos

    def check_collision_with_player(self, player_rect, gap=5):
        """Check for collision with the player, leaving a small gap."""
        # Check collision with a small gap around the player
        boss_rect = pygame.Rect(self.rect.x, self.rect.y, self.size, self.size)
        expanded_player_rect = player_rect.inflate(gap * 2, gap * 2)  # Expand player's rect by the gap

        # If the boss is close to the player but not touching
        return boss_rect.colliderect(expanded_player_rect)

    def update(self, player, walls, camera_offset, enemies):
        """Update boss logic."""
        super().update(player, walls, camera_offset, enemies)
        # Call melee attack to check if the player is in range and deal damage
        self.melee_attack(player)

    def melee_attack(self, player):
        """Perform a melee attack on the player, covering all adjacent tiles."""
        current_time = pygame.time.get_ticks()

        # Define the attack range: covering one tile left, one tile up, two tiles down, and two tiles right
        boss_attack_range = pygame.Rect(
            self.rect.x - TILE_SIZE,  # One tile to the left
            self.rect.y - TILE_SIZE,  # One tile above
            self.size + TILE_SIZE * 2,  # Cover two tiles to the right
            self.size + TILE_SIZE * 2   # Cover two tiles below
        )

        # Check if the player is within this larger attack range and if the cooldown is over
        if boss_attack_range.colliderect(player.rect) and current_time - self.last_attack_time >= self.attack_cooldown:
            # Perform attack
            player.take_damage(self.melee_damage)
            self.last_attack_time = current_time  # Update last attack time
            print(f"Boss dealt {self.melee_damage} damage to the player!")
