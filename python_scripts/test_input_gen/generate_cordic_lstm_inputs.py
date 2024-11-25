# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

from cordic_dnn_operations import cordic_matrix_multiply
from write_mem_utils import write_mem_file, write_matrix_to_files
from fp_logic import fp_quantize
from cordic_dnn_operations import get_matrix, cordic_matrix_multiply
import numpy as np


def main():
    n = 11  # number of inputs in X
    m = 4  # number of outputs of Ax + b
    x1 = np.random.uniform(-1, 1-1/2**12, n)
    x1_fp = fp_quantize(x1, r=12)
    x2 = np.random.uniform(-1, 1-1/2**12, n)
    x2_fp = fp_quantize(x2, r=12)
    h1 = np.zeros((m))
    one = fp_quantize(1, r=12) - 1
    input1_fp = np.hstack((x1_fp, h1, one)).astype(int)

    A1 = get_matrix(m, m+n+1)
    A2 = get_matrix(m, m+n+1)
    A3 = get_matrix(m, m+n+1)
    A4 = get_matrix(m, m+n+1)
    
    out1_1 = cordic_matrix_multiply(input1_fp, A1)
    out1_2 = cordic_matrix_multiply(input1_fp, A2)
    out1_3 = cordic_matrix_multiply(input1_fp, A3)
    out1_4 = cordic_matrix_multiply(input1_fp, A4)

    filt = out1_1 < 0
    out1_1[filt] = 0

    input2_fp = np.hstack((x2_fp, out1_1, one)).astype(int)
    out2_1 = cordic_matrix_multiply(input2_fp, A1)
    out2_2 = cordic_matrix_multiply(input2_fp, A2)
    out2_3 = cordic_matrix_multiply(input2_fp, A3)
    out2_4 = cordic_matrix_multiply(input2_fp, A4)

    filt = out2_1 < 0
    out2_1[filt] = 0
    inputs = np.hstack((x1_fp, x2_fp))
    outputs = np.hstack((out1_1, out2_1))

    
    # write inputs and outputs to mem files
    path = './hdl_design/hdl_design.srcs/lstm_layer_tb/mem'
    write_matrix_to_files(A1, path, 16, 6)
    write_matrix_to_files(A2, path, 16, 7)
    write_matrix_to_files(A3, path, 16, 8)
    write_matrix_to_files(A4, path, 16, 9)
    write_mem_file(inputs.astype(int), f'{path}/lstm_input', 16)
    write_mem_file(outputs.astype(int), f'{path}/lstm_output', 16)


if __name__ == '__main__':
    main()