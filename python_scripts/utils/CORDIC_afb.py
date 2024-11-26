import fp_logic as fp
import numpy as np
from CORDIC import CORDIC as cordic
import matplotlib.pyplot as plt

"""
Akash Shetty
Tanh calculation from cascading hyperbolic CORDIC processors to computer sinh and cosh

"""

def Kh_extended_calc(M, N):
    """
    Calculate the extended constant Kh for hyperbolic CORDIC.
    
    This function computes the product of scaling factors for 
    hyperbolic iterations. It combines negatively and positively
    indexed iterations to achieve better convergence.

    Args:
    - M: Number of negatively indexed iterations.
    - N: Number of positively indexed iterations.

    Returns:
    - Kh: The extended constant for hyperbolic scaling.
    """
    product_neg = np.prod([np.sqrt(1 - (1 - 2**(i-2))**2) for i in range(-M, 1)])
    product_pos = np.prod([np.sqrt(1 - (2**-i)**2) for i in range(1, N+1)])
    return product_neg * product_pos

# Partition index calculation
def calculate_partition_index(N):
    """
    Calculate the partition index for splitting hyperbolic iterations.
    
    This index determines how the iterations are divided between 
    negatively indexed iterations and standard iterations.

    Args:
    - N: Total number of iterations.

    Returns:
    - Partition index as an integer.
    """

    return int(round((N - 2) / 3))

# On-the-fly bit extraction
def bit_slice(num, i):
    """
    Extract a specific bit from a number.
    
    This is used to analyze binary representation of numbers,
    especially for calculating rotation directions.

    Args:
    - num: The input number.
    - i: The index of the bit to extract.

    Returns:
    - The i-th bit (0 or 1).
    """
    return ((num >> i) & 0x0001)


def calculate_rotation_direction(z_in, n):
    p_index = calculate_partition_index(n)
    directions = [0] * (n - p_index + 1)
    #directions = [0] * (n)
    d_i = 0
    sign_bit = (z_in >> (n - 1)) & 1  # Extract the most significant bit (sign bit)
    
    for i in range(p_index, n):
       
        b_i = bit_slice(z_in, n - i)
        print(f'signbit: {sign_bit} bit2 {b_i} at {i} bit before at {bit_slice(z_in, n-i-1)}')

        if b_i == 0:
            directions[d_i] = 1
        else:
            directions[d_i] = -1
        d_i +=1
    print(f"Directions: {directions}")

    return directions
    

