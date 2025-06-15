import vnoise
import numpy as np
import pygame
import random

from config import LAND_COLORS, TILE_SIZE, WINDOW_X, WINDOW_Y, FPS


noise = vnoise.Noise(seed=random.random())

def get_perlin_grid(w, h, scale=40):
    grid = np.zeros((h, w), dtype=int)
    for y in range(h):
        for x in range(w):
            n = noise.noise2(x / scale, y / scale)
            frequency = 1.0
            amplitude = 1.0
            offset_x = 25
            offset_y = 15
            for _ in range(4):  # 4 octaves
                n += amplitude * noise.noise2((x+offset_x) * frequency / scale, (y+offset_y) * frequency / scale)
                frequency *= 2
                amplitude *= 0.5
            if n < -0.5:
                grid[y][x] = 999
            elif n < -0.3:
                grid[y][x] = 4
            elif n < 0:
                grid[y][x] = 2
            else:
                grid[y][x] = 1
    return grid.tolist()


# Pygame setup
pygame.init()
pygame.display.set_caption('Mai multi serpisori genetici')
window = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
fps = pygame.time.Clock()

# Generate terrain grid
terrain_grid = get_perlin_grid(WINDOW_X // TILE_SIZE + 11, 
                               WINDOW_Y // TILE_SIZE + 99)

# Draw grid
for y in range(WINDOW_Y // TILE_SIZE):
    for x in range(WINDOW_X // TILE_SIZE):
        color = LAND_COLORS[terrain_grid[y][x]]
        pygame.draw.rect(window, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    fps.tick(FPS)

pygame.quit()