import numpy as np
import random
from typing import List, Tuple
import core.config as config
from vnoise import Noise

class World:
    def __init__(self, width: int = None, height: int = None):
        self.width = width or (config.WINDOW_X // config.TILE_SIZE)
        self.height = height or (config.WINDOW_Y // config.TILE_SIZE)
        self.grid = self._generate_perlin_terrain()
        self.foods = []
        
    def _generate_perlin_terrain(self) -> np.ndarray:
        """Generate terrain using Perlin noise with obstacles."""
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

    def spawn_food(self, count: int) -> List[Tuple[int, int]]:
        """Spawn food avoiding obstacles and snakes."""
        valid_positions = [
            (x, y) for y in range(self.height) 
            for x in range(self.width) 
            if self.grid[y][x] != 999
        ]
        return random.sample(valid_positions, min(count, len(valid_positions)))

    def get_terrain_cost(self, pos: Tuple[int, int]) -> int:
        """Get movement cost for a position."""
        x, y = pos
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return 999  # Out-of-bounds counts as impassable

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is walkable."""
        x, y = pos
        return (
            0 <= x < self.width and 
            0 <= y < self.height and 
            self.grid[y][x] != 999
        )

    def respawn_food(self, eaten_pos: Tuple[int, int]) -> None:
        """Replace eaten food at a new location."""
        self.foods.remove(eaten_pos)
        new_food = self.spawn_food(1)
        if new_food:
            self.foods.append(new_food[0])