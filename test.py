from game.snake import Snake

snake_A = Snake(1, 1, "green")
snake_B = Snake(1, 1, "black")

snake_C = Snake(1, 1, "purple", snake_A.chr, snake_B.chr)

print(snake_A)
print(snake_B)
print(snake_C)

snake_C.mutate()
print("Mutated: ")
print(snake_C)