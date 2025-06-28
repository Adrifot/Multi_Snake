import numpy as np
import random
import core.config as config
from vnoise import Noise
from entities.food import Food
from core.genes import mutate

# configurable vars
OFFSET_X = random.random() * 100
OFFSET_Y = random.random() * 100
SCALING_FACTOR = 10
OCTAVES = 3
PERSISTENCE = 0.5
LACUNARITY = 1.25

class World:
    """Controls terrain math and food spawn logic"""
    def __init__(self):
        self.width = config.WINDOW_WIDTH// config.TILE_SIZE
        self.height = config.WINDOW_HEIGHT // config.TILE_SIZE
        self.grid = self.generate_perlin_terrain()
        self.foods = []
        
        
    def generate_perlin_terrain(self):
        """Generate world map using Perlin noise"""
        noise = Noise(seed=random.randint(0, 1000))
        grid = np.zeros((self.height, self.width), dtype=int)
        for x in range(self.height):      # x = row
            for y in range(self.width):   # y = col
                n = noise.noise2(x/SCALING_FACTOR, y/SCALING_FACTOR, octaves=OCTAVES, persistence=PERSISTENCE, lacunarity=LACUNARITY)  
                if n < -0.4:
                    grid[x][y] = 999  # Impassable
                elif n < -0.25:
                    grid[x][y] = 7    # Mountains (high cost)
                elif n < 0:
                    grid[x][y] = 3    # Hills (medium cost)
                else:
                    grid[x][y] = 1    # Grass (low cost)
        return grid

        
        
    def spawn_food(self, count, snakes=None, parent_foods=None):
        """Spawn config.FOOD_NR food entities"""
        occupied = set()
        if snakes:
            for snake in snakes:
                occupied.update(snake.body)
        valid_positions = [
            (x, y)
            for x in range(self.grid.shape[0])
            for y in range(self.grid.shape[1])
            if self.grid[x][y] != 999 and (x, y) not in occupied
        ]
        # Use survivor foods as parents
        new_foods = []
        for _ in range(min(count, len(valid_positions))):
            pos = random.choice(valid_positions)
            if parent_foods and len(parent_foods) > 1:
                parent1 = random.choice(parent_foods)
                parent2 = random.choice(parent_foods)
                while parent2 == parent1:
                    parent2 = random.choice(parent_foods)

                chr = 0
                for i in range(5): 
                    bit_mask = 1 << i
                    if random.random() < 0.5:
                        chr |= (parent1.chromosome & bit_mask)
                    else:
                        chr |= (parent2.chromosome & bit_mask)

                # Mutation
                chr = mutate(chr, 0.15, 5) # 15% mutation chance
                new_foods.append(Food(pos, chromosome=chr))
            else:
                new_foods.append(Food(pos))
        return new_foods