def cordic_paper_hyperbolic(x, y, z, cb, is_vectoring=False, is_hyperbolic=True):
    """
    Perform hyperbolic CORDIC computations.
    
    This implements the hyperbolic CORDIC pipeline for iterative
    computation of hyperbolic functions like sinh, cosh, and tanh.

    Args:
    - x, y, z: Input values.
    - cb: CORDIC block configuration.
    - is_vectoring: Whether to operate in vectoring mode (default False).
    - is_hyperbolic: Whether to use hyperbolic mode (default True).

    Returns:
    - x, y, z: Final computed values.
    - sigma: Rotation directions used during computation.
    """
    x, y, z = cb._fix_types(x, y, z)
    
    # create result arrays
    x_out = np.zeros((cb._n_rotations + 5, x.shape[1]))
    y_out = np.zeros((cb._n_rotations + 5, x.shape[1]))
    z_out = np.zeros((cb._n_rotations + 5, x.shape[1]))
    sigma = np.zeros((cb._n_rotations+2, x.shape[1]))
    x_out[0, :] = x[0, :]
    y_out[0, :] = y[0, :]
    z_out[0, :] = z[0, :]

    x_out[1, :] = x_out[0, :]
    y_out[1, :] = y_out[0, :]
    z_out[1, :] = z_out[0, :]
    
   
    # rename for readability, now that things are saved
    x = x_out
    y = y_out
    z = z_out
    # set partition index
    p_index = calculate_partition_index(cb._n_rotations)

    # set appropriate lookup table for the operation
    lut, K, index, m = cb.get_rotation_constants(is_hyperbolic)

    M = 1
    K_extend = .2652
    Kh = fp.fp_quantize(1 / K_extend, cb._n_x, cb._r_x)
    index_expand = [i for i in range(-M, 1)]
    index_expand = np.array(index_expand)
    lut_expand = np.arctanh(1-np.power(2.0, index_expand-2))
    lut_expand = fp.fp_quantize(lut_expand, cb._n_z, cb._r_z)

   
    #print(lut_expand)
    #print(len(lut))
    #print(index)
    for i in range(M+1):
        j_current = index_expand[i]
        #print(i)
        filt = z[i+1, :] < 0
        sigma[i, filt] = 1
        sigma[i, ~filt] = -1

        x[i+2, :] = x[i+1, :] - sigma[i, :] * y[i+1, :] * (1- (2.0**(j_current-2)))
        y[i+2, :] = y[i+1, :] - sigma[i, :] * x[i+1, :] * (1- (2.0**(j_current-2)))
        z[i+2, :] = z[i+1, :] + sigma[i, :] * lut_expand[i]
        
        #print(x[i+2, :], y[i+2, :], z[i+2,:],sigma[i, :])
        #print(lut_expand[i])
    
    for i in range(p_index):
        j_current = index[i]

        filt = z[i+3, :] < 0
        sigma[i+2, filt] = 1
        sigma[i+2, ~filt] = -1

        x[i+4, :] = x[i+3, :] - sigma[i+2, :] * y[i+3, :] * (2.0**(-j_current))
        y[i+4, :] = y[i+3, :] - sigma[i+2, :] * x[i+3, :] * (2.0**(-j_current))
        z[i+4, :] = z[i+3, :] + sigma[i+2, :] * lut[i]
        #print(x[i+4, :], y[i+4, :], z[i+4,:],sigma[i+2, :])
    
        
    
    #directions = calculate_rotation_direction(int(z[p_index+3, :]), cb._n_rotations )
    
    for i in range(p_index-1, len(index)):
        dir_index = 0
        j_current = index[i]

        filt = z[i+3, :] < 0
        sigma[i+2, filt] = 1
        sigma[i+2, ~filt] = -1

        x[i+4, :] = x[i+3, :] - sigma[i+2,:] * y[i+3, :] * (2.0**(-j_current))
        y[i+4, :] = y[i+3, :] - sigma[i+2,:] * x[i+3, :] * (2.0**(-j_current))
        z[i+4, :] = z[i+3, :] + sigma[i+2,:] * fp.fp_quantize(2.0**(-j_current))
        #print(x[i+4, :], y[i+4, :], z[i+4,:],sigma[i+2, :], j_current)
        dir_index+1
      
    
    
    x[-1, :] = fp.fp_mult(x[-2, :], Kh, cb._n_x, cb._n_x, cb._r_x, \
                           cb._r_x, cb._n_x, cb._r_x)
    y[-1, :] = fp.fp_mult(y[-2, :], Kh, cb._n_x, cb._n_x, cb._r_x, \
                           cb._r_x, cb._n_x, cb._r_x)
    z[-1, :] = z[-2, :]
    print(x[-1,:], y[-1,:])
    sigma[sigma == 0] = -1

    return x, y, z, sigma

def cordic_paper_linear(x, y, z, cb, is_vectoring=True, is_hyperbolic=False):
    """
    Perform linear mode CORDIC computations.
    
    This function computes linear functions iteratively using the CORDIC algorithm in linear mode.
    It calculates values such as linear interpolation and functions like atan or scaling.

    Args:
    - x, y, z: Initial input values (arrays).
    - cb: CORDIC block configuration, providing constants and parameters.
    - is_vectoring: Boolean indicating whether the vectoring mode is used (default True).
    - is_hyperbolic: Boolean indicating if hyperbolic mode is used (default False).

    Returns:
    - x, y, z: Updated arrays after CORDIC iterations.
    - sigma: Rotation directions used during computation.
    """
    x, y, z = cb._fix_types(x, y, z)

    # create result arrays
    x_out = np.zeros((cb._n_rotations + 2, x.shape[1]))
    y_out = np.zeros((cb._n_rotations + 2, x.shape[1]))
    z_out = np.zeros((cb._n_rotations + 2, x.shape[1]))
    sigma = np.zeros((cb._n_rotations+2, x.shape[1]))
    x_out[0, :] = x[0, :]
    y_out[0, :] = y[0, :]
    z_out[0, :] = z[0, :]

    x = x_out
    y = y_out
    z = z_out
    
    index  = np.array([i for i in range(cb._n_rotations+1)])
    lut = np.power(2.0, -index)
    lut = fp.fp_quantize(lut, cb._n_z, cb._r_z)
    #print(lut)

    for i in range(len(index)):
        j_current = index[i]

        filt = y[i, :]< 0
        sigma[i, filt] = -1
        sigma[i, ~filt] = 1

        x[i+1, :] = x[i, :]
        y[i+1, :] = y[i, :] - sigma[i, :] * x[i, :] * (2.0**(-j_current))
        z[i+1, :] = z[i, :] + sigma[i, :] * lut[i]
    
    
    return x, y, z, sigma


