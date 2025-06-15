import random
import core.algorithms as algos

# --- Constants ---
CHROMOSOME_LENGTH = 8  # Total bits in chromosome

# Gene layout: {gene_name: (start_bit, length)}
LAYOUT = {
    "algorithm": (0, 2),    # 2 bits (4 possible algorithms)
    "vision_range": (2, 2), # 2 bits (4 range options)
    "gene_dominance": (4, 2), # 2 bits (affects crossover)
    "mutability": (6, 2)    # 2 bits (mutation probability)
}

# Decoders for gene values
DECODER = {
    "algorithm": {
        0b00: algos.greedy,
        0b01: algos.bfs,
        0b10: algos.dijkstra, 
        0b11: algos.a_star
    },
    "vision_range": {
        0b00: 5,   # Short
        0b01: 10,  # Medium
        0b10: 15,  # Long
        0b11: 20   # Very long
    },
    "gene_dominance": {
        0b00: -0.2,  # Recessive
        0b01: 0.0,   # Neutral
        0b10: 0.1,   # Dominant
        0b11: 0.3    # Highly dominant
    },
    "mutability": {
        0b00: 0.01,  # Stable (1% mutation chance)
        0b01: 0.05,  # Moderate (5%)
        0b10: 0.1,   # High (10%)
        0b11: 0.2    # Extreme (20%)
    }
}

# --- Core Functions ---
def extract(chromosome: int, start: int, length: int) -> int:
    """Extract bits from a chromosome."""
    mask = (1 << length) - 1
    return (chromosome >> start) & mask

def random_chromosome() -> int:
    """Generate a random chromosome."""
    return random.getrandbits(CHROMOSOME_LENGTH)

def mutate(chromosome: int, mutation_rate: float) -> int:
    """Randomly flip bits based on mutation rate."""
    if random.random() < mutation_rate:
        bit_to_flip = random.randint(0, CHROMOSOME_LENGTH - 1)
        return chromosome ^ (1 << bit_to_flip)
    return chromosome

def crossover(parent1: int, parent2: int) -> int:
    """Combine genes from two parents with dominance bias."""
    child = 0
    for gene, (start, length) in LAYOUT.items():
        # Get dominance bias from parents
        p1_dom = DECODER["gene_dominance"][extract(parent1, *LAYOUT["gene_dominance"])]
        p2_dom = DECODER["gene_dominance"][extract(parent2, *LAYOUT["gene_dominance"])]
        bias = 0.5 + (p1_dom - p2_dom)  # Weighted probability
        
        # Inherit from parent1 or parent2 based on bias
        inherited_gene = extract(parent1, start, length) if random.random() < bias else extract(parent2, start, length)
        child |= (inherited_gene << start)
    
    return child

# --- Decoding Helpers ---
def decode_chromosome(chromosome):
    """Convert chromosome to trait dictionary."""
    traits = {}
    for gene, (start, length) in LAYOUT.items():
        raw_value = extract(chromosome, start, length)
        traits[gene] = DECODER[gene][raw_value]
    return traits