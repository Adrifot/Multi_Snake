import numpy as np
import random
import core.config as config
from vnoise import Noise
from entities.food import Food

# configurable vars
OFFSET_X = random.random() * 100
OFFSET_Y = random.random() * 100
SCALING_FACTOR = 10
OCTAVES = 2
PERSISTENCE = 0.4
LACUNARITY = 1.5

class World:
    def __init__(self):
        self.width = config.WINDOW_WIDTH// config.TILE_SIZE
        self.height = config.WINDOW_HEIGHT // config.TILE_SIZE
        self.grid = self.generate_perlin_terrain()
        self.foods = []
        
        
    def generate_perlin_terrain(self):
        noise = Noise(seed=random.randint(0, 1000))
        grid = np.zeros((self.height, self.width), dtype=int)
        print(f"Self height: {self.height}")
        print(f"Self width: {self.width}")
        for x in range(self.height):      # x = row
            for y in range(self.width):   # y = col
                n = noise.noise2(x/SCALING_FACTOR, y/SCALING_FACTOR, octaves=OCTAVES, persistence=PERSISTENCE, lacunarity=LACUNARITY)  
                if n < -0.55:
                    grid[x][y] = 999  # Impassable
                elif n < -0.3:
                    grid[x][y] = 4    # Mountains (high cost)
                elif n < 0:
                    grid[x][y] = 2    # Hills (medium cost)
                else:
                    grid[x][y] = 1    # Grass (low cost)
        return grid

    def get_terrain_cost(self, pos):
        x, y = pos
        if 0 <= x < self.height and 0 <= y < self.width:
            return self.grid[x][y]
        return 999

    def is_valid_position(self, pos):
        x, y = pos
        return (
            0 <= x < self.height and 
            0 <= y < self.width and 
            self.grid[x][y] != 999
        )
        
        
    def spawn_food(self, count, snakes=None):
        if snakes is None:
            snakes = []
        return Food.spawn_batch(self.grid, count, snakes)