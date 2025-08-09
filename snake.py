
import pygame 
import random 
from enum import Enum
from common import Point
import numpy as np 
import pygame.time
from a_star import a_star


pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2 
    UP = 3
    DOWN = 4

MULTIPLIER =2
# Constants
BLOCK_SIZE = 20*MULTIPLIER
SPEED = 30
GREENISH = (227, 208, 149)
GREY = (54, 69, 79)
MARGIN = 50 * MULTIPLIER
BORDER = MARGIN - 10 * MULTIPLIER
FONT = pygame.font.Font('Bellerose.ttf', 20*MULTIPLIER)

CRASH = (138, 154, 91)

class Snake:
    def __init__(self, width=640*MULTIPLIER, height=480 * MULTIPLIER,display_enabled=True):
        self.width = width
        self.height = height
        if display_enabled:
            self.display = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Snake AI")
            self.clock = pygame.time.Clock()
        else:
            self.display = None
            self.clock = None

        self.reset()
     
    
    def play_step(self, action=None, manual=False):
        self.frame_iteration += 1
        # Handle events
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
            #         self.direction = Direction.LEFT
            #     elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
            #         self.direction = Direction.RIGHT
            #     elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
            #         self.direction = Direction.UP
            #     elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
            #         self.direction = Direction.DOWN 
        

        
        # Move
        if manual:
            self.move_manual()
        else:
            self.move(action)
        self.snake.insert(0, self.head)
        reward = 0
        # Check if food is eaten
        if self.head == self.food:
            self.score += 1
            reward += 10 
            self._place_food()
        else:
            self.snake.pop()

        # Check collision or if the game takes way too long 
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            if self.display is not None: 
                #hacky way hoping it works 
                self.snake.pop(0)
                self.snake.pop()

                for point in self.snake:
                    pygame.draw.rect(self.display, CRASH, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
                    pygame.draw.rect(self.display, GREENISH, pygame.Rect(point.x+2, point.y+2, BLOCK_SIZE-4, BLOCK_SIZE-4))
                    pygame.draw.rect(self.display, CRASH, pygame.Rect(point.x+4, point.y+4, BLOCK_SIZE-8, BLOCK_SIZE-8))
                pygame.display.update()
                pygame.time.delay(500)  # delay for 0.5 seconds
                reward -= 10
                return reward, True, self.score
        if self.display is not None: 
            # Update UI
            self._update_ui()
            self.clock.tick(SPEED)
            reward-= 0.1 

        return reward, False, self.score 
    
    def move(self, action): 
        x, y = self.head.x, self.head.y 
        #[straight, right, left]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]): 
            new_direction = clock_wise[index]
        elif np.array_equal(action, [0, 1, 0]):
            next_index = (index + 1)% 4
            new_direction = clock_wise[next_index]
        else: 
            next_index = (index - 1)% 4
            new_direction = clock_wise[next_index]
       
        self.direction = new_direction 

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction  == Direction.LEFT: 
            x -= BLOCK_SIZE
        elif self.direction  == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction  == Direction.DOWN:
            y += BLOCK_SIZE
        self.head = Point(x, y)

    def is_collision(self, point=None): 
        if point is None: 
            point = self.head
        # Wall collision
        if point.x >= (self.width - BORDER) or point.x < BORDER:
            return True 
        if point.y >= (self.height - BORDER) or point.y < BORDER:
            return True 
        # Self collision
        if point in self.snake[1:]:
            return True
        return False
    
    def reset(self): 
        self.direction = Direction.RIGHT 
        self.head = Point(self.width//2, self.height//2)
        self.snake = [
            self.head, 
            Point(self.head.x - BLOCK_SIZE, self.head.y), 
            Point(self.head.x - 2*BLOCK_SIZE, self.head.y)
        ]

        self.score = 0
        self.food = None 
        self._place_food()
        self.frame_iteration = 0 

    def move_manual(self):
        x, y = self.head.x, self.head.y

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE

        self.head = Point(x, y)


    def _update_ui(self): 
        if self.display is None:
            return  # Skip rendering in simulation
        self.display.fill(GREENISH)

        # Snake
        for point in self.snake:
            pygame.draw.rect(self.display, GREY, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREENISH, pygame.Rect(point.x+2, point.y+2, BLOCK_SIZE-4, BLOCK_SIZE-4))
            pygame.draw.rect(self.display, GREY, pygame.Rect(point.x+4, point.y+4, BLOCK_SIZE-8, BLOCK_SIZE-8))

        # Food
        pygame.draw.rect(self.display, GREY, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        # Score + Borders
        text = FONT.render(f"score: {self.score}" , True, GREY)
        self.display.blit(text, [MARGIN, 0])

        pygame.draw.line(self.display, GREY, [BORDER, BORDER], [self.width - BORDER, BORDER], width=2)
        pygame.draw.line(self.display, GREY, [BORDER, BORDER], [BORDER, self.height - BORDER], width=2)
        pygame.draw.line(self.display, GREY, [BORDER, self.height - BORDER], [self.width - BORDER, self.height - BORDER], width=2)
        pygame.draw.line(self.display, GREY, [self.width - BORDER, BORDER], [self.width - BORDER, self.height - BORDER], width=2)
        
        pygame.display.flip()

    def _place_food(self): 
        while True:
            x = random.randint(0, (self.width - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.height - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            food = Point(x, y)
            if (
                BORDER <= food.x < self.width - BORDER and
                BORDER <= food.y < self.height - BORDER and
                food not in self.snake
            ):
                self.food = food
                break
    
    def clone_for_simulation(self):
        clone = clone = Snake(self.width, self.height, display_enabled=False)

        # Copy state manually (exclude pygame.Surface etc.)
        clone.direction = self.direction
        clone.head = self.head
        clone.snake = list(self.snake)
        clone.score = self.score
        clone.food = self.food
        clone.frame_iteration = self.frame_iteration

        # Disable rendering in simulation
        clone.display = None
        clone.clock = None
        return clone
    
    def get_binary_grid(self):
        """
        Returns a grid representation:
        0 = empty
        1 = snake body (including head)
        2 = food
        """
        rows = self.height // BLOCK_SIZE
        cols = self.width // BLOCK_SIZE
        grid = np.zeros((rows, cols), dtype=np.uint8)

        for segment in self.snake:
            row = segment.y // BLOCK_SIZE
            col = segment.x // BLOCK_SIZE
            grid[row][col] = 1

        if self.food:
            food_row = self.food.y // BLOCK_SIZE
            food_col = self.food.x // BLOCK_SIZE
            grid[food_row][food_col] = 2

        return grid

    def get_cnn_input(self):
        """
        Returns a 3-channel tensor:
        [0] = snake body
        [1] = food
        [2] = wall/boundary
        """
        rows = self.height // BLOCK_SIZE
        cols = self.width // BLOCK_SIZE
        grid = np.zeros((3, rows, cols), dtype=np.float32)

        # Snake
        for segment in self.snake:
            r = segment.y // BLOCK_SIZE
            c = segment.x // BLOCK_SIZE
            grid[0][r][c] = 1

        # Food
        if self.food:
            r = self.food.y // BLOCK_SIZE
            c = self.food.x // BLOCK_SIZE
            grid[1][r][c] = 1

        # Walls (borders)
        border_cells = BORDER // BLOCK_SIZE
        for r in range(rows):
            for c in range(cols):
                if r < border_cells or r >= rows - border_cells or c < border_cells or c >= cols - border_cells:
                    grid[2][r][c] = 1

        return grid




    def get_next_astar_action(self):
        # Run A*
        path = a_star(
            self.head,
            self.food,
            set(self.snake[1:]),  # exclude head from obstacles
            self.width,
            self.height,
            BLOCK_SIZE,
            BORDER
        )

        # If no path, use simple fallback logic
        if not path:
            #NO DQN to guess 
            # head_pos = self.snake[0]
            # point_forward = Point(head_pos.x + (BLOCK_SIZE if self.direction == Direction.RIGHT else -BLOCK_SIZE if self.direction == Direction.LEFT else 0),
            #                     head_pos.y + (BLOCK_SIZE if self.direction == Direction.DOWN else -BLOCK_SIZE if self.direction == Direction.UP else 0))
            # point_left = Point(head_pos.x + (BLOCK_SIZE if self.direction == Direction.UP else -BLOCK_SIZE if self.direction == Direction.DOWN else 0),
            #                 head_pos.y + (BLOCK_SIZE if self.direction == Direction.LEFT else -BLOCK_SIZE if self.direction == Direction.RIGHT else 0))
            # point_right = Point(head_pos.x + (-BLOCK_SIZE if self.direction == Direction.UP else BLOCK_SIZE if self.direction == Direction.DOWN else 0),
            #                     head_pos.y + (-BLOCK_SIZE if self.direction == Direction.LEFT else BLOCK_SIZE if self.direction == Direction.RIGHT else 0))

            # # Forward clear → keep going
            # if not self.is_collision(point_forward):
            #     return [1, 0, 0]  # straight

            # # Forward blocked → try left first
            # if not self.is_collision(point_left):
            #     return [0, 1, 0]  # turn left

            # # Left blocked too → try right
            # if not self.is_collision(point_right):
            #     return [0, 0, 1]  # turn right

            # No options → just keep going (likely game over)
            return None


        # A* should return path where path[0] is the next tile (not the head)
        next_point = path[0]
        dx = next_point.x - self.head.x
        dy = next_point.y - self.head.y

        # Desired absolute direction
        if dx > 0:
            desired = Direction.RIGHT
        elif dx < 0:
            desired = Direction.LEFT
        elif dy > 0:
            desired = Direction.DOWN
        elif dy < 0:
            desired = Direction.UP
        else:
            # Unexpected: no movement delta -> go straight
            return [1, 0, 0]

        # Convert absolute direction to relative action expected by move()
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        current_idx = clock_wise.index(self.direction)
        desired_idx = clock_wise.index(desired)

        if desired_idx == current_idx:
            return [1, 0, 0]               # straight
        elif desired_idx == (current_idx + 1) % 4:
            return [0, 1, 0]               # right turn
        elif desired_idx == (current_idx - 1) % 4:
            return [0, 0, 1]               # left turn
        else:
            # Opposite direction (cannot reverse). Prefer turning right.
            return [0, 1, 0]
    # inside class Snake

    def _is_adjacent(self, a: Point, b: Point):
        return (abs(a.x - b.x) + abs(a.y - b.y)) == BLOCK_SIZE

    def _in_bounds(self, p: Point, width, height, border):
        return border <= p.x < width - border and border <= p.y < height - border

    def _reachable_area(self, start: Point, obstacles_set, width, height, border):
        # BFS counting reachable cells from start (used for fallback choice)
        from collections import deque
        q = deque([start])
        seen = {start}
        count = 0
        while q:
            cur = q.popleft()
            count += 1
            for dx, dy in [(-BLOCK_SIZE,0),(BLOCK_SIZE,0),(0,-BLOCK_SIZE),(0,BLOCK_SIZE)]:
                nx, ny = cur.x + dx, cur.y + dy
                nb = Point(nx, ny)
                if not self._in_bounds(nb, width, height, border): 
                    continue
                if nb in seen or nb in obstacles_set:
                    continue
                seen.add(nb)
                q.append(nb)
        return count

    def get_longest_safe_path(self, start, goal, snake_body, width, height, block_size, border):
        # 1) shortest path (exclude head from obstacles)
        obstacles = set(snake_body[1:])
        shortest = a_star(start, goal, obstacles, width, height, block_size, border)
        if not shortest:
            return None

        # Ensure we include start at front for easier segment iteration
        shortest_with_start = [start] + shortest

        stretched = []
        used = set(snake_body)  # avoid inserting into snake body cells

        for i in range(len(shortest_with_start) - 1):
            current = shortest_with_start[i]
            nxt = shortest_with_start[i + 1]

            # append current if not already last
            if not stretched or stretched[-1] != current:
                stretched.append(current)

            dx = nxt.x - current.x
            dy = nxt.y - current.y

            # perpendicular detours (pixel deltas)
            perp_dirs = [(-dy, dx), (dy, -dx)]

            for pdx, pdy in perp_dirs:
                det1 = Point(current.x + pdx, current.y + pdy)
                det2 = Point(nxt.x + pdx, nxt.y + pdy)

                # adjacency checks (det1 adjacent to current, det2 adjacent to nxt, det1 adjacent to det2)
                if not (self._is_adjacent(det1, current) and self._is_adjacent(det2, nxt) and self._is_adjacent(det1, det2)):
                    continue

                # bounds check
                if not (self._in_bounds(det1, width, height, border) and self._in_bounds(det2, width, height, border)):
                    continue

                # don't reuse cells (snake body or already used)
                if det1 in used or det2 in used:
                    continue

                # don't insert detours that will cause re-entry into the remainder of the shortest path
                # (prevents small cycles)
                if det1 in shortest_with_start or det2 in shortest_with_start:
                    continue

                # Passed all checks: insert the detour pair
                stretched.append(det1)
                used.add(det1)
                stretched.append(det2)
                used.add(det2)
                break  # only one detour per segment

        # append final goal
        if not stretched or stretched[-1] != shortest_with_start[-1]:
            stretched.append(shortest_with_start[-1])

        # final validation: path must be simple and consecutive points adjacent
        # if validation fails, return the safe fallback: the (start +) shortest path
        if len(set(stretched)) != len(stretched):
            # got duplicates → revert to shortest
            return [start] + shortest

        for i in range(len(stretched) - 1):
            if not self._is_adjacent(stretched[i], stretched[i+1]):
                # invalid adjacency, revert
                return [start] + shortest

        return stretched
        
    def danger_zone_checker(self, head, step_size=2):
        horizontal_forward = head.x + step_size//2 * BLOCK_SIZE
        horizontal_backward = head.x - step_size//2 * BLOCK_SIZE
        vertical_up = head.y - step_size//2 * BLOCK_SIZE
        vertical_down = head.y + step_size//2 * BLOCK_SIZE

        two_forward = head.x + step_size * BLOCK_SIZE
        two_backward = head.x - step_size * BLOCK_SIZE
        two_up = head.y - step_size * BLOCK_SIZE
        two_down = head.y + step_size * BLOCK_SIZE

        # Points
        point_forward_1 = Point(horizontal_forward, head.y)
        point_forward_2 = Point(two_forward, head.y)
        point_backward_1 = Point(horizontal_backward, head.y)
        point_backward_2 = Point(two_backward, head.y)
        point_up_1 = Point(head.x, vertical_up)
        point_up_2 = Point(head.x, two_up)
        point_down_1 = Point(head.x, vertical_down)
        point_down_2 = Point(head.x, two_down)

        #Prioritize eating 
        if self.is_collision(self.food): 
            return False


        danger = False
        if self.direction == Direction.LEFT:
            danger = (self.is_collision(point_backward_1) and self.is_collision(point_up_1)) or \
                    (self.is_collision(point_backward_1) and self.is_collision(point_down_1)) or \
                    (self.is_collision(point_backward_2) and self.is_collision(point_up_2)) or \
                    (self.is_collision(point_backward_2) and self.is_collision(point_down_2))
        elif self.direction == Direction.RIGHT:
            danger = (self.is_collision(point_forward_1) and self.is_collision(point_up_1)) or \
                    (self.is_collision(point_forward_1) and self.is_collision(point_down_1)) or \
                    (self.is_collision(point_forward_2) and self.is_collision(point_up_2)) or \
                    (self.is_collision(point_forward_2) and self.is_collision(point_down_2))
        elif self.direction == Direction.UP:
            danger = (self.is_collision(point_up_1) and self.is_collision(point_forward_1)) or \
                    (self.is_collision(point_up_1) and self.is_collision(point_backward_1)) or \
                    (self.is_collision(point_up_2) and self.is_collision(point_forward_2)) or \
                    (self.is_collision(point_up_2) and self.is_collision(point_backward_2))
        elif self.direction == Direction.DOWN:
            danger = (self.is_collision(point_down_1) and self.is_collision(point_forward_1)) or \
                    (self.is_collision(point_down_1) and self.is_collision(point_backward_1)) or \
                    (self.is_collision(point_down_2) and self.is_collision(point_forward_2)) or \
                    (self.is_collision(point_down_2) and self.is_collision(point_backward_2))

        return danger



    def get_safest_astar_action(self):
        # Try the stretched path first
        path = self.get_longest_safe_path(
            self.head,
            self.food,
            self.snake,
            self.width,
            self.height,
            BLOCK_SIZE,
            BORDER
        )

        # If no path or path too short, fallback using reachable-area heuristic
        if not path or len(path) < 2:
            return self._fallback_action_by_area()

        # Our stretched path is returned with start included: path[0] == head, so use path[1]
        next_point = path[1]
        dx = next_point.x - self.head.x
        dy = next_point.y - self.head.y

        if dx > 0:
            desired = Direction.RIGHT
        elif dx < 0:
            desired = Direction.LEFT
        elif dy > 0:
            desired = Direction.DOWN
        elif dy < 0:
            desired = Direction.UP
        else:
            return [1, 0, 0]

        # convert to relative action
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        current_idx = clock_wise.index(self.direction)
        desired_idx = clock_wise.index(desired)

        if desired_idx == current_idx:
            return [1, 0, 0]   # straight
        elif desired_idx == (current_idx + 1) % 4:
            return [0, 1, 0]   # right
        elif desired_idx == (current_idx - 1) % 4:
            return [0, 0, 1]   # left
        else:
            # opposite - prefer right
            return [0, 1, 0]

    def _fallback_action_by_area(self):
        # Evaluate the three candidate moves (straight, left, right) and pick the one with the largest reachable area.
        head = self.head
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        candidates = []
        # map relative action to new head point
        for rel_action, offset_idx in ( ([1,0,0], idx), ([0,1,0], (idx+1)%4), ([0,0,1], (idx-1)%4) ):
            dir_ = clock_wise[offset_idx]
            nx, ny = head.x, head.y
            if dir_ == Direction.RIGHT: nx += BLOCK_SIZE
            elif dir_ == Direction.LEFT: nx -= BLOCK_SIZE
            elif dir_ == Direction.UP: ny -= BLOCK_SIZE
            elif dir_ == Direction.DOWN: ny += BLOCK_SIZE
            new_pt = Point(nx, ny)

            # If immediate collision, reachable area = -1 (disqualify)
            if not self._in_bounds(new_pt, self.width, self.height, BORDER) or new_pt in set(self.snake[1:]):
                area = -1
            else:
                # obstacles are current snake body excluding tail (tail will move), but excluding head since we're measuring after moving head
                obstacles = set(self.snake[1:])  # conservative
                # simulate that new_pt becomes head and old tail will free — being conservative here is okay
                area = self._reachable_area(new_pt, obstacles, self.width, self.height, BORDER)

            candidates.append((area, rel_action))

        # choose best area (largest), tiebreaker prefer straight, then right, then left
        candidates.sort(key=lambda x: (x[0], [1,0,0]==x[1], [0,1,0]==x[1]), reverse=True)
        best_area, best_action = candidates[0]
        if best_area <= 0:
            # nothing good — go straight as last resort
            return [1, 0, 0]
        return best_action






def play_manual():
    game = Snake()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and game.direction != Direction.RIGHT:
                    game.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and game.direction != Direction.LEFT:
                    game.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and game.direction != Direction.DOWN:
                    game.direction = Direction.UP
                elif event.key == pygame.K_DOWN and game.direction != Direction.UP:
                    game.direction = Direction.DOWN

        reward, done, score = game.play_step(manual=True)

        if done:
            print('Game Over. Score:', score)
            game.reset()


def play_with_astar():
    game = Snake()

    while True:
        action = game.get_next_astar_action()
        reward, done, score = game.play_step(action=action, manual=False)
        if done:
            print('Game Over. Score:', score)
            game.reset()

if __name__ == "__main__":
    play_with_astar()
    #play_manual()
    