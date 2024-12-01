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
from write_mem_utils import write_mem_file, get_2s_complement_hex_string
from cordic_dnn_operations import cordic_linear_divide, cordic_hyperbolic, \
    cordic_afb, get_hyperbolic_constants
import pandas as pd
import pdb


def analyze_hyperbolic_results():
    '''
    Compares the results of CORDIC sinh and cosh with ideal floating-point sinh and cosh.
    '''
    N = 16
    R = 12
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
    Plots expected result and ideal on top of each other
    '''
    R = 12
    inputs = np.linspace(-5, 5, num=500)

    # plot ideal inputs
    cosh_fp = fp_quantize(np.cosh(inputs))
    sinh_fp = fp_quantize(np.sinh(inputs))
    zout = cordic_linear_divide(cosh_fp, sinh_fp, 12, True, 16, R) / 2**R
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


def analyze_afb_results():
    '''
    Plots sigmoid and tanh functions with full range of inputs
    '''
    N = 16
    R = 12

    # set input to have expanded range
    inputs = np.linspace(-10, 10, num=500)
    inputs_fp = fp_quantize(inputs, N, R)

    # generate ideal outputs
    sigm_ideal = np.exp(inputs) / (1 + np.exp(inputs))
    tanh_ideal = np.tanh(inputs)

    # cordic outputs in fixed point
    sigm_fp = cordic_afb(inputs_fp, False, N, R) / 2**R
    tanh_fp = cordic_afb(inputs_fp, True, N, R) / 2**R

    # plot sigmoid outputs
    plt.figure()
    plt.subplot(211)
    plt.plot(inputs, sigm_ideal, label='ideal')
    plt.plot(inputs, sigm_fp, '--', label='CORDIC')
    plt.ylabel('$\\sigma(\\theta)$')
    plt.legend()
    plt.grid()

    # plot tanh outputs
    plt.subplot(212)
    plt.plot(inputs, tanh_ideal, label='ideal')
    plt.plot(inputs, tanh_fp, '--', label='CORDIC')
    plt.ylabel('$tanh(\\theta)$')
    plt.xlabel('$\\theta$')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('./pictures/afb_comparison.png')


def analyze_hardware_results():
    R = 12
    results_sigm = pd.read_csv('./hdl_design/hdl_design.sim/afb_sigmoid_tb/behav/xsim/output.csv')
    results_tanh = pd.read_csv('./hdl_design/hdl_design.sim/afb_tanh_tb/behav/xsim/output.csv')

    # ideal values
    inputs = np.linspace(-10, 10, num=500)
    sigm_ideal = np.exp(inputs) / (1 + np.exp(inputs))
    tanh_ideal = np.tanh(inputs)

    # received values in fixed point
    sigm_fp = results_sigm['received'] / 2**12
    tanh_fp = results_tanh['received'] / 2**12
    
    # quantization error
    q_sigm = np.abs(sigm_ideal - sigm_fp)
    q_tanh = np.abs(tanh_ideal - tanh_fp)

    # plot sigmoid
    plt.figure(figsize=(20, 7))
    plt.subplot(4, 2, 1)
    plt.plot(inputs, q_sigm)
    plt.grid()
    plt.ylabel('Quantization Error')
    plt.title('Sigmoid Function')
    plt.subplot(4, 2, (3, 5))
    plt.plot(inputs, sigm_ideal, label='ideal')
    plt.plot(inputs, sigm_fp, '--', label='CORDIC HDL')
    plt.xlabel('$\\theta$')
    plt.ylabel('$\\sigma(\\theta)$')
    plt.legend()
    plt.grid()

    # plot tanh
    plt.subplot(4, 2, 2)
    plt.plot(inputs, q_tanh)
    plt.grid()
    plt.ylabel('Quantization Error')
    plt.title('Tanh Function')
    plt.subplot(4, 2, (4, 6))
    plt.plot(inputs, tanh_ideal, label='ideal')
    plt.plot(inputs, tanh_fp, '--', label='CORDIC HDL')
    plt.xlabel('$\\theta$')
    plt.ylabel('$\\tanh(\\theta)$')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('./pictures/hdl_afb_comparison')


def print_hyperbolic_constants(N, R):
    Kh, index_expand, index_standard, lut_expand, lut_standard = \
        get_hyperbolic_constants(1, 13, N, R)
    Kh_str = get_2s_complement_hex_string(Kh[0], N)
    index_expand_str = [get_2s_complement_hex_string(i, 4) for i in index_expand]
    index_standard_str = [get_2s_complement_hex_string(i, 4) for i in index_standard]
    lut_expand_str = [get_2s_complement_hex_string(i, N) for i in lut_expand]
    lut_standard_str = [get_2s_complement_hex_string(i, N) for i in lut_standard]

    # print outputs
    print(f'Kh = {Kh_str}')
    print(index_expand_str)
    print(index_standard_str)
    print(lut_expand_str)
    print(lut_standard_str)


def main():
    N = 16
    R = 12
    inputs = np.linspace(-10, 10, (500))
    inputs_fp = fp_quantize(inputs, N, R)

    # analyze subblocks
    analyze_linear_divide_results()
    analyze_hyperbolic_results()
    analyze_afb_results()
    analyze_hardware_results()
    print_hyperbolic_constants(N, R)

    # debug values
    cosht, sinht = cordic_hyperbolic(inputs_fp[115], is_tanh=False, R=R)
    pdb.set_trace()
    out = cordic_linear_divide(cosht, sinht, R=R)

    # get expected outputs
    outputs_tanh = cordic_afb(inputs_fp, True, N, R)
    outputs_sigm = cordic_afb(inputs_fp, False, N, R)

    # send expected inputs and outputs to files
    path_tanh = './hdl_design/hdl_design.srcs/cordic_tanh_tb/mem/'
    path_sigmoid = './hdl_design/hdl_design.srcs/cordic_sigmoid_tb/mem/'
    write_mem_file(inputs_fp, f'{path_tanh}cordic_afb_inputs', N)
    write_mem_file(outputs_tanh, f'{path_tanh}cordic_afb_outputs', N)
    write_mem_file(inputs_fp, f'{path_sigmoid}cordic_afb_inputs', N)
    write_mem_file(outputs_sigm, f'{path_sigmoid}cordic_afb_outputs', N)


if __name__ == '__main__':
    main()