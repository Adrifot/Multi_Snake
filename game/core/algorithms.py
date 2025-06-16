import heapq
from collections import deque


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(grid, pos, vision_range=None):
    x, y = pos
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
            if grid[ny][nx] != 999:  # Skip obstacles
                if vision_range is None or manhattan(pos, (nx, ny)) <= vision_range:
                    neighbors.append((nx, ny))
    return neighbors


def foods_in_vision(snake_pos, foods, vision_range):
    visible = []
    for food in foods:
        if manhattan(snake_pos, food) <= vision_range:
            visible.append(food)
    return visible


# ------- PATHFINDING -------
def greedy(grid, start, goals, vision_range):
    goals = set(goals)
    queue = deque([start])
    came_from = {start: None}
    
    while queue:
        current = queue.popleft()
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        neighbors = get_neighbors(grid, current, vision_range)
        neighbors.sort(key=lambda n: min(manhattan(n, g) for g in goals)) 
        
        for neighbor in neighbors:
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)
    
    return None  


def bfs(grid, start, goals, vision_range):
    goals = set(goals)
    queue = deque([start])
    came_from = {start: None}
    
    while queue:
        current = queue.popleft()
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        for neighbor in get_neighbors(grid, current, vision_range):
            if neighbor not in came_from:
                came_from[neighbor] = current
                queue.append(neighbor)
    
    return None 


def dijkstra(grid, start, goals, vision_range):
    goals = set(goals)
    heap = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while heap:
        cost, current = heapq.heappop(heap)
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        for neighbor in get_neighbors(grid, current, vision_range):
            nx, ny = neighbor
            new_cost = cost + grid[ny][nx]
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))
                came_from[neighbor] = current
    
    return None  


def a_star(grid, start, goals, vision_range):
    goals = set(goals)
    heap = [(0 + min(manhattan(start, g) for g in goals), 0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while heap:
        _, cost, current = heapq.heappop(heap)
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        
        for neighbor in get_neighbors(grid, current, vision_range):
            new_cost = cost + grid[neighbor[1]][neighbor[0]]  
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + min(manhattan(neighbor, g) for g in goals)
                heapq.heappush(heap, (priority, new_cost, neighbor))
                came_from[neighbor] = current
    return None  


__all__ = ['a_star', 'bfs', 'greedy', 'foods_in_vision']