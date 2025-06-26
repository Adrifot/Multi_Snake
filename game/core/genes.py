import random
import core.algorithms as algos

# ----- Constants ------
CHROMOSOME_LENGTH = 12

# Gene layout: gene_name: (start_bit, length)
LAYOUT = {
    "algorithm": (0, 2),    # 2 bits (pathfinding algorithm)
    "vision_range": (2, 2), # 2 bits (distance of perception)
    "gene_dominance": (4, 2), # 2 bits (affects crossover bias)
    "mutability": (6, 2),    # 2 bits (mutation probability)
    "exploration": (8, 2), # 2 bits (chance of random movements in the absence of food)
    "max_energy": (10, 2) # starting and maximum energy
}

# Decoder for gene values
DECODER = {
    "algorithm": {
        0b00: algos.greedy,
        0b01: algos.bfs,
        0b10: algos.dijkstra, 
        0b11: algos.a_star
    },
    "vision_range": {
        0b00: 15, 
        0b01: 25,  
        0b10: 25,  
        0b11: 35   
    },
    "gene_dominance": {
        0b00: -0.1,  
        0b01: 0.0,   
        0b10: 0.0,  
        0b11: 0.1    
    },
    "mutability": {
        0b00: 0.1,  
        0b01: 0.15,  
        0b10: 0.15,   
        0b11: 0.2    
    },
    "exploration": {
        0b00: 0.1,
        0b01: 0.25,
        0b10: 0.25,
        0b11: 0.40
    },
    "max_energy": {
        0b00: 100,
        0b01: 150,
        0b10: 150,
        0b11: 200
    }
}


def extract(chromosome: int, start: int, length: int) -> int:
    mask = (1 << length) - 1
    return (chromosome >> start) & mask


def random_chromosome() -> int:
    return random.getrandbits(CHROMOSOME_LENGTH)


def mutate(chromosome: int, mutation_rate: float) -> int:
    if random.random() < mutation_rate:
        bit_to_flip = random.randint(0, CHROMOSOME_LENGTH - 1)
        return chromosome ^ (1 << bit_to_flip)
    return chromosome


def crossover(parent1: int, parent2: int) -> int:
    child = 0
    for gene, (start, length) in LAYOUT.items():
        p1_dom = DECODER["gene_dominance"][extract(parent1, *LAYOUT["gene_dominance"])]
        p2_dom = DECODER["gene_dominance"][extract(parent2, *LAYOUT["gene_dominance"])]
        bias = 0.5 + (p1_dom - p2_dom)  
        
        inherited_gene = extract(parent1, start, length) if random.random() < bias else extract(parent2, start, length)
        child |= (inherited_gene << start)
    
    return child


def decode_chromosome(chromosome):
    traits = {}
    for gene, (start, length) in LAYOUT.items():
        raw_value = extract(chromosome, start, length)
        traits[gene] = DECODER[gene][raw_value]
    return traits