import pygame
import time
import random
import heapq

snake_speed = 20 # frames per second

# Window size
window_x = 800
window_y = 800

black = pygame.Color(0, 0, 0)  
white = pygame.Color(255, 255, 255) 
red = pygame.Color(255, 0, 0)  
green = pygame.Color(0, 255, 0)  
blue = pygame.Color(0, 0, 255) 
yellow = pygame.Color(255, 255, 0)
purple = pygame.Color(128, 0, 128)
orange = pygame.Color(255, 165, 0)
pink = pygame.Color(255, 192, 203)
# reminder: add more colors later 

pygame.init()

pygame.display.set_caption('Mai multi serpisori nazdravani')
game_window = pygame.display.set_mode((window_x, window_y))
fps = pygame.time.Clock()

# === CONFIGURABLE VARS ===

M = 5 # Number of foods
N = 3 # Number of snakes

# Food positions
foods = [
    [random.randrange(1, (window_x//10))*10, random.randrange(1, (window_y//10))*10]
    for _ in range(M)
]

# Snake structure: position, body, direction, alive, score, color
snakes = []
snake_colors = [green, blue, red, orange, yellow, purple, pink]
for i in range(N): # For now, all snakes spawn in parallel in the top-left corner (TO BE CHANGED)
    start_x = 100 + i*30
    color = snake_colors[i % len(snake_colors)]
    snake = {
        'position': [start_x, 50],
        'body': [[start_x, 50], [start_x-10, 50], [start_x-20, 50]],
        'direction': "RIGHT",
        'alive': True,
        'score': 0,
        'color': color
    }
    snakes.append(snake)

# === PATHFINDING - A* ===
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b): # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(snake_body, start, end, grid_size, all_snake_bodies):
    start_node = Node(start)
    end_node = Node(end)
    open_list = [] # Frontier
    closed_set = set() # Already explored nodes
    heapq.heappush(open_list, (start_node.f, start_node))
    
    movements = [(0, -10), (0, 10), (-10, 0), (10, 0)]
    
    # Avoid all snakes' bodies except the tail of the current snake
    snake_set = set()
    for body in all_snake_bodies:
        snake_set.update(tuple(segment) for segment in body) # Each tile already occupied by a snake
    
    if len(snake_body) > 0: # Allow the tail of the current snake (it will move anyway)
        snake_set.discard(tuple(snake_body[-1]))

    while open_list: # While there are nodes to explore
        current_node = heapq.heappop(open_list)[1] # Get the node with the lowest f value
        closed_set.add(current_node.position) # Mark as explored

        if current_node == end_node: # Found the goal node
            path = []
            current = current_node
            while current is not None: # Reconstruct path by following parent nodes
                path.append(current.position)
                current = current.parent
            return path[::-1]

        for move in movements: # Check all possible movements and discard invalid ones
            node_position = (current_node.position[0] + move[0], current_node.position[1] + move[1])
            if (node_position[0] < 0 or node_position[0] >= grid_size[0] or # Out of bounds
                node_position[1] < 0 or node_position[1] >= grid_size[1]):
                continue
            if node_position in snake_set: # Occupied with a snake body
                continue
            if node_position in closed_set: # Already explored
                continue

            # Otherwise, create a new node and calculate its g, h, f values
            new_node = Node(node_position, current_node)
            new_node.g = current_node.g + 10
            new_node.h = heuristic(new_node.position, end_node.position)
            new_node.f = new_node.g + new_node.h

            # Check if this node is already in the open list with a better g value
            skip = False
            for f, open_node in open_list:
                if new_node == open_node and new_node.g >= open_node.g:
                    skip = True
                    break
            if not skip:
                heapq.heappush(open_list, (new_node.f, new_node))

    return None

def get_next_move(snake, foods, snakes):
    # Find closest food
    min_dist = float('inf')
    target_food = None
    for food in foods:
        dist = heuristic(tuple(snake['position']), tuple(food))
        if dist < min_dist:
            min_dist = dist
            target_food = food
    if not target_food:
        return snake['direction']

    # Gather all snake bodies (except current snake) for collision detection
    all_bodies = []
    for s in snakes:
        if s['alive']:
            if s is snake:
                all_bodies.append(s['body'][:-1])  # Exclude tail from current snake
            else:
                all_bodies.append(s['body'])

    grid_size = (window_x, window_y)
    
    path = a_star_search(snake['body'], tuple(snake['position']), tuple(target_food), grid_size, all_bodies)
    if path and len(path) > 1:
        next_pos = path[1]
        current_pos = snake['position']
        if next_pos[0] > current_pos[0]:
            return "RIGHT"
        elif next_pos[0] < current_pos[0]:
            return "LEFT"
        elif next_pos[1] > current_pos[1]:
            return "DOWN"
        elif next_pos[1] < current_pos[1]:
            return "UP"
    return snake['direction']

def show_score(snakes):
    font = pygame.font.SysFont("papyrus", 20)
    y = 10
    for idx, snake in enumerate(snakes):
        score_surface = font.render(f"Snake {idx+1}: {snake['score']}", True, snake['color'])
        score_rect = score_surface.get_rect(topleft=(10, y))
        game_window.blit(score_surface, score_rect)
        y += 25

def game_over(snakes):
    game_window.fill(black)
    font = pygame.font.SysFont("papyrus", 50)
    y = window_y // 2 - 50
    for idx, snake in enumerate(snakes):
        msg = f"Snake {idx+1} score: {snake['score']}"
        surface = font.render(msg, True, snake['color'])
        rect = surface.get_rect(center=(window_x//2, y))
        game_window.blit(surface, rect)
        y += 60
    pygame.display.flip()
    time.sleep(5)
    pygame.quit()
    quit()

# === MAIN LOOP ===
while any(s['alive'] for s in snakes):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    for snake in snakes:
        if not snake['alive']:
            continue

        # AI decision
        change_to = get_next_move(snake, foods, snakes)
        
        # Prevent 180 turns
        if change_to == 'UP' and snake['direction'] != 'DOWN':
            snake['direction'] = 'UP'
        if change_to == 'DOWN' and snake['direction'] != 'UP':
            snake['direction'] = 'DOWN'
        if change_to == 'LEFT' and snake['direction'] != 'RIGHT':
            snake['direction'] = 'LEFT'
        if change_to == 'RIGHT' and snake['direction'] != 'LEFT':
            snake['direction'] = 'RIGHT'

        # Move snake
        if snake['direction'] == 'UP':
            snake['position'][1] -= 10
        if snake['direction'] == 'DOWN':
            snake['position'][1] += 10
        if snake['direction'] == 'LEFT':
            snake['position'][0] -= 10
        if snake['direction'] == 'RIGHT':
            snake['position'][0] += 10

        # Insert new head
        snake['body'].insert(0, list(snake['position']))

        # Check for food collision
        ate_food = False
        for food in foods:
            if snake['position'][0] == food[0] and snake['position'][1] == food[1]:
                snake['score'] += 10
                foods.remove(food)
                foods.append([random.randrange(1, (window_x//10))*10, random.randrange(1, (window_y//10))*10])
                ate_food = True
                break
        if not ate_food:
            snake['body'].pop()

        # Wall collision
        if (snake['position'][0] < 0 or snake['position'][0] > window_x-10 or
            snake['position'][1] < 0 or snake['position'][1] > window_y-10):
            snake['alive'] = False
            continue

        # Self collision
        if snake['position'] in snake['body'][1:]:
            snake['alive'] = False
            continue

        # Collision with other snakes
        for other in snakes:
            if other is snake or not other['alive']:
                continue
            if snake['position'] in other['body']:
                snake['alive'] = False
                break

    # Draw everything
    game_window.fill(black)
    for food in foods:
        pygame.draw.rect(game_window, white, pygame.Rect(food[0], food[1], 10, 10))
    for snake in snakes:
        if snake['alive']:
            for pos in snake['body']:
                pygame.draw.rect(game_window, snake['color'], pygame.Rect(pos[0], pos[1], 10, 10))
    show_score(snakes)
    pygame.display.update()
    fps.tick(snake_speed)

game_over(snakes)