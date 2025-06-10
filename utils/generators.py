import random
import genes 

def random_chromosome(n_bits):
    return random.getrandbits(n_bits)

def crossover(chr1, chr2):
    print("Parent A:", bin(chr1))
    print("Parent B:", bin(chr2))
    

    # Binary representations of the genetic dominance gene
    start, length = genes.LAYOUT["gene_dominance"]
    raw_dom1 = genes.extract(chr1, start, length)
    raw_dom2 = genes.extract(chr2, start, length)
    
    # Decoded values for the genes above
    dom1 = genes.DECODER["gene_dominance"][raw_dom1]
    dom2 = genes.DECODER["gene_dominance"][raw_dom2]
    
    relative_dom = dom1 - dom2
    crossover_weight= 0.5 + relative_dom
    child = 0 # initialize child chromosome
    
    for gene, (start, length) in genes.LAYOUT.items():
        gene1 = genes.extract(chr1, start, length)
        gene2 = genes.extract(chr1, start, length)
        winning_gene = gene1 if random.random() < crossover_weight else gene2
        child |= (winning_gene << start)
        
    print("Child:", bin(child))
    return child
    