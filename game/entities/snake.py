import random
import core.config as config
from core import algorithms, genes

class Snake:
    
    def __init__(self, position, direction, color,
                 parent1=None, parent2=None):
        self.position = position
        self.direction = direction
        self.color = color
        self.body = [position]
        self.score = 0
        self.alive = True
        
        self.path = []
        self.step = 0
        
        if parent1 is not None and parent2 is not None:
            self.chr = genes.crossover(parent1.chr, parent2.chr)
            self.mutate()
        else:
            self.chr = genes.random_chromosome()
        self.decode_genes()
        
        
    def __str__(self):
        return f"Chr: {bin(self.chr)} | Vision: {self.vision_range} | Muta: {self.mutability}"
    
    
    def decode_genes(self):
        ''' Decode the binary-valued genes into behavioral traits and save them in instance variables '''
        traits = genes.decode_chromosome(self.chr)
        self.algorithm = traits["algorithm"]
        self.vision_range = traits["vision_range"]
        self.mutability = traits["mutability"]
        
        
    def mutate(self):
        ''' 
        Cause a random one-bit mutation (bit flip)\n
        Chance depends on mutability
        '''
        start, length = genes.LAYOUT["mutability"]
        if random.random() < genes.DECODER["mutability"][genes.extract(self.chr, start, length)]:
            self.chr = genes.mutate(self.chr, random.randint(0, genes.CHROMOSOME_LENGTH-1))
            

    def decide_movement(self, grid, foods):
        visible_food = algorithms.foods_in_vision(self.position, foods, self.vision_range)
        if visible_food:
            self.path = self.algorithm(grid, self.position, visible_food, self.vision_range)
            self.step = 0
        else:
            self.path = []
            self.step = 0
            
            
    def move(self, grid, other_bodies=None):
        if other_bodies is None:
            other_bodies = set()
        if self.path:
            self.follow_path(grid, other_bodies)
            return self.alive
        else:
            next_pos = (self.position[0] + self.direction[0],
                        self.position[1] + self.direction[1])

            # Check boundaries and obstacles
            if (not (0 <= next_pos[0] < len(grid[0]) and 0 <= next_pos[1] < len(grid)) or
                grid[next_pos[1]][next_pos[0]] == 999 or
                next_pos in other_bodies):
                possible_dirs = [ # Find all valid alternative directions
                    d for d in [(0,1),(0,-1),(1,0),(-1,0)]
                    if (0 <= self.position[0] + d[0] < len(grid[0]) and
                        0 <= self.position[1] + d[1] < len(grid) and
                        grid[self.position[1] + d[1]][self.position[0] + d[0]] != 999 and
                        (self.position[0] + d[0], self.position[1] + d[1]) not in other_bodies)
                ]
                random.shuffle(possible_dirs)

                if possible_dirs:
                    self.direction = possible_dirs[0]
                    next_pos = (self.position[0] + self.direction[0],
                                self.position[1] + self.direction[1])
                else:
                    self.alive = False
                    return False

            # Check for collision with body after fallback
            if next_pos in other_bodies:
                self.alive = False
                return False

        # Execute movement
        self.position = next_pos
        self.body.insert(0, self.position)
        if len(self.body) > max(3, self.score + 3):
            self.body.pop()
        print(f"Snake at {self.position} | Path: {len(self.path)} steps | Step: {self.step}")
        return True


    def follow_path(self, grid, other_bodies=None):
        if other_bodies is None:
            other_bodies = set()
        if self.path and self.step < len(self.path):
            next_pos = self.path[self.step]
            # Check if next position is valid
            if (0 <= next_pos[0] < len(grid[0]) and 
                0 <= next_pos[1] < len(grid) and 
                grid[next_pos[1]][next_pos[0]] != 999 and
                next_pos not in other_bodies):
                
                self.direction = (next_pos[0] - self.position[0], 
                                next_pos[1] - self.position[1])
                self.position = next_pos
                self.body.insert(0, self.position)
                self.step += 1

                if len(self.body) > max(3, self.score + 3):
                    self.body.pop()
            else:
                # Collision -> snake dies
                self.alive = False
        else:
            # Invalid path step -> abandon path
            self.path = []
            self.step = 0
                
                
    def grow(self):
        self.score += 1
        self.body.append(self.body[-1])
        
        
    def get_fallback_move(self, grid, other_bodies):
        
        possible_dirs = [
            d for d in [(0,1),(0,-1),(1,0),(-1,0)]
            if (0 <= self.position[0] + d[0] < len(grid[0]) and
                0 <= self.position[1] + d[1] < len(grid) and
                grid[self.position[1] + d[1]][self.position[0] + d[0]] != 999 and
                (self.position[0] + d[0], self.position[1] + d[1]) not in other_bodies)
        ]
        random.shuffle(possible_dirs)
        for d in possible_dirs:
            candidate = (self.position[0] + d[0], self.position[1] + d[1])
            return candidate 
        
        return (self.position[0] + self.direction[0], self.position[1] + self.direction[1])