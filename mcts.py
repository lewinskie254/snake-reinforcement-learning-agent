import numpy as np 
import random 

class MCTSNode:
    def __init__(self, game, parent=None, action=None):
        self.game = game
        self.parent = parent
        self.children = []
        self.visits = 0
        self.total_reward = 0
        self.action = action  # Action taken to reach this node


class MCTSAgent:
    def __init__(self, simulations_per_move=200):
        self.simulations = simulations_per_move
        self.actions = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # Straight, right, left

    def select_action(self, game):
        root = MCTSNode(self.copy_game(game))

        for _ in range(self.simulations):
            node = self.select(root)
            reward = self.simulate(node.game)
            self.backpropagate(node, reward)

        # Choose child with best average reward
        best_child = max(root.children, key=lambda c: c.total_reward / c.visits)
        return best_child.action

    def select(self, node):
        # Expansion
        if not node.children:
            for action in self.actions:
                new_game = self.copy_game(node.game)
                reward, done, _ = new_game.play_step(action)
                if not done:
                    child = MCTSNode(new_game, parent=node, action=action)
                    node.children.append(child)
            if node.children:
                return random.choice(node.children)
            else:
                return node  # Terminal node

        # UCB1 Selection
        log_N = np.log(node.visits + 1)
        best_score = -float('inf')
        best_child = None
        for child in node.children:
            if child.visits == 0:
                return child
            exploit = child.total_reward / child.visits
            explore = np.sqrt(log_N / child.visits)
            score = exploit + 1.41 * explore  # Exploration parameter
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def simulate(self, game):
        # Play until game over or max steps
        max_steps = 20
        total_reward = 0
        for _ in range(max_steps):
            action = random.choice(self.actions)
            reward, done, _ = game.play_step(action)
            total_reward += reward
            if done:
                break
        return total_reward

    def backpropagate(self, node, reward):
        while node:
            node.visits += 1
            node.total_reward += reward
            node = node.parent

    def copy_game(self, game):
        return game.clone_for_simulation()

