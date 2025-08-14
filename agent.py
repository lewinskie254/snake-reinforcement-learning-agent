import torch 
import random 
import numpy as np 
import matplotlib.pyplot as plt 
from snake import Snake, Direction, Point, BLOCK_SIZE, MULTIPLIER
from collections import deque 
from model import Linear_QNet, QTrainer
from helper import plot 
from mcts import MCTSAgent

MAX_MEMORY = 100000
BATCH_SIZE = 1000 
LR = 0.001
MODEL_TO_USE = 'models/model.pth'
     # Load and continue training from a saved model
class Agent:
    def __init__(self, model_path=None):
        self.number_of_games = 0 
        self.gamma = 0.9
        self.input_channels = 3  # or 3 if you're using RGB channels; adjust based on your input shape
        self.memory = deque(maxlen=MAX_MEMORY) #if it exceeds Max Memory it deque.popleft()
        self.model = Linear_QNet(input_size=14, hidden_size=392, output_size=3)
        # self.grid_height = grid_height  # or from game
        # self.grid_width = grid_width   # or from game

        # self.model = Conv_QNet(
        #     input_channels=self.input_channels,
        #     height=self.grid_height,
        #     width=self.grid_width,
        #     output_size=3  # [straight, right, left]
        # )

        self.model_path = model_path
        if self.model_path:
            self.model.load(model_path)  # Load weights if path is provided
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

        point_in_body_x, point_in_body_y = self.body_in_the_way(game.snake[0], game.direction, game.snake)

        # State vector for agent
        state = [
            danger_straight, danger_right, danger_left,
            direction_left, direction_right, direction_up, direction_down,
            game.food.x < head.x,   # food is to the left
            game.food.x > head.x,   # food is to the right
            game.food.y < head.y,   # food is above
            game.food.y > head.y,   # food is below
            self.is_path_blocked_by_body(game.snake[0], game.food, game.snake, game.width, game.height), 
            point_in_body_x == game.snake[0].x +BLOCK_SIZE or point_in_body_x == game.snake[0].x -BLOCK_SIZE,
            point_in_body_y == game.snake[0].y +BLOCK_SIZE or point_in_body_y == game.snake[0].y -BLOCK_SIZE,
        ]

        return np.array(state, dtype=int)
    
    def is_path_blocked_by_body(self, start, target, snake_body, board_width, board_height):
        visited = set()
        queue = deque()
        queue.append(start)

        snake_body = set(snake_body)  # Fast lookup

        while queue:
            pos = queue.popleft()
            if pos == target:
                return False  # Path exists

            for dx, dy in [(-BLOCK_SIZE, 0), (BLOCK_SIZE, 0), (0, -BLOCK_SIZE), (0, BLOCK_SIZE)]:
                next_pos = Point(pos.x + dx, pos.y + dy)
                
                # Stay within bounds
                if not (0 <= next_pos.x < board_width and 0 <= next_pos.y < board_height):
                    continue

                if next_pos in snake_body or next_pos in visited:
                    continue

                visited.add(next_pos)
                queue.append(next_pos)

        return True  # No path found → body blocks it


    def body_in_the_way(self, head, direction, body):
        if direction == Direction.LEFT:
            next_point = Point(head.x - BLOCK_SIZE, head.y)
        elif direction == Direction.RIGHT:
            next_point = Point(head.x + BLOCK_SIZE, head.y)
        elif direction == Direction.UP:
            next_point = Point(head.x, head.y - BLOCK_SIZE)
        elif direction == Direction.DOWN:
            next_point = Point(head.x, head.y + BLOCK_SIZE)
        
        return (next_point.x, next_point.y) if next_point in body else (0, 0)


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


    def get_action(self, state, epsilon=0.1) :
        if self.number_of_games > 80:
            epsilon = 0 
        self.epsilon = epsilon
        actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        if random.random() < self.epsilon:
            action = random.choice(actions)
        else: 
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            action = torch.argmax(prediction).item()
            action = actions[action]

        return action 
    
    def get_cnn_action(self, state, epsilon=0.1):
        self.epsilon = epsilon
        actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        if random.random() < self.epsilon:
            return random.choice(actions)

        state_tensor = torch.tensor(state, dtype=torch.float).unsqueeze(0)  # Shape: [1, 3, H, W]
        prediction = self.model(state_tensor)
        action_idx = torch.argmax(prediction).item()
        return actions[action_idx]

    
    def get_cnn_state(self, game):
        grid = np.zeros((3, game.height // BLOCK_SIZE, game.width // BLOCK_SIZE), dtype=np.float32)

        for i, point in enumerate(game.snake):
            x, y = point.x // BLOCK_SIZE, point.y // BLOCK_SIZE
            if i == 0:
                grid[0][y][x] = 1.0  # Head
            else:
                grid[0][y][x] = 0.5  # Body

        food_x, food_y = game.food.x // BLOCK_SIZE, game.food.y // BLOCK_SIZE
        grid[1][food_y][food_x] = 1.0  # Food

        # Optional wall layer (if needed)
        grid[2][0, :] = 1.0
        grid[2][-1, :] = 1.0
        grid[2][:, 0] = 1.0
        grid[2][:, -1] = 1.0

        return grid

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    best_score = 0 

    game = Snake()
    agent = Agent(model_path=MODEL_TO_USE)
    agent.number_of_games += 1
    wiggle_moves = 0  # <-- Persist across frames
    while True:
        # Get current state
        state_old = agent.get_state(game)
        #state_old = agent.get_cnn_state(game)
        
        # --- Imitation Learning: get expert move ---
        final_move = agent.get_action(state_old, epsilon=0)
        danger, food_zone = game.danger_zone_checker(game.snake[0])
        if len(game.snake) < 70: 
            if danger and not food_zone: 
                wiggle_moves = 5 
            elif danger and food_zone: 
                final_move = agent.get_action(state_old, epsilon=0)
            elif wiggle_moves: 
                wiggle_moves -= 1
                final_move = game.get_safest_astar_action()
            else: 
                final_move = game.get_next_astar_action()
                if final_move is None: 
                    final_move = agent.get_action(state_old, epsilon=0)
        else: 
            danger, food_zone = game.danger_zone_checker(game.snake[0])
            if danger and food_zone: 
                wiggle_moves = 5
            elif danger and not food_zone: 
                wiggle_moves = 7
            
            if wiggle_moves: 
                wiggle_moves -= 1
                final_move = game.get_safest_astar_action()
            else: 
                final_move = game.get_next_astar_action()

                if final_move is None: 
                    final_move = agent.get_action(state_old, epsilon=0)
        if final_move is None: 
            final_move = agent.get_action(state_old, epsilon=0) 
        # Perform the move
        reward, done, score = game.play_step(final_move)

        # New state
        state_new = agent.get_state(game)

        # Train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # Remember (imitation + experience replay)
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            game.reset()
            agent.number_of_games += 1
            agent.train_long_memory() 

            if score > best_score:
                best_score = score 
                agent.model.save() 

            print('Game', agent.number_of_games, 'Score', score, 'Best Score', best_score)

            plot_scores.append(score)
            total_score += score 
            mean_score = total_score / agent.number_of_games 
            plot_mean_scores.append(mean_score)

            if agent.number_of_games % 100 == 1: 
                plot(plot_scores, plot_mean_scores)
                


def play():
    game = Snake()
    agent = Agent(model_path='models/model copy 10.pth')
    wiggle_moves = 0  # <-- Persist across frames
    epsilon = 0

    while True:
        state = agent.get_state(game=game)
        final_move = game.get_next_astar_action()
        danger, food_zone = game.danger_zone_checker(game.snake[0])
        if len(game.snake) < 70: 
            if danger and not food_zone: 
                wiggle_moves = 5 
            elif danger and food_zone: 
                #print("DQN Agent")
                final_move = agent.get_action(state, epsilon)
            elif wiggle_moves: 
                wiggle_moves -= 1
                #print("Hamiltonian Agent")
                final_move = game.get_safest_astar_action()
            else: 
                #print("A* Agent")
                final_move = game.get_next_astar_action()
                if final_move is None: 
                    #print("DQN Agent")
                    final_move = agent.get_action(state, epsilon)
        else: 
            danger, food_zone = game.danger_zone_checker(game.snake[0])
            if danger and food_zone: 
                wiggle_moves = 5
            elif danger and not food_zone: 
                wiggle_moves = 7
            
            if wiggle_moves: 
                wiggle_moves -= 1
                #print("Hamiltonian")
                final_move = game.get_safest_astar_action()
            else: 
                #print("A star")
                final_move = game.get_next_astar_action()

                if final_move is None: 
                    #print("DQN Algo")
                    final_move = agent.get_action(state, epsilon)

        
        reward, done, score = game.play_step(final_move)

        if done:
            print('Game Over. Score:', score)
            game.reset()



def play_mcts():
    agent = MCTSAgent(simulations_per_move=50)  # Adjust for speed/quality
    game = Snake()

    while True:
        action = agent.select_action(game)
        reward, done, score = game.play_step(action)
        if done:
            print('Game Over. Score:', score)
            game.reset()



if __name__ == "__main__":
    #train() 
    play()
    #play_mcts()
