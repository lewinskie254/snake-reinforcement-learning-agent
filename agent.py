import torch 
import random 
import numpy as np 
import matplotlib.pyplot as plt 
from snake import Snake, Direction, Point, BLOCK_SIZE, MULTIPLIER
from collections import deque 
from model import Linear_QNet, QTrainer
from helper import plot 

MAX_MEMORY = 100000
BATCH_SIZE = 1000 
LR = 0.001
GRID_WIDTH = 640 * MULTIPLIER// BLOCK_SIZE
GRID_HEIGHT = 480 * MULTIPLIER// BLOCK_SIZE
MAX_SNAKE_LENGTH = GRID_WIDTH * GRID_HEIGHT

class Agent:
    def __init__(self):
        self.number_of_games = 0 
        self.epsilon = 0.1 
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY) #if it exceeds Max Memory it deque.popleft()
        self.model = Linear_QNet(input_size=12, hidden_size=256, output_size=3)
        self.trainer = QTrainer(model=self.model, learning_rate=LR, gamma=self.gamma)
        #TODO: model, trainer 


    def get_state(self, game):
        head = game.snake[0]


        
        # Using BLOCK_SIZE instead of self.margin
        point_left = Point(head.x - BLOCK_SIZE, head.y)
        point_right = Point(head.x +  BLOCK_SIZE, head.y)
        point_up = Point(head.x, head.y - BLOCK_SIZE)
        point_down = Point(head.x, head.y + BLOCK_SIZE)

        # Current direction
        direction_left = game.direction == Direction.LEFT
        direction_right = game.direction == Direction.RIGHT 
        direction_up = game.direction == Direction.UP
        direction_down = game.direction == Direction.DOWN

        # Danger directly in front
        danger_straight = (
            (direction_up and game.is_collision(point_up)) or
            (direction_down and game.is_collision(point_down)) or
            (direction_left and game.is_collision(point_left)) or
            (direction_right and game.is_collision(point_right))
        )

        # Danger to the right of current direction
        danger_right = (
            (direction_up and game.is_collision(point_right)) or
            (direction_down and game.is_collision(point_left)) or
            (direction_left and game.is_collision(point_up)) or
            (direction_right and game.is_collision(point_down))
        )

        # Danger to the left of current direction
        danger_left = (
            (direction_up and game.is_collision(point_left)) or
            (direction_down and game.is_collision(point_right)) or
            (direction_left and game.is_collision(point_down)) or
            (direction_right and game.is_collision(point_up))
        )

        # State vector for agent
        state = [
            danger_straight, danger_right, danger_left,
            direction_left, direction_right, direction_up, direction_down,
            game.food.x < head.x,   # food is to the left
            game.food.x > head.x,   # food is to the right
            game.food.y < head.y,   # food is above
            game.food.y > head.y,   # food is below
            len(game.snake) / MAX_SNAKE_LENGTH
        ]

        return np.array(state, dtype=int)


    def remember(self, state, action, reward, next_state, done): 
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples 
        else: 
            mini_sample =self.memory 
        mini_sample = np.array(mini_sample, dtype=object)  # Convert list of tuples to ndarray (dtype=object is important)

        states      = np.stack(mini_sample[:, 0])
        actions     = np.stack(mini_sample[:, 1])
        rewards     = np.stack(mini_sample[:, 2])
        next_states = np.stack(mini_sample[:, 3])
        dones       = np.stack(mini_sample[:, 4])
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state):
        self.epsilon = 0.1
        actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        if random.random() < self.epsilon:
            action = random.choice(actions)
        else: 
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            action = torch.argmax(prediction).item()
            action = actions[action]

        return action 

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    best_score = 0 
    agent = Agent()
    game = Snake()
    agent.number_of_games += 1

    while True:
        # get the old state or current state 
        state_old = agent.get_state(game)

        #get move 
        final_move = agent.get_action(state_old)

        #perform the move 
        reward, done, score = game.play_step(final_move)

        #new state 
        state_new = agent.get_state(game)

        #train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        #remember 
        agent.remember(state_old, final_move, reward, state_new, done)

        if done: 
            #train the long memory 
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory() 

            if score > best_score:
                best_score = score 
                agent.model.save() 
            print('Game', agent.number_of_games, 'Score', score, 'Best Score', best_score)

            if len(plot_scores) >= 10:
                best_recent = max(plot_scores[-10:])
                if score > best_recent:
                    agent.model.save('best_most_recent.pth')

            plot_scores.append(score)
            total_score += score 
            mean_score = total_score / agent.number_of_games 
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
                





if __name__ == "__main__":
    train() 

