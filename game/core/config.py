WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 1000
TILE_SIZE = 10
STATS_WIDTH = 300

FPS = 20
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

SNAKE_COLORS = { # generated with coolors.co palette generator
    "darkblue": (3, 37, 108),
    "pink": (247, 174, 248),
    "orange": (209, 122, 34),
    "neongreen": (5, 241, 64),
    "lightblue": (34, 174, 209),
    "olive": (162, 173, 89),
    "indigo": (84, 13, 110),
    "darkgreen": (42, 77, 20),
    "black": (12, 9, 13),
    "magenta": (186, 44, 115),
    "red": (253, 21, 27),
    "green": (53, 134, 0),
    "palegreen": (178, 239, 155),
    "pistachio": (187, 214, 134),
    "amber": (255, 191, 0),
    "lapis": (18, 94, 138),
    "mindaro": (219, 254, 135),
    "lilac": (181, 148, 182),
    "winered": (119, 51, 68),
    "lavender": (171, 129, 205),
    "neoncyan": (0, 229, 232),
    "navyblue": (21, 5, 120),
    "lightgreen": (171, 255, 79),
    "purple": (125, 91, 166),
    "mint": (9, 188, 138),
    "pumpkinorange": (249, 105, 0),
    "pear": (220, 237, 49),
    "ceruleanblue": (66, 129, 164),
    "coral": (235, 130, 88),
    "aquamarine": (35, 240, 199),
    "jasper": (199, 81, 70),
    "absred": (250, 0, 0),
    "absgreen": (0, 250, 0),
    "absblue": (0, 0, 250),
}  