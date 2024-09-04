import pygame

class Inventory:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.inventory_width = int(screen_width * 0.6)  # Inventory covers 60% of the screen width
        self.inventory_height = int(screen_height * 0.6)  # Inventory covers 60% of the screen height
        self.inventory_x = (screen_width - self.inventory_width) // 2  # Center horizontally
        self.inventory_y = (screen_height - self.inventory_height) // 2  # Center vertically
        self.font = pygame.font.SysFont(None, 24)
        self.is_open = False
        self.player_points = 0  # Variable to store player points
        self.unlocked_attacks = {
            "Projectile Attack": True,  # Basic attack unlocked by default
            "Melee Attack": True,       # Basic melee unlocked by default
            "Fireball Attack": False,   # Placeholder attack
            "Teleport Attack": False,   # Placeholder for teleport-enhanced attack
            "Lightning Strike": False,  # Placeholder attack
        }
        self.attack_costs = {
            "Projectile Attack": 0,   # Basic attack is free
            "Melee Attack": 0,        # Basic melee is free
            "Fireball Attack": 3,     # Costs 3 points to unlock
            "Teleport Attack": 5,     # Costs 5 points to unlock
            "Lightning Strike": 4,    # Costs 4 points to unlock
        }
        self.selected_attack_index = 0  # Track the current selected skill

    def draw(self, screen):
        inventory_background = pygame.Surface((self.inventory_width, self.inventory_height))
        inventory_background.fill((50, 50, 50))
        
        text_surface = self.font.render("Inventory Screen", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.inventory_width // 2, 30))
        screen.blit(inventory_background, (self.inventory_x, self.inventory_y))
        screen.blit(text_surface, (self.inventory_x + text_rect.x, self.inventory_y + text_rect.y))

        points_surface = self.font.render(f"Points: {self.player_points}", True, (255, 255, 255))
        points_rect = points_surface.get_rect(center=(self.inventory_width // 2, 60))
        screen.blit(points_surface, (self.inventory_x + points_rect.x, self.inventory_y + points_rect.y))

        # Display available attacks with arrow
        for idx, (attack, unlocked) in enumerate(self.unlocked_attacks.items()):
            attack_text = f"{attack} - {'Unlocked' if unlocked else f'Cost: {self.attack_costs[attack]}'}"
            attack_surface = self.font.render(attack_text, True, (0, 255, 0) if unlocked else (255, 0, 0))
            attack_rect = attack_surface.get_rect(left=self.inventory_x + 40, top=self.inventory_y + 100 + idx * 40)
            screen.blit(attack_surface, attack_rect)

            # Draw arrow next to selected attack
            if idx == self.selected_attack_index:
                arrow_surface = self.font.render("->", True, (255, 255, 255))
                arrow_rect = arrow_surface.get_rect(right=self.inventory_x + 30, top=self.inventory_y + 100 + idx * 40)
                screen.blit(arrow_surface, arrow_rect)
        
        pygame.display.flip()

    def toggle(self):
        self.is_open = not self.is_open

    def update_points(self, points):
        self.player_points = points

    def unlock_attack(self):
        # Get the name of the selected attack
        selected_attack = list(self.unlocked_attacks.keys())[self.selected_attack_index]
        if selected_attack in self.unlocked_attacks and not self.unlocked_attacks[selected_attack]:
            cost = self.attack_costs[selected_attack]
            if self.player_points >= cost:
                self.unlocked_attacks[selected_attack] = True
                self.player_points -= cost
                print(f"{selected_attack} unlocked!")
            else:
                print("Not enough points to unlock this attack.")
        else:
            print("Attack already unlocked or does not exist.")

    def move_selection_up(self):
        if self.selected_attack_index > 0:
            self.selected_attack_index -= 1

    def move_selection_down(self):
        if self.selected_attack_index < len(self.unlocked_attacks) - 1:
            self.selected_attack_index += 1
