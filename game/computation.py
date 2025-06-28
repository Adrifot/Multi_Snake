import numpy as np
from simulation.world import World

def get_mean_of_terrain_averages(generator_func, generations):
    """
    generator_func: a function that returns a terrain grid when called
    generations: how many times to generate terrain and average it
    """
    averages = []
    for _ in range(generations):
        grid = generator_func()
        avg = np.mean(grid)
        averages.append(avg)
    mean_of_averages = np.mean(averages)
    return mean_of_averages


# Example if your terrain generator is a class:
world = World()  # Or whatever your terrain class is

mean_avg = get_mean_of_terrain_averages(world.generate_perlin_terrain, 1000)

print("Mean of terrain cost averages:", mean_avg)