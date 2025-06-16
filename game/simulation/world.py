import numpy as np
import random
import core.config as config
from vnoise import Noise
from entities.food import Food

class World:
    def __init__(self):
        self.width = config.WINDOW_X // config.TILE_SIZE
        self.height = config.WINDOW_Y // config.TILE_SIZE
        self.grid = self.generate_perlin_terrain()
        self.foods = []
        
        
    def generate_perlin_terrain(self):
        noise = Noise(seed=random.randint(0, 1000))
        grid = np.zeros((self.height, self.width), dtype=int)
        
        for y in range(self.height):
            for x in range(self.width):
                n = noise.noise2(x/40, y/40)
                if n < -0.55:
                    grid[y][x] = 999  # Impassable
                elif n < -0.3:
                    grid[y][x] = 4    # Mountains (high cost)
                elif n < 0:
                    grid[y][x] = 2    # Hills (medium cost)
                else:
                    grid[y][x] = 1    # Grass (low cost)
        return grid
    
    
    def get_terrain_cost(self, pos):
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return 999
    
    
    def is_valid_position(self, pos):
        x, y = pos
        return (
            0 <= x < self.width and 
            0 <= y < self.height and 
            self.grid[y][x] != 999
        )
        
        
    def spawn_food(self, count, snakes=None):
        if snakes is None:
            snakes = []
        return Food.spawn_batch(self.grid, count, snakes)