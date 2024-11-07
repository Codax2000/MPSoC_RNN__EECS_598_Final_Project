'''
Alex Knowlton
11/1/2024

Generate code for testing LSTM layer. Generate a random matrix
of weights quantized to (8, 8) between the values of -1 and 1 and a random
stream of input data between (-2, 2) quantized to (16, 8). There should 
be an input vector of size 15 and an output vector of size 8. Also adds a bias
term. In other words, stores test data for y = Ax + b

Writes several files:
- /hdl_design/hdl_design.srcs/lstm_layer_tb/mem/fc_input.mem - x inputs
- /hdl_design/hdl_design.srcs/lstm_layer_tb/mem/fc_output.mem - Ax outputs
- /hdl_design/hdl_design.srcs/lstm_layer_tb/mem/i_j.mem - A weights and biases
'''

import numpy as np
from fp_logic import *
from write_mem_utils import write_mem_file
import pdb


def get_matrix(m, n):
    '''
    Returns a random A, b matrix of size m, n between -1 and 1
    '''
    A = np.random.randn(m, n+1) / 10
    return A


def write_matrix_to_files(A, path, n, layer_num):
    '''
    writes a quantized matrix to a file
    '''
    for i in range(len(A)):
        current_vector = A[i, :]
        padded_string = str(i).zfill(3)
        write_mem_file(current_vector, f'{path}/{layer_num}_{padded_string}', n)


def main():
    m = 16  # size of output vector Ax + b
    n = 16  # size of X vector
    Nx = 16  # X quantized to (16,8)
    Rx = 8  # R quantized to (8,8)
    Nw = 8
    Rw = 8

    # generate data
    one = fp_quantize(np.ones((1, 1)), Nx, Rx)
    x0 = np.random.randn(n,1)
    x0_q = fp_quantize(x0, Nx, Rx)  # note - this is the first input
    h0 = np.zeros((m, 1))

    x_hat0 = np.vstack((x0_q, h0, one))

    A1 = get_matrix(m, n + m)
    A2 = get_matrix(m, n + m)
    A3 = get_matrix(m, n + m)
    A4 = get_matrix(m, n + m)
    A1_q = fp_quantize(A1, Nw, Rw)
    A2_q = fp_quantize(A2, Nw, Rw)
    A3_q = fp_quantize(A3, Nw, Rw)
    A4_q = fp_quantize(A4, Nw, Rw)

    # let the output come from A1
    y1 = A1_q @ x_hat0  # choose this one!
    y2 = A2_q @ x_hat0
    y3 = A3_q @ x_hat0
    y4 = A4_q @ x_hat0

    # pass y1 through ReLU
    filt = y1 < 0
    y1[filt] = 0
    y1 = fp_quantize(y1 / (2**Rw), Nx, 0)

    # get second data stream
    x1 = np.random.randn(n,1)
    x1_q = fp_quantize(x1, Nx, Rx)
    h1_q = y1
    x_hat1 = np.vstack((x1_q, h1_q, one))

    y5 = A1_q @ x_hat1  # choose this one!
    y6 = A2_q @ x_hat1
    y7 = A3_q @ x_hat1
    y8 = A4_q @ x_hat1

    # pass through ReLU
    filt = y5 < 0
    y5[filt] = 0
    y5 = fp_quantize(y5 / (2**Rw), Nx, 0)
    
    path = './hdl_design/hdl_design.srcs/lstm_layer_tb/mem'
    write_matrix_to_files(A1_q, path, Nw, 6)
    write_matrix_to_files(A2_q, path, Nw, 7)
    write_matrix_to_files(A3_q, path, Nw, 8)
    write_matrix_to_files(A4_q, path, Nw, 9)

    # write inputs and outputs
    x_q = np.vstack((x0_q, x1_q))
    result = np.vstack((y1, y5))

    # print outputs
    print('X0')
    print(x0_q / 2**Rx)

    print('X1')
    print(x1_q / 2**Rx)

    print('A1')
    print(A1_q / 2**Rw)

    print('H1')
    print(y1 / 2**Rx)

    print('Result')
    print(result / 2**Rx)

    write_mem_file(x_q.T[0], f'{path}/lstm_input', Nx)
    write_mem_file(result.T[0], f'{path}/lstm_output', Nx)


if __name__ == '__main__':
    main()