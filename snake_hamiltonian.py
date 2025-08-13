# snake_hybrid_meander.py
# Hybrid Snake: A* + Hamiltonian PATH + Meander fallback
# Usage: python snake_hybrid_meander.py

import pygame
import sys
import random
from collections import deque, deque as DQ
import heapq

# ---------- CONFIG ----------
CELL_SIZE = 20
GRID_W = 20
GRID_H = 15
WINDOW_MARGIN = 20
FPS = 12
START_LENGTH = 4

# Colors
BG = (12, 12, 12)
PLAY_BG = (18, 18, 20)
GRID_COLOR = (40, 40, 40)
SNAKE_HEAD = (80, 220, 80)
SNAKE_BODY = (40, 160, 40)
FOOD_COLOR = (220, 50, 50)
TEXT_COLOR = (230, 230, 230)

# ---------- HELPERS ----------
def in_bounds(pos):
    x, y = pos
    return 0 <= x < GRID_W and 0 <= y < GRID_H

def neighbors(pos):
    x, y = pos
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
        nx, ny = x+dx, y+dy
        if 0 <= nx < GRID_W and 0 <= ny < GRID_H:
            yield (nx, ny)

def manhattan(a,b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ---------- HAMILTONIAN PATH (serpentine) ----------
def build_hamiltonian_path(width, height):
    path = []
    for y in range(height):
        if y % 2 == 0:
            for x in range(width):
                path.append((x, y))
        else:
            for x in range(width - 1, -1, -1):
                path.append((x, y))
    return path

# ---------- A* PATHFINDING ----------
def astar(start, goal, blocked_set):
    """A* from start to goal avoiding blocked_set (set of coords).
       If goal is in blocked_set, we still allow it (food sits there).
       Returns list of coords from start's neighbor ... goal (not including start),
       or None if no path.
    """
    def h(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
    open_heap = []
    heapq.heappush(open_heap, (h(start, goal), 0, start))
    came_from = {}
    gscore = {start: 0}
    closed = set()
    allowed_goal = goal

    while open_heap:
        _, g, current = heapq.heappop(open_heap)
        if current == goal:
            # Reconstruct path (exclude start)
            path = []
            node = current
            while node != start:
                path.append(node)
                node = came_from[node]
            path.reverse()
            return path
        if current in closed:
            continue
        closed.add(current)

        for nb in neighbors(current):
            if nb != allowed_goal and nb in blocked_set:
                continue
            tentative = g + 1
            if tentative < gscore.get(nb, float('inf')):
                came_from[nb] = current
                gscore[nb] = tentative
                f = tentative + h(nb, goal)
                heapq.heappush(open_heap, (f, tentative, nb))
    return None

# ---------- FLOOD-FILL (space estimation) ----------
def flood_fill_count(start, blocked_set):
    """Return number of reachable free cells from start (excluding blocked_set).
       We treat positions in blocked_set as walls.
    """
    if start in blocked_set or not in_bounds(start):
        return 0
    q = deque([start])
    visited = set([start])
    count = 0
    while q:
        cur = q.popleft()
        count += 1
        for nb in neighbors(cur):
            if nb in visited or nb in blocked_set:
                continue
            visited.add(nb)
            q.append(nb)
    return count

# ---------- SAFETY CHECKS ----------
def simulate_path_and_check_tail_reachable(snake_deque, path_to_food, food_pos):
    """
    Simulate moving the snake along the provided path (list of coords) until food eaten
    and then check whether after eating there exists a path from new head to the tail
    (i.e., the snake won't be trapped).
    Returns True if safe, False otherwise.
    """
    sim_snake = deque(snake_deque)  # copy
    # Simulate steps
    for step in path_to_food:
        # Move head
        sim_snake.appendleft(step)
        if step == food_pos:
            # we ate food -> grow (do NOT pop tail this turn)
            break
        else:
            sim_snake.pop()

    # After eating (or finishing path if it passed through), check that head can reach tail
    head = sim_snake[0]
    tail = sim_snake[-1]
    blocked = set(sim_snake)
    # allow tail as reachable target since tail will move in future (we can treat it as free)
    blocked.remove(tail)
    # BFS from head to tail avoiding blocked
    q = deque([head])
    seen = set([head])
    while q:
        cur = q.popleft()
        if cur == tail:
            return True
        for nb in neighbors(cur):
            if nb in seen or nb in blocked:
                continue
            seen.add(nb)
            q.append(nb)
    return False

# ---------- MEANDER (safe space-maximizing move) ----------
def meander_move(head, snake_set, tail_pos):
    """
    Consider all legal neighbor moves (not into snake body except tail),
    score each by flood_fill_count (treating tail as free), and return the best next cell.
    Tie-breaker: smaller Manhattan distance to food is not used here; caller may prefer that.
    """
    best = None
    best_score = -1
    for nb in neighbors(head):
        # allow moving into tail (safe) because tail will move away unless we're about to grow
        if nb in snake_set and nb != tail_pos:
            continue
        # For counting space, treat tail as free because it moves
        blocked = set(snake_set)
        if tail_pos in blocked:
            blocked.remove(tail_pos)
        # temporarily mark nb as occupied (we move there)
        blocked.add(nb)
        # flood from nb
        score = flood_fill_count(nb, blocked)
        # prefer larger score
        if score > best_score:
            best_score = score
            best = nb
    return best

# ---------- GAME ----------
class HybridMeanderSnake:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen_w = GRID_W * CELL_SIZE + WINDOW_MARGIN*2
        self.screen_h = GRID_H * CELL_SIZE + WINDOW_MARGIN*2
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Snake — Hybrid A* + Hamiltonian Path + Meander")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 20)
        self.bigfont = pygame.font.SysFont(None, 36)

        # Precompute serpentine Hamiltonian path
        self.path = build_hamiltonian_path(GRID_W, GRID_H)
        self.pos_to_index = {pos:i for i,pos in enumerate(self.path)}
        self.path_len = len(self.path)

        self.reset()

    def reset(self):
        # Initialize snake using first START_LENGTH cells of Hamiltonian path
        self.snake = deque(self.path[:START_LENGTH])  # head at left (index 0)
        self.food = None
        self.spawn_food()
        self.speed = FPS
        self.score = 0
        self.paused = False
        self.game_over = False
        self.win = False
        # Track Hamiltonian direction and head_index for fallback
        self.direction = 1  # +1 forward, -1 backward along path indices
        self.head_index = START_LENGTH - 1  # matches self.snake[0] position in path
        # planned A* path being followed (list of coords excluding current head)
        self.planned_astar = []

    def spawn_food(self):
        free = [pos for pos in self.path if pos not in self.snake]
        self.food = random.choice(free) if free else None

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if ev.key == pygame.K_p:
                    self.paused = not self.paused
                if ev.key == pygame.K_r:
                    self.reset()
                if ev.key == pygame.K_SPACE:
                    # flip Hamiltonian direction safely (works when on path)
                    self.direction *= -1

    def step(self):
        if self.paused or self.game_over or self.win:
            return

        head = self.snake[0]
        snake_set = set(self.snake)
        tail = self.snake[-1]

        # 1) Attempt A* to food
        use_astar = False
        astar_path = None
        if self.food:
            astar_path = astar(head, self.food, snake_set)
            if astar_path:
                # safety: simulate eating along astar_path and ensure tail reachable after eat
                safe = simulate_path_and_check_tail_reachable(self.snake, astar_path, self.food)
                if safe:
                    use_astar = True
                    # planned_astar holds steps (coords) to follow (we'll pop first each tick)
                    self.planned_astar = astar_path

        # 2) If no safe astar, try Hamiltonian next step (path-based fallback)
        next_pos = None
        if use_astar and self.planned_astar:
            next_pos = self.planned_astar.pop(0)
        else:
            # If head not on path mapping (rare), fallback to meander
            if head not in self.pos_to_index:
                next_pos = None
            else:
                # compute next index along path with reversal at endpoints
                idx = self.pos_to_index[head]
                next_idx = idx + self.direction
                if next_idx < 0 or next_idx >= self.path_len:
                    # reverse direction and recalc
                    self.direction *= -1
                    next_idx = idx + self.direction
                candidate = self.path[next_idx]
                # ensure we are not moving into body (except tail)
                if candidate in snake_set and candidate != tail:
                    # can't take Hamiltonian step safely
                    next_pos = None
                else:
                    # additional safety: simulate taking this step and see if tail reachable after (if we eat or not)
                    sim_path = [candidate]
                    safe = simulate_path_and_check_tail_reachable(self.snake, sim_path, self.food)
                    if safe:
                        next_pos = candidate
                    else:
                        next_pos = None

        # 3) If neither A* nor Hamiltonian step is available/safe, meander
        if next_pos is None:
            next_pos = meander_move(head, snake_set, tail)

        # If still None, no legal move — game over
        if next_pos is None:
            self.game_over = True
            return

        # Make the move: check collision
        if next_pos in snake_set and next_pos != tail:
            self.game_over = True
            return

        self.snake.appendleft(next_pos)
        if self.food and next_pos == self.food:
            # ate food
            self.score += 1
            if self.score % 5 == 0:
                self.speed += 1
            self.spawn_food()
            # if we were following planned_astar, clear it
            self.planned_astar = []
        else:
            # normal move: remove tail
            self.snake.pop()

        # Update head_index if head lies on path
        if self.snake[0] in self.pos_to_index:
            self.head_index = self.pos_to_index[self.snake[0]]
        # Win
        if len(self.snake) == GRID_W * GRID_H:
            self.win = True

    def draw_grid(self):
        x0 = WINDOW_MARGIN
        y0 = WINDOW_MARGIN
        for x in range(GRID_W + 1):
            pygame.draw.line(self.screen, GRID_COLOR, (x0 + x * CELL_SIZE, y0), (x0 + x * CELL_SIZE, y0 + GRID_H * CELL_SIZE))
        for y in range(GRID_H + 1):
            pygame.draw.line(self.screen, GRID_COLOR, (x0, y0 + y * CELL_SIZE), (x0 + GRID_W * CELL_SIZE, y0 + y * CELL_SIZE))

    def draw(self):
        self.screen.fill(BG)
        x0 = WINDOW_MARGIN; y0 = WINDOW_MARGIN
        pygame.draw.rect(self.screen, PLAY_BG, (x0 - 2, y0 - 2, GRID_W * CELL_SIZE + 4, GRID_H * CELL_SIZE + 4))

        # grid
        self.draw_grid()

        # food
        if self.food:
            fx, fy = self.food
            pygame.draw.rect(self.screen, FOOD_COLOR, (x0 + fx*CELL_SIZE + 1, y0 + fy*CELL_SIZE + 1, CELL_SIZE-2, CELL_SIZE-2))

        # snake
        for i, (sx, sy) in enumerate(self.snake):
            color = SNAKE_HEAD if i == 0 else SNAKE_BODY
            pygame.draw.rect(self.screen, color, (x0 + sx*CELL_SIZE + 1, y0 + sy*CELL_SIZE + 1, CELL_SIZE-2, CELL_SIZE-2))

        # HUD
        mode = "A*" if self.planned_astar else "Hamiltonian" 
        info = f"Score: {self.score}  Mode: {mode}  Speed: {self.speed} FPS"
        self.screen.blit(self.font.render(info, True, TEXT_COLOR), (10, 6))
        self.screen.blit(self.font.render("Keys: P Pause | R Restart | Space Flip Dir | Esc Quit", True, TEXT_COLOR), (10, 26))

        if self.paused:
            surf = self.bigfont.render("PAUSED", True, (255, 210, 0))
            self.screen.blit(surf, (self.screen_w//2 - surf.get_width()//2, 80))
        if self.game_over:
            surf = self.bigfont.render("GAME OVER", True, (220, 60, 60))
            self.screen.blit(surf, (self.screen_w//2 - surf.get_width()//2, 80))
        if self.win:
            surf = self.bigfont.render("YOU WIN! Board Filled", True, (100, 220, 180))
            self.screen.blit(surf, (self.screen_w//2 - surf.get_width()//2, 80))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.step()
            self.draw()
            self.clock.tick(self.speed)

# ---------- ENTRY ----------
if __name__ == "__main__":
    game = HybridMeanderSnake()
    print("Hybrid Snake running. Strategy: A* -> Hamiltonian -> Meander fallback.")
    print("Controls: P pause, R restart, Space flip Hamiltonian direction (safe), Esc quit.")
    game.run()
