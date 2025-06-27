import random
import core.algorithms as algos

# ----- Constants ------
CHROMOSOME_LENGTH = 20

# Gene layout: gene_name: (start_bit, length)
LAYOUT = {
    "algorithm": (0, 2),    # 2 bits (pathfinding algorithm)
    "vision_range": (2, 2), # 2 bits (distance of perception)
    "gene_dominance": (4, 2), # 2 bits (affects crossover bias)
    "mutability": (6, 2),    # 2 bits (mutation probability)
    "exploration": (8, 2), # 2 bits (chance of random movements in the absence of food)
    "max_energy": (10, 2), # starting and maximum energy
    "timidity": (12, 2),
    "toxic_reaction": (14, 2),
    "toxic_resistance": (16, 2),
    "food_preference": (18, 2),
}

# Decoder for gene values
DECODER = {
    "algorithm": {
        0b00: algos.greedy,
        0b01: algos.bfs,
        0b10: algos.ucs, 
        0b11: algos.a_star
    },
    "vision_range": {
        0b00: 5, 
        0b01: 10,  
        0b10: 10,  
        0b11: 15   
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
        0b00: 700,
        0b01: 1000,
        0b10: 1000,
        0b11: 1300
    },
    "timidity": { # number of tiles around other snakes that will be avoided
        0b00: 0,
        0b01: 1,
        0b10: 1,
        0b11: 4
    },
    "toxic_reaction": {
        0b00: "ignore",
        0b01: "avoid",
        0b10: "avoid",
        0b11: "prefer"
    },
    "toxic_resistance": {
        0b00: 1.5,
        0b01: 1.0,
        0b10: 1.0,
        0b11: 0.5
    },
    "food_preference": {
        0b00: "low",
        0b01: "none",
        0b10: "none",
        0b11: "high"
    }
}


def extract(chromosome: int, start: int, length: int) -> int:
    mask = (1 << length) - 1
    return (chromosome >> start) & mask


def random_chromosome(l = CHROMOSOME_LENGTH) -> int:
    return random.getrandbits(l)


def mutate(chromosome: int, mutation_rate: float, l=CHROMOSOME_LENGTH) -> int:
    if random.random() < mutation_rate:
        bit_to_flip = random.randint(0, l - 1)
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