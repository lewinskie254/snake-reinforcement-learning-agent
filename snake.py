import pygame 
import random 
from enum import Enum
from collections import namedtuple

pygame.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2 
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# Constants
BLOCK_SIZE = 20
SPEED = 10
GREENISH = (227, 208, 149)
GREY = (54, 69, 79)
MARGIN = 50 
BORDER = MARGIN - 10
FONT = pygame.font.Font('Bellerose.ttf', 25)

class Snake:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        # Init display 
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake AI")
        self.clock = pygame.time.Clock()

        # Init game state 
     
    
    def play_step(self, action):
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
        self.move(self.direction)
        self.snake.insert(0, self.head)

        # Check if food is eaten
        if self.head == self.food:
            self.score += 1
            self._place_food()
        else:
            self.snake.pop()

        # Check collision
        if self.is_collision():
            return True, self.score

        # Update UI
        self._update_ui()
        self.clock.tick(SPEED)

        return False, self.score 
    
    def move(self, direction): 
        x, y = self.head.x, self.head.y 
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT: 
            x -= BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        self.head = Point(x, y)

    def is_collision(self): 
        # Wall collision
        if self.head.x >= (self.width - BORDER) or self.head.x < BORDER:
            return True 
        if self.head.y >= (self.height - BORDER) or self.head.y < BORDER:
            return True 
        # Self collision
        if self.head in self.snake[1:]:
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
        self.display.blit(text, [20, 0])

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

if __name__ == "__main__":
    game = Snake()
    while True: 
        game_over, score = game.play_step()
        if game_over:
            break 
    print(f"Final Score: {score}")
    pygame.quit()
