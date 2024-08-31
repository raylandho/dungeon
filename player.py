import pygame
from settings import PLAYER_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from projectile import Projectile, MeleeAttack

class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill((0, 255, 0))  # Green player
        self.rect = self.image.get_rect(topleft=(x, y))
        self.max_health = 100  # Store max health for refilling purposes
        self.health = self.max_health  # Current health
        self.max_mana = 50  # Store max mana for refilling purposes
        self.mana = self.max_mana  # Current mana
        self.xp = 0        # Start with 0 XP
        self.xp_for_next_level = 100  # XP required for the next level
        self.level = 1     # Start at level 1
        self.attack_cooldown = 500  # 500ms cooldown for melee attacks
        self.last_attack_time = pygame.time.get_ticks()
        self.projectile_cooldown = 1000  # 1000ms cooldown for ranged attacks
        self.last_projectile_time = pygame.time.get_ticks()
        self.aim_direction = pygame.math.Vector2(1, 0)  # Default aim direction (right)
        self.font = pygame.font.SysFont(None, 24)  # Font for rendering text

    def handle_movement(self, keys, walls):
        new_pos = self.rect.topleft

        if keys[pygame.K_LEFT]:
            new_pos = (new_pos[0] - 5, new_pos[1])
        if keys[pygame.K_RIGHT]:
            new_pos = (new_pos[0] + 5, new_pos[1])
        if keys[pygame.K_UP]:
            new_pos = (new_pos[0], new_pos[1] - 5)
        if keys[pygame.K_DOWN]:
            new_pos = (new_pos[0], new_pos[1] + 5)

        if not self.check_collision(new_pos, walls):
            self.rect.topleft = new_pos

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
        future_rect = pygame.Rect(new_pos, (PLAYER_SIZE, PLAYER_SIZE))
        for wall in walls:
            if future_rect.colliderect(wall):
                return True
        return False

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        self.draw_health_and_mana(screen)
        self.draw_xp_text(screen)
        self.draw_level_text(screen)  # Draw player level
        self.draw_aim_arrow(screen)

    def draw_health_and_mana(self, screen):
        """Draw the player's health and mana bars on the screen, scaling the outlines."""
        base_bar_width = 200  # Base width for the bars
        bar_height = 20       # Height for all bars

        # Calculate widths based on max values
        health_bar_width = int(base_bar_width * (self.max_health / 100))
        mana_bar_width = int(base_bar_width * (self.max_mana / 100))

        # Health bar
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, int(health_bar_width * (self.health / self.max_health)), bar_height))  # Red bar
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, health_bar_width, bar_height), 2)  # White border

        # Mana bar
        pygame.draw.rect(screen, (0, 0, 255), (10, 40, int(mana_bar_width * (self.mana / self.max_mana)), bar_height))  # Blue bar
        pygame.draw.rect(screen, (255, 255, 255), (10, 40, mana_bar_width, bar_height), 2)  # White border

    def draw_xp_text(self, screen):
        """Draw the current XP and XP needed for the next level as text."""
        xp_text = f"XP: {self.xp} / {self.xp_for_next_level}"
        xp_surface = self.font.render(xp_text, True, (255, 255, 255))
        screen.blit(xp_surface, (10, 70))  # Position the text below the health and mana bars

    def draw_level_text(self, screen):
        """Draw the player's current level as text."""
        level_text = f"Level: {self.level}"
        level_surface = self.font.render(level_text, True, (255, 255, 255))
        screen.blit(level_surface, (10, 100))  # Position the text below the XP text

    def draw_aim_arrow(self, screen):
        """Draw an arrow pointing in the current aim direction."""
        arrow_length = 30  # Increase the length of the arrow
        arrowhead_size = 10  # Size of the arrowhead

        start_pos = self.rect.center
        end_pos = (
            start_pos[0] + self.aim_direction.x * arrow_length,
            start_pos[1] + self.aim_direction.y * arrow_length
        )

        # Draw arrowhead
        if self.aim_direction.length() > 0:
            angle = self.aim_direction.angle_to(pygame.Vector2(1, 0))
            arrowhead_points = [
                (end_pos[0] + arrowhead_size * self.aim_direction.rotate(135).x, end_pos[1] + arrowhead_size * self.aim_direction.rotate(135).y),
                (end_pos[0] + arrowhead_size * self.aim_direction.rotate(-135).x, end_pos[1] + arrowhead_size * self.aim_direction.rotate(-135).y)
            ]
            pygame.draw.polygon(screen, (255, 255, 255), [end_pos] + arrowhead_points)

    def melee_attack(self, enemies):
        """Perform a melee attack on enemies within range."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            melee_attack = MeleeAttack(self.rect)
            kills = melee_attack.check_collision(enemies)  # Check for collisions and count kills
            if kills > 0:
                self.gain_xp(50 * kills)  # Award XP for each kill (adjust XP per kill as needed)

    def ranged_attack(self, projectiles):
        """Shoot a projectile in the direction the player is facing."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_projectile_time >= self.projectile_cooldown and self.mana >= 10:
            projectile = Projectile(self.rect.centerx, self.rect.centery, self.aim_direction)
            projectiles.append(projectile)
            self.use_mana(10)  # Reduce mana
            self.last_projectile_time = current_time  # Update the last projectile time

    def gain_xp(self, amount):
        """Increase the player's XP and handle leveling up."""
        self.xp += amount
        if self.xp >= self.xp_for_next_level:
            self.level_up()

    def level_up(self):
        """Handle leveling up the player."""
        self.level += 1
        self.xp -= self.xp_for_next_level  # Carry over extra XP
        self.xp_for_next_level *= 1.5  # Increase the XP required for the next level
        print(f"Level up! You are now level {self.level}")

        # Refill health and mana
        self.health = self.max_health
        self.mana = self.max_mana
        print("Health and mana refilled!")

    def take_damage(self, amount):
        """Reduce the player's health by a specified amount."""
        self.health = max(0, self.health - amount)

    def use_mana(self, amount):
        """Reduce the player's mana by a specified amount."""
        self.mana = max(0, self.mana - amount)

    def restore_health(self, amount):
        """Increase the player's health by a specified amount."""
        self.health = min(self.max_health, self.health + amount)

    def restore_mana(self, amount):
        """Increase the player's mana by a specified amount."""
        self.mana = min(self.max_mana, self.mana + amount)
