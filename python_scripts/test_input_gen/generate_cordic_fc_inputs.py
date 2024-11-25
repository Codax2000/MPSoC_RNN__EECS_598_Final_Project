# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

# import utility functions
from cordic_dnn_operations import cordic_matrix_multiply, get_matrix
from write_mem_utils import write_mem_file, write_matrix_to_files
from fp_logic import fp_quantize
import numpy as np


def main():

    n = 5  # number of inputs in X
    m = 3  # number of outputs of Ax + b
    x = np.random.uniform(-1, 1-1/2**12, n)
    x_hat = np.hstack((x, 1))
    x_hat_fp = fp_quantize(x_hat, r=12)
    x_hat_fp[-1] -= 1
    x2 = np.random.uniform(-1, 1-1/2**12, n)
    x2_hat = np.hstack((x2, 1))
    x2_hat_fp = fp_quantize(x2_hat, r=12)
    x2_hat_fp[-1] -= 1
    A_fp = get_matrix(m, n + 1)
    print(x_hat_fp)
    outputs = cordic_matrix_multiply(x_hat_fp, A_fp)
    outputs2 = cordic_matrix_multiply(x2_hat_fp, A_fp)
    outputs = np.hstack((outputs, outputs2))
    inputs = np.hstack((x_hat_fp[:-1], x2_hat_fp[:-1]))

    print('\nExpected Inputs/Outputs in fixed point')
    print(inputs)
    print(outputs)
    print('\nExpected Fixed Point Matrix')
    print(A_fp)

    # real valued approximation
    A = A_fp / 2**12
    print('\nExpected Outputs:')
    print(outputs / 2**12)
    print(A @ x_hat.reshape((n+1, 1)))
    path = './hdl_design/hdl_design.srcs/fc_layer_tb/mem'
    write_matrix_to_files(A_fp, path, 16, 4)
    write_mem_file(inputs.astype(int), f'{path}/fc_input', 16)
    write_mem_file(outputs.astype(int), f'{path}/fc_output', 16)


if __name__ == '__main__':
    main()