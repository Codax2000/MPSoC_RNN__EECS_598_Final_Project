import torch
import os
from torch.utils.data import Dataset


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
                values = line.strip().split(',')  # Split by comma character
                data.append([float(value) for value in values])  # Convert each value to float
        
        # Load corresponding label/target
        key_path = os.path.join(self.key_dir, self.key_files[idx])
        with open(key_path, 'r') as f:
            key = []
            for line in f:
                values = line.strip().split(',')  # Split by comma character
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