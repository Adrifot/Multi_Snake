from typing import List, Tuple, Optional
import random
import core.config as config
from core import algorithms, genes

class Snake:
    def __init__(
        self,
        position: Tuple[int, int],
        direction: Tuple[int, int],
        color: str,
        parent1_chr: Optional[int] = None,
        parent2_chr: Optional[int] = None
    ):
        self.position = position
        self.direction = direction
        self.color = color
        self.body = [position]  # Head-first
        self.score = 0
        self.alive = True
        self.vision_range = 10  # Default, overridden by genes
        
        # Genetic initialization
        self.chr = (
            genes.crossover(parent1_chr, parent2_chr)
            if parent1_chr and parent2_chr
            else genes.random_chromosome()
        )
        self._decode_genes()
        
        # Movement
        self.path: List[Tuple[int, int]] = []
        self.current_step = 0

    def _decode_genes(self):
        """Apply genetic traits to snake behavior."""
        traits = genes.decode_chromosome(self.chr)
        self.algorithm = traits["algorithm"]  # a_star, bfs, etc.
        self.vision_range = traits["vision_range"]
        self.mutability = traits["mutability"]

    def mutate(self):
        """Randomly mutate based on genetic mutability."""
        if random.random() < self.mutability:
            self.chr = genes.mutate(self.chr, random.randint(0, genes.CHROMOSOME_LENGTH-1))
            self._decode_genes()

    def decide_movement(self, grid, foods: List[Tuple[int, int]]) -> None:
        """Use genetic algorithm to find path to food."""
        visible_food = algorithms.foods_in_vision(self.position, foods, self.vision_range)
        if visible_food:
            self.path = self.algorithm(grid, self.position, visible_food, self.vision_range)
            self.current_step = 0

    def follow_path(self, path):
        """Move along precomputed path."""
        if self.current_step < len(self.path):
            next_pos = self.path[self.current_step]
            self.direction = (next_pos[0] - self.position[0], next_pos[1] - self.position[1])
            self.position = next_pos
            self.body.insert(0, self.position)
            self.current_step += 1
            if len(self.body) > self.score + 3:  # Maintain body length
                self.body.pop()

    def move(self, grid) -> bool:
        """Handle movement and collisions. Returns True if moved."""
        if self.path:
            self.follow_path()
        else:
            # Fallback: random movement
            next_pos = (self.position[0] + self.direction[0], 
                       self.position[1] + self.direction[1])
            
            if not (0 <= next_pos[0] < len(grid[0]) and 0 <= next_pos[1] < len(grid)):
                self.alive = False
                return False
            
            if grid[next_pos[1]][next_pos[0]] == 999:  # Obstacle
                self.direction = random.choice([
                    d for d in [(0,1),(0,-1),(1,0),(-1,0)] 
                    if d != (-self.direction[0], -self.direction[1])  # No 180 turns
                ])
                return False
            
            self.position = next_pos
            self.body.insert(0, self.position)
            if len(self.body) > self.score + 3:
                self.body.pop()
        
        return True

    def grow(self):
        """Increase size when eating."""
        self.score += 1
        self.body.append(self.body[-1])  # Duplicate tail