from typing import Tuple, List
import random
import core.config as config

class Food:
    def __init__(self, position: Tuple[int, int], nutrition: int = 1):
        self.position = position
        self.nutrition = nutrition
        self.age = 0
        self.spoilage_rate = 0.01  # Chance to spoil per frame

    @classmethod
    def spawn_batch(cls, grid: List[List[int]], count: int) -> List['Food']:
        """Generate food avoiding obstacles."""
        valid_positions = [
            (x, y) for y in range(len(grid)) 
            for x in range(len(grid[0]))
            if grid[y][x] != 999  # Not an obstacle
        ]
        return [
            Food(position, nutrition=random.randint(1, 3))
            for position in random.sample(valid_positions, min(count, len(valid_positions)))
        ]

    def update(self):
        """Age food with chance to spoil."""
        self.age += 1
        if random.random() < self.spoilage_rate:
            self.nutrition = max(0, self.nutrition - 0.5)

    @property
    def is_spoiled(self) -> bool:
        return self.nutrition <= 0