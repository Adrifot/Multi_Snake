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
    """Controls game graphics"""
    def __init__(self, world):
        pygame.init()
        self.world = world
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH + config.STATS_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption(f"Snake Genetics Simulation")
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_large = pygame.font.SysFont("Arial", 24)
        self.clock = pygame.time.Clock()
        
        
    def draw_terrain(self):
        """Draww world map"""
        for x in range(self.world.grid.shape[0]):
            for y in range(self.world.grid.shape[1]):
                terrain_type = self.world.grid[x][y]
                color = config.LAND_COLORS.get(terrain_type, (0, 0, 0))
                pygame.draw.rect(
                    self.screen, color,
                    (y * config.TILE_SIZE, x * config.TILE_SIZE, 
                    config.TILE_SIZE, config.TILE_SIZE)
                )


    def draw_snakes(self, snakes):
        """Draw snake entities"""
        if snakes is None:
            snakes = []
        for snake in snakes:
            if not snake.alive:
                continue
            for i, segment in enumerate(snake.body):
                pygame.draw.rect(
                    self.screen, snake.color,
                    (segment[1] * config.TILE_SIZE, segment[0] * config.TILE_SIZE,  
                    config.TILE_SIZE, config.TILE_SIZE)
                )


    def draw_food(self, foods):
        """Draw food entities"""
        for food in foods:
            # Decide color based on toxicity and energy factor
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
            
            
    def draw_snake_path(self, snake):
        """Draw current path for a selected snake"""
        if not hasattr(snake, "path") or not snake.path:
            return
        points = [(y * config.TILE_SIZE + config.TILE_SIZE // 2,
                x * config.TILE_SIZE + config.TILE_SIZE // 2)
                for x, y in snake.path]
        if len(points) > 1:
            pygame.draw.lines(self.screen, (255, 255, 0), False, points, 3)

        
    def draw_stats(self, snakes, foods, generation, tick, selected_entity):
        """Render current world stats"""
        
        if not snakes:
            return
        
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
            color_name = next((name for name, rgb in config.SNAKE_COLORS.items() if rgb == snake.color), str(snake.color))
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

            color_line = f"Color: {color_name} | Fitness: {config.LENGTH_WEIGHT * len(snake.body) + config.ENERGY_WEIGHT * (snake.energy//100) + config.SCORE_WEIGHT * snake.score}"
            text = font.render(color_line, True, (255, 255, 255))
            self.screen.blit(text, (x_offset + 5, y))
            y += 40

        y += 20
        if selected_entity is not None:
            self.screen.blit(self.font_large.render("Selected Entity:", True, (255,255,0)), (x_offset, y))
            y += 28
            if hasattr(selected_entity, "body"):  # Snake
                chr_bin = format(selected_entity.chr, '020b')
                chr_spaced = ' '.join([chr_bin[i:i+2] for i in range(0, 20, 2)])
                # Find color name from RGB tuple
                color_name = next((name for name, rgb in config.SNAKE_COLORS.items() if rgb == selected_entity.color), str(selected_entity.color))
                self.draw_snake_path(selected_entity)
                self.screen.blit(self.font_small.render(f"Type: Snake", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Score: {selected_entity.score}", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Length: {len(selected_entity.body)}", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Energy: {selected_entity.energy}/{selected_entity.max_energy}", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Color: {color_name}", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Genes: {chr_spaced}", True, (0,255,0)), (x_offset, y)); y += 18
            elif hasattr(selected_entity, "position"):  # Food
                self.screen.blit(self.font_small.render(f"Type: Food", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Energy Factor: {getattr(selected_entity, 'energy_factor', '?')}", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Toxic: {getattr(selected_entity, 'toxic', '?')}", True, (255,255,255)), (x_offset, y)); y += 18
                self.screen.blit(self.font_small.render(f"Genes: {format(getattr(selected_entity, 'chromosome', 0), '05b')}", True, (0,255,0)), (x_offset, y)); y += 18
    
    def draw_selected_entity_contour(self, selected_entity):
        """Draw a yellow contour around the selected entity."""
        if selected_entity is None:
            return
        contour_color = (255, 255, 0)  # Yellow

        if hasattr(selected_entity, "body"):  # Snake
            for segment in selected_entity.body:
                rect = pygame.Rect(
                    segment[1] * config.TILE_SIZE,
                    segment[0] * config.TILE_SIZE,
                    config.TILE_SIZE,
                    config.TILE_SIZE
                )
                pygame.draw.rect(self.screen, contour_color, rect, 1)
        elif hasattr(selected_entity, "position"):  # Food
            pos = selected_entity.position
            rect = pygame.Rect(
                pos[1] * config.TILE_SIZE,
                pos[0] * config.TILE_SIZE,
                config.TILE_SIZE,
                config.TILE_SIZE
            )
            pygame.draw.rect(self.screen, contour_color, rect, 3)
            
    def show_game_over_screen(self, message="SIMULATION OVER"):
        font = pygame.font.SysFont("Arial", 48)
        text = font.render(message, True, (255, 0, 0))
        subfont = pygame.font.SysFont("Arial", 24)
        subtext = subfont.render("Press any key to exit...", True, (255, 255, 255))
        self.screen.fill((0, 0, 0))
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2,
                                self.screen.get_height() // 2 - text.get_height()))
        self.screen.blit(subtext, (self.screen.get_width() // 2 - subtext.get_width() // 2,
                                self.screen.get_height() // 2 + 20))
        pygame.display.flip()
        
            
    def draw(self, snakes, foods, generation, tick, selected_entity):
        """General function that combines all other Renderer class methods"""
        self.screen.fill((0, 0, 0))
        self.draw_terrain()
        self.draw_food(foods)
        self.draw_snakes(snakes)
        self.draw_selected_entity_contour(selected_entity)
        self.draw_stats(snakes, foods, generation, tick, selected_entity)
        pygame.display.flip()
        self.clock.tick(config.FPS)