import pygame
import random
from settings import TILE_SIZE

class Dungeon:
    def __init__(self, width_in_tiles, height_in_tiles):
        self.tiles_x = width_in_tiles
        self.tiles_y = height_in_tiles
        self.tile_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tile_image.fill((139, 69, 19))  # Brown tiles for walls
        self.font = pygame.font.SysFont(None, 24)  # Font for rendering numbers
        self.layout = self.generate_dungeon()

    def generate_dungeon(self):
        # Create an open layout with walkable space ('0') and walls ('1')
        layout = [['0' for _ in range(self.tiles_x)] for _ in range(self.tiles_y)]
        
        # Add predefined shapes and DFS structures
        self.add_structures(layout)
        self.add_dfs_structures(layout)

        return layout

    def add_structures(self, layout):
        # Define some predefined shapes
        shapes = [
            # Long horizontal wall
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],

            # Long vertical wall
            [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],

            # L-shape
            [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)],

            # U-shape
            [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)],

            # Helix shape
            [(0, 0), (1, 0), (2, 0), (2, 1), (1, 1), (1, 2), (2, 2)]
        ]

        # Add a few smaller structures
        num_structures = random.randint(15, 20)
        for _ in range(num_structures):
            shape = random.choice(shapes)
            width = max(x for x, y in shape) + 1
            height = max(y for x, y in shape) + 1
            x = random.randint(0, self.tiles_x - width - 1)
            y = random.randint(0, self.tiles_y - height - 1)

            for dx, dy in shape:
                layout[y + dy][x + dx] = '1'

    def add_dfs_structures(self, layout):
        num_structures = random.randint(8, 12)
        for _ in range(num_structures):
            start_x = random.randint(1, self.tiles_x - 2)
            start_y = random.randint(1, self.tiles_y - 2)
            self.dfs_structure(layout, start_x, start_y, depth_limit=10)
            
    def dfs_structure(self, layout, x, y, depth_limit):
        stack = [(x, y, 0)]
        layout[y][x] = '1'

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while stack:
            cx, cy, depth = stack[-1]
            random.shuffle(directions)  # Randomize the direction order
            moved = False

            for dx, dy in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.tiles_x and 0 <= ny < self.tiles_y and layout[ny][nx] == '0':
                    if depth < depth_limit:  # Limit the depth of the DFS
                        layout[ny][nx] = '1'
                        stack.append((nx, ny, depth + 1))
                        moved = True
                        break

            if not moved:
                stack.pop()  # Backtrack if no movement is possible

    def clear_spawn_area(self, layout, x, y):
        """Ensure that the spawn area is clear."""
        if 0 <= x < self.tiles_x and 0 <= y < self.tiles_y:
            layout[y][x] = '0'
            if x + 1 < self.tiles_x:
                layout[y][x + 1] = '0'
            if y + 1 < self.tiles_y:
                layout[y + 1][x] = '0'
                if x + 1 < self.tiles_x:
                    layout[y + 1][x + 1] = '0'

    def get_walls(self):
        walls = []
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                if tile == "1":
                    wall_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    walls.append(wall_rect)
        return walls

    def get_random_open_position(self):
        """Return a random open position (i.e., '0') in the dungeon."""
        while True:
            x = random.randint(1, self.tiles_x - 2)
            y = random.randint(1, self.tiles_y - 2)
            if self.layout[y][x] == '0':  # Ensure the tile is walkable
                return x * TILE_SIZE, y * TILE_SIZE

    def draw(self, screen, camera_offset):
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                screen_x = col_index * TILE_SIZE - camera_offset[0]
                screen_y = row_index * TILE_SIZE - camera_offset[1]

                if tile == "1":
                    screen.blit(self.tile_image, (screen_x, screen_y))
                
                # Render the tile's value (0 or 1) on top of the tile
                text_surface = self.font.render(tile, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(screen_x + TILE_SIZE // 2, screen_y + TILE_SIZE // 2))
                screen.blit(text_surface, text_rect)