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

Point = namedtuple('Point', 'x', 'y')

BLOCK_SIZE = 20

class Snake:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height

        #init display 
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake Ai")
        self.clock = pygame.time.Clock()

        #init game state 
        self.direction = Direction.RIGHT 

        #snake 
        self.head = Point(self.width//2, self.height//2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y), 
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None 
        self._place_food() 
    
    def play_step(self):
        return self.display
    

    #place food 
    def _place_food(self): 
        x = random.randint(0, (self.width-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        y = random.randint(0, (self.height-BLOCK_SIZE)//BLOCK_SIZE)*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake: 
            return self._place_food()


if __name__ == "__main__":
    game = Snake()

    #game loop 
    while True: 
        game.play_step()


        #break if game over 
        
        #print final store 


        #pygame quit 
        pygame.quit()