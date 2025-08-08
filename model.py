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
        
        
     


