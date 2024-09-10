import pygame
import random
from settings import TILE_SIZE
from projectile import EnemyProjectile

class Enemy:
    def __init__(self, x, y):
        self.size = 40  # Example size, adjust as needed
        self.original_idle_images = [pygame.transform.scale(pygame.image.load('assets/goblinidle.png').convert_alpha(), (self.size, self.size)),
                                     pygame.transform.scale(pygame.image.load('assets/goblinidle2.png').convert_alpha(), (self.size, self.size))]
        self.original_walk_images = [pygame.transform.scale(pygame.image.load('assets/goblinwalk.png').convert_alpha(), (self.size, self.size)),
                                     pygame.transform.scale(pygame.image.load('assets/goblinwalk2.png').convert_alpha(), (self.size, self.size))]
        self.original_attack_images = [pygame.transform.scale(pygame.image.load('assets/goblinattack.png').convert_alpha(), (self.size, self.size)),
                                       pygame.transform.scale(pygame.image.load('assets/goblinattack2.png').convert_alpha(), (self.size, self.size))]
        
        # Set initial images
        self.idle_images = self.original_idle_images[:]
        self.walk_images = self.original_walk_images[:]
        self.attack_images = self.original_attack_images[:]
        
        self.image = self.idle_images[0]
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

        # Animation frame tracking
        self.current_idle_frame = 0
        self.current_walk_frame = 0
        self.current_attack_frame = 0
        self.animation_speed = 300  # Time in milliseconds between frames
        self.last_animation_time = pygame.time.get_ticks()
        
        # Attack animation tracking
        self.attacking = False
        self.attack_animation_duration = 500  # Time in milliseconds for the attack animation
        self.attack_animation_start_time = 0
        
        # Direction tracking
        self.facing_right = True  # Goblin starts facing right

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
        self.flash_start_time = pygame.time.get_ticks()  # Record the time when the flash starts
        
    def update_flash(self):
        """Update the flash effect and restore the original sprite after the flash duration."""
        current_time = pygame.time.get_ticks()

        if current_time - self.flash_start_time < self.flash_duration:
            # Apply a flashing effect by adjusting the alpha value
            flash_surface = self.image.copy()
            flash_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = flash_surface
        else:
            self.is_flashing = False
            # Restore the normal image (no flashing)
            self.restore_current_frame()
    
    def restore_current_frame(self):
        """Restores the current frame of the enemy (idle, walk, or shoot) after flashing."""
        if self.walking:
            self.update_walk_animation()
        else:
            self.update_idle_animation()

    def update(self, player, walls, camera_offset, enemies):
        """Update enemy state, including movement, attacking, and flashing."""
        self.move_towards_player(player.rect, walls, enemies)
        self.melee_attack(player)

        # Handle flashing state
        if self.is_flashing:
            self.update_flash()
        else:
            # Update animations based on movement and actions
            if self.walking:
                self.update_walk_animation()
            else:
                self.update_idle_animation()

    def update_idle_animation(self):
        """Update the idle animation by switching between the idle frames."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_time >= self.animation_speed:
            # Switch to the next frame
            self.current_idle_frame = (self.current_idle_frame + 1) % len(self.idle_images)
            self.image = self.idle_images[self.current_idle_frame]
            self.last_animation_time = current_time

        # Ensure correct facing direction
        self.flip_animations_if_needed()

    def update_walk_animation(self):
        """Update the walk animation by switching between the walk frames."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_animation_time >= self.animation_speed:
            # Switch to the next walk frame
            self.current_walk_frame = (self.current_walk_frame + 1) % len(self.walk_images)
            self.image = self.walk_images[self.current_walk_frame]
            self.last_animation_time = current_time

        # Ensure correct facing direction
        self.flip_animations_if_needed()

    def update_attack_animation(self):
        """Update the attack animation by switching between the attack frames."""
        current_time = pygame.time.get_ticks()

        # Check if the animation duration has passed
        if current_time - self.attack_animation_start_time >= self.attack_animation_duration:
            # End attack animation and reset to idle or walk
            self.attacking = False
            return

        # Switch to the next attack frame
        frame_duration = self.attack_animation_duration // len(self.attack_images)
        frame_index = (current_time - self.attack_animation_start_time) // frame_duration
        self.image = self.attack_images[int(frame_index) % len(self.attack_images)]

        # Ensure correct facing direction
        self.flip_animations_if_needed()

    def move_towards_player(self, player_rect, walls, enemies):
        """Move the enemy towards the player without overlapping other enemies or the player."""
        dx = player_rect.x - self.rect.x
        dy = player_rect.y - self.rect.y

        # Determine whether the goblin should face left or right
        if dx > 0 and not self.facing_right:
            self.facing_right = True
            self.flip_animations_if_needed()
        elif dx < 0 and self.facing_right:
            self.facing_right = False
            self.flip_animations_if_needed()

        if abs(dx) > abs(dy):
            new_pos = (self.rect.x + (self.speed if dx > 0 else -self.speed), self.rect.y)
        else:
            new_pos = (self.rect.x, self.rect.y + (self.speed if dy > 0 else -self.speed))

        # Prevent overlapping with walls, other enemies, and the player
        if not self.check_collision(new_pos, walls, enemies) and not self.check_collision_with_player(new_pos, player_rect):
            self.rect.topleft = new_pos
            self.walking = True  # Set walking state when moving
        else:
            self.walking = False  # Set to idle when not moving

    def flip_animations_if_needed(self):
        """Flip all animations if the direction changes."""
        if self.facing_right:
            self.idle_images = self.original_idle_images[:]
            self.walk_images = self.original_walk_images[:]
            self.attack_images = self.original_attack_images[:]
        else:
            self.idle_images = [pygame.transform.flip(img, True, False) for img in self.original_idle_images]
            self.walk_images = [pygame.transform.flip(img, True, False) for img in self.original_walk_images]
            self.attack_images = [pygame.transform.flip(img, True, False) for img in self.original_attack_images]

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

    def melee_attack(self, player):
        """Perform a melee attack on the player if within range and cooldown is over."""
        current_time = pygame.time.get_ticks()
        
        # Use pygame.Vector2 for distance calculation
        enemy_pos = pygame.math.Vector2(self.rect.center)
        player_pos = pygame.math.Vector2(player.rect.center)
        distance_to_player = enemy_pos.distance_to(player_pos)
        
        if distance_to_player <= self.melee_range and current_time - self.last_attack_time >= self.attack_cooldown:
            self.attacking = True
            self.attack_animation_start_time = pygame.time.get_ticks()  # Start the attack animation timer
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
        
        # Load animation images for idle, walking, and shooting
        self.original_idle_images = [pygame.transform.scale(pygame.image.load('assets/mageidle.png').convert_alpha(), (self.size, self.size)),
                                     pygame.transform.scale(pygame.image.load('assets/mageidle2.png').convert_alpha(), (self.size, self.size))]
        self.original_walk_images = [pygame.transform.scale(pygame.image.load('assets/magewalk.png').convert_alpha(), (self.size, self.size)),
                                     pygame.transform.scale(pygame.image.load('assets/magewalk2.png').convert_alpha(), (self.size, self.size))]
        self.original_shoot_images = [pygame.transform.scale(pygame.image.load('assets/magecast.png').convert_alpha(), (self.size, self.size)),
                                      pygame.transform.scale(pygame.image.load('assets/magecast2.png').convert_alpha(), (self.size, self.size))]
        
        # Initialize the current image sets
        self.idle_images = self.original_idle_images[:]
        self.walk_images = self.original_walk_images[:]
        self.shoot_images = self.original_shoot_images[:]
        
        self.image = self.idle_images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.projectiles = []  # List to store enemy projectiles
        
        # Colors and shoot cooldown
        self.original_color = (255, 165, 0)  # Orange color for ranged enemies
        self.shoot_cooldown = 1500  # Cooldown between shots (milliseconds)
        self.last_shot_time = 0  # Track the last time the enemy shot
        
        # Direction tracking
        self.facing_right = True  # Start facing right

        # Animation frame tracking
        self.current_idle_frame = 0
        self.current_walk_frame = 0
        self.current_shoot_frame = 0
        self.animation_speed = 300  # Time in milliseconds between frames
        self.last_animation_time = pygame.time.get_ticks()

        # Shooting animation tracking
        self.shooting = False
        self.shoot_animation_duration = 500  # Time in milliseconds for the shoot animation
        self.shoot_animation_start_time = 0
        
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
            self.shooting = True  # Start the shoot animation
            self.shoot_animation_start_time = current_time  # Record the start time of the shooting animation
            self.last_shot_time = current_time

    def update(self, player, walls, camera_offset, enemies):
        """Update enemy logic, including shooting, flashing, and animations."""
        self.move_towards_player(player.rect, walls, enemies)  # Handle movement
        
        # Handle shooting
        self.shoot(player)

        # Handle flashing state
        if self.is_flashing:
            self.update_flash()  # Apply flash effect
        else:
            # Update the animation based on whether the enemy is shooting or walking
            if self.shooting:
                self.update_shoot_animation()
            elif self.walking:
                self.update_walk_animation()
            else:
                self.update_idle_animation()

    def update_flash(self):
        """Update the flash effect and restore the original sprite after the flash duration."""
        current_time = pygame.time.get_ticks()

        if current_time - self.flash_start_time < self.flash_duration:
            # Apply a flashing effect by adjusting the alpha value
            flash_surface = self.image.copy()
            flash_surface.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_MULT)
            self.image = flash_surface
        else:
            self.is_flashing = False
            # Restore the normal image (no flashing)
            self.restore_current_frame()

    def restore_current_frame(self):
        """Restores the current frame of the enemy (idle, walking, or shooting) after flashing."""
        if self.shooting:
            self.update_shoot_animation()
        elif self.walking:
            self.update_walk_animation()
        else:
            self.update_idle_animation()

    def update_shoot_animation(self):
        """Update the shoot animation by switching between the shooting frames."""
        current_time = pygame.time.get_ticks()

        # Check if the animation duration has passed
        if current_time - self.shoot_animation_start_time >= self.shoot_animation_duration:
            # End shoot animation and reset to idle or walk
            self.shooting = False
            return

        # Switch to the next shoot frame
        frame_duration = self.shoot_animation_duration // len(self.shoot_images)
        frame_index = (current_time - self.shoot_animation_start_time) // frame_duration
        self.image = self.shoot_images[int(frame_index) % len(self.shoot_images)]

        # Ensure correct facing direction
        self.flip_animations_if_needed()

    def flip_animations_if_needed(self):
        """Flip all animations if the direction changes."""
        if self.facing_right:
            self.idle_images = self.original_idle_images[:]
            self.walk_images = self.original_walk_images[:]
            self.shoot_images = self.original_shoot_images[:]
        else:
            self.idle_images = [pygame.transform.flip(img, True, False) for img in self.original_idle_images]
            self.walk_images = [pygame.transform.flip(img, True, False) for img in self.original_walk_images]
            self.shoot_images = [pygame.transform.flip(img, True, False) for img in self.original_shoot_images]

    def draw(self, screen, camera_offset):
        """Draw the ranged enemy and projectiles."""
        # Draw the ranged enemy
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))

        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen, camera_offset)

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
