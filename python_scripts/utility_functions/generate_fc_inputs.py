'''
Alex Knowlton
11/1/2024

Generate code for testing fully-connected layer. Generate a random matrix
of weights quantized to (8, 4) between the values of -1 and 1 and a random
stream of input data between (-2, 2) quantized to (16, 8). There should 
be an input vector of size 15 and an output vector of size 8. Also adds a bias
term. In other words, stores test data for y = Ax + b

Writes several files:
- /hdl_design/hdl_design.srcs/fc_layer_tb/mem/fc_input.mem - x inputs
- /hdl_design/hdl_design.srcs/fc_layer_tb/mem/fc_output.mem - Ax outputs
- /hdl_design/hdl_design.srcs/fc_layer_tb/mem/4_i.mem - A weights and biases
'''
import numpy as np
import os
from fp_logic import *
from write_mem_utils import write_mem_file
import pdb


def get_matrix(m, n):
    '''
    Returns a random A, b matrix of size m, n between -1 and 1
    '''
    A = np.random.randn(m, n+1) / 10
    return A


def write_matrix_to_files(A, path, n):
    '''
    writes a quantized matrix to a file
    '''
    for i in range(len(A)):
        current_vector = A[i, :]
        padded_string = str(i).zfill(3)
        write_mem_file(current_vector, f'{path}/4_{padded_string}', n)


def main():
    m = 56  # size of output vector Ax + b
    n = 16  # size of X vector
    Nx = 16
    Rx = 8
    Nw = 8
    Rw = 8
    x = np.random.randn(n,1)
    x_hat = np.vstack((x, np.ones((1, 1))))
    path = './hdl_design/hdl_design.srcs/fc_layer_tb/mem'
    x_q = fp_quantize(x_hat, Nx, Rx)
    A = get_matrix(m, n)
    A_q = fp_quantize(A, Nw, Rw)
    result = fp_quantize((A_q @ x_q) / (2**Rw), Nx, 0)
    print(A_q / 2**Rw)
    print(x_q / 2**Rx)
    print(result / 2**Rx)
    write_matrix_to_files(A_q, path, Nw)
    write_mem_file(x_q.T[0, :-1], f'{path}/fc_input', Nx)
    write_mem_file(result.T[0], f'{path}/fc_output', Nx)


if __name__ == '__main__':
    main()