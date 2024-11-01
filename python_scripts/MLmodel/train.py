from model import model
from torch.utils.data import Dataset, DataLoader
import torch
import os
from os import walk
import copy
import pickle
import matplotlib.pyplot as plt
import numpy as np
import torch.nn.functional as F
from torchinfo import summary
import torch.optim as optim
import torch.nn as nn
from tqdm import tqdm



# Custom dataset class
class TextDataset(Dataset):
    def __init__(self, data_dir, key_dir, transform=None):
        self.data_dir = data_dir
        self.key_dir = key_dir
        self.data_files = sorted(os.listdir(data_dir))
        self.key_files = sorted(os.listdir(key_dir))
        self.transform = transform

    def __len__(self):
        return len(self.data_files)

    def __getitem__(self, idx):
        # Load input data
        data_path = os.path.join(self.data_dir, self.data_files[idx])
        with open(data_path, 'r') as f:
            data = []
            for line in f:
                values = line.strip().split('\t')  # Split by tab character
                data.append([float(value) for value in values])  # Convert each value to float
        
        # Load corresponding label/target
        key_path = os.path.join(self.key_dir, self.key_files[idx])
        with open(key_path, 'r') as f:
            key = []
            for line in f:
                values = line.strip().split('\t')  # Split by tab character
                key.append([float(value) for value in values])  # Convert each value to float

        # Optionally apply any transformation
        if self.transform:
            data = self.transform(data)
            key = self.transform(key)

        # Convert data and key to tensors
        data_tensor = torch.tensor(data, dtype=torch.float32)
        # data_tensor = data_tensor.view(-1, input_len)
        key_tensor = torch.tensor(key, dtype=torch.float32)
        # key_tensor = key_tensor.view(-1, input_len)
        
        return data_tensor, key_tensor

def train(num_epochs, model, criterion, optimizer, train_loader, val_loader):
    for epoch in range(num_epochs):
        
        train_loss = 0
        eval_loss = 0

        #train
        print('Training Epoch [{}/{}]'.format(epoch, num_epochs))
        for data, key in tqdm(train_loader):
            optimizer.zero_grad()

            data = data.to(device)
            key = key.to(device)

            output = model(data)
            loss = criterion(output, key)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        # eval
        print('Evaluating epoch [{}/{}]'.format(epoch, num_epochs))
        
        with torch.no_grad():
            for data, key in tqdm(val_loader):
                data = data.to(device)
                key = key.to(device)
                output = model(data)
                loss = criterion(output, key)
                eval_loss += loss.item()
        print('Epoch [{}/{}] completed: train loss = {:.4f}, eval loss = {:.4f} ' \
              .format(epoch, num_epochs, train_loss, eval_loss))
        PATH = 'python_scripts\\MLmodel\\weights\\epoch{}.pth'.format(epoch)
        torch.save(net.state_dict(), PATH)




if __name__ == "__main__":

    #check GPU
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        print("Using the GPU!")
    else:
        print("WARNING: Could not find GPU! Using CPU only.")
    
    #define model
    net = model().to(device)
    summary(net)

    #hyper_params:
    num_epochs = 5
    batch_size = 32
    sequence_len = 30
    input_len = 90
    lr = 0.01
    criterion = nn.MSELoss() #use MSE loss to optimize for closest abs val to target
    optimizer  = optim.Adam(net.parameters(), lr = lr)

    # Define file paths
    train_data_directory = 'python_scripts\\MLmodel\\Dataset\\Split\\test_data'
    train_key_directory = 'python_scripts\\MLmodel\\Dataset\\Split\\test_key'

    val_data_directory = 'python_scripts\\MLmodel\\Dataset\\Split\\val_data'
    val_key_directory = 'python_scripts\\MLmodel\\Dataset\\Split\\val_key'

    # Instantiate the dataset and DataLoader
    train_dataset = TextDataset(data_dir=train_data_directory, key_dir=train_key_directory)
    train_loader = DataLoader(train_dataset,batch_size=batch_size, shuffle=True)

    val_dataset = TextDataset(data_dir=val_data_directory, key_dir=val_key_directory)
    val_loader = DataLoader(val_dataset,batch_size=batch_size, shuffle=True)

    train(num_epochs, net, criterion, optimizer, train_loader, val_loader)



