import pygame
import numpy as np
import core.config as config
from entities.snake import Snake
from simulation.world import World

class Renderer:
    def __init__(self, world):
        pygame.init()
        self.world = world
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH + config.STATS_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(f"Snake Genetics Simulation")
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_large = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        
        
    def draw_terrain(self):
        for x in range(self.world.grid.shape[0]):
            for y in range(self.world.grid.shape[1]):
                terrain_type = self.world.grid[x][y]
                color = config.LAND_COLORS.get(terrain_type, (0, 0, 0))
                pygame.draw.rect(
                    self.screen, color,
                    (y * config.TILE_SIZE, x * config.TILE_SIZE,  # <-- swapped x and y
                    config.TILE_SIZE, config.TILE_SIZE)
                )

    def draw_snakes(self, snakes):
        if snakes is None:
            snakes = []
        for snake in snakes:
            if not snake.alive:
                continue
            for i, segment in enumerate(snake.body):
                pygame.draw.rect(
                    self.screen, snake.color,
                    (segment[1] * config.TILE_SIZE, segment[0] * config.TILE_SIZE,  # <-- swapped
                    config.TILE_SIZE, config.TILE_SIZE)
                )

    def draw_food(self, foods):
        for food in foods:
            # Decide color based on toxicity and energy_factor
            if food.energy_factor == 0.5:
                color = config.FOOD_COLORS["low"]
            elif food.energy_factor == 1.0:
                color = config.FOOD_COLORS["med"]
            else:
                color = config.FOOD_COLORS["high"]

            rect = pygame.Rect(
                food.position[1] * config.TILE_SIZE,
                food.position[0] * config.TILE_SIZE,
                config.TILE_SIZE,
                config.TILE_SIZE
            )

            pygame.draw.rect(self.screen, color, rect)

            if food.toxic:
                pygame.draw.line(self.screen, (255, 0, 0), rect.topleft, rect.bottomright, 2)
                pygame.draw.line(self.screen, (255, 0, 0), rect.topright, rect.bottomleft, 2)
            
            
        
    def draw_stats(self, snakes, foods, generation):
        x_offset = config.WINDOW_WIDTH + 10  # Start drawing in the stats area
        y = 10
        font = self.font_small
        stats = [
            f"Generation: {generation}",
            f"Alive snakes: {sum(1 for s in snakes if s.alive)}",
            f"Total food: {len(foods)}",
            f"Toxic food: {sum(1 for f in foods if getattr(f, 'toxic', False))}",
        ]
        # Top 5 snakes by score
        top_snakes = sorted(snakes, key=lambda s: getattr(s, 'score', 0), reverse=True)[:5]
        for i, snake in enumerate(top_snakes, 1):
            stats.append(
                f"#{i}: Score={snake.score} Len={len(snake.body)} "
                f"Gene: {getattr(snake, 'toxic_reaction', '?')}, "
                f"Resist: {getattr(snake, 'toxic_resistance', '?')}, "
                f"Pref: {getattr(snake, 'food_preference', '?')}"
            )
        for line in stats:
            text = font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (x_offset, y))
            y += 18
            
    def draw(self, snakes, foods, generation=0):
        self.screen.fill((0, 0, 0))
        self.draw_terrain()
        self.draw_food(foods)
        self.draw_snakes(snakes)
        self.draw_stats(snakes, foods, generation)
        pygame.display.flip()
        self.clock.tick(config.FPS)