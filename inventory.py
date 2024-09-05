import pygame

class Inventory:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.inventory_width = int(screen_width * 0.6)
        self.inventory_height = int(screen_height * 0.6)
        self.inventory_x = (screen_width - self.inventory_width) // 2
        self.inventory_y = (screen_height - self.inventory_height) // 2
        self.font = pygame.font.SysFont(None, 24)
        self.is_open = False
        self.unlocked_attacks = {
            "Projectile Attack": True,
            "Melee Attack": True,
            "Fireball": False,
            "Teleport Attack": False,
            "Lightning Strike": False,
        }
        self.attack_costs = {
            "Projectile Attack": 0,
            "Melee Attack": 0,
            "Fireball": 3,
            "Teleport Attack": 5,
            "Lightning Strike": 4,
            "Increase Max Health": 1,
            "Increase Max Mana": 1,
        }
        self.selected_attack_index = 0

    def draw(self, screen, player):
        inventory_background = pygame.Surface((self.inventory_width, self.inventory_height))
        inventory_background.fill((50, 50, 50))
        
        text_surface = self.font.render("Inventory Screen", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.inventory_width // 2, 30))
        screen.blit(inventory_background, (self.inventory_x, self.inventory_y))
        screen.blit(text_surface, (self.inventory_x + text_rect.x, self.inventory_y + text_rect.y))

        points_surface = self.font.render(f"Points: {player.points}", True, (255, 255, 255))
        points_rect = points_surface.get_rect(center=(self.inventory_width // 2, 60))
        screen.blit(points_surface, (self.inventory_x + points_rect.x, self.inventory_y + points_rect.y))

        for idx, (attack, unlocked) in enumerate(self.unlocked_attacks.items()):
            attack_text = f"{attack} - {'Unlocked' if unlocked else f'Cost: {self.attack_costs[attack]}'}"
            attack_surface = self.font.render(attack_text, True, (0, 255, 0) if unlocked else (255, 0, 0))
            attack_rect = attack_surface.get_rect(left=self.inventory_x + 40, top=self.inventory_y + 100 + idx * 40)
            screen.blit(attack_surface, attack_rect)

            if idx == self.selected_attack_index:
                arrow_surface = self.font.render("->", True, (255, 255, 255))
                arrow_rect = arrow_surface.get_rect(right=self.inventory_x + 30, top=self.inventory_y + 100 + idx * 40)
                screen.blit(arrow_surface, arrow_rect)
        
        # Draw the health and mana upgrade options at the bottom
        health_upgrade_text = f"Increase Max Health - Cost: {self.attack_costs['Increase Max Health']}"
        health_upgrade_surface = self.font.render(health_upgrade_text, True, (255, 255, 0))
        health_upgrade_rect = health_upgrade_surface.get_rect(left=self.inventory_x + 40, top=self.inventory_y + 100 + len(self.unlocked_attacks) * 40)
        screen.blit(health_upgrade_surface, health_upgrade_rect)

        if self.selected_attack_index == len(self.unlocked_attacks):
            arrow_surface = self.font.render("->", True, (255, 255, 255))
            arrow_rect = arrow_surface.get_rect(right=self.inventory_x + 30, top=health_upgrade_rect.top)
            screen.blit(arrow_surface, arrow_rect)

        mana_upgrade_text = f"Increase Max Mana - Cost: {self.attack_costs['Increase Max Mana']}"
        mana_upgrade_surface = self.font.render(mana_upgrade_text, True, (255, 255, 0))
        mana_upgrade_rect = mana_upgrade_surface.get_rect(left=self.inventory_x + 40, top=self.inventory_y + 100 + (len(self.unlocked_attacks) + 1) * 40)
        screen.blit(mana_upgrade_surface, mana_upgrade_rect)

        if self.selected_attack_index == len(self.unlocked_attacks) + 1:
            arrow_surface = self.font.render("->", True, (255, 255, 255))
            arrow_rect = arrow_surface.get_rect(right=self.inventory_x + 30, top=mana_upgrade_rect.top)
            screen.blit(arrow_surface, arrow_rect)

        pygame.display.flip()

    def toggle(self):
        self.is_open = not self.is_open

    def unlock_attack(self, player):
        selected_attack = list(self.unlocked_attacks.keys())[self.selected_attack_index] if self.selected_attack_index < len(self.unlocked_attacks) else None
        
        if selected_attack:
            if selected_attack in self.unlocked_attacks and not self.unlocked_attacks[selected_attack]:
                cost = self.attack_costs[selected_attack]
                if player.points >= cost:
                    self.unlocked_attacks[selected_attack] = True
                    player.points -= cost
                    print(f"{selected_attack} unlocked!")
                    if selected_attack == "Fireball":
                        player.unlock_fireball()
                else:
                    print("Not enough points to unlock this attack.")
            else:
                print("Attack already unlocked or does not exist.")
        else:
            # Handle health or mana upgrade
            if self.selected_attack_index == len(self.unlocked_attacks):
                cost = self.attack_costs['Increase Max Health']
                if player.points >= cost:
                    player.increase_max_health(20)
                    player.points -= cost
                    print(f"Max health increased to {player.max_health}!")
                else:
                    print("Not enough points to increase health.")
            elif self.selected_attack_index == len(self.unlocked_attacks) + 1:
                cost = self.attack_costs['Increase Max Mana']
                if player.points >= cost:
                    player.increase_max_mana(10)
                    player.points -= cost
                    print(f"Max mana increased to {player.max_mana}!")
                else:
                    print("Not enough points to increase mana.")

    def move_selection_up(self):
        if self.selected_attack_index > 0:
            self.selected_attack_index -= 1

    def move_selection_down(self):
        if self.selected_attack_index < len(self.unlocked_attacks) + 1:  # +1 for the health and mana upgrades
            self.selected_attack_index += 1