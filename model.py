import torch 
import numpy as np 
import torch.nn as nn 
import torch.optim as optim 
import torch.nn.functional as f 
import os 

class Linear_QNet(nn.Module): 
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear_1 = nn.Linear(input_size, hidden_size)
        self.linear_4 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x): 
        x = f.relu(self.linear_1(x))
        x = self.linear_4(x)
        return x

    
    def save(self, file_name='model.pth'):
        model_folder = "./models"
        if not os.path.exists(model_folder):
            os.mkdir(model_folder)

        file_name = os.path.join(model_folder, file_name)
        torch.save(self.state_dict(), file_name)
    
    def load(self, file_name='model.pth'):
        self.load_state_dict(torch.load(file_name))
        self.eval()  # set to evaluation mode


class QTrainer:
    def __init__(self, model, learning_rate, gamma):
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.model = model 
        self.optimizer = optim.Adam(model.parameters(), lr =self.learning_rate) 
        self.loss  = nn.MSELoss()
    
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float32)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float32)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, axis=0)
            next_state = torch.unsqueeze(next_state, axis=0)
            action = torch.unsqueeze(action, axis=0)
            reward = torch.unsqueeze(reward, axis=0)
            done = (done, )
        
        #1: predicted Q-Values with current state  
        pred = self.model(state)
        target = pred.clone()

        #2: reward + gamma * next prediction value 
        for index in range(len(done)):
            Q_new = reward[index]
            if not done[index]: 
                future_q = self.model(next_state[index])
                Q_new = reward[index] +self.gamma * torch.max(future_q)
            
            target[index][torch.argmax(action).item()] = Q_new
        
        self.optimizer.zero_grad()
        loss = self.loss(target, pred)
        loss.backward()

        self.optimizer.step()
        
    # def train_step(self, state, action, reward, next_state, done):
    #     # Convert all to tensors
    #     state = torch.tensor(state, dtype=torch.float32)       # (batch, 1, 10, 10)
    #     next_state = torch.tensor(next_state, dtype=torch.float32)
    #     action = torch.tensor(action, dtype=torch.long)        # (batch, 3) one-hot
    #     reward = torch.tensor(reward, dtype=torch.float32)
    #     done = torch.tensor(done, dtype=torch.bool)

    #     # Make sure there's a batch dimension
    #     if len(state.shape) == 3:
    #         state = state.unsqueeze(0)         # (1, 1, 10, 10)
    #         next_state = next_state.unsqueeze(0)
    #         action = action.unsqueeze(0)
    #         reward = reward.unsqueeze(0)
    #         done = done.unsqueeze(0)

    #     # 1. Predict Q-values from current state
    #     pred = self.model(state)               # (batch, 3)

    #     # 2. Predict Q-values from next state
    #     with torch.no_grad():
    #         next_pred = self.model(next_state) # (batch, 3)

    #     target = pred.clone()
    #     for idx in range(len(done)):
    #         q_new = reward[idx]
    #         if not done[idx]:
    #             q_new += self.gamma * torch.max(next_pred[idx])
    #         move_idx = torch.argmax(action[idx]).item()
    #         target[idx][move_idx] = q_new

    #     # 3. Backpropagation
    #     self.optimizer.zero_grad()
    #     loss = self.loss(pred, target)
    #     loss.backward()
    #     self.optimizer.step()

     


class Conv_QNet(nn.Module):
    def __init__(self, input_channels, height, width, output_size):
        super().__init__()
        self.conv1 = nn.Conv2d(input_channels, 16, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.conv3 = nn.Conv2d(32, 64, 3, padding=1)

        # Compute the flattened size dynamically
        with torch.no_grad():
            sample_input = torch.zeros(1, input_channels, height, width)
            x = self.pool(f.relu(self.conv1(sample_input)))
            x = self.pool(f.relu(self.conv2(x)))
            x = self.pool(f.relu(self.conv3(x)))
            self.flattened_size = x.view(1, -1).size(1)

        self.fc1 = nn.Linear(self.flattened_size, 256)
        self.fc2 = nn.Linear(256, output_size)

    def forward(self, x):
        x = self.pool(f.relu(self.conv1(x)))
        x = self.pool(f.relu(self.conv2(x)))
        x = self.pool(f.relu(self.conv3(x)))
        x = x.view(x.size(0), -1)  # Flatten
        x = f.relu(self.fc1(x))
        x = self.fc2(x)
        return x


    def save(self, file_name='model.pth'):
        model_folder = "./models"
        if not os.path.exists(model_folder):
            os.mkdir(model_folder)
        file_name = os.path.join(model_folder, file_name)
        torch.save(self.state_dict(), file_name)

    def load(self, file_name='model.pth'):
        self.load_state_dict(torch.load(file_name))
        self.eval()
