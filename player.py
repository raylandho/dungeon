import pygame
from settings import PLAYER_SIZE, TILE_SIZE
from projectile import Projectile, MeleeAttack

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
        self.attack_cooldown = 500  # Cooldown for attacks
        self.last_attack_time = pygame.time.get_ticks()
        self.aim_direction = pygame.math.Vector2(1, 0)
        self.font = pygame.font.SysFont(None, 24)

    def handle_movement(self, keys, walls, dungeon_width, dungeon_height):
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

        # Check collisions
        if not self.check_collision((new_x, new_y), walls):
            self.rect.topleft = (new_x, new_y)

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

    def check_collision(self, new_pos, walls):
        future_rect = pygame.Rect(new_pos, (self.size, self.size))
        for wall in walls:
            if future_rect.colliderect(wall):
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

    def draw(self, screen, camera_offset):
        screen_x = self.rect.x - camera_offset[0]
        screen_y = self.rect.y - camera_offset[1]
        screen.blit(self.image, (screen_x, screen_y))
        self.draw_health_and_mana(screen)
        self.draw_xp_text(screen)
        self.draw_level_text(screen)
        self.draw_aim_arrow(screen, camera_offset)

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
        xp_surface = self.font.render(xp_text, True, (255, 255, 255))
        screen.blit(xp_surface, (10, 70))

    def draw_level_text(self, screen):
        level_text = f"Level: {self.level}"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
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
            pygame.draw.polygon(screen, (255, 255, 255), [end_pos] + arrowhead_points)

    def melee_attack(self, enemies):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            melee_attack = MeleeAttack(self.rect)
            kills = melee_attack.check_collision(enemies)
            if kills > 0:
                self.gain_xp(50 * kills)

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

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def use_mana(self, amount):
        self.mana = max(0, self.mana - amount)

    def restore_health(self, amount):
        self.health = min(self.max_health, self.health + amount)

    def restore_mana(self, amount):
        self.mana = min(self.max_mana, self.mana + amount)
