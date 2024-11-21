
import torch
import torch.nn as nn
from model import model

def print_weight_ranges(model):
    for name, param in model.named_parameters():
        if "weight" in name:
            weight_min = param.data.min().item()
            weight_max = param.data.max().item()
            print(f"{name}: min={weight_min:.6f}, max={weight_max:.6f}")

def analyze_packed_params(state_dict):
    """
    Analyzes the dynamic range of packed parameters in a quantized model
    """
    print("\nAnalyzing dynamic ranges of quantized weights:")
    print("-" * 50)
    
    # Group related parameters
    layer_params = {}
    for key in state_dict.keys():
        if '_packed_params._packed_params' in key:
            base_name = key.split('._packed_params')[0]
            if base_name not in layer_params:
                layer_params[base_name] = {}
            layer_params[base_name]['packed_params'] = state_dict[key]
            layer_params[base_name]['scale'] = state_dict[f'{base_name}.scale']
            layer_params[base_name]['zero_point'] = state_dict[f'{base_name}.zero_point']
            layer_params[base_name]['dtype'] = state_dict[f'{base_name}._packed_params.dtype']
    
    # Analyze each layer
    for layer_name, params in layer_params.items():
        packed_params = params['packed_params']
        scale = params['scale']
        zero_point = params['zero_point']
        dtype = params['dtype']
        
        # Extract the weight tensor from the packed params tuple
        weight_tensor = packed_params[0]  # First element is always the weight
        
        # For quantized tensors, we need to use int_repr() to get the underlying integer representation
        int_repr = weight_tensor.int_repr()

        # min / max for int representation
        int_min = int_repr.min().item()
        int_max = int_repr.max().item()
        
        # Get the actual range
        actual_float_min = weight_tensor.min().item()
        actual_float_max = weight_tensor.max().item()

        calc_scale_min = int_min / actual_float_min
        calc_scale_max = int_max / actual_float_max

        
        
        # Dequantize to get the float range
        float_min = (int_min - zero_point) / calc_scale_min
        float_max = (int_max - zero_point) / calc_scale_max
        
        print(f"\nLayer: {layer_name}")
        print("calc scale: ", calc_scale_min, ", ", calc_scale_max)
        print(f"Int8 range: [{int_min}, {int_max}]")
        print(f"Float range: [{float_min:.6f}, {float_max:.6f}]")
        print(f"Scale: {scale:.6f}")
        print(f"Zero point: {zero_point}")
        print(f"Dynamic range: {float_max - float_min:.6f}")
        print(f"Data type: {dtype}")
        print(f"Weight shape: {weight_tensor.shape}")

if __name__ == "__main__":
    # # Load the quantized weights
    # checkpoint_path_q = 'python_scripts\\MLmodel\\weights\\epoch50q.pth'
    # state_dict = torch.load(checkpoint_path_q, map_location='cpu')
    
    # # Analyze the weights
    # analyze_packed_params(state_dict)


    # Instantiate the model
    net = model()
    device = torch.device("cpu")
    checkpoint_path = 'python_scripts\\MLmodel\\weights\\epoch50.pth'
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    net.load_state_dict(checkpoint)
    print("\nAnalyzing dynamic ranges of not quantized weights:")
    print_weight_ranges(net)

    # Instantiate the model (manual quantize)
    net = model()
    device = torch.device("cpu")
    checkpoint_path = 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth'
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    net.load_state_dict(checkpoint)
    print("\nAnalyzing dynamic ranges of manually quantized weights:")
    print_weight_ranges(net)
