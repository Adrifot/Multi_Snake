import pygame
from simulation.controller import GameController
import core.config as config

def main():
    print(f"Starting simulation with {config.SNAKE_COUNT} snakes in a {config.WINDOW_WIDTH // config.TILE_SIZE}x{config.WINDOW_HEIGHT // config.TILE_SIZE} grid")
    controller = GameController()
    controller.run()
    
if __name__ == "__main__":
    main()