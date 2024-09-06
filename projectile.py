import pygame
from settings import PLAYER_SIZE, TILE_SIZE

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

        # Set up the fireball's appearance
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)  # Use SRCALPHA for transparency
        self.image.fill((0, 0, 0, 0))  # Fully transparent background
        pygame.draw.circle(self.image, (255, 69, 0), (self.size // 2, self.size // 2), self.size // 2)  # Draw a fireball (orange circle)
        self.damage = 100  # Fireball deals more damage
        self.mana_cost = 30  # Fireball has a higher mana cost

    def move(self, walls, enemies, player):
        """Move the fireball and check for collisions with walls and enemies."""
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

        # Check for collision with walls
        if self.check_collision(walls):
            return False  # Return False to indicate the fireball should be removed

        # Check for collision with enemies and deal damage
        for enemy in enemies[:]:
            if self.rect.colliderect(enemy.rect):
                enemy.take_damage(self.damage)
                if enemy.health <= 0:  # Ensure enemy is removed if health is 0 or less
                    enemies.remove(enemy)
                    #print("Enemy killed by fireball.")
                    player.gain_xp(50)  # Ensure XP is granted for killing the enemy

        return True  # Fireball keeps moving until it hits a wall

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
