# Snake Reinforcement Learning Agent

A reinforcement learning agent that learns to play the classic Snake game using **Deep Q-Learning (DQN)** implemented in **PyTorch**. The project explores several search and planning techniques—including **A\*** pathfinding, **Monte Carlo Tree Search (MCTS)**, **Hamiltonian Cycles**, and **Imitation Learning**—to improve navigation and survival.

The repository serves as an experimental environment for comparing learning-based and search-based approaches to autonomous game playing.

---

## Features

- Deep Q-Network (DQN) implementation
- PyTorch neural network
- Experience Replay
- Target Q-learning
- Epsilon-Greedy exploration
- A* pathfinding
- Monte Carlo Tree Search (MCTS)
- Hamiltonian cycle navigation
- Imitation learning utilities
- Model checkpoint saving and loading
- Training visualization

---

## Technologies

- Python 3
- PyTorch
- NumPy
- Pygame
- Matplotlib

---

## Repository Structure

```
snake-reinforcement-learning-agent/
│
├── agent.py                 # Reinforcement learning agent
├── model.py                 # Deep Q-Network
├── snake.py                 # Snake game environment
├── snake_hamiltonian.py     # Hamiltonian cycle implementation
├── a_star.py                # A* pathfinding
├── mcts.py                  # Monte Carlo Tree Search
├── imitation_utils.py       # Imitation learning utilities
├── helper.py                # Plotting and helper functions
├── common.py                # Shared utilities
├── models/                  # Saved models
├── *.pth                    # Trained model checkpoints
├── requirements.txt
└── README.md
```

---

## Reinforcement Learning Pipeline

The agent learns by interacting with the Snake environment.

```
Game State
      │
Neural Network
      │
Choose Action
      │
Play Game
      │
Receive Reward
      │
Store Experience
      │
Replay Memory
      │
Update Network
```

---

## State Representation

The agent observes features describing the game environment, including:

- Immediate dangers
- Snake movement direction
- Relative food position
- Collision awareness
- Spatial information used for decision making

---

## Learning Algorithm

The Deep Q-Network learns an optimal policy through:

- Experience Replay
- Bellman Equation updates
- Discounted future rewards
- Mini-batch gradient descent
- Exploration vs. exploitation using ε-greedy action selection

---

## Additional Search Algorithms

Beyond reinforcement learning, the project experiments with several classical AI techniques.

### A* Pathfinding

Computes the shortest collision-free path to food using heuristic search.

### Monte Carlo Tree Search (MCTS)

Explores future game states by simulating possible action sequences before selecting the next move.

### Hamiltonian Cycle

Implements a deterministic strategy that traverses the board safely, maximizing survival and avoiding self-collisions.

### Imitation Learning

Provides utilities for incorporating expert behavior into the training process, allowing the agent to learn from predefined strategies.

---

## Installation

Clone the repository

```bash
git clone https://github.com/yourusername/snake-reinforcement-learning-agent.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Training

Start training the reinforcement learning agent:

```bash
python agent.py
```

---

## Playing the Game

Run the Snake environment:

```bash
python snake.py
```

---

## Saved Models

Trained network weights are stored as `.pth` checkpoints and can be loaded for continued training or evaluation.

---

## Learning Objectives

This project explores several important topics in artificial intelligence and reinforcement learning:

- Deep Reinforcement Learning
- Deep Q-Networks (DQN)
- Reward optimization
- Search algorithms
- Path planning
- Game AI
- Experience Replay
- Neural network training with PyTorch
- Hybrid planning and learning approaches

---

## Future Improvements

- Double DQN
- Dueling DQN
- Prioritized Experience Replay
- Rainbow DQN
- Proximal Policy Optimization (PPO)
- Multi-agent Snake
- Curriculum learning
- Parallel environment training

---

## License

Released under the MIT License.
