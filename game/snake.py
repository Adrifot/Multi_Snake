import genes
import utils.generators as gget
import random

class Snake:
    # Constructor
    def __init__(self, position, direction, color, parent1_chr=None, parent2_chr=None):
        self.position = position
        self.direction = direction
        self.color = color
        # self.body = [position[:]]
        self.score = 0
        self.alive = True
        
        if (parent1_chr is None or parent2_chr is None):
            self.chr = gget.random_chromosome(genes.CHROMOSOME_LENGTH)
        else:
            self.chr = gget.crossover(parent1_chr, parent2_chr) 
    
    # print() overwrite
    def __str__(self):
        return bin(self.chr) + "\n"
    
    # Mutation function        
    def mutate(self):
        start, length = genes.LAYOUT["mutability"]
        mutation_gene = genes.extract(self.chr, start, length)
        mutation_chance = genes.DECODER["mutability"][mutation_gene]
        
        if (random.random() < mutation_chance):
            mutated_idx = random.randint(0, genes.CHROMOSOME_LENGTH-1)
            self.chr = genes.mutate(self.chr, mutated_idx)