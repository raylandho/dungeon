import pygame
from settings import TILE_SIZE

class Dungeon:
    def __init__(self, screen_width, screen_height):
        self.tiles_x = screen_width // TILE_SIZE
        self.tiles_y = screen_height // TILE_SIZE
        self.tile_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tile_image.fill((0, 0, 0))  # Black tiles for walls
        self.border_color = (255, 255, 255)  # White color for border
        self.border_thickness = 2  # Thickness of the border
        self.layout = self.generate_dungeon()

    def generate_dungeon(self):
        layout = []
        for row in range(self.tiles_y):
            if row == 0 or row == self.tiles_y - 1:
                layout.append("1" * self.tiles_x)  # Top and bottom walls
            else:
                layout.append("1" + "0" * (self.tiles_x - 2) + "1")  # Side walls with open space in the middle
        return layout

    def get_walls(self):
        walls = []
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                if tile == "1":
                    wall_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    walls.append(wall_rect)
        return walls

    def draw(self, screen):
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                if tile == "1":
                    # Draw the wall tile
                    screen.blit(self.tile_image, (col_index * TILE_SIZE, row_index * TILE_SIZE))

                    # Check neighboring tiles to draw borders only on the inner-facing edges
                    # Top edge
                    if row_index > 0 and self.layout[row_index - 1][col_index] == "0":
                        pygame.draw.line(
                            screen,
                            self.border_color,
                            (col_index * TILE_SIZE, row_index * TILE_SIZE),
                            ((col_index + 1) * TILE_SIZE, row_index * TILE_SIZE),
                            self.border_thickness
                        )
                    
                    # Bottom edge
                    if row_index < self.tiles_y - 1 and self.layout[row_index + 1][col_index] == "0":
                        pygame.draw.line(
                            screen,
                            self.border_color,
                            (col_index * TILE_SIZE, (row_index + 1) * TILE_SIZE),
                            ((col_index + 1) * TILE_SIZE, (row_index + 1) * TILE_SIZE),
                            self.border_thickness
                        )
                    
                    # Left edge
                    if col_index > 0 and self.layout[row_index][col_index - 1] == "0":
                        pygame.draw.line(
                            screen,
                            self.border_color,
                            (col_index * TILE_SIZE, row_index * TILE_SIZE),
                            (col_index * TILE_SIZE, (row_index + 1) * TILE_SIZE),
                            self.border_thickness
                        )
                    
                    # Right edge
                    if col_index < self.tiles_x - 1 and self.layout[row_index][col_index + 1] == "0":
                        pygame.draw.line(
                            screen,
                            self.border_color,
                            ((col_index + 1) * TILE_SIZE, row_index * TILE_SIZE),
                            ((col_index + 1) * TILE_SIZE, (row_index + 1) * TILE_SIZE),
                            self.border_thickness
                        )

                    # Handle corners explicitly to ensure no border is drawn
                    if row_index == 0 and col_index == 0:
                        # Top-left corner
                        pass

                    if row_index == 0 and col_index == self.tiles_x - 1:
                        # Top-right corner
                        pass

                    if row_index == self.tiles_y - 1 and col_index == 0:
                        # Bottom-left corner
                        pass

                    if row_index == self.tiles_y - 1 and col_index == self.tiles_x - 1:
                        # Bottom-right corner
                        pass
