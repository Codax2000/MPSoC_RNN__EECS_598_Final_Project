# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

from write_mem_utils import write_mem_file, write_matrix_to_files
from fp_logic import fp_quantize
from cordic_dnn_operations import get_matrix, cordic_matrix_multiply, cordic_afb, bbr_mac
import numpy as np
import pdb


def activation_function(xi, xu, xf, xo, ct, nx=16, rx=12):
    it = cordic_afb(xi, is_tanh=False, N=nx, R=rx)
    ut = cordic_afb(xu, is_tanh=True, N=nx, R=rx)
    ft = cordic_afb(xf, is_tanh=False, N=nx, R=rx)
    ot = cordic_afb(xo, is_tanh=False, N=nx, R=rx)
    mult1 = pointwise_mult(ut, it, nx, rx)
    mult2 = pointwise_mult(ft, ct, nx, rx)
    ct = mult1 + mult2
    tan_out = cordic_afb(ct, is_tanh=True, N=nx, R=rx)
    ht = pointwise_mult(ot, tan_out, nx=rx, rx=rx)
    return ct, ht


def pointwise_mult(x1, x2, nx=16, rx=12):
    '''
    Returns vector of pointwise multiplication between x1 and x2
    Inputs
    x1 - first vector, must have shape (N,)
    x2 - second vector, must also have shape (N,) and be within [-1, 1)
    '''
    result = np.zeros(x1.shape)
    for i in range(x1.shape[0]):
        result[i] = bbr_mac(x1[i], 0, x2[i], nx, rx)
    return result.astype(int)


def main():
    n = 4  # number of inputs in X
    m = 3 # number of outputs of Ax + b
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

    out1, ct = activation_function(out1_1, out1_2, out1_3, out1_4, ct, nx, rx)

    input2_fp = np.hstack((out1, x2_fp, one)).astype(int)
    out2_1 = cordic_matrix_multiply(out1, A1)
    out2_2 = cordic_matrix_multiply(out1, A2)
    out2_3 = cordic_matrix_multiply(out1, A3)
    out2_4 = cordic_matrix_multiply(out1, A4)

    out2, ct = activation_function(out2_1, out2_2, out2_3, out2_4, ct, nx, rx)

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
    print('\nInput Vectors')
    print(input1_fp)
    print(input2_fp)
    print('\nOutput Vectors')
    print(out1_1)
    print(out2_1)


if __name__ == '__main__':
    main()