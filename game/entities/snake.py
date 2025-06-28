# entities/snake.py
import random
import core.config as config
from core import algorithms, genes

class Snake:
    """Snake entity class"""
    def __init__(self, position, direction, color, parent1=None, parent2=None):
        self.position = position
        self.direction = direction
        dx, dy = direction
        self.body = [
            position,
            (position[0] - dx, position[1] - dy),
            (position[0] - 2*dx, position[1] - 2*dy)
        ]
        self.color = color
        self.score = 0
        self.alive = True
        self.energy_since_last_shrink = 0
        self.path = []
        self.step = 0
        self.just_ate = False

        if parent1 and parent2:
            self.chr = genes.crossover(parent1.chr, parent2.chr)
            self.mutate()
        else:
            self.chr = genes.random_chromosome()
            
        self.decode_genes()



    def decode_genes(self):
        """Decode bit gene values into traits"""
        traits = genes.decode_chromosome(self.chr)
        self.algorithm = traits["algorithm"]
        self.vision_range = traits["vision_range"]
        self.mutability = traits["mutability"]
        self.exploration = traits["exploration"]
        self.max_energy = traits["max_energy"]
        self.energy = self.max_energy
        self.timidity = traits["timidity"]
        self.toxic_reaction = traits["toxic_reaction"]
        self.toxic_resistance = traits["toxic_resistance"]
        self.food_preference = traits["food_preference"]
        return traits



    def mutate(self):
        """Mutate 1 bit within chromosome"""
        start, length = genes.LAYOUT["mutability"]
        if random.random() < genes.DECODER["mutability"][genes.extract(self.chr, start, length)]:
            self.chr = genes.mutate(self.chr, random.randint(0, genes.CHROMOSOME_LENGTH - 1))



    def decide_movement(self, grid, foods, other_bodies=None):
        """Call pathfinding algorithm and decide a path to follow"""
        if other_bodies is None:
            other_bodies = set()
        
        expanded_obstacles = set()
        for pos in other_bodies:
            for dx in range(-self.timidity, self.timidity + 1): # expand/narrow obstacle area based on timidity
                for dy in range(-self.timidity, self.timidity + 1):
                    nx, ny = pos[0] + dx, pos[1] + dy
                    if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                        expanded_obstacles.add((nx, ny))
        
        obstacles = expanded_obstacles.union(set(self.body[1:-1])) # own head and tail not obstacles
        
        visible_food = algorithms.foods_in_vision(self.position, foods, self.vision_range)
        # sort food based on preference
        if self.food_preference == "high":
            visible_food.sort(key=lambda f: -f.energy_factor)
        elif self.food_preference == "low":
            visible_food.sort(key=lambda f: f.energy_factor)

        if visible_food:
            food_positions = [f.position for f in visible_food]
            if food_positions:
                self.path = self.algorithm(
                    grid, self.position, food_positions, self.vision_range, obstacles, self.direction
                )
        else:
            self.path = []
            
        self.step = 0



    def move(self, grid, other_bodies=None, other_snakes=None):
        """Move snake on the grid"""
        if other_bodies is None:
            other_bodies = set()

        collision_bodies = other_bodies.union(set(self.body[1:-1])) # own head and tail not obstacles

        next_pos = None 
        if self.path and self.step < len(self.path): # if still on path
            next_pos = self.path[self.step]
            if not (0 <= next_pos[1] < grid.shape[1] and  # check out of bounds/impassable tiles/other snakes
                    0 <= next_pos[0] < grid.shape[0]) or \
                    grid[next_pos[0]][next_pos[1]] == 999 or \
                    next_pos in collision_bodies:
                next_pos = None
                self.path = []
                self.step = 0

        if next_pos is None: # no valid path towards food found
            next_pos = self.get_fallback_move(grid, collision_bodies)

        # head to head collision detection
        other_heads = {s.position for s in other_snakes if s != self and s.alive}
        if (next_pos in collision_bodies) or (next_pos in other_heads):
            self.alive = False
            return False

        # head to body collision detection
        if next_pos in collision_bodies:
            self.alive = False
            return False

        # wall collision detection
        if not (0 <= next_pos[1] < grid.shape[1] and 0 <= next_pos[0] < grid.shape[0]):
            self.alive = False
            return False

        # mountain peak collision detection
        if grid[next_pos[0]][next_pos[1]] == 999:
            self.alive = False
            return False

        self.position = next_pos # move
        self.body.insert(0, self.position)

        if not self.just_ate:
            self.body.pop() # remove tail so the snake doesn't grow every move
        else: 
            self.just_ate = False # snake grows by 1 tile

        terrain_cost = max(1, grid[self.position[0]][self.position[1]])
        self.energy -= terrain_cost
        self.energy_since_last_shrink += terrain_cost

        if self.energy_since_last_shrink >= config.SHRINK_ENERGY_INTERVAL and len(self.body) > 3:
            shrink_count = self.energy_since_last_shrink // config.SHRINK_ENERGY_INTERVAL
            shrink_count =  min(int(shrink_count), len(self.body) - 1)
            self.body = self.body[:-shrink_count]
            self.energy_since_last_shrink %= config.SHRINK_ENERGY_INTERVAL

        if self.energy <= 0: # no energy => death
            self.alive = False
            return False

        if len(self.body) < 3: # length < 3 => death
            self.alive = False
            return False
        
        return True


    def grow(self):
        """Grow snake by 1 tile"""
        self.score += 1
        self.body.append(self.body[-1])
        self.just_ate = True


    def get_fallback_move(self, grid, collision_bodies):
        """Move in absence of food or a valid path"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        safe_moves = []

        for dx, dy in directions: # get safe moves checking for collisions
            nx, ny = self.position[0] + dx, self.position[1] + dy
            if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                if grid[nx][ny] != 999 and (nx, ny) not in collision_bodies:
                    safe_moves.append((dx, dy))

        if safe_moves:
            if random.random() <= self.exploration:
                chosen = random.choice(safe_moves)
            elif self.direction in safe_moves:
                chosen = self.direction
            else:
                chosen = random.choice(safe_moves)
        else: # no safe moves - continue forward (and die)
            chosen = self.direction

        self.direction = chosen
        next_pos = (self.position[0] + chosen[0], self.position[1] + chosen[1])
        return next_pos