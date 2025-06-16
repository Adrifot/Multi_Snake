import random
import core.config as config

class Food:
    def __init__(self, position):
        self.position = position
    
    @classmethod
    def spawn_batch(cls, grid, count, snakes=[]):
        occupied = set()
        
        for snake in snakes:
            occupied.update(snake.body)
            
        valid_positions = [
            (x, y)
            for y in range(len(grid))
            for x in range(len(grid[0]))
            if grid[y][x] != 999 and (x, y) not in occupied
        ]
        
        return [
            Food(position) for position in random.sample(
                valid_positions, 
                min(count, len(valid_positions))
            )
        ]