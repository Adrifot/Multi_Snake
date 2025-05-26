import pygame
import time
import random
import heapq

snake_speed = 100

# Window size
window_x = 720
window_y = 480

black = pygame.Color(0, 0, 0)  
white = pygame.Color(255, 255, 255) 
red = pygame.Color(255, 0, 0)  
green = pygame.Color(0, 255, 0)  
blue = pygame.Color(0, 0, 255) 

pygame.init()

# Game window init 
pygame.display.set_caption('Serpisorul nazdravan care se joaca singur')
game_window = pygame.display.set_mode((window_x, window_y))

fps = pygame.time.Clock() # fps controller

snake_position = [100, 50] # default snake position
snake_body = [[100, 50], [90, 50], [80, 50]] # default snake body - the first 3 blocks

fruit_position = [random.randrange(1, (window_x//10))*10, random.randrange(1, (window_y//10))*10] 
fruit_spawn = True # fruit spawn flag

# Default direction
direction = "RIGHT"
change_to = direction

score = 0 # initial score

# A* pathfinding
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start to current node
        self.h = 0  # Heuristic 
        self.f = 0  # Total cost (g + h)
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    # Manhattan distance 
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(snake_body, start, end, grid_size):
    start_node = Node(start)
    end_node = Node(end)
    open_list = []
    closed_set = set()  
    heapq.heappush(open_list, (start_node.f, start_node))
    movements = [(0, -10), (0, 10), (-10, 0), (10, 0)]
    snake_set = set(tuple(segment) for segment in snake_body[:-1])  

    while open_list:
        current_node = heapq.heappop(open_list)[1]
        closed_set.add(current_node.position)

        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]

        for move in movements:
            node_position = (current_node.position[0] + move[0], current_node.position[1] + move[1])
            if (node_position[0] < 0 or node_position[0] >= grid_size[0] or 
                node_position[1] < 0 or node_position[1] >= grid_size[1]):
                continue
            if node_position in snake_set:
                continue
            if node_position in closed_set:
                continue

            new_node = Node(node_position, current_node)
            new_node.g = current_node.g + 10
            new_node.h = heuristic(new_node.position, end_node.position)
            new_node.f = new_node.g + new_node.h

            # Only add to open_list if not already present with lower g
            skip = False
            for f, open_node in open_list:
                if new_node == open_node and new_node.g >= open_node.g:
                    skip = True
                    break
            if not skip:
                heapq.heappush(open_list, (new_node.f, new_node))

    return None

def get_next_move(snake_body, fruit_position):
    grid_size = (window_x, window_y)
    path = a_star_search(snake_body, tuple(snake_body[0]), tuple(fruit_position), grid_size)
    
    if path and len(path) > 1:
        next_pos = path[1]  # path[0] is current position
        current_pos = snake_body[0]
        
        if next_pos[0] > current_pos[0]:
            return "RIGHT"
        elif next_pos[0] < current_pos[0]:
            return "LEFT"
        elif next_pos[1] > current_pos[1]:
            return "DOWN"
        elif next_pos[1] < current_pos[1]:
            return "UP"
    
    # If no path found, continue in current direction or find safe move
    return direction

# Score display func
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size) # font object
    score_surface = score_font.render("Score : " + str(score), True, color) # display surface object
    score_rect = score_surface.get_rect() # create rect object for text surface
    game_window.blit(score_surface, score_rect) # display text
    
# Game over func
def game_over():
    my_font = pygame.font.SysFont("papyrus", 50) # font obj
    game_over_surface = my_font.render("Your score is : " + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (window_x/2, window_y/2) # setting text position
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    quit()

# Main code
while True:
    # AI decision making
    change_to = get_next_move(snake_body, fruit_position)
    
    # Don't let the snake make 180 direction changes          
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'
        
    # Moving the snake
    if direction == 'UP':
        snake_position[1] -= 10
    if direction == 'DOWN':
        snake_position[1] += 10
    if direction == 'LEFT':
        snake_position[0] -= 10
    if direction == 'RIGHT':
        snake_position[0] += 10
        
    # Body growing logic
    snake_body.insert(0, list(snake_position))
    if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
        score += 10
        fruit_spawn = False
    else:
        snake_body.pop()
        
    if not fruit_spawn:
        fruit_position = [random.randrange(1, (window_x//10)) * 10, random.randrange(1, (window_y//10)) * 10]
        
    fruit_spawn = True
    game_window.fill(black)
    
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
        
    pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))
    
    # Game over conditions
    # wall collide
    if snake_position[0] < 0 or snake_position[0] > window_x-10:
        game_over()
    if snake_position[1] < 0 or snake_position[1] > window_y-10:
        game_over()
        
    # self collide
    for block in snake_body[1:]:
        if snake_position[0] == block[0] and snake_position[1] == block[1]:
            game_over()
    
    show_score(1, white, "papyrus", 20) # display score continuously
    pygame.display.update() # refresh screen
    fps.tick(snake_speed) # refresh rate