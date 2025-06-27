import random
import core.config as config
import core.genes as genes

class Food:
    def __init__(self, position, chromosome=None):
        self.position = position
        self.chromosome = chromosome if chromosome is not None else genes.random_chromosome(5)
        self.decode_genes()
        

    def decode_genes(self):
        chr = self.chromosome
        self.moving = genes.extract(chr, 0, 1) != 0
        self.toxic = genes.extract(chr, 1, 2) == 0b11
        energy_factor = genes.extract(chr, 3, 2)
        if energy_factor == 0b00:
            self.energy_factor = 0.5
        elif energy_factor in (0b01, 0b10):
            self.energy_factor = 1.0
        else:
            self.energy_factor = 1.5
    
    
    def move(self, grid, snakes):
        if not self.moving:
            return
        from core.algorithms import get_neighbors
        occupied = {pos for snake in snakes for pos in snake.body}
        neighbors = get_neighbors(grid, self.position)
        valid = [n for n in neighbors if n not in occupied]
        if valid and random.random() <= 0.33:
            new_pos = random.choice(valid)
            # print(f"Food at {self.position} moves to {new_pos}")
            self.position = new_pos