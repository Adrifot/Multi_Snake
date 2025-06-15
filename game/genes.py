import random

# Constants
CHROMOSOME_LENGTH = 8

# Dictionaries
LAYOUT = { # gene: (start_bit, length)
    "algorithm": (0, 2),
    "vision_range": (2, 2),
    "gene_dominance": (4, 2),
    "mutability": (6, 2)
}

DECODER = {
    "algorithm": {
        0b00: "greedy",
        0b01: "bfs",
        0b10: "dijkstra",
        0b11: "a*"
    },
    
    "vision_range": {
        0b00: 5,
        0b01: 10,
        0b10: 10,
        0b11: 15
    },
    
    "gene_dominance": {
        0b00: -0.05, # recessive
        0b01: 0, 
        0b10: 0,
        0b11: 0.05 # dominant
    },
    
    "mutability": {
        0b00: 0.05, # more stability
        0b01: 0.1, # 10% chance (much bigger than IRL)
        0b10: 0.1,
        0b11: 0.15 # more mutation
    }
}

# Functions
def extract(chr, start, length):
    mask = (1 << length) - 1
    return (chr >> start) & mask

def mutate(chr, idx):
    return chr ^ (1 << idx)


def random_chromosome(n_bits):
    return random.getrandbits(n_bits)

def crossover(chr1, chr2):
    
    # Binary representations of the genetic dominance gene
    start, length = LAYOUT["gene_dominance"]
    raw_dom1 = extract(chr1, start, length)
    raw_dom2 = extract(chr2, start, length)
    
    # Decoded values for the genes above
    dom1 = DECODER["gene_dominance"][raw_dom1]
    dom2 = DECODER["gene_dominance"][raw_dom2]
    
    relative_dom = dom1 - dom2
    crossover_weight= 0.5 + relative_dom
    child = 0 # initialize child chromosome
    
    for gene, (start, length) in LAYOUT.items():
        gene1 = extract(chr1, start, length)
        gene2 = extract(chr1, start, length)
        winning_gene = gene1 if random.random() < crossover_weight else gene2
        child |= (winning_gene << start)
        
    # print("Child:", bin(child))
    return child
    