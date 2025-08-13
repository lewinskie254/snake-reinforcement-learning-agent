# imitation_utils.py  (or add into your agent module)

import os
import random
import numpy as np
from collections import deque
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from enum import Enum 
import pygame  

class Direction(Enum):
    RIGHT = 1
    LEFT = 2 
    UP = 3
    DOWN = 4

MULTIPLIER =2
# Constants
BLOCK_SIZE = 20*MULTIPLIER
SPEED = 20
GREENISH = (227, 208, 149)
GREY = (54, 69, 79)
MARGIN = 50 * MULTIPLIER
BORDER = MARGIN - 10 * MULTIPLIER
FONT = pygame.font.Font('Bellerose.ttf', 20*MULTIPLIER)

CRASH = (138, 154, 91)
# ---------------------------------------------------------
# Helper: convert an expert "final_move" (what you pass to play_step)
# into agent action index 0/1/2 consistent with your agent actions list
# actions = [straight, right, left] (as one-hot vectors earlier)
# We compute relative turn based on game.direction and the candidate next head pos.
# ---------------------------------------------------------
def move_to_action_index(game, expert_move):
    # expert_move is what you'd pass to game.play_step (e.g. a direction vector or one-hot)
    # If expert_move is already an agent-style one-hot, map directly:
    actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if expert_move in actions:
        return actions.index(expert_move)

    # Otherwise, expert_move might be a Point target or direction enum — normalize by next head pos.
    head = game.snake[0]
    # compute next head position from expert_move if it's a Point
    try:
        nx, ny = expert_move.x, expert_move.y
    except Exception:
        # fallback: if expert_move is None, return straight as default
        return 0

    # delta from head to next
    dx, dy = nx - head.x, ny - head.y

    # translate relative to current direction into straight/right/left
    dir = game.direction
    # straight vector
    if dir == Direction.UP:
        straight = (0, -BLOCK_SIZE); right = (BLOCK_SIZE, 0); left = (-BLOCK_SIZE, 0)
    elif dir == Direction.DOWN:
        straight = (0, BLOCK_SIZE); right = (-BLOCK_SIZE, 0); left = (BLOCK_SIZE, 0)
    elif dir == Direction.LEFT:
        straight = (-BLOCK_SIZE, 0); right = (0, -BLOCK_SIZE); left = (0, BLOCK_SIZE)
    elif dir == Direction.RIGHT:
        straight = (BLOCK_SIZE, 0); right = (0, BLOCK_SIZE); left = (0, -BLOCK_SIZE)
    else:
        straight = (0, -BLOCK_SIZE); right = (BLOCK_SIZE, 0); left = (-BLOCK_SIZE, 0)

    d = (dx, dy)
    if d == straight:
        return 0
    if d == right:
        return 1
    if d == left:
        return 2
    # fallback
    return 0

# ---------------------------------------------------------
# Collect expert trajectories by running pure expert policy.
# Returns arrays: states (N x state_dim), action_idxs (N,)
# You can call with num_games to accumulate many examples
# ---------------------------------------------------------
def collect_expert_data(game_class, num_games=200, max_steps_per_game=2000, verbose=True):
    states = []
    actions = []

    for g in range(num_games):
        game = game_class()
        wiggle_moves = 0
        steps = 0
        while True:
            # get state formatted for agent.get_state
            # NOTE: Agent.get_state expects a game instance; you can call the same
            # state function you use for training. We'll build a temporary Agent for this.
            temp_agent = Agent(model_path=None)  # lightweight; only for state extraction
            state = temp_agent.get_state(game)
            # expert decision: mimic your expert logic (A* and Hamiltonian)
            final_move = game.get_next_astar_action()
            danger, food_zone = game.danger_zone_checker(game.snake[0])

            if danger and not food_zone:
                wiggle_moves = 10
                if wiggle_moves > 0:
                    wiggle_moves -= 1
                    final_move = game.get_safest_astar_action()
            elif danger and food_zone:
                # random pick between A* and Hamiltonian (same as you wanted)
                if random.choice([True, False]):
                    final_move = game.get_next_astar_action()
                else:
                    final_move = game.get_safest_astar_action()
            elif final_move is None:
                final_move = game.get_safest_astar_action()

            # convert expert move to action index compatible with agent
            action_idx = move_to_action_index(game, final_move)
            states.append(state)
            actions.append(action_idx)

            # perform move
            reward, done, score = game.play_step(final_move)
            steps += 1
            if done or steps > max_steps_per_game:
                break

        if verbose and (g + 1) % 10 == 0:
            print(f'Collected expert games: {g+1}/{num_games} (total samples: {len(states)})')

    states = np.stack(states).astype(np.int64)  # match agent dtype
    actions = np.array(actions, dtype=np.int64)
    return states, actions

# ---------------------------------------------------------
# Supervised pretraining: use CrossEntropyLoss on the agent's network head.
# This treats agent.model(state) -> logits over 3 classes.
# ---------------------------------------------------------
def pretrain_supervised(agent, states, actions, epochs=5, batch_size=128, lr=1e-3, device=None):
    device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    agent.model.to(device)
    agent.model.train()

    X = torch.tensor(states, dtype=torch.float)
    y = torch.tensor(actions, dtype=torch.long)
    dataset = TensorDataset(X, y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, drop_last=False)

    optimizer = torch.optim.Adam(agent.model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(1, epochs + 1):
        running_loss = 0.0
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            optimizer.zero_grad()
            logits = agent.model(xb)  # shape [B, 3]
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * xb.size(0)
        avg_loss = running_loss / len(dataset)
        print(f'Pretrain epoch {epoch}/{epochs} — loss: {avg_loss:.4f}')

    # after pretraining, move back to eval
    agent.model.to('cpu')
    agent.model.eval()

# ---------------------------------------------------------
# DAgger helper: during RL you can query expert and append to the expert dataset
# ---------------------------------------------------------
def dagger_update(states_buf, actions_buf, new_states, new_actions, max_size=200000):
    # states_buf, actions_buf are numpy arrays or lists; we append and cap size
    states_buf.extend(new_states)
    actions_buf.extend(new_actions)
    # cap
    if len(states_buf) > max_size:
        del states_buf[:len(states_buf) - max_size]
    if len(actions_buf) > max_size:
        del actions_buf[:len(actions_buf) - max_size]
