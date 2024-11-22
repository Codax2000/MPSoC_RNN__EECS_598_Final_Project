'''
Alex Knowlton
11/21/24

Attempt to write AFB that does both tanh and sigmoid functions in fixed
point logic.
'''
import numpy as np
import matplotlib.pyplot as plt
from fp_logic import fp_quantize
from write_mem_utils import get_2s_complement_hex_string, write_mem_file
import pandas as pd
import pdb


def cordic_linear_divide(xin, yin, n_rotations=10, is_tanh=True, N=16, R=8):
    '''
    Returns the linear division of yin / xin.

    Inputs:
        xin - x input array in fixed point form
        yin - y input array in fixed point form
        is_tanh - Boolean that if is tanh, does nothing to output, otherwise
        adds 1 and divides by 2
    
    Returns
        div_out - divided values after being adjusted for tanh
    '''
    div_out = np.zeros([n_rotations+2, xin.shape[0]])
    for i in range(1, n_rotations+1):
        filt = yin < 0
        delta = np.ones(filt.shape)
        delta[filt] = -1
        theta_i = 2**R / np.power(2, i)
        div_out[i, :] = div_out[i - 1, :] + np.trunc(delta * theta_i)
        yin = yin - np.trunc(xin * delta / (2**i))
    if is_tanh:
        div_out[-1, :] = div_out[-2, :]
    else:
        div_out[-1, :] = (div_out[-2, :] + 2**R) / 2
    return div_out


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
    plt.show()


def main():
    N = 16
    R = 8
    inputs = np.linspace(-5, 5, num=500)

    # plot ideal inputs
    cosh_fp = fp_quantize(np.cosh(inputs))
    sinh_fp = fp_quantize(np.sinh(inputs))
    zout = cordic_linear_divide(cosh_fp, sinh_fp)[-1, :] / 2**R
    
    analyze_linear_divide_results()

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