import torch

def fixed_point_quantize(tensor, n=16, r=8):
    # Calculate scaling factor based on the fractional bits
    scale_factor = 2 ** r
    
    # Quantize: multiply by scale, round, clip to fit within n-bit range, and then scale back
    max_val = 2 ** (n - 1) - 1  # Maximum integer that can be represented
    min_val = -2 ** (n - 1)      # Minimum integer that can be represented
    
    # Apply scaling, round, and clamp to the range
    quantized_tensor = torch.clamp((tensor * scale_factor).round(), min_val, max_val).to(torch.float32) / scale_factor
    
    return quantized_tensor


def fixed_point_quantize_int(tensor, n=16, r=8):
    # Calculate scaling factor based on the fractional bits
    scale_factor = 2 ** r
    
    # Quantize: multiply by scale, round, clip to fit within n-bit range, and then scale back
    max_val = 2 ** (n - 1) - 1  # Maximum integer that can be represented
    min_val = -2 ** (n - 1)      # Minimum integer that can be represented
    
    # Apply scaling, round, and clamp to the range
    quantized_tensor = torch.clamp((tensor * scale_factor).round(), min_val, max_val).to(torch.float32)
    
    return quantized_tensor