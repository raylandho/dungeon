import pygame
from settings import PLAYER_SIZE, TILE_SIZE
from projectile import Projectile, MeleeAttack, Fireball, LightningStrike

class Player:
    def __init__(self, x, y):
        self.size = PLAYER_SIZE
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill((0, 255, 0))  # Green player
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_health = 100
        self.health = self.max_health
        self.max_mana = 50
        self.mana = self.max_mana
        self.xp = 0
        self.xp_for_next_level = 100
        self.level = 1
        self.points = 0  # Points for leveling up
        self.is_dead = False
        self.attack_cooldown = 500  # Cooldown for attacks
        self.melee_attack_object = None
        self.last_attack_time = pygame.time.get_ticks()
        self.teleport_cooldown = 2000  # Cooldown for teleporting (in milliseconds)
        self.last_teleport_time = pygame.time.get_ticks()  # Time of last teleport
        self.aim_direction = pygame.math.Vector2(1, 0)
        self.font = pygame.font.SysFont(None, 24)
        self.fireball_unlocked = False
        self.is_placing_lightning = False
        self.lightning_strike = None
        self.lightning_unlocked = False
        self.teleport_attack_unlocked = False

    def handle_movement(self, keys, walls, dungeon_width, dungeon_height, enemies):
        movement_speed = 3
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_LEFT]:
            direction.x = -1
        if keys[pygame.K_RIGHT]:
            direction.x = 1
        if keys[pygame.K_UP]:
            direction.y = -1
        if keys[pygame.K_DOWN]:
            direction.y = 1

        # Normalize the direction vector to ensure consistent speed in all directions
        if direction.length() > 0:
            direction.normalize_ip()

        # Calculate new position
        new_x = self.rect.x + direction.x * movement_speed
        new_y = self.rect.y + direction.y * movement_speed

        # Check map boundaries
        if new_x < 0 or new_x + self.size > dungeon_width * TILE_SIZE:
            new_x = self.rect.x  # Prevent horizontal movement off the map
        if new_y < 0 or new_y + self.size > dungeon_height * TILE_SIZE:
            new_y = self.rect.y  # Prevent vertical movement off the map

        # Check collisions with walls and enemies
        if not self.check_collision((new_x, new_y), walls, enemies):
            self.rect.topleft = (new_x, new_y)

    def teleport(self, screen, camera_offset, walls, dungeon_width, dungeon_height, dungeon, screen_width, screen_height, enemies, projectiles):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_teleport_time < self.teleport_cooldown:
            return  # Teleport is on cooldown

        teleport_distance = TILE_SIZE * 3  # Limit teleport to 3 tiles
        teleport_x = self.rect.x + self.aim_direction.x * teleport_distance
        teleport_y = self.rect.y + self.aim_direction.y * teleport_distance

        # Ensure teleport doesn't move the player off the map (no wrapping)
        if teleport_x < 0 or teleport_x + self.size > dungeon_width * TILE_SIZE:
            return  # Invalid teleport position, abort teleport
        if teleport_y < 0 or teleport_y + self.size > dungeon_height * TILE_SIZE:
            return  # Invalid teleport position, abort teleport

        # Save the original position in case the teleport is invalid
        original_position = self.rect.topleft
        self.rect.topleft = (teleport_x, teleport_y)

        # Check for collisions at the new position
        if self.check_collision(self.rect.topleft, walls, enemies):
            self.rect.topleft = original_position
            return  # Collision detected, abort teleport
        self.play_teleport_animation(screen, camera_offset, original_position)
        # Update the last teleport time
        self.last_teleport_time = current_time
        #print("Teleport successful")

    def teleport_attack(self, screen, camera_offset, walls, dungeon_width, dungeon_height, dungeon, screen_width, screen_height, enemies, projectiles):
        """Teleport attack method which moves the player and damages enemies."""
        current_time = pygame.time.get_ticks()

        if current_time - self.last_teleport_time >= self.teleport_cooldown:
            teleport_distance = TILE_SIZE * 3  # 3 tiles teleport distance
            teleport_x = self.rect.x + self.aim_direction.x * teleport_distance
            teleport_y = self.rect.y + self.aim_direction.y * teleport_distance

            # Ensure teleport doesn't move the player off the map
            if teleport_x < 0 or teleport_x + self.size > dungeon_width * TILE_SIZE:
                return  # Invalid teleport position, abort teleport
            if teleport_y < 0 or teleport_y + self.size > dungeon_height * TILE_SIZE:
                return  # Invalid teleport position, abort teleport

            # Save the original position in case teleport is invalid
            original_position = self.rect.topleft
            self.rect.topleft = (teleport_x, teleport_y)

            # Check for collisions at the new position
            if self.check_collision(self.rect.topleft, walls, enemies):
                self.rect.topleft = original_position
                return  # Collision detected, abort teleport

            # List to track enemies to remove
            enemies_to_remove = []

            # Now, apply damage and knockback to nearby enemies
            for enemy in enemies:
                enemy_position = pygame.Vector2(enemy.rect.center)
                player_position = pygame.Vector2(self.rect.center)

                distance = player_position.distance_to(enemy_position)

                if distance <= TILE_SIZE * 3:  # Adjust damage range
                    enemy.take_damage(25)  # Example damage value

                    # Apply knockback to the enemy
                    knockback_vector = (enemy_position - player_position).normalize() * TILE_SIZE
                    enemy.rect.x += knockback_vector.x
                    enemy.rect.y += knockback_vector.y

                    # Check for collisions with other enemies after knockback
                    for other_enemy in enemies:
                        if other_enemy != enemy and enemy.rect.colliderect(other_enemy.rect):
                            # If there is a collision, adjust the position to avoid overlap
                            overlap_vector = pygame.Vector2(enemy.rect.center) - pygame.Vector2(other_enemy.rect.center)
                            if overlap_vector.length() > 0:  # Avoid division by zero
                                overlap_vector.normalize_ip()
                                enemy.rect.x += overlap_vector.x * TILE_SIZE
                                enemy.rect.y += overlap_vector.y * TILE_SIZE

                    # If enemy's health is <= 0, mark it for removal and grant XP
                    if enemy.health <= 0:
                        enemies_to_remove.append(enemy)
                        self.gain_xp(50)  # Grant XP for killing the enemy

            # Remove the dead enemies from the main enemy list
            for enemy in enemies_to_remove:
                enemies.remove(enemy)

            self.last_teleport_time = current_time  # Update the last teleport time
            print("Teleport attack successful")
    
    def play_teleport_animation(self, screen, camera_offset, original_position):
        """Play the teleport animation at the given position."""
        teleport_images = [
            #pygame.transform.scale(pygame.image.load('assets/teleport.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pygame.transform.scale(pygame.image.load('assets/teleport2.png').convert_alpha(), (TILE_SIZE, TILE_SIZE)),
            pygame.transform.scale(pygame.image.load('assets/teleport3.png').convert_alpha(), (TILE_SIZE, TILE_SIZE))
        ]

        # Calculate the position for the animation (center it on the original position)
        screen_x = original_position[0] - camera_offset[0]
        screen_y = original_position[1] - camera_offset[1]

        # Loop through each frame and display it with a slight delay
        for image in teleport_images:
            screen.blit(image, (screen_x, screen_y))
            pygame.display.flip()  # Update the display
            pygame.time.delay(100)  # Delay for 100 milliseconds per frame

    def update_aim_direction(self, keys):
        direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_LEFT]:
            direction.x = -1
        if keys[pygame.K_RIGHT]:
            direction.x = 1
        if keys[pygame.K_UP]:
            direction.y = -1
        if keys[pygame.K_DOWN]:
            direction.y = 1

        if direction.length() > 0:
            direction.normalize_ip()
            self.aim_direction = direction

    def check_collision(self, new_pos, walls, enemies):
        """Check for collisions with walls or enemies at the new position."""
        future_rect = pygame.Rect(new_pos, (self.size, self.size))

        # Check collision with walls
        for wall in walls:
            if future_rect.colliderect(wall):
                return True

        # Check collision with enemies
        for enemy in enemies:
            if future_rect.colliderect(enemy.rect):
                return True

        return False

    def draw(self, screen, camera_offset):
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))
        self.draw_health_and_mana(screen)
        self.draw_xp_text(screen)
        self.draw_level_text(screen)
        self.draw_aim_arrow(screen, camera_offset)
        if self.is_placing_lightning:
            self.lightning_strike.draw(screen, camera_offset)

    def draw_health_and_mana(self, screen):
        base_bar_width = 200
        bar_height = 20

        health_bar_width = int(base_bar_width * (self.max_health / 100))
        mana_bar_width = int(base_bar_width * (self.max_mana / 100))

        pygame.draw.rect(screen, (255, 0, 0), (10, 10, int(health_bar_width * (self.health / self.max_health)), bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, health_bar_width, bar_height), 2)

        pygame.draw.rect(screen, (0, 0, 255), (10, 40, int(mana_bar_width * (self.mana / self.max_mana)), bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (10, 40, mana_bar_width, bar_height), 2)

    def draw_xp_text(self, screen):
        xp_text = f"XP: {self.xp} / {self.xp_for_next_level}"
        xp_surface = self.font.render(xp_text, True, (0, 0, 0))
        screen.blit(xp_surface, (10, 70))

    def draw_level_text(self, screen):
        level_text = f"Level: {self.level}"
        level_surface = self.font.render(level_text, True, (0, 0, 0))
        screen.blit(level_surface, (10, 100))

    def draw_aim_arrow(self, screen, camera_offset):
        arrow_length = 30
        arrowhead_size = 10

        start_pos = (
            self.rect.centerx - camera_offset[0] + self.aim_direction.x * (self.rect.width // 2 + 2),
            self.rect.centery - camera_offset[1] + self.aim_direction.y * (self.rect.height // 2 + 2)
        )
        end_pos = (
            start_pos[0] + self.aim_direction.x * arrow_length,
            start_pos[1] + self.aim_direction.y * arrow_length
        )

        if self.aim_direction.length() > 0:
            arrowhead_points = [
                (end_pos[0] + arrowhead_size * self.aim_direction.rotate(135).x, end_pos[1] + arrowhead_size * self.aim_direction.rotate(135).y),
                (end_pos[0] + arrowhead_size * self.aim_direction.rotate(-135).x, end_pos[1] + arrowhead_size * self.aim_direction.rotate(-135).y)
            ]
            pygame.draw.polygon(screen, (0, 0, 0), [end_pos] + arrowhead_points)

    def melee_attack(self, enemies, dungeon):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            melee_attack = MeleeAttack(self.rect, self.aim_direction)  # Pass aim direction
            kills = melee_attack.check_collision(enemies, dungeon)
            if kills > 0:
                self.gain_xp(50 * kills)
            self.melee_attack_object = melee_attack  # Store the melee attack object
            return melee_attack

    def ranged_attack(self, projectiles, screen_width, screen_height):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown and self.mana >= 10:
            projectile = Projectile(
                self.rect.centerx, 
                self.rect.centery, 
                self.aim_direction, 
                screen_width, 
                screen_height
            )
            projectiles.append(projectile)
            self.use_mana(10)
            self.last_attack_time = current_time
    
    def fireball_attack(self, projectiles, screen_width, screen_height):
        current_time = pygame.time.get_ticks()
        fireball_mana_cost = 20  # Adjust mana cost for the fireball

        if current_time - self.last_attack_time >= self.attack_cooldown and self.mana >= fireball_mana_cost:
            fireball = Fireball(
                self.rect.centerx, 
                self.rect.centery, 
                self.aim_direction, 
                screen_width, 
                screen_height
            )
            projectiles.append(fireball)
            self.use_mana(fireball_mana_cost)
            self.last_attack_time = current_time
    
    def unlock_fireball(self):
        self.fireball_unlocked = True
        
    def start_lightning_strike(self, screen_width, screen_height):
        """Initialize lightning strike mode and freeze player movement."""
        lightning_strike_mana_cost = 30  # Set the mana cost for lightning strike

        # Check if player has enough mana
        if self.mana >= lightning_strike_mana_cost:
            self.is_placing_lightning = True
            # Start lightning strike at the player's position initially
            self.lightning_strike = LightningStrike(self.rect.centerx, self.rect.centery, screen_width, screen_height)
            self.use_mana(lightning_strike_mana_cost)  # Deduct mana
        else:
            print("Not enough mana to use Lightning Strike!")

    def confirm_lightning_strike(self, enemies, screen, camera_offset): 
        """Confirm the lightning strike, damage enemies, and exit lightning mode."""
        if self.lightning_strike:
            # Play the animation where the circle is
            self.play_lightning_animation(screen, camera_offset)
            struck_enemies = self.lightning_strike.check_enemies_in_range(enemies, self)
            print(f"Lightning Strike hit {struck_enemies} enemies!")
        self.is_placing_lightning = False
        self.lightning_strike = None
    
    def play_lightning_animation(self, screen, camera_offset):
        """Play the 4-part lightning strike animation in quick succession."""
        lightning_images = [
            pygame.transform.scale(pygame.image.load('assets/lightning.png').convert_alpha(), (TILE_SIZE * 4, TILE_SIZE * 4)),
            pygame.transform.scale(pygame.image.load('assets/lightning2.png').convert_alpha(), (TILE_SIZE * 4, TILE_SIZE * 4)),
            pygame.transform.scale(pygame.image.load('assets/lightning3.png').convert_alpha(), (TILE_SIZE * 4, TILE_SIZE * 4)),
            pygame.transform.scale(pygame.image.load('assets/lightning4.png').convert_alpha(), (TILE_SIZE * 4, TILE_SIZE * 4))
        ]

        # Calculate the position where the animation should play (center it on the lightning strike target)
        screen_x = self.lightning_strike.target_position.x - camera_offset[0] - (TILE_SIZE * 2)  # Centering the image
        screen_y = self.lightning_strike.target_position.y - camera_offset[1] - (TILE_SIZE * 2)  # Centering the image

        # Loop through each frame and display it with a slight delay
        for image in lightning_images:
            screen.blit(image, (screen_x, screen_y))
            pygame.display.flip()  # Update the display
            pygame.time.delay(100)

    def move_lightning_strike_target(self, direction):
        """Move the lightning strike targeting circle if in lightning strike mode."""
        if self.is_placing_lightning and self.lightning_strike:
            self.lightning_strike.move(direction)

    def unlock_lightning_strike(self):
        """Unlock the Lightning Strike ability."""
        self.lightning_unlocked = True
        print("Lightning Strike unlocked!")
        
    def unlock_teleport_attack(self):
        """Unlock the Teleport Attack ability."""
        self.teleport_attack_unlocked = True
        print("Teleport attack unlocked!")
        
    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_for_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= self.xp_for_next_level
        self.xp_for_next_level *= 1.5
        self.points += 3  # Add 3 points on level up
        print(f"Level up! You are now level {self.level}")
        print(f"You have {self.points} points to spend.")

        self.health = self.max_health
        self.mana = self.max_mana
        print("Health and mana refilled!")

    def increase_max_health(self, amount):
        self.max_health += amount
        self.health += amount
        print(f"Max health increased to {self.max_health}!")

    def increase_max_mana(self, amount):
        self.max_mana += amount
        self.mana += amount 
        print(f"Max mana increased to {self.max_mana}!")
        
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.die()
    
    def die(self):
        """Trigger player death."""
        print("Player died!")
        self.is_dead = True  # Set player to dead state

    def reset(self, x, y, inventory):
        """Reset player to initial state when restarting the game."""
        self.rect.topleft = (x, y)
        self.max_health = 100
        self.health = self.max_health
        self.max_mana = 50
        self.mana = self.max_mana
        self.xp = 0
        self.xp_for_next_level = 100
        self.level = 1
        self.points = 0
        self.is_dead = False
        self.fireball_unlocked = False
        self.lightning_unlocked = False
        self.teleport_attack_unlocked = False
        self.is_placing_lightning = False
        self.last_attack_time = pygame.time.get_ticks()
        self.last_teleport_time = pygame.time.get_ticks()
        print("Game restarted! Player state reset.")
        # Refresh inventory to reflect reset state
        inventory.update_inventory(self)

    def use_mana(self, amount):
        self.mana = max(0, self.mana - amount)

    def restore_health(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def restore_mana(self, amount):
        self.mana = min(self.max_mana, self.mana + amount)