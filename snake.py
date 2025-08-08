
import pygame 
import random 
from enum import Enum
from collections import namedtuple
import numpy as np 
import pygame.time

pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2 
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')
MULTIPLIER =2 
# Constants
BLOCK_SIZE = 20*MULTIPLIER
SPEED = 60
GREENISH = (227, 208, 149)
GREY = (54, 69, 79)
MARGIN = 50 * MULTIPLIER
BORDER = MARGIN - 10 * MULTIPLIER
FONT = pygame.font.Font('Bellerose.ttf', 20*MULTIPLIER)

CRASH = (138, 154, 91)

class Snake:
    def __init__(self, width=640*MULTIPLIER, height=480 * MULTIPLIER):
        self.width = width
        self.height = height

        # Init display 
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake AI")
        self.clock = pygame.time.Clock()

        # Init game state 
        self.reset()  # <-- add this line
     
    
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

if __name__ == "__main__":
    play_manual()