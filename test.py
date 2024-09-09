import pygame
from settings import TILE_SIZE

ground_tile_image = pygame.image.load("assets/dirt2.png")
image_width, image_height = ground_tile_image.get_size()
print(f"Ground tile image size: {image_width}x{image_height}")

ground_tile_image = pygame.transform.scale(ground_tile_image, (TILE_SIZE, TILE_SIZE))
print(f"Ground tile image size after scaling: {ground_tile_image.get_size()}")