import pygame
import random
from settings import TILE_SIZE

class Dungeon:
    def __init__(self, screen_width, screen_height):
        self.tiles_x = screen_width // TILE_SIZE
        self.tiles_y = screen_height // TILE_SIZE
        self.tile_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tile_image.fill((139, 69, 19))  # Brown tiles for walls
        self.exit_image = pygame.Surface((TILE_SIZE, TILE_SIZE))  # Make exit image 1 tile wide
        self.exit_image.fill((0, 0, 255))  # Blue tiles for exits
        self.font = pygame.font.SysFont(None, 24)  # Font for rendering numbers
        self.layout = self.generate_dungeon()

    def generate_dungeon(self):
        # Create a simple rectangular layout with walls ('1') and open space ('0')
        layout = [['0' for _ in range(self.tiles_x)] for _ in range(self.tiles_y)]
        
        # Add outer walls
        for i in range(self.tiles_x):
            layout[0][i] = '1'  # Top wall
            layout[self.tiles_y - 1][i] = '1'  # Bottom wall
        for i in range(self.tiles_y):
            layout[i][0] = '1'  # Left wall
            layout[i][self.tiles_x - 1] = '1'  # Right wall

        # Add some random internal walls
        for _ in range(10):  # You can adjust the number of internal walls
            x = random.randint(1, self.tiles_x - 2)
            y = random.randint(1, self.tiles_y - 2)
            layout[y][x] = '1'

        # Add exits on the outer walls
        self.add_exits(layout)

        return layout

    def add_exits(self, layout):
        # Add 2 random exits in the outer walls
        exits = []
        while len(exits) < 2:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                x = random.randint(1, self.tiles_x - 3)
                layout[0][x:x+2] = '2' * 2
                exits.append((0, x))
            elif side == 'bottom':
                x = random.randint(1, self.tiles_x - 3)
                layout[self.tiles_y - 1][x:x+2] = '2' * 2
                exits.append((self.tiles_y - 1, x))
            elif side == 'left':
                y = random.randint(1, self.tiles_y - 3)
                layout[y][0] = '2'
                layout[y+1][0] = '2'
                exits.append((y, 0))
            elif side == 'right':
                y = random.randint(1, self.tiles_y - 3)
                layout[y][self.tiles_x - 1] = '2'
                layout[y+1][self.tiles_x - 1] = '2'
                exits.append((y, self.tiles_x - 1))

    def clear_spawn_area(self, layout, x, y):
        """Ensure that the spawn area near an exit is clear."""
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

    def get_exit_positions(self):
        exits = []
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                if tile == "2":
                    exits.append((col_index * TILE_SIZE, row_index * TILE_SIZE))
        return exits

    def get_random_open_position(self):
        """Return a random open position (i.e., '0') in the dungeon."""
        while True:
            x = random.randint(1, self.tiles_x - 2)
            y = random.randint(1, self.tiles_y - 2)
            if self.layout[y][x] == '0':  # Ensure the tile is walkable
                return x * TILE_SIZE, y * TILE_SIZE

    def draw(self, screen):
        for row_index, row in enumerate(self.layout):
            for col_index, tile in enumerate(row):
                if tile == "1":
                    screen.blit(self.tile_image, (col_index * TILE_SIZE, row_index * TILE_SIZE))
                elif tile == "2":
                    screen.blit(self.exit_image, (col_index * TILE_SIZE, row_index * TILE_SIZE))

                # Optional: Uncomment the following lines to render tile numbers (0, 1, or 2) on top of the tiles
                # text_surface = self.font.render(tile, True, (255, 255, 255))
                # text_rect = text_surface.get_rect(center=(col_index * TILE_SIZE + TILE_SIZE // 2, row_index * TILE_SIZE + TILE_SIZE // 2))
                # screen.blit(text_surface, text_rect)
