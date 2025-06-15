from game.snake import Snake

snake_A = Snake(1, 1, "green")
snake_B = Snake(1, 1, "black")

snake_C = Snake(1, 1, "purple", snake_A.chr, snake_B.chr)

print("Parent 1: " + bin(snake_A.chr) + "\n")
print("Parent 2: " + bin(snake_B.chr) + "\n")
print("Child: " + bin(snake_C.chr) + "\n")

snake_C.mutate()
print("Child after mutation: " + bin(snake_C.chr) + "\n")