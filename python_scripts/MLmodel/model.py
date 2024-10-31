import os
from os import walk
import copy
import pickle

import matplotlib.pyplot as plt
import numpy as np
# from tqdm import tqdm

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchinfo import summary
import torch.optim as optim


device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
if torch.cuda.is_available():
    print("Using the GPU!")
else:
    print("WARNING: Could not find GPU! Using CPU only.")

# Sample network provided by paper
class Net(nn.Module):
    def __init__(self):
        super().__init__()

        # Initialize hidden and cell states
        self.h_t = torch.zeros(1, 40)
        self.c_t = torch.zeros(1, 40)

        self.fc1 = nn.Sequential(
            nn.Linear(in_features=90, out_features = 60, bias = True),
            nn.Tanh())
        
        self.fc2 = nn.Sequential(
            nn.Linear(in_features=60, out_features = 30, bias = True),
            nn.Tanh())
        
        self.lstm = nn.LSTMCell(input_size = 30, hidden_size = 40, bias = True)
        
        self.fc3 = nn.Sequential(
            nn.Linear(in_features=40, out_features = 20, bias = True),
            nn.Tanh())
        
        self.fc4 = nn.Sequential(
            nn.Linear(in_features=20, out_features = 1, bias = True),
            nn.Tanh())
        
    def forward(self, x):
        # Fully connected layers
        x = self.fc1(x)
        x = self.fc2(x)
        #LSTM layer
        self.h_t, self.c_t = self.lstm(x, (self.h_t, self.c_t))
        # Pass the last LSTM output through fully connected layers
        x = self.fc3(self.c_t)
        x = self.fc4(x)

net = Net()
net.to(device)
summary(net, input_size = (1,90))