def compute_tanh(z, n_rotations=16, n_x=16, r_x=8, n_z=16, r_z=8):
    """
    Compute the hyperbolic tangent (tanh) using cascading hyperbolic and linear CORDIC processors.

    This function uses a hyperbolic CORDIC block to compute sinh and cosh,
    and then uses a linear CORDIC block to calculate the tanh.

    Args:
    - z: Input value for tanh computation.
    - n_rotations: Number of CORDIC iterations (default 16).
    - n_x, r_x: Fixed-point parameters for x-axis precision.
    - n_z, r_z: Fixed-point parameters for z-axis precision.

    Returns:
    - Final computed tanh(z) value.
    """

    cordic_block1 = cordic(n_rotations=n_rotations, n_x=n_x, r_x=r_x, n_z=n_z, r_z=r_z)
    cordic_block3 = cordic(n_rotations=n_rotations, n_x=n_x, r_x=r_x, n_z=n_z, r_z=r_z)

   
    Kh = .2652

    x_in = fp.fp_quantize(1 / Kh, n_x, r_x)
    y_in = 0
    z_in = fp.fp_quantize(z, n_z, r_z)
    #print(x_in, z_in)
    
    x1, y1, z1, _ = cordic_paper_hyperbolic(x_in, y_in, z_in, cordic_block1)
    #print(x1)
    #print(x1[-2,:], y1[-2,:])
    x_final, y_final, z_final, _ = cordic_paper_linear(x1[-2,:], y1[-2,:], 0, cordic_block3)

    return x1[-2,:], y1[-2,:],z_final[-1,:]

def compute_sigmoid(z, n_rotations=16, n_x=16, r_x=8, n_z=16, r_z=8):
    """
    Compute the sigmoid function using the relationship between sigmoid and tanh.

    The sigmoid function is computed as:
        sigmoid(z) = (1 + tanh(z / 2)) / 2

    Args:
    - z: Input value for sigmoid computation.
    - n_rotations: Number of CORDIC iterations (default 16).
    - n_x, r_x: Fixed-point parameters for x-axis precision.
    - n_z, r_z: Fixed-point parameters for z-axis precision.

    Returns:
    - Final computed sigmoid(z) value.
    """
    z_half = z / 2
    _,_,tanh_half = compute_tanh(z_half, n_rotations=n_rotations, n_x=n_x, r_x=r_x, n_z=n_z, r_z=r_z)
    
    sigmoid = (1 + tanh_half / (2 ** r_z)) / 2
    return sigmoid

def sigmoid(z):
    """
    Compute the sigmoid function using a direct exponential formulation.
    
    Args:
    - z: Input value for sigmoid computation.

    Returns:
    - Computed sigmoid(z) value.
    """
    return 1/(1 + np.exp(-z))

