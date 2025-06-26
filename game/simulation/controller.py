import pygame
import core.config as config
from core.algorithms import manhattan
from entities.snake import Snake
from simulation.world import World
from simulation.renderer import Renderer
import random
from operator import attrgetter

class GameController:
    def __init__(self):
        self.world = World()
        self.renderer = Renderer(self.world)
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        self.generation = 0
        self.snakes = []  
        self.foods = []   
        self._spawn_initial_snakes() 

    def _spawn_initial_snakes(self):
        valid_starts = []
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
        if spawn_count == 0:
            raise ValueError("No valid spawn positions available in the world")
        chosen = random.sample(valid_starts, spawn_count)
        self.snakes = [
            Snake(position=pos, direction=dir, color=random.choice(list(config.SNAKE_COLORS.keys())))
            for pos, dir in chosen
        ]
        self.foods = self.world.spawn_food(config.FOOD_NR, self.snakes)
        print(f"Snakes after spawn: {len(self.snakes)}")
        print(f"Alive snakes: {sum(1 for s in self.snakes if s.alive)}")
        return self.snakes

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                # elif event.key == pygame.K_r:
                #     self.reset_simulation()

    def reset_simulation(self):
        print(f"Alive snakes: {sum(1 for s in self.snakes if s.alive)}")
        self.generation += 1
        self.snakes = self.evolve_snakes()
        self.foods = self.world.spawn_food(config.FOOD_NR, self.snakes)

    def evolve_snakes(self):
        if not self.snakes:
            return self._spawn_initial_snakes()

        # Sort snakes by score and take top 20%
        survivors = sorted(self.snakes, key=attrgetter('score'), reverse=True)[:max(1, len(self.snakes)//5)]
        new_snakes = []
        
        # Create offspring from survivors
        for _ in range(len(self.snakes)):
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
        if self.paused:
            return

        # Get all body positions from living snakes
        all_bodies = {pos for s in self.snakes if s.alive for pos in s.body} # 'NoneType' object is not iterable - why is self.snakes None???

        # First decide movements for all snakes
        for snake in self.snakes:
            if not snake.alive:
                continue
                
            # Get nearby bodies from other snakes (within vision range, excluding our own body)
            other_bodies = {
                pos for pos in all_bodies - set(snake.body)
                if manhattan(snake.position, pos) <= snake.vision_range
            }
            snake.decide_movement(self.world.grid, [f.position for f in self.foods], other_bodies)

        for snake in self.snakes:
            if not snake.alive:
                continue
                
            # Get other snakes' bodies
            other_bodies = all_bodies - set(snake.body)
            moved = snake.move(self.world.grid, other_bodies)
            if not moved:
                continue
                
            for food in self.foods[:]: 
                if snake.position == food.position:
                    snake.grow()
                    snake.energy += config.FOOD_ENERGY
                    self.foods.remove(food)
                    break

        # Remove dead snakes
        self.snakes = [s for s in self.snakes if s.alive]

        # Check for extinction
        if not self.snakes:
            print("sim reset") 
            self.reset_simulation()

        # Maintain food count
        if len(self.foods) < config.FOOD_NR:
            new_food = self.world.spawn_food(config.FOOD_NR - len(self.foods), self.snakes)
            self.foods.extend(new_food)

    def run(self):
        self.running = True
        print("Grid shape:", self.world.grid.shape)
        while self.running:
            self.handle_events()
            self.update()
            self.renderer.draw(self.snakes, self.foods)
            self.clock.tick(config.FPS)
        pygame.quit()