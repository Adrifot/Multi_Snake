import pygame
import time
import random

snake_speed = 15

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
pygame.display.set_caption('Serpisorul nazdravan')
game_window = pygame.display.set_mode((window_x, window_y))

fps = pygame.time.Clock() # fps controller

snake_position = [100, 50] # default snake position

snake_body = [[100, 50], [90, 50], [80, 50], [70, 50]] # default snake body - the first 4 blocks

fruit_position = [random.randrange(1, (window_x//10))*10, random.randrange(1, (window_y//10))*10] 
fruit_spawn = True # fruit spawn flag

# Default direction
direction = "RIGHT"
change_to = direction

score = 0 # initial score

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
    
    # Key-press event handling
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = "UP"
            if event.key == pygame.K_DOWN:
                change_to = "DOWN"
            if event.key == pygame.K_LEFT:
                change_to = "LEFT"
            if event.key == pygame.K_RIGHT:
                change_to = "RIGHT"
    
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