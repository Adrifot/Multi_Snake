WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
TILE_SIZE = 10
STATS_WIDTH = 300

FPS = 15
FOOD_NR = 50
FOOD_ENERGY = 250 # energy provided by 1 food with energy factor gene encoding 10 or 01
FOOD_RESPAWN_RATE = 100 # ticks

SHRINK_ENERGY_INTERVAL = 200 # energy spent before shrinking

SNAKE_COUNT = 25
SNAKE_GENERATION_INTERVAL = 500

# Fitness weights
LENGTH_WEIGHT = 3
SCORE_WEIGHT = 3
ENERGY_WEIGHT = 1

LAND_COLORS = {
    1: (105, 153, 93),  # green fields
    3: (237, 180, 88),  # yellow hills
    7: (49, 39, 32),  # brown mountains 
    999: (25, 20, 16) # dark impassable peaks
}

FOOD_COLORS = {
    "low": (150, 150, 150),
    "med": (200, 200, 200),
    "high": (250, 250, 250),
}

SNAKE_COLORS = {
    "blue": (38, 84, 124),
    "lightblue": (110, 250, 251),
    "darkblue": (9, 77, 146),
    "pink": (239, 71, 111),
    "darkgreen": (13, 40, 24),
    "purple": (105, 3, 117),
    "yellow": (254, 228, 64),
    "black": (0, 0, 0),
    "red": (219, 22, 47),
    "darkred": (147, 3, 46),
    "cyan": (0, 255, 231),
    "gray": (120, 138, 163),
    "beige": (255, 202, 212)
}  