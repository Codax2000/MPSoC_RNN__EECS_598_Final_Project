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


def cordic_hyperbolic_trig(theta, n_rotations=10, is_tanh=True, N=16, R=8):
    # account for being sigmoid instead of tanh
    if is_tanh:
        theta = np.trunc(theta / 2)
    
    # set initial x values, y is 0
    x = np.ones(theta.shape) / Kh_extended_calc(1, R)
    x = fp_quantize(x, N, R)

    # calculate repeated iterations
    repeated = []
    k = 1
    while 3 * k + 1 <= n_rotations:
        repeated.append(3 * k + 1)
        k = 3 * k + 1
    iterations = np.arange(-1, n_rotations+1)
    iterations = np.hstack((iterations, np.array(repeated)))
    iterations = np.sort(iterations)
    tanh_lut = None  # TODO: sort out tanh LUT with extended range
    tanh_lut = fp_quantize(tanh_lut, N, R)
    theta_results = np.zeros(len(iterations)+1, len(theta))
    x_results = np.zeros(len(iterations)+1, len(theta))
    y_results = np.zeros(len(iterations)+1, len(theta))
    theta_results[0, :] = theta
    x_results[0, :] = x
    for i in range(len(iterations)):
        delta = None  # TODO: compute delta based on theta and such
        x_results[i+1, :] = None  # TODO: compute X based on CORDIC algorithm
        y_results[i+1, :] = None  # TODO: compute Y based on CORDIC algorithm
    return x_results, y_results


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
    cordic_hyperbolic_trig(fp_quantize(inputs))
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