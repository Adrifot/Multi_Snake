import heapq
from collections import deque

def manhattan(a, b):
    """Calculate Manhattan distance between two points (x1,y1) and (x2,y2)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(grid, pos, current_direction=None):
    """Return valid neighbor positions (x, y) for a given position (x, y) in the grid."""
    x, y = pos
    neighbors = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    if current_direction is not None:
        opposite_dir = (-current_direction[0], -current_direction[1])
        directions = [d for d in directions if d != opposite_dir]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if grid[nx][ny] != 999:
                neighbors.append((nx, ny))
    return neighbors

def foods_in_vision(snake_pos, foods, vision_range):
    """Find foods within vision range of snake_pos (x, y)"""
    return [food for food in foods if manhattan(snake_pos, food) <= vision_range]

def greedy(grid, start, goals, vision_range, obstacles=None, current_direction=None):
    """Greedy best-first search: always expand the node closest to any goal."""
    goals = set(goals)
    queue = deque([start])
    came_from = {start: None}
    visited = set([start])

    while queue:
        current = queue.popleft()
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        neighbors = get_neighbors(grid, current, current_direction)
        if obstacles:
            neighbors = [n for n in neighbors if n not in obstacles]
        # Only consider neighbors within vision range of the start
        neighbors = [n for n in neighbors if manhattan(start, n) <= vision_range]

        # Sort neighbors by distance to closest goal
        neighbors.sort(key=lambda n: min(manhattan(n, g) for g in goals))

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
    return None

def bfs(grid, start, goals, vision_range, obstacles=None, current_direction=None):
    """Breadth-first search for shortest path (ignores terrain cost)."""
    goals = set(goals)
    queue = deque([start])
    came_from = {start: None}
    visited = set([start])

    while queue:
        current = queue.popleft()
        if current in goals:
            path = []
            while current != start:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        neighbors = get_neighbors(grid, current, current_direction)
        if obstacles:
            neighbors = [n for n in neighbors if n not in obstacles]
        neighbors = [n for n in neighbors if manhattan(start, n) <= vision_range]

        for neighbor in neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
    return None

def ucs(grid, start, goals, vision_range, obstacles=None, current_direction=None):
    """UCS algorithm for lowest-cost path (terrain cost)."""
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

        neighbors = get_neighbors(grid, current, current_direction)
        if obstacles:
            neighbors = [n for n in neighbors if n not in obstacles]
        neighbors = [n for n in neighbors if manhattan(start, n) <= vision_range]

        for neighbor in neighbors:
            new_cost = cost + grid[neighbor[0]][neighbor[1]]
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                heapq.heappush(heap, (new_cost, neighbor))
                came_from[neighbor] = current
    return None

def a_star(grid, start, goals, vision_range, obstacles=None, current_direction=None):
    """A* search for lowest-cost path with heuristic (terrain cost + manhattan)."""
    goals = set(goals)
    heap = [(min(manhattan(start, g) for g in goals), 0, start)]
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

        neighbors = get_neighbors(grid, current, current_direction)
        if obstacles:
            neighbors = [n for n in neighbors if n not in obstacles]
        neighbors = [n for n in neighbors if manhattan(start, n) <= vision_range]

        for neighbor in neighbors:
            new_cost = cost + grid[neighbor[0]][neighbor[1]]
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + min(manhattan(neighbor, g) for g in goals)
                heapq.heappush(heap, (priority, new_cost, neighbor))
                came_from[neighbor] = current
    return None

__all__ = ['a_star', 'bfs', 'greedy', 'foods_in_vision', 'ucs']