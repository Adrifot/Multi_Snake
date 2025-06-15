import pygame
from typing import List
import core.config as config
from core.algorithms import a_star, bfs, dijkstra, greedy, manhattan
from entities.snake import Snake
from core.genes import crossover, mutate
from simulation.world import World
from simulation.renderer import Renderer
import random

class GameController:
    def __init__(self):
        pygame.init()
        self.world = World(
            width=config.WINDOW_X // config.TILE_SIZE,
            height=config.WINDOW_Y // config.TILE_SIZE
        )
        self.renderer = Renderer(self.world)
        self.clock = pygame.time.Clock()
        self.running = False
        self.paused = False
        self.generation = 0
        
        # Initialize snakes with genetic diversity
        self.snakes = [
            Snake(
                position=(10, 10),
                direction=(1, 0),
                color="blue"
            ) for _ in range(5)  # Start with 5 snakes
        ]
        self.foods = self.world.spawn_food(config.FOOD_NR)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self._reset_simulation()

    def _reset_simulation(self):
        """Reset the simulation for a new generation."""
        self.generation += 1
        self.snakes = self._evolve_snakes()
        self.foods = self.world.spawn_food(config.FOOD_NR)

    def _evolve_snakes(self) -> List[Snake]:
        """Create next generation using genetic algorithms."""
        # Select top performers (top 20% by score)
        survivors = sorted(self.snakes, key=lambda s: s.score, reverse=True)[:len(self.snakes)//5]
        new_snakes = []
        
        # Breed survivors
        for _ in range(len(self.snakes)):
            parent1, parent2 = random.choices(survivors, k=2)
            child_chromo = crossover(parent1.chr, parent2.chr)
            child_chromo = mutate(child_chromo, mutation_rate=0.1)
            new_snake = Snake(
                position=(random.randint(5, 15), random.randint(5, 15)),
                direction=random.choice([(1,0), (-1,0), (0,1), (0,-1)]),
                color=random.choice(list(config.SNAKE_COLORS.keys())),
                parent1_chr=parent1.chr,
                parent2_chr=parent2.chr
            )
            new_snakes.append(new_snake)
        
        return new_snakes

    def update(self):
        if self.paused:
            return

        # Update all snakes
        for snake in self.snakes:
            if not snake.alive:
                continue
            
            # Genetic decision-making
            visible_food = [
                food for food in self.foods 
                if manhattan(snake.position, food) <= snake.vision_range
            ]
            if visible_food:
                path = snake.algorithm(
                    self.world.grid,
                    snake.position,
                    visible_food,
                    snake.vision_range
                )
                if path:
                    snake.follow_path(path)

            # Movement and collisions
            snake.move(self.world.grid)
            if snake.position in self.foods:
                self.foods.remove(snake.position)
                snake.grow()
                self.foods.extend(self.world.spawn_food(1))  # Replace eaten food

        # End generation if all snakes die
        if all(not snake.alive for snake in self.snakes):
            self._reset_simulation()

    def run(self):
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.renderer.draw(self.snakes, self.foods, self.generation)
            self.clock.tick(config.FPS)
        pygame.quit()