# Testbench for z_values from 
def testbench(z_values):
    """
    Test the CORDIC-based sigmoid and tanh implementations.

    This function compares the CORDIC-based sigmoid and tanh
    with numpy implementations, calculates errors, and plots
    results for analysis.

    Args:
    - z_values: Array of input values to test over.

    Outputs:
    - Plots showing errors and comparisons between CORDIC and numpy results.
    """
    cordic_results_tanh = []
    actual_results_tanh = []
    errors_tanh = []
    cordic_results_sigmoid = []
    actual_results_sigmoid = []
    errors_sigmoid = []
    for z in z_values:
        """
        cordic_sigmoid_result = compute_sigmoid(z)
        cordic_results_sigmoid.append(cordic_sigmoid_result)

        numpy_sigmoid = sigmoid(z)
        actual_results_sigmoid.append(numpy_sigmoid)

        error_sigmoid = abs(cordic_sigmoid_result - numpy_sigmoid)
        errors_sigmoid.append(error_sigmoid)
        """
        _,_,cordic_tanh_result = compute_tanh(z)
        
        cordic_tanh_float = cordic_tanh_result / (2 ** 8)
        cordic_results_tanh.append(cordic_tanh_float)

        numpy_tanh_result = np.tanh(z)
        actual_results_tanh.append(numpy_tanh_result)

        error_tanh = abs(cordic_tanh_float - numpy_tanh_result)
        errors_tanh.append(error_tanh)
        
        #print(f"input z {z} | Cordic Out:{cordic_tanh_float} | Expected Out:{numpy_tanh_result} | error:{error}")
    
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [1, 4]})

    # Plot 1: Error
    axs[0].plot(z_values, errors_tanh, color="green", label="Error")
    axs[0].set_ylabel("Error")
    axs[0].set_title("Error between CORDIC sigmoid and numpy sigmoid")
    axs[0].grid(True)
    axs[0].legend()

    # Plot 2: CORDIC tanh vs numpy tanh
    axs[1].plot(z_values, actual_results_tanh, label="Real-Valued", color="red")
    axs[1].plot(z_values, cordic_results_tanh, label="CORDIC", color="black", linestyle="--")
    axs[1].set_xlabel("Input z")
    axs[1].set_ylabel("sigmoid(z)")
    axs[1].set_title("CORDIC sigmoid vs numpy sigmoid")
    axs[1].grid(True)
    axs[1].legend()

    # Adjust layout
    plt.tight_layout()
    plt.show()

def testbench2(z_values):
    """
    Test the CORDIC-based sigmoid and tanh implementations.

    This function compares the CORDIC-based sigmoid and tanh
    with numpy implementations, calculates errors, and plots
    results for analysis.

    Args:
    - z_values: Array of input values to test over.

    Outputs:
    - Plots showing errors and comparisons between CORDIC and numpy results.
    """
    cordic_results_tanh = []
    actual_results_tanh = []
    errors_tanh = []
    cordic_results_sigmoid = []
    actual_results_sigmoid = []
    errors_sigmoid = []
    for z in z_values:
        """
        cordic_sigmoid_result = compute_sigmoid(z)
        cordic_results_sigmoid.append(cordic_sigmoid_result)

        numpy_sigmoid = sigmoid(z)
        actual_results_sigmoid.append(numpy_sigmoid)

        error_sigmoid = abs(cordic_sigmoid_result - numpy_sigmoid)
        errors_sigmoid.append(error_sigmoid)
        """
        _,cordic_cos_result,_ = compute_tanh(z)
        
        cordic_tanh_float = cordic_cos_result / (2 ** 8)
        cordic_results_tanh.append(cordic_tanh_float)

        numpy_tanh_result = np.sinh(z)
        actual_results_tanh.append(numpy_tanh_result)

        error_tanh = abs(cordic_tanh_float - numpy_tanh_result)
        errors_tanh.append(error_tanh)
        
        #print(f"input z {z} | Cordic Out:{cordic_tanh_float} | Expected Out:{numpy_tanh_result} | error:{error}")
    
    fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True, gridspec_kw={'height_ratios': [1, 4]})

    # Plot 1: Error
    axs[0].plot(z_values, errors_tanh, color="green", label="Error")
    axs[0].set_ylabel("Error")
    axs[0].set_title("Error between CORDIC sigmoid and numpy sigmoid")
    axs[0].grid(True)
    axs[0].legend()

    # Plot 2: CORDIC tanh vs numpy tanh
    axs[1].plot(z_values, actual_results_tanh, label="Real-Valued", color="red")
    axs[1].plot(z_values, cordic_results_tanh, label="CORDIC", color="black", linestyle="--")
    axs[1].set_xlabel("Input z")
    axs[1].set_ylabel("sigmoid(z)")
    axs[1].set_title("CORDIC sigmoid vs numpy sigmoid")
    axs[1].grid(True)
    axs[1].legend()

    # Adjust layout
    plt.tight_layout()
    plt.show()





z_test_values = np.linspace(-3,3, 500)
testbench(z_test_values)

print(compute_tanh(-1) / 2**8)
print(np.tanh(-1))
