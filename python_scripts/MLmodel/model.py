import torch
import torch.nn as nn

# Sample network provided by paper
class model(nn.Module):
    def __init__(self):
        super().__init__()

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
        batch_size, seq_len, _ = x.size()  
        h_t = torch.zeros(batch_size, 40, device=x.device)
        c_t = torch.zeros(batch_size, 40, device=x.device)
        outputs = []

        for t in range(seq_len):
            # Fully connected layers
            x = self.fc1(x[:, t, :])
            x = self.fc2(x)
            #LSTM layer
            h_t, c_t = self.lstm(x, (h_t, c_t))
            # Pass the last LSTM output through fully connected layers
            x = self.fc3(h_t)
            x = self.fc4(x)
            outputs.append(x)

        outputs = torch.stack(outputs, dim=1)
        return outputs



