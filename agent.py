import torch 
import random 
import numpy as np 
import matplotlib as plt 
from .snake import Snake, Direction, Point
from collections import deque 


MAX_MEMORY = 100000
BATCH_SIZE = 1000 
LR = 0.001

class Agent:
    def __init__(self):
        self.number_of_games = 0 
        self.epsilon = 0 
        self.gamma = 0 
        self.memory = deque(maxlen=MAX_MEMORY)
        #TODO: model, trainer 


    def get_state(self, game):
        pass

    def remember(self, state, action, reward, next_state, done): 
        pass

    def train_long_memory(self, state, action, reward, next_state, done):
        pass 

    def train_short_memory(self):
        pass 

    def get_action(self, state):
        pass 


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    best_score = 0 
    agent = Agent()
    game = Snake()

    while True:
        # get the old state or current state 
        state_old = agent.get_state()

        #get move 
        final_move = agent.get_action(state_old)

        #perform the move 
        reward, done, score = game.play_step(final_move)

        #new state 
        state_new = agent.get_state()

        #train short memory 
        agent.train_short_memory()





if __name__ == "__main__":
    train() 

