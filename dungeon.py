# dungeon.py

import pygame
from settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Dungeon:
    def __init__(self):
        self.tiles_x = SCREEN_WIDTH // TILE_SIZE
        self.tiles_y = SCREEN_HEIGHT // TILE_SIZE
        self.tile_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tile_image.fill((255, 255, 255))  # White tiles
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
                    screen.blit(self.tile_image, (col_index * TILE_SIZE, row_index * TILE_SIZE))
