# entities/snake.py
import random
import core.config as config
from core import algorithms, genes

class Snake:

    def __init__(self, position, direction, color, parent1=None, parent2=None):
        self.position = position
        self.direction = direction
        dx, dy = direction
        # print(f"Spawning direction is {self.direction}")
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

    def __str__(self):
        return f"Chr: {bin(self.chr)} | Vision: {self.vision_range} | Muta: {self.mutability}"

    def decode_genes(self):
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

    def mutate(self):
        start, length = genes.LAYOUT["mutability"]
        if random.random() < genes.DECODER["mutability"][genes.extract(self.chr, start, length)]:
            self.chr = genes.mutate(self.chr, random.randint(0, genes.CHROMOSOME_LENGTH - 1))


    def decide_movement(self, grid, foods, other_bodies=None):
        if other_bodies is None:
            other_bodies = set()
        
        # expand obstacles using timidity
        expanded_obstacles = set()
        for pos in other_bodies:
            for dx in range(-self.timidity, self.timidity + 1):
                for dy in range(-self.timidity, self.timidity + 1):
                    nx, ny = pos[0] + dx, pos[1] + dy
                    if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
                        expanded_obstacles.add((nx, ny))
        
        # Include own body (except tail) in obstacles
        obstacles = expanded_obstacles.union(set(self.body[1:-1]))
        
        visible_food = algorithms.foods_in_vision(self.position, foods, self.vision_range)
        if self.food_preference == "high":
            visible_food.sort(key=lambda f: -f.energy_factor)
        elif self.food_preference == "low":
            visible_food.sort(key=lambda f: f.energy_factor)
        # print(f"{len(visible_food)} foods seen")
        if visible_food:
            # print(f"FOOD DETECTED: {len(visible_food)} foods seen")
            # print(f"Calling {self.algorithm.__name__} with: position={self.position}, visible_food={visible_food}, obstacles={obstacles}")
            food_positions = [f.position for f in visible_food]
            if food_positions:
                self.path = self.algorithm(
                    grid, self.position, food_positions, self.vision_range, obstacles, self.direction
                )
        else:
            self.path = []
        self.step = 0


    def move(self, grid, other_bodies=None, other_snakes=None):
        if other_bodies is None:
            other_bodies = set()

        # Include own body (except head) in collision checks
        collision_bodies = other_bodies.union(set(self.body[1:-1]))

        next_pos = None 
        if self.path and self.step < len(self.path):
            next_pos = self.path[self.step]
            if not (0 <= next_pos[1] < grid.shape[1] and 
                    0 <= next_pos[0] < grid.shape[0]) or \
                    grid[next_pos[0]][next_pos[1]] == 999 or \
                    next_pos in collision_bodies:
                next_pos = None
                self.path = []
                self.step = 0

        if next_pos is None:
            next_pos = self.get_fallback_move(grid, collision_bodies)

        # Final collision check - ADD HEAD-TO-HEAD COLLISION CHECK
        # Get all other snake heads
        other_heads = {s.position for s in other_snakes if s != self and s.alive}
        if (next_pos in collision_bodies) or (next_pos in other_heads):
            self.alive = False
            print(f"Died: collision with body or head at {next_pos}")
            return False

        # Final collision check
        if next_pos in collision_bodies:
            self.alive = False
            print(f"Died: collision with body at {next_pos}")
            return False

        # In snake.py's move method:
        if not (0 <= next_pos[1] < grid.shape[1] and 0 <= next_pos[0] < grid.shape[0]):
            self.alive = False
            print(f"Died: hit wall at {next_pos}")
            return False

        if grid[next_pos[0]][next_pos[1]] == 999:
            print(f"Died: hit mountain at {next_pos}")
            self.alive = False
            return False

        # Update position and body
        self.position = next_pos
        self.body.insert(0, self.position)

        if not self.just_ate:
            self.body.pop()
        else: 
            self.just_ate = False

        terrain_cost = max(1, grid[self.position[0]][self.position[1]])
        self.energy -= terrain_cost
        self.energy_since_last_shrink += terrain_cost
        # print(f"Energy = {self.energy}")

        if self.energy_since_last_shrink >= config.SHRINK_ENERGY_INTERVAL and len(self.body) > 3:
            shrink_count = self.energy_since_last_shrink // config.SHRINK_ENERGY_INTERVAL
            shrink_count =  min(int(shrink_count), len(self.body) - 1)
            self.body = self.body[:-shrink_count]
            self.energy_since_last_shrink %= config.SHRINK_ENERGY_INTERVAL

        if self.energy <= 0:
            self.alive = False
            print(f"Died: out of energy")
            return False

        if len(self.body) < 3:
            self.alive = False
            print("Died: too short")
            return False

        # print(f"Moved to position {self.position}")
        
        return True


    def grow(self):
        self.score += 1
        self.body.append(self.body[-1])
        self.just_ate = True


    def get_fallback_move(self, grid, collision_bodies):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        safe_moves = []

        for dx, dy in directions:
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
        else:
            # Nothing is safe, so force forward
            chosen = self.direction

        self.direction = chosen
        next_pos = (self.position[0] + chosen[0], self.position[1] + chosen[1])
        return next_pos