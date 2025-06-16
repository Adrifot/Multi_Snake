import pygame
import core.config as config
from core.algorithms import manhattan
from entities.snake import Snake
from core.genes import crossover, mutate
from simulation.world import World
from simulation.renderer import Renderer
import random

class GameController:
    def __init__(self):
        self.world = World()
        self.renderer = Renderer(self.world)
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        self.generation = 0
        
        valid_tiles = [
            (x, y)
            for y in range(len(self.world.grid))
            for x in range(len(self.world.grid[0]))
            if self.world.grid[y][x] != 999
        ]
        
        initial_snake_count = config.SNAKE_COUNT
        
        spawn_positions = random.sample(valid_tiles, initial_snake_count)
        
        self.snakes = [
            Snake(
                position=pos,
                direction=random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]),
                color=random.choice(list(config.SNAKE_COLORS.keys()))
            )
            for pos in spawn_positions
        ]
        
        self.foods = self.world.spawn_food(config.FOOD_NR, self.snakes)
        
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset_simulation()
                   
                    
    def reset_simulation(self):
        self.generation += 1
        self.snakes = self.evolve_snakes()
        self.foods = self.world.spawn_food(config.FOOD_NR, self.snakes)
        
        
    def evolve_snakes(self):
        survivors = sorted(self.snakes, key=lambda s: s.score, reverse=True)[:max(1, len(self.snakes)//5)]
        new_snakes = []
        if not survivors:
            # No survivors, create new random snakes
            valid_tiles = [
                (x, y)
                for y in range(len(self.world.grid))
                for x in range(len(self.world.grid[0]))
                if self.world.grid[y][x] != 999
            ]
            spawn_positions = random.sample(valid_tiles, config.SNAKE_COUNT)
            for pos in spawn_positions:
                new_snakes.append(
                    Snake(
                        position=pos,
                        direction=random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)]),
                        color=random.choice(list(config.SNAKE_COLORS.keys()))
                    )
                )
            return new_snakes


        for _ in range(len(self.snakes)):
            parent1, parent2 = random.choices(survivors, k=2)
            new_snakes.append(
                Snake(
                    position=(random.randint(5, 15), random.randint(5, 15)),
                    direction=random.choice([(1,0), (-1,0), (0,1), (0,-1)]),
                    color=random.choice(list(config.SNAKE_COLORS.keys())),
                    parent1=parent1, parent2=parent2
                )
            )
        return new_snakes
    
    
    def update(self):
        if self.paused:
            return

        # Phase 1: Decide next moves
        next_positions = {}
        all_bodies = set()
        for snake in self.snakes:
            if snake.alive:
                all_bodies.update(snake.body)

        for snake in self.snakes:
            if not snake.alive:
                continue
            # Only include bodies within vision range
            other_bodies = {pos for pos in all_bodies
                            if manhattan(snake.position, pos) <= snake.vision_range}
            other_bodies -= set(snake.body[-1:])
            snake.decide_movement(self.world.grid, [food.position for food in self.foods])
        
            for snake in self.snakes:
                if not snake.alive:
                    continue
            
                other_bodies = {pos for pos in all_bodies
                                if manhattan(snake.position, pos) <= snake.vision_range}
                other_bodies -= set(snake.body[-1:])
                snake.decide_movement(self.world.grid, [food.position for food in self.foods])

                next_pos = None
                if snake.path and snake.step < len(snake.path):
                    candidate = snake.path[snake.step]
                    if (0 <= candidate[0] < len(self.world.grid[0]) and
                        0 <= candidate[1] < len(self.world.grid) and
                        self.world.grid[candidate[1]][candidate[0]] != 999 and
                        candidate not in other_bodies):
                        next_pos = candidate
                    else:
                        next_pos = snake.get_fallback_move(self.world.grid, other_bodies)
                else:
                    next_pos = snake.get_fallback_move(self.world.grid, other_bodies)
                    
                next_positions[snake] = next_pos

        # Phase 2: Check for collisions
        occupied = {}
        for snake, pos in next_positions.items():
            if not (0 <= pos[0] < len(self.world.grid[0]) and 0 <= pos[1] < len(self.world.grid)):
                snake.alive = False
                continue
            if self.world.grid[pos[1]][pos[0]] == 999:
                snake.alive = False
                continue
            # Check if another snake is moving to the same position
            if pos in occupied:
                snake.alive = False
                occupied[pos].alive = False
                continue
            # Check if moving into any body
            body_positions = set()
            for other in self.snakes:
                if not other.alive:
                    continue
                # Exclude own tail (since it will move)
                if other is snake:
                    body_positions.update(other.body[:-1])
                else:
                    body_positions.update(other.body)
            if pos in body_positions:
                snake.alive = False
                continue

        # Phase 3: Move snakes
        for snake in self.snakes:
            if not snake.alive:
                continue
            pos = next_positions[snake]
            snake.position = pos
            snake.body.insert(0, pos)
            if len(snake.body) > max(3, snake.score + 3):
                snake.body.pop()
            if snake.path and snake.step < len(snake.path):
                snake.step += 1

            for food in self.foods:
                if snake.position == food.position:
                    snake.grow()
                    self.foods.remove(food)
                    break

        # Remove dead snakes
        self.snakes = [snake for snake in self.snakes if snake.alive]

        if all(not snake.alive for snake in self.snakes):
            self.reset_simulation()
        
        # Pahse 4: spawn more food
        food_needed = config.FOOD_NR - len(self.foods)
        if food_needed > 0:
            new_foods = self.world.spawn_food(food_needed, self.snakes)
            self.foods.extend(new_foods)
    
    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.renderer.draw(self.snakes, self.foods)
            self.clock.tick(config.FPS)
        pygame.quit()