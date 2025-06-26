import pygame
import numpy as np
import core.config as config
from entities.snake import Snake
from simulation.world import World

class Renderer:
    def __init__(self, world):
        pygame.init()
        self.world = world
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(f"Snake Genetics Simulation")
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_large = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        
        
    def draw_terrain(self):
        for x in range(self.world.grid.shape[0]):
            for y in range(self.world.grid.shape[1]):
                terrain_type = self.world.grid[x][y]
                color = config.LAND_COLORS.get(terrain_type, (0, 0, 0))
                pygame.draw.rect(
                    self.screen, color,
                    (y * config.TILE_SIZE, x * config.TILE_SIZE,  # <-- swapped x and y
                    config.TILE_SIZE, config.TILE_SIZE)
                )

    def draw_snakes(self, snakes):
        if snakes is None:
            snakes = []
        for snake in snakes:
            if not snake.alive:
                continue
            for i, segment in enumerate(snake.body):
                pygame.draw.rect(
                    self.screen, snake.color,
                    (segment[1] * config.TILE_SIZE, segment[0] * config.TILE_SIZE,  # <-- swapped
                    config.TILE_SIZE, config.TILE_SIZE)
                )

    def draw_food(self, foods):
        for food in foods:
            pygame.draw.rect(
                self.screen, config.FOOD_COLOR,
                (food.position[1] * config.TILE_SIZE, food.position[0] * config.TILE_SIZE,  # <-- swapped
                config.TILE_SIZE, config.TILE_SIZE)
            )
            
            
    def draw(self, snakes, foods):
        self.screen.fill((0, 0, 0))
        self.draw_terrain()
        self.draw_food(foods)
        self.draw_snakes(snakes)
        pygame.display.flip()
        self.clock.tick(config.FPS)
            