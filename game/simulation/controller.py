import pygame
import core.config as config
from core.algorithms import manhattan
from entities.snake import Snake
from simulation.world import World
from simulation.renderer import Renderer
import random
from operator import attrgetter

class GameController:
    """Controls main game logic"""
    def __init__(self):
        self.world = World()
        self.renderer = Renderer(self.world)
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        self.generation = 0
        self.tick_count = 0
        self.snakes = []  
        self.foods = []   
        self.spawn_initial_snakes() 
        self.selected_entity = None



    def spawn_initial_snakes(self):
        """Spawn config.SNAKE_NR snakes"""
        valid_starts = []
        # Get valid positions for spawning snake entities
        for x in range(self.world.grid.shape[0]):  # x = row
            for y in range(self.world.grid.shape[1]):  # y = col
                for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
                    ok = True
                    body_positions = []
                    for i in range(3):
                        nx, ny = x - i*dx, y - i*dy
                        if not (0 <= nx < self.world.grid.shape[0] and 0 <= ny < self.world.grid.shape[1]):
                            ok = False
                            break
                        if self.world.grid[nx][ny] == 999:
                            ok = False
                            break
                        body_positions.append((nx, ny))
                    if ok and len(set(body_positions)) == 3:
                        valid_starts.append(((x, y), (dx, dy)))
                        
        spawn_count = min(config.SNAKE_COUNT, len(valid_starts))
        if spawn_count == 0: # should not happen, in most cases at least - IF it runs, tinker with core.config.py
            raise ValueError("No valid spawn positions available in the world")
        
        chosen = random.sample(valid_starts, spawn_count)
        self.snakes = [
            Snake(position=pos, direction=dir, color=random.choice(list(config.SNAKE_COLORS.keys())))
            for pos, dir in chosen
        ]
        
        self.foods = self.world.spawn_food(config.FOOD_NR, self.snakes) # call World's spawn_food method
        print(f"Snakes after spawn: {len(self.snakes)}")
        print(f"Alive snakes: {sum(1 for s in self.snakes if s.alive)}")
        return self.snakes


    def handle_events(self):
        """Handle keyboard and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if mx < config.WINDOW_WIDTH and my < config.WINDOW_HEIGHT:
                    grid_x = my // config.TILE_SIZE
                    grid_y = mx // config.TILE_SIZE
                    self.selected_entity = None
                    for snake in self.snakes: # check if clicked on a snake
                        if (grid_x, grid_y) in snake.body:
                            self.selected_entity = snake
                            break
                    if self.selected_entity is None: # no snake => maybe food
                        for food in self.foods:
                            if food.position == (grid_x, grid_y):
                                self.selected_entity = food
                                break

    def reset_simulation(self):
        """Reset current world state and begin a new generation of snakes"""
        print(f"Alive snakes: {sum(1 for s in self.snakes if s.alive)}")
        self.generation += 1
        print(f"Generation {self.generation}")
        
        top_snakes = sorted(self.snakes, key=lambda s: (
            config.LENGTH_WEIGHT * len(s.body) +
            config.SCORE_WEIGHT * s.score +
            config.ENERGY_WEIGHT * (s.energy // 100)
        ), reverse=True)[:3]
        
        with open("snake_log.txt", "a") as f: # generation data logging
            f.write(f"Generation {self.generation}:\n")
            for i, snake in enumerate(top_snakes, 1):
                chr_bin = format(snake.chr, '020b')
                f.write(
                    f"PLACEHOLDER TEXT FOR NOW"
                )
            f.write("\n")
        print(f"Top snakes logged for generation {self.generation}")
        
        self.snakes = self.evolve_snakes()

        survivor_foods = self.foods[:]  # keep current foods
        needed = config.FOOD_NR - len(survivor_foods)
        if needed > 0:
            new_foods = self.world.spawn_food(needed, self.snakes, survivor_foods)
            self.foods = survivor_foods + new_foods
        else:
            self.foods = survivor_foods
        
        

    def evolve_snakes(self):
        """Evolve survivor snakes and return a new generation"""
        if not self.snakes:
            return self.spawn_initial_snakes() # REMIDNER - IF NO SNAKES - STOP SIMULATION

        for snake in self.snakes:
            snake.fitness = len(snake.body) * config.LENGTH_WEIGHT + snake.score * config.SCORE_WEIGHT + (snake.energy//100) * config.ENERGY_WEIGHT
        
        num_snakes = len(self.snakes)
        
        def get_selected_count(survived_nr):
            if survived_nr in range(2, 5):
                return 2
            elif survived_nr in range(6, 17):
                return 3
            else:
                return survived_nr//5 # 20%
            
        selected_count = get_selected_count(num_snakes)
        survivors = sorted(self.snakes, key=attrgetter('fitness'), reverse=True)[:selected_count]
        
        print(f"{len(survivors)} snakes survived. Yay!")
        new_snakes = []
        
        # Create offspring from survivors
        for _ in range(config.SNAKE_COUNT + random.randint(-2, 2) * config.SNAKE_COUNT//4): # chance to spawn more or less snakes for each generation
            parent1 = random.choice(survivors)
            parent2 = random.choice(survivors)
            while parent2 == parent1 and len(survivors) > 1:
                parent2 = random.choice(survivors)
                
            valid_tiles = [
                (x, y)
                for x in range(self.world.grid.shape[0])
                for y in range(self.world.grid.shape[1])
                if self.world.grid[x][y] != 999
            ]
            spawn_pos = random.choice(valid_tiles)
            
            new_snakes.append(
                Snake(position=spawn_pos,
                      direction=random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]),
                      color=random.choice(list(config.SNAKE_COLORS.keys())),
                      parent1=parent1,
                      parent2=parent2)
            )
        return new_snakes


    def update(self):
        """Update game state by one tick"""
        if self.paused:
            return
        self.tick_count += 1
        
        all_bodies = {pos for s in self.snakes if s.alive for pos in s.body} # 'NoneType' object is not iterable - why is self.snakes None???

        # Decide movements for all snakes
        for snake in self.snakes:
            if not snake.alive:
                continue
            other_bodies = {
                pos for pos in all_bodies - set(snake.body)
                if manhattan(snake.position, pos) <= snake.vision_range
            }
            snake.decide_movement(self.world.grid, self.foods, other_bodies)

        for snake in self.snakes:
            if not snake.alive:
                continue
                s
            other_bodies = all_bodies - set(snake.body)
            moved = snake.move(self.world.grid, other_bodies, self.snakes)
            if not moved:
                continue
                
            for food in self.foods[:]: 
                if snake.position == food.position: # snake ate some food
                    if food.toxic == False:
                        snake.grow()
                        snake.energy += config.FOOD_ENERGY
                        snake.energy = min(snake.energy, snake.max_energy)
                    else:
                        penalty = food.energy_factor * config.FOOD_ENERGY * snake.toxic_resistance
                        snake.energy -= penalty
                        snake.energy_since_last_shrink += penalty
                        snake.score += 3
                    self.foods.remove(food)
                    break
            
        for food in self.foods[:]: 
            food.move(self.world.grid, self.snakes)

        self.snakes = [s for s in self.snakes if s.alive] # remove dead snakes

        # Check for extinction
        if not self.snakes: # REMINDER - MODIFY TO END THE SIMULATION HERE AND SHOW STATS
            print("sim reset") 
            self.reset_simulation()

        # food respawn
        if self.tick_count % config.FOOD_RESPAWN_RATE == 0:
            survivor_foods = self.foods[:] # the foods still on the map
            needed = config.FOOD_NR - len(survivor_foods) 
            if needed > 0:
                new_foods = self.world.spawn_food(needed, self.snakes, survivor_foods)
                self.foods.extend(new_foods)
                
        if self.tick_count % config.SNAKE_GENERATION_INTERVAL == 0:
            self.reset_simulation()


    def run(self):
        self.running = True
        print("Grid shape:", self.world.grid.shape)
        while self.running:
            self.handle_events()
            self.update()
            self.renderer.draw(self.snakes, self.foods, self.generation, self.tick_count, self.selected_entity)
            self.clock.tick(config.FPS)
        pygame.quit()