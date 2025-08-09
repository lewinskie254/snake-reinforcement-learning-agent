import heapq
from common import Point

def heuristic(a, b):
    return abs(a.x - b.x) + abs(a.y - b.y)

def get_neighbors(pos, block_size, width, height, border):
    neighbors = []
    for dx, dy in [(-block_size, 0), (block_size, 0), (0, -block_size), (0, block_size)]:
        x2, y2 = pos.x + dx, pos.y + dy
        if border <= x2 < width - border and border <= y2 < height - border:
            neighbors.append(Point(x2, y2))
    return neighbors

def a_star(start, goal, snake_body, width, height, block_size, border):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    visited = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path  # path starts with NEXT tile, not head

        visited.add(current)

        for neighbor in get_neighbors(current, block_size, width, height, border):
            if neighbor in snake_body or neighbor in visited:
                continue

            tentative_g = g_score[current] + 1
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return []
