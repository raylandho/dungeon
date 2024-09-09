import pygame
import math
from settings import PLAYER_SIZE, TILE_SIZE

class Projectile:
    def __init__(self, x, y, direction, screen_width, screen_height, speed=5, size=None, damage=25):
        self.size = size or TILE_SIZE  # Default size based on tile size

        # Load both projectile images for animation
        self.projectile_images = [
            pygame.transform.scale(pygame.image.load('assets/energy.png').convert_alpha(), (self.size, self.size)),
            pygame.transform.scale(pygame.image.load('assets/energy2.png').convert_alpha(), (self.size, self.size))
        ]

        self.rect = self.projectile_images[0].get_rect(center=(x, y))
        self.direction = direction.normalize()  # Ensure the direction vector is normalized
        self.speed = speed
        self.screen_width = screen_width  # Store screen width for boundary checks
        self.screen_height = screen_height  # Store screen height for boundary checks
        self.damage = damage  # Damage dealt by the projectile

        # Animation variables
        self.animation_timer = 0
        self.animation_interval = 200  # Switch image every 200 milliseconds
        self.current_image_index = 0
        self.image = self.rotate_image_by_direction(self.projectile_images[self.current_image_index], self.direction)  # Initialize with rotated image

    def rotate_image_by_direction(self, image, direction):
        """Rotate the image based on the direction of movement."""
        # Calculate the angle of rotation in degrees
        angle = math.degrees(math.atan2(-direction.y, direction.x))  # Negative y because Pygame's y-axis is inverted
        adjusted_angle = angle - 225  # Adjust by 225 degrees to account for the initial bottom-left orientation
        rotated_image = pygame.transform.rotate(image, adjusted_angle)
        return rotated_image

    def update_animation(self):
        """Switch between projectile images to create an animation."""
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_interval:
            self.animation_timer = current_time
            self.current_image_index = (self.current_image_index + 1) % len(self.projectile_images)  # Toggle between the two images

        # Rotate the current image based on the direction of the projectile
        self.image = self.rotate_image_by_direction(self.projectile_images[self.current_image_index], self.direction)

    def move(self, walls):
        """Move the projectile and check for collisions with walls."""
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Update the projectile animation
        self.update_animation()

        # Check for collision with walls
        for wall in walls:
            if self.rect.colliderect(wall):
                return False  # Collision, projectile should be removed

        return True  # No collision, projectile continues moving

    def is_off_screen(self, camera_offset):
        """Check if the projectile is off the screen, considering the camera offset."""
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        return not (0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height)

    def draw(self, screen, camera_offset):
        """Draw the projectile, taking the camera offset into account."""
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))  # Use the rotated image
    
class Fireball(Projectile):
    def __init__(self, x, y, direction, screen_width, screen_height, speed=7, size=None):
        if size is None:
            size = PLAYER_SIZE * 2.5  # Default size for the fireball
        self.size = size

        # Calculate the fireball's initial position directly in front of the player
        offset_x = direction.x * (PLAYER_SIZE // 2 + self.size // 2)
        offset_y = direction.y * (PLAYER_SIZE // 2 + self.size // 2)

        # Initialize the fireball's position
        fireball_x = x + offset_x
        fireball_y = y + offset_y

        super().__init__(fireball_x, fireball_y, direction, screen_width, screen_height, speed, self.size)

         # Load both fireball images for animation
        self.fireball_images = [
            pygame.transform.scale(pygame.image.load('assets/fireball.png').convert_alpha(), (self.size, self.size)),
            pygame.transform.scale(pygame.image.load('assets/fireball2.png').convert_alpha(), (self.size, self.size))
        ]
        
        self.damage = 100  # Fireball deals more damage
        self.mana_cost = 30  # Fireball has a higher mana cost

        # Track enemies that have already been hit
        self.enemies_hit = set()  # This set will track enemies that have been hit to avoid multiple hits
        
        # Animation variables
        self.animation_timer = 0
        self.animation_interval = 200  # Switch image every 200 milliseconds
        self.current_image_index = 0
        
        # Rotate the initial fireball image based on direction
        self.image = self.rotate_image_by_direction(self.fireball_images[self.current_image_index], direction)
        
    def rotate_image_by_direction(self, image, direction):
        """Rotate the image based on the direction of movement."""
        # Calculate the angle of rotation in degrees
        angle = math.degrees(math.atan2(-direction.y, direction.x))  # Negative y because Pygame's y-axis is inverted
        adjusted_angle = angle - 225
        rotated_image = pygame.transform.rotate(image, adjusted_angle)
        return rotated_image
    
    def update_animation(self):
        """Switch between fireball images to create an animation."""
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_interval:
            self.animation_timer = current_time
            self.current_image_index = (self.current_image_index + 1) % len(self.fireball_images)  # Toggle between the two images
            # Rotate the new image based on direction
            self.image = self.rotate_image_by_direction(self.fireball_images[self.current_image_index], self.direction)

    def check_collision(self, walls):
        """Check if the fireball collides with any walls."""
        for wall in walls:
            if self.rect.colliderect(wall):
                return True
        return False

    def move(self, walls, enemies, player):
        """Move the fireball and check for collisions with walls and enemies."""
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        
        self.update_animation()

        # Check for collision with walls
        if self.check_collision(walls):
            return False  # Return False to indicate the fireball should be removed if it hits a wall

        # Check for collision with enemies and deal damage
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect) and enemy not in self.enemies_hit:
                enemy.take_damage(self.damage)  # Inflict damage
                self.enemies_hit.add(enemy)  # Mark the enemy as hit
                if enemy.health <= 0:  # Ensure the enemy is removed if health is 0 or less
                    enemies.remove(enemy)
                    player.gain_xp(50)  # Grant XP for killing the enemy

        return True  # Fireball keeps moving until it hits a wall or goes off-screen

class LightningStrike:
    def __init__(self, player_x, player_y, map_width, map_height, strike_radius=TILE_SIZE * 2):
        self.strike_radius = strike_radius  # The size of the lightning strike circle
        self.color = (173, 216, 230)  # Light blue color for the lightning strike
        self.map_width = map_width
        self.map_height = map_height
        self.target_position = pygame.Vector2(player_x, player_y)  # Start circle at the player's position

    def move(self, direction):
        """Move the lightning strike targeting circle based on user input."""
        if direction == "left" and self.target_position.x > self.strike_radius:
            self.target_position.x -= TILE_SIZE
        if direction == "right" and self.target_position.x < self.map_width - self.strike_radius:
            self.target_position.x += TILE_SIZE
        if direction == "up" and self.target_position.y > self.strike_radius:
            self.target_position.y -= TILE_SIZE
        if direction == "down" and self.target_position.y < self.map_height - self.strike_radius:
            self.target_position.y += TILE_SIZE

    def draw(self, screen, camera_offset):
        """Draw the lightning strike targeting circle on the screen."""
        screen_x = self.target_position.x - camera_offset[0]
        screen_y = self.target_position.y - camera_offset[1]
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.strike_radius, 3)

    def check_enemies_in_range(self, enemies, player):
        """Damage enemies within the lightning strike circle, reward player XP, and remove dead enemies."""
        struck_enemies = 0
        enemies_to_remove = []  # Track enemies that should be removed
        for enemy in enemies:
            enemy_distance = self.target_position.distance_to(enemy.rect.center)
            if enemy_distance <= self.strike_radius:
                if enemy.take_damage(75):  # Lightning does 75 damage
                    print(f"Enemy took 75 damage, remaining health: {enemy.health}")
                if enemy.health <= 0:  # Enemy is dead, mark for removal and reward XP
                    enemies_to_remove.append(enemy)
                    player.gain_xp(50)  # Reward 50 XP for each kill
                    struck_enemies += 1

        # Remove dead enemies from the list
        for enemy in enemies_to_remove:
            enemies.remove(enemy)
        return struck_enemies

class MeleeAttack:
    def __init__(self, player_rect, aim_direction, attack_range=50, damage=50):
        # Set the attack range to be in front of the player based on aim direction
        attack_offset_x = aim_direction.x * (player_rect.width // 2 + attack_range // 2)
        attack_offset_y = aim_direction.y * (player_rect.height // 2 + attack_range // 2)

        # Create a rectangle that represents the melee hitbox directly in front of the player
        self.rect = pygame.Rect(
            player_rect.centerx + attack_offset_x - attack_range // 2,
            player_rect.centery + attack_offset_y - attack_range // 2,
            attack_range,
            attack_range
        )
        self.damage = damage

    def check_collision(self, enemies):
        """Check if the melee attack hits any enemies and apply damage."""
        kills = 0
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                if enemy.take_damage(self.damage):
                    enemies.remove(enemy)
                    kills += 1
        return kills

class EnemyProjectile(Projectile):
    def __init__(self, x, y, direction, screen_width, screen_height, speed=5, size=None):
        self.size = size or TILE_SIZE // 2  # Default size based on tile size

        # Load both projectile images for animation
        self.projectile_images = [
            pygame.transform.scale(pygame.image.load('assets/energy.png').convert_alpha(), (self.size, self.size)),
            pygame.transform.scale(pygame.image.load('assets/energy2.png').convert_alpha(), (self.size, self.size))
        ]

        self.rect = self.projectile_images[0].get_rect(center=(x, y))
        self.direction = direction.normalize()  # Ensure the direction vector is normalized
        self.speed = speed
        self.screen_width = screen_width  # Store screen width for boundary checks
        self.screen_height = screen_height  # Store screen height for boundary checks
        self.damage = 15  # Set enemy projectile damage to 15

        # Animation variables
        self.animation_timer = 0
        self.animation_interval = 200  # Switch image every 200 milliseconds
        self.current_image_index = 0

    def update_animation(self):
        """Switch between projectile images to create an animation."""
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer > self.animation_interval:
            self.animation_timer = current_time
            self.current_image_index = (self.current_image_index + 1) % len(self.projectile_images)  # Toggle between the two images
            self.image = self.projectile_images[self.current_image_index]

    def move(self, walls):
        """Move the projectile and check for collisions with walls."""
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Update the projectile animation
        self.update_animation()

        # Check for collision with walls
        for wall in walls:
            if self.rect.colliderect(wall):
                return False  # Collision, projectile should be removed

        return True  # No collision, projectile continues moving

    def is_off_screen(self, camera_offset):
        """Check if the projectile is off the screen, considering the camera offset."""
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        return not (0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height)

    def draw(self, screen, camera_offset):
        """Draw the projectile, taking the camera offset into account."""
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.projectile_images[self.current_image_index], (screen_x, screen_y))