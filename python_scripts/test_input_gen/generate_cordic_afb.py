'''
Alex Knowlton
11/21/24

Attempt to write AFB that does both tanh and sigmoid functions in fixed
point logic.
'''
# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

import numpy as np
import matplotlib.pyplot as plt
from fp_logic import fp_quantize
from write_mem_utils import get_2s_complement_hex_string, write_mem_file
from cordic_dnn_operations import cordic_linear_divide, cordic_hyperbolic
import pandas as pd
import pdb


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


def analyze_hyperbolic_results():
    '''
    Compares the results of CORDIC sinh and cosh with ideal floating-point sinh and cosh.
    '''
    N = 16
    R = 8
    inputs = np.linspace(-3, 3, num=500)

    # Ideal floating-point values
    sinh_ideal = np.sinh(inputs)
    cosh_ideal = np.cosh(inputs)
    
    sinh_fp, cosh_fp = np.zeros(500), np.zeros(500)

    # Fixed-point values using CORDIC
    theta_fp = fp_quantize(inputs, N, R)
    cosh_fp, sinh_fp = cordic_hyperbolic(theta_fp, True, N, R)
       
    # Convert fixed-point results back to float
    sinh_cordic = sinh_fp / (2 ** R)
    cosh_cordic = cosh_fp / (2 ** R)

    # Quantization error
    sinh_error = np.abs(sinh_ideal - sinh_cordic)
    cosh_error = np.abs(cosh_ideal - cosh_cordic)

    # Plot results
    plt.figure(figsize=(12, 10))

    # Quantization error
    plt.subplot(3, 1, 1)
    plt.title('CORDIC Hyperbolic Function Results')
    plt.plot(inputs, sinh_error, label='sinh quantization error')
    plt.plot(inputs, cosh_error, label='cosh quantization error')
    plt.ylabel('Quantization Error')
    plt.legend()
    plt.grid()

    # sinh comparison
    plt.subplot(3, 1, 2)
    plt.plot(inputs, sinh_ideal, label='Ideal sinh')
    plt.plot(inputs, sinh_cordic, '--', label='CORDIC sinh')
    plt.ylabel('sinh')
    plt.legend()
    plt.grid()

    # cosh comparison
    plt.subplot(3, 1, 3)
    plt.plot(inputs, cosh_ideal, label='Ideal cosh')
    plt.plot(inputs, cosh_cordic, '--', label='CORDIC cosh')
    plt.xlabel('Input ($\\theta$)')
    plt.ylabel('cosh')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('./pictures/cordic_hyperbolic.png')


def analyze_linear_divide_results():
    '''
    Imports output.csv and plots the result on top of the expected result and
    ideal
    '''
    R = 8
    inputs = np.linspace(-5, 5, num=500)

    # plot ideal inputs
    cosh_fp = fp_quantize(np.cosh(inputs))
    sinh_fp = fp_quantize(np.sinh(inputs))
    zout = cordic_linear_divide(cosh_fp, sinh_fp)[-1, :] / 2**R
    quant_error = np.abs(np.tanh(inputs) - zout)

    # plot division as a tanh function
    plt.figure(figsize=(10, 7))
    plt.subplot(4, 1, 1)
    plt.title('CORDIC Linear Divide')
    plt.plot(inputs, quant_error)
    plt.ylabel('Quantization Error')
    plt.subplot(4, 1, (2, 4))
    plt.plot(inputs, np.tanh(inputs), label='ideal')
    plt.plot(inputs, zout, '--', label='CORDIC')
    plt.xlabel('$\\theta$')
    plt.ylabel('$tanh(\\theta)$')
    plt.legend()
    plt.grid()
    plt.savefig('./pictures/cordic_linear_divide.png')


def main():
    N = 16
    R = 8
    inputs = np.linspace(-5, 5, num=500)

    # plot ideal inputs
    cosh_fp = fp_quantize(np.cosh(inputs))
    sinh_fp = fp_quantize(np.sinh(inputs))
    zout = cordic_linear_divide(cosh_fp, sinh_fp)[-1, :] / 2**R
    analyze_linear_divide_results()
    analyze_hyperbolic_results()

    # send expected inputs and outputs to files
    path = './hdl_design/hdl_design.srcs/cordic_divide_tb/mem/'
    write_mem_file((zout * 2**R).astype(int), f'{path}cordic_divide_outputs', N)
    with open(f'{path}cordic_divide_inputs.mem', 'w') as f:
        for i in range(len(cosh_fp)):
            cos_str = get_2s_complement_hex_string(cosh_fp[i], N)
            sin_str = get_2s_complement_hex_string(sinh_fp[i], N)
            print(f'{sin_str}_{cos_str}', file=f)

if __name__ == '__main__':
    main()