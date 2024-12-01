
import torch
import torch.nn as nn
from model import model
from torch.utils.data import Dataset, DataLoader
import os
from quantize_tensor import *
from textDataset import *


def prepare_model_for_quantization(checkpoint):
    # Create model instance
    net = model()

    # Load the trained weights
    
    net.load_state_dict(checkpoint)
    
    net.eval()
    quantized_model = torch.ao.quantization.quantize_dynamic(
        net,
        {nn.Linear},  # custom LSTM is made up of Linear layers
        dtype=torch.qint8,
        inplace=False
    )
    
    return quantized_model


def static_quantize(checkpoint):
    net = model()
    net.load_state_dict(checkpoint)
    net.eval()
    net.qconfig = torch.ao.quantization.get_default_qconfig('x86')
    net_prepared = torch.ao.quantization.prepare(net)

    val_data_directory = 'python_scripts\\MLmodel\\Dataset\\Split\\val_data'
    val_key_directory = 'python_scripts\\MLmodel\\Dataset\\Split\\val_key'

    test_dataset = TextDataset(data_dir=val_data_directory, key_dir=val_key_directory)
    test_loader = DataLoader(test_dataset,batch_size=32, shuffle=True)

    for data, key in test_loader:
        net_prepared(data)

    model_int8 = torch.ao.quantization.convert(net_prepared)

    return model_int8


def quantize_fix_manual(checkpoint, n, r):
    net = model()
    net.load_state_dict(checkpoint)

    quantized_dict = {}
    for key, tensor in net.state_dict().items():
        # quantized_dict[key] = fixed_point_quantize(tensor, n, r)
        quantized_dict[key] = fixed_point_quantize_int(tensor, n, r) # for fixed int

    net.load_state_dict(quantized_dict)
    return net

    

if __name__ == "__main__":

    # dynamic quantize: 
    
    # Quantize the model
    checkpoint = torch.load('python_scripts\\MLmodel\\weights\\epoch50.pth', map_location='cpu')
    # quantized_model = prepare_model_for_quantization(checkpoint) 
    # quantized_model = static_quantize(checkpoint)
    quantized_model = quantize_fix_manual(checkpoint,16,12)
    
    # Save the quantized model
    # torch.save(quantized_model.state_dict(), 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth')
    torch.save(quantized_model.state_dict(), 'python_scripts\\MLmodel\\weights\\epoch50q_manual_int.pth')
    
    # Print state dict keys to verify quantization
    state_dict = quantized_model.state_dict()
    print("\nQuantized model state dict keys:")
    for key in state_dict.keys():
        print(key)