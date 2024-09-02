import pygame

class Inventory:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font = pygame.font.SysFont(None, 74)
        self.is_open = False
        self.player_points = 0  # Variable to store player points

    def draw(self, screen):
        inventory_background = pygame.Surface((self.screen_width, self.screen_height))
        inventory_background.fill((50, 50, 50))
        
        text_surface = self.font.render("Inventory Screen", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        
        points_surface = self.font.render(f"Points: {self.player_points}", True, (255, 255, 255))
        points_rect = points_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))

        screen.blit(inventory_background, (0, 0))
        screen.blit(text_surface, text_rect)
        screen.blit(points_surface, points_rect)
        pygame.display.flip()

    def toggle(self):
        self.is_open = not self.is_open

    def update_points(self, points):
        self.player_points = points
