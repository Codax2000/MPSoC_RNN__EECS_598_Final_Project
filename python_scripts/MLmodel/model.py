import torch
import torch.nn as nn

class QuantizableLSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size, bias=True):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Split LSTM operations into linear layers for proper quantization
        self.ih = nn.Linear(input_size, 4 * hidden_size, bias=bias)
        self.hh = nn.Linear(hidden_size, 4 * hidden_size, bias=bias)

    def forward(self, x, hidden):
        h_prev, c_prev = hidden
        
        # Compute gates using quantizable linear layers
        gates_ih = self.ih(x)
        gates_hh = self.hh(h_prev)
        
        # Combine gates
        gates = gates_ih + gates_hh
        
        # Split gates
        i_gate, f_gate, g_gate, o_gate = gates.chunk(4, dim=1)
        
        # Apply activations
        i_gate = torch.sigmoid(i_gate)
        f_gate = torch.sigmoid(f_gate)
        g_gate = torch.tanh(g_gate)
        o_gate = torch.sigmoid(o_gate)
        
        # Compute new cell and hidden states
        c_next = f_gate * c_prev + i_gate * g_gate
        h_next = o_gate * torch.tanh(c_next)
        
        return h_next, c_next

# Sample network provided by paper
class model(nn.Module):
    def __init__(self):
        super().__init__()

        self.quant = torch.ao.quantization.QuantStub()

        self.fc1 = nn.Sequential(
            nn.Linear(in_features=90, out_features = 60, bias = True),
            nn.Tanh())
        
        self.fc2 = nn.Sequential(
            nn.Linear(in_features=60, out_features = 30, bias = True),
            nn.Tanh())
        
        self.lstm = QuantizableLSTMCell(input_size = 30, hidden_size = 40, bias = True)
        
        self.fc3 = nn.Sequential(
            nn.Linear(in_features=40, out_features = 20, bias = True),
            nn.Tanh())
        
        self.fc4 = nn.Sequential(
            nn.Linear(in_features=20, out_features = 1, bias = True),
            nn.Tanh())
        
        self.dequant = torch.ao.quantization.DeQuantStub()
        
    def forward(self, x):
        batch_size, seq_len, _ = x.size()  
        h_t = torch.zeros(batch_size, 40, device=x.device)
        c_t = torch.zeros(batch_size, 40, device=x.device)
        outputs = []

        for t in range(seq_len):
            # Fully connected layers
            step_in = x[:, t, :]
            step_in = self.fc1(step_in)
            step_in = self.fc2(step_in)
            #LSTM layer
            h_t, c_t = self.lstm(step_in, (h_t, c_t))
            # Pass the last LSTM output through fully connected layers
            step_in = self.fc3(h_t)
            step_in = self.fc4(step_in)
            outputs.append(step_in)

        outputs = torch.stack(outputs, dim=1)
        outputs = self.dequant(outputs)
        return outputs



