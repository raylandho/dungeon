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
            "Fireball": 5,
            "Teleport Attack": 2,
            "Lightning Strike": 4,
            "Increase Max Health": 1,
            "Increase Max Mana": 1,
        }
        self.keybindings = {
            "Melee Attack": pygame.K_SPACE,
            "Ranged Attack": pygame.K_r,
            "Fireball": pygame.K_f,
            "Teleport": pygame.K_t,
            "Lightning Strike": pygame.K_l
        }
        self.selected_attack_index = 0
        self.rebinding_mode = False  # Track if in rebinding mode
        self.selected_keybind = None  # Track which keybind is being changed

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

        # Draw attacks
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

        # Draw keybindings
        keybinding_start_y = mana_upgrade_rect.bottom + 40
        for idx, (action, key) in enumerate(self.keybindings.items()):
            key_text = f"{action}: {pygame.key.name(key)}"
            key_surface = self.font.render(key_text, True, (255, 255, 255))
            key_rect = key_surface.get_rect(left=self.inventory_x + 40, top=keybinding_start_y + idx * 40)
            screen.blit(key_surface, key_rect)

            if self.selected_attack_index == len(self.unlocked_attacks) + 2 + idx:
                arrow_surface = self.font.render("->", True, (255, 255, 255))
                arrow_rect = arrow_surface.get_rect(right=self.inventory_x + 30, top=keybinding_start_y + idx * 40)
                screen.blit(arrow_surface, arrow_rect)

        pygame.display.flip()

    def toggle(self):
        self.is_open = not self.is_open

    def move_selection_up(self):
        if self.selected_attack_index > 0:
            self.selected_attack_index -= 1

    def move_selection_down(self):
        max_selection_index = len(self.unlocked_attacks) + 1 + len(self.keybindings) + 1
        if self.selected_attack_index < max_selection_index - 1:  # Adjust max index to prevent overflow
            self.selected_attack_index += 1

    def select(self, player):
        """Handle selecting an attack to unlock or entering keybinding mode."""
        if self.selected_attack_index < len(self.unlocked_attacks):
            # Unlocking attacks
            selected_attack = list(self.unlocked_attacks.keys())[self.selected_attack_index]
            cost = self.attack_costs[selected_attack]
            
            if not self.unlocked_attacks[selected_attack] and player.points >= cost:
                self.unlocked_attacks[selected_attack] = True
                player.points -= cost
                print(f"{selected_attack} unlocked!")

                # Call specific methods to unlock player abilities
                if selected_attack == "Fireball":
                    player.unlock_fireball()
                elif selected_attack == "Lightning Strike":
                    player.unlock_lightning_strike()
                elif selected_attack == "Teleport Attack":
                    player.unlock_teleport_attack()
                    
        elif self.selected_attack_index == len(self.unlocked_attacks):
            # Increase health
            cost = self.attack_costs["Increase Max Health"]
            if player.points >= cost:
                player.increase_max_health(20)
                player.points -= cost
                print(f"Max health increased to {player.max_health}!")
        elif self.selected_attack_index == len(self.unlocked_attacks) + 1:
            # Increase mana
            cost = self.attack_costs["Increase Max Mana"]
            if player.points >= cost:
                player.increase_max_mana(10)
                player.points -= cost
                print(f"Max mana increased to {player.max_mana}!")
        else:
            # Keybinding mode
            keybind_index = self.selected_attack_index - (len(self.unlocked_attacks) + 2)
            if keybind_index >= 0 and keybind_index < len(self.keybindings):
                action = list(self.keybindings.keys())[keybind_index]
                self.start_rebinding(action)

    def start_rebinding(self, action):
        """Start rebinding the key for a specific action."""
        self.rebinding_mode = True
        self.selected_keybind = action
        print(f"Press a new key for {action}")

    def process_keybinding(self, event):
        """Rebind the selected key when the user presses a key."""
        if self.rebinding_mode and self.selected_keybind:
            self.keybindings[self.selected_keybind] = event.key
            print(f"Rebound {self.selected_keybind} to {pygame.key.name(event.key)}")
            self.rebinding_mode = False
            self.selected_keybind = None

    def update_inventory(self, player):
        """Update inventory UI based on player's current abilities and stats."""
        self.unlocked_attacks["Fireball"] = player.fireball_unlocked
        self.unlocked_attacks["Lightning Strike"] = player.lightning_unlocked
        self.unlocked_attacks["Teleport Attack"] = player.teleport_attack_unlocked
        self.points = player.points
        print("Inventory updated after respawn.")
