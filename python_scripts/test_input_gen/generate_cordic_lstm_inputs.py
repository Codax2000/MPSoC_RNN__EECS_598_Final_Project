# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

from write_mem_utils import write_mem_file, write_matrix_to_files
from fp_logic import fp_quantize
from cordic_dnn_operations import get_matrix, cordic_matrix_multiply, activation_function
import numpy as np
import pdb


def main():
    n = 30  # number of inputs in X
    m = 40 # number of outputs of Ax + b
    nx = 16
    rx = 12
    x1 = np.random.uniform(-1, 1-1/2**12, n)
    x1_fp = fp_quantize(x1, nx, rx)
    x2 = np.random.uniform(-1, 1-1/2**12, n)
    x2_fp = fp_quantize(x2, nx, rx)
    h1 = np.zeros((m))
    ct = np.zeros((m)).astype(int)
    one = fp_quantize(1, nx, rx) - 1
    input1_fp = np.hstack((h1, x1_fp, one)).astype(int)

    A1 = get_matrix(m, m+n+1, nx, rx)
    A2 = get_matrix(m, m+n+1, nx, rx)
    A3 = get_matrix(m, m+n+1, nx, rx)
    A4 = get_matrix(m, m+n+1, nx, rx)

    out1_1 = cordic_matrix_multiply(input1_fp, A1)
    out1_2 = cordic_matrix_multiply(input1_fp, A2)
    out1_3 = cordic_matrix_multiply(input1_fp, A3)
    out1_4 = cordic_matrix_multiply(input1_fp, A4)

    out1, ct1 = activation_function(out1_1, out1_2, out1_3, out1_4, ct, nx, rx)

    input2_fp = np.hstack((out1, x2_fp, one)).astype(int)
    out2_1 = cordic_matrix_multiply(input2_fp, A1)
    out2_2 = cordic_matrix_multiply(input2_fp, A2)
    out2_3 = cordic_matrix_multiply(input2_fp, A3)
    out2_4 = cordic_matrix_multiply(input2_fp, A4)

    out2, ct2 = activation_function(out2_1, out2_2, out2_3, out2_4, ct1, nx, rx)

    inputs = np.hstack((x1_fp, x2_fp))
    outputs = np.hstack((out1, out2))
    
    # write inputs and outputs to mem files
    path = './hdl_design/hdl_design.srcs/lstm_layer_tb/mem'
    write_matrix_to_files(A1, path, nx, 6)
    write_matrix_to_files(A2, path, nx, 7)
    write_matrix_to_files(A3, path, nx, 8)
    write_matrix_to_files(A4, path, nx, 9)
    write_mem_file(inputs, f'{path}/lstm_input', nx)
    write_mem_file(outputs, f'{path}/lstm_output', nx)

    # print outputs for easier debugging
    print('A Matrix')
    print(A1)
    print()
    print(A2)
    print()
    print(A3)
    print()
    print(A4)
    print('\nInput Vectors')
    print(input1_fp)
    print(input2_fp)
    print('\nOutput Vectors')
    print(out1_1)
    print(out1_2)
    print(out1_3)
    print(out1_4)
    print(out2_1)
    print(out2_2)
    print(out2_3)
    print(out2_4)
    print('\nAFB Output')
    print(out1)
    print(out2)
    print('\nCt outputs')
    print(ct1)
    print(ct2)



if __name__ == '__main__':
    main()