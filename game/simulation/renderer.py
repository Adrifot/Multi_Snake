import pygame
import numpy as np
import core.config as config
from entities.snake import Snake
from simulation.world import World

colors = [
    (255, 0, 0),      # red
    (255, 128, 0),    # orange
    (255, 255, 0),    # yellow
    (0, 255, 0),      # green
    (0, 255, 255),    # cyan
    (0, 128, 255),    # light blue
    (64, 64, 255),      # blue
    (128, 0, 255),    # purple
    (255, 0, 255),    # magenta
    (255, 0, 128),    # pink
]

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
            
            
        
    def draw_stats(self, snakes, foods, generation, tick):
        x_offset = config.WINDOW_WIDTH + 10
        y = 10
        
        font = self.font_small

        colors = [
            (255, 0, 0), (255, 128, 0), (255, 255, 0),
            (0, 255, 0), (0, 255, 255), (0, 128, 255),
            (0, 0, 255), (128, 0, 255), (255, 0, 255), (255, 0, 128),
        ]

        stats = [
            f"Current tick: {tick}",
            f"Generation: {generation}",
            f"Alive snakes: {sum(1 for s in snakes if s.alive)}",
            f"Total food: {len(foods)}",
            f"Toxic food: {sum(1 for f in foods if getattr(f, 'toxic', False))}",
            "---------------------",
            "Top 5 Snakes:"
        ]
        
        for line in stats:
            text = font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (x_offset, y))
            y += 18

        top_snakes = sorted(
            snakes,
            key=lambda s: (config.LENGTH_WEIGHT * len(s.body) + 
                           config.SCORE_WEIGHT * s.score + 
                           config.ENERGY_WEIGHT * (s.energy//100)),
            reverse=True
        )[:5]

        if not top_snakes:
            stats.append("No snakes to show!")

        for i, snake in enumerate(top_snakes, 1):
            chr_bin = format(snake.chr, '020b')
            pairs = [chr_bin[j:j+2] for j in range(0, 20, 2)]

            line = f"#{i}: Score={snake.score} Len={len(snake.body)} Energy={snake.energy}/{snake.max_energy}"
            text = font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (x_offset, y))
            y += 18

            pair_x = x_offset + 5
            for idx, pair in enumerate(pairs):
                color = colors[idx % len(colors)]
                pair_text = font.render(pair, True, color)
                self.screen.blit(pair_text, (pair_x, y))
                pair_x += pair_text.get_width() + 2
            y += 18

            color_line = f"Color: {snake.color} | Fitness: {config.LENGTH_WEIGHT * len(snake.body) + config.ENERGY_WEIGHT * (snake.energy//100) + config.SCORE_WEIGHT * snake.score}"
            text = font.render(color_line, True, (255, 255, 255))
            self.screen.blit(text, (x_offset + 5, y))
            y += 20

        # Always show static stats too
        
            
    def draw(self, snakes, foods, generation, tick):
        self.screen.fill((0, 0, 0))
        self.draw_terrain()
        self.draw_food(foods)
        self.draw_snakes(snakes)
        self.draw_stats(snakes, foods, generation, tick)
        pygame.display.flip()
        self.clock.tick(config.FPS)