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


def generate_divide_inputs():
    N = 16
    R = 12
    inputs = np.linspace(-5, 5, num=500)
    inputs_fp = fp_quantize(inputs, N, R)
    cosh_fp, sinh_fp = cordic_hyperbolic(inputs_fp, False, N, R)
    sigm_fp = cordic_linear_divide(cosh_fp, sinh_fp, 12, False, N, R)

    # plot just to make sure
    sigm_ideal = np.exp(inputs) / (1 + np.exp(inputs))
    plt.figure()
    plt.plot(inputs, sigm_ideal, label='ideal')
    plt.plot(inputs, sigm_fp / 2**R, '--', label='CORDIC')
    plt.xlabel('$\\theta$')
    plt.ylabel('$\\sigma(\\theta)$')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()

    # write inputs to file
    path = './hdl_design/hdl_design.srcs/cordic_divide_tb/mem'
    with open(f'{path}/cordic_divide_inputs.mem', 'w') as fd:
        for i in range(len(cosh_fp)):
            cosh_str = get_2s_complement_hex_string(cosh_fp[i], N)
            sinh_str = get_2s_complement_hex_string(sinh_fp[i], N)
            hex_string = f'{cosh_str}_{sinh_str}'
            print(hex_string, file=fd)
    
    write_mem_file(sigm_fp, f'{path}/cordic_divide_outputs', N)


def generate_hyperbolic_inputs():
    N = 16
    R = 12
    inputs = np.linspace(-10, 10, num=500)
    inputs_fp = fp_quantize(inputs, N, R)
    cosh_fp, sinh_fp = cordic_hyperbolic(inputs_fp, True, N, R)

    # plot just to make sure
    plt.figure()
    plt.subplot(211)
    plt.plot(inputs, cosh_fp)
    plt.ylabel('$\\cosh(\\theta)$')
    plt.grid()
    plt.subplot(212)
    plt.plot(inputs, sinh_fp)
    plt.xlabel('$\\theta$')
    plt.ylabel('$\\sinh(\\theta)$')
    plt.grid()
    plt.tight_layout()
    plt.show()

    # write inputs to file
    path = './hdl_design/hdl_design.srcs/cordic_hyperbolic_tb/mem'
    with open(f'{path}/cordic_hyperbolic_outputs.mem', 'w') as fd:
        for i in range(len(cosh_fp)):
            cosh_str = get_2s_complement_hex_string(cosh_fp[i], N)
            sinh_str = get_2s_complement_hex_string(sinh_fp[i], N)
            hex_string = f'{cosh_str}_{sinh_str}'
            print(hex_string, file=fd)
    
    write_mem_file(inputs_fp, f'{path}/cordic_hyperbolic_inputs', N)


def main():
    # generate_divide_inputs()
    generate_hyperbolic_inputs()


if __name__ == '__main__':
    main()