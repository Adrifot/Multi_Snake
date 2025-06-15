import genes
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
            self.chr = genes.random_chromosome(genes.CHROMOSOME_LENGTH)
        else:
            self.chr = genes.crossover(parent1_chr, parent2_chr) 
            
        self.decode_chromosome()
    
    # Mutation function        
    def mutate(self):
        mutation_chance = self.mutability
        
        if (random.random() < mutation_chance):
            mutated_idx = random.randint(0, genes.CHROMOSOME_LENGTH-1)
            self.chr = genes.mutate(self.chr, mutated_idx)
            self.decode_chromosome()
    
    # Chromosome decoder function 
    def decode_chromosome(self):
        self.traits = {}
        for gene_name, (start, length) in genes.LAYOUT.items():
            raw_gene = genes.extract(self.chr, start, length)
            decoded_gene = genes.DECODER[gene_name][raw_gene]
            self.traits[gene_name] = decoded_gene
            setattr(self, gene_name, decoded_gene)
          
    # Print override        
    def __str__(self):
        traits = ", ".join(f"{k}={v}" for k, v in self.traits.items())
        return f"Snake(chr={bin(self.chr)}, {traits})"
    
    def show_chr(self):
        print(bin(self.chr))