import pygame
import numpy as np
from typing import List, Tuple
import core.config as config
from entities.snake import Snake
from simulation.world import World

class Renderer:
    def __init__(self, world: World):
        pygame.init()
        self.world = world
        self.screen = pygame.display.set_mode((config.WINDOW_X, config.WINDOW_Y))
        pygame.display.set_caption(f"Snake Genetics Gen 0")
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_large = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()

        # Color gradient for fitness visualization
        self.fitness_gradient = [
            np.array(config.SNAKE_COLORS["red"]) * (i / 10) + 
            np.array(config.SNAKE_COLORS["darkgreen"]) * (1 - i / 10)
            for i in range(10)
        ]

    def draw_terrain(self):
        """Draw the Perlin noise terrain."""
        for y in range(len(self.world.grid)):
            for x in range(len(self.world.grid[0])):
                terrain_type = self.world.grid[y][x]
                color = config.LAND_COLORS.get(terrain_type, (0, 0, 0))
                pygame.draw.rect(
                    self.screen, color,
                    (x * config.TILE_SIZE, y * config.TILE_SIZE,
                     config.TILE_SIZE, config.TILE_SIZE)
                )

    def draw_snakes(self, snakes: List[Snake]):
        """Draw snakes with fitness-based coloring."""
        for snake in snakes:
            if not snake.alive:
                continue

            # Color intensity based on fitness (score)
            fitness_level = min(snake.score // 5, 9)  # Scale score to gradient index
            color = self.fitness_gradient[fitness_level]

            for i, segment in enumerate(snake.body):
                # Head is brighter
                segment_color = color if i > 0 else (color * 1.5).clip(0, 255)
                pygame.draw.rect(
                    self.screen, segment_color,
                    (segment[0] * config.TILE_SIZE, segment[1] * config.TILE_SIZE,
                     config.TILE_SIZE, config.TILE_SIZE)
                )

    def draw_food(self, foods: List[Tuple[int, int]]):
        """Draw food items."""
        for food in foods:
            pygame.draw.rect(
                self.screen, config.FOOD_COLOR,
                (food[0] * config.TILE_SIZE, food[1] * config.TILE_SIZE,
                 config.TILE_SIZE, config.TILE_SIZE)
            )

    def draw_stats(self, snakes: List[Snake], generation: int):
        """Display genetic statistics."""
        alive_count = sum(1 for s in snakes if s.alive)
        avg_score = sum(s.score for s in snakes) / max(1, len(snakes))
        
        # Generation info
        gen_text = self.font_large.render(
            f"Gen {generation} | Alive: {alive_count}/{len(snakes)}", 
            True, (255, 255, 255))
        self.screen.blit(gen_text, (10, 10))

        # Top performers
        top_snakes = sorted(snakes, key=lambda s: s.score, reverse=True)[:3]
        for i, snake in enumerate(top_snakes):
            traits = [
                f"A: {snake.algorithm.__name__}",
                f"V: {snake.vision_range}",
                f"S: {snake.score}"
            ]
            trait_text = self.font_small.render(
                f"#{i+1}: {', '.join(traits)}", 
                True, snake.color)
            self.screen.blit(trait_text, (10, 40 + i * 20))

    def draw(self, snakes: List[Snake], foods: List[Tuple[int, int]], generation: int):
        """Main draw loop."""
        self.screen.fill((0, 0, 0))
        self.draw_terrain()
        self.draw_food(foods)
        self.draw_snakes(snakes)
        self.draw_stats(snakes, generation)
        pygame.display.flip()
        self.clock.tick(config.FPS)