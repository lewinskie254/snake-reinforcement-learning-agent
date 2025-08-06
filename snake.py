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

BLOCK_SIZE = 20
SPEED = 40
GREENISH = (227, 208, 149)
GREY = (54, 69, 79)

FONT = pygame.font.Font('Retrolight.tff', 25)

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
        #collect user input 

        #move 
        self.move(self.direction)

        #check if game is over 


        #place new food 
        

        #update UI and clock 
        self._update_ui()
        self.clock.tick(SPEED)

        #return game over and score 
        game_over = False
        return game_over, self.score 
    
    def move(self, direction): 
        ...
    
    #update UI
    def _update_ui(self): 
        self.display.fill(GREENISH)

        for point in self.snake:
            pygame.draw.rect(self.display, GREY, pygame.Rect(point.x, point.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREENISH, pygame.Rect(point.x+2, point.y+2, BLOCK_SIZE-4, BLOCK_SIZE-4))
            pygame.draw.rect(self.display, GREY, pygame.Rect(point.x+4, point.y+4, BLOCK_SIZE-8, BLOCK_SIZE-8))

        pygame.draw.rect(self.display, GREY, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        text = FONT.render("score: " + self.score, True, GREY)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

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
        game_over, score = game.play_step()


        #break if game over 
        if game_over == True:
            break 

    #print final store 
    print(f"Final Score: {score}")

    #pygame quit 
    pygame.quit()