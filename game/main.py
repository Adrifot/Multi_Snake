#!/usr/bin/env python3
import pygame
import argparse
from simulation.controller import GameController
import core.config as config

def parse_args():
    """Handle command-line arguments for customization."""
    parser = argparse.ArgumentParser(description='Snake Genetic Simulation')
    parser.add_argument('--speed', type=int, default=config.FPS, 
                       help=f'Simulation speed (default: {config.FPS})')
    parser.add_argument('--grid', type=str, default=f"{config.WINDOW_X//config.TILE_SIZE}x{config.WINDOW_Y//config.TILE_SIZE}",
                       help='Grid size WxH (e.g., 100x80)')
    parser.add_argument('--snakes', type=int, default=5,
                       help='Number of snakes (default: 5)')
    return parser.parse_args()

def main():
    # try:
        args = parse_args()
        
        # Override config if args provided
        if args.grid:
            w, h = map(int, args.grid.split('x'))
            config.WINDOW_X = w * config.TILE_SIZE
            config.WINDOW_Y = h * config.TILE_SIZE
        config.FPS = args.speed

        print(f"Starting simulation with {args.snakes} snakes at {args.grid} grid")
        
        controller = GameController()
        controller.run()
        
    # except Exception as e:
    #     print(f"Error: {e}")
    #     pygame.quit()
    # finally:
        pygame.quit()

if __name__ == "__main__":
    main()