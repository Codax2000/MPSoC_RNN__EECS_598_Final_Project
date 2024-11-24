from bbr_mac import cordic_vector_multiply
from write_mem_utils import write_mem_file
from fp_logic import fp_quantize
from generate_lstm_inputs import write_matrix_to_files
from generate_cordic_fc_inputs import get_matrix, cordic_matrix_multiply
import numpy as np


def main():
    n = 90  # number of inputs in X
    m = 60  # number of outputs of Ax + b
    x1 = np.random.uniform(-1, 1-1/2**6, n)
    x1_fp = fp_quantize(x1, r=6)
    x2 = np.random.uniform(-1, 1-1/2**6, n)
    x2_fp = fp_quantize(x2, r=12)
    # h1 = np.zeros((m))
    one = fp_quantize(1, r=6) - 1
    input1_fp = np.hstack((x1_fp, one)).astype(int)

    A1 = get_matrix(m, n+1,rx=6)
    print(A1)
    print(input1_fp)
    # A2 = get_matrix(m, m+n+1)
    # A3 = get_matrix(m, m+n+1)
    # A4 = get_matrix(m, m+n+1)
    
    # out1_1 = cordic_matrix_multiply(input1_fp, A1)
    # out1_2 = cordic_matrix_multiply(input1_fp, A2)
    # out1_3 = cordic_matrix_multiply(input1_fp, A3)
    # out1_4 = cordic_matrix_multiply(input1_fp, A4)

    # in1 =  np.random.uniform(-1, 1-1/2**12, n)
    # in1_q = fp_quantize(in1, r=12)

    out1_1 = cordic_matrix_multiply(input1_fp, A1, 6)
    
    a = out1_1/2**6
    b=(A1/2**6) @ (input1_fp/2**6)
    print(a)
    print(b)
    print(sum(abs(b-a)))

    inputs = x1_fp

    filt = out1_1 < 0
    out1_1[filt] = 0
    outputs = out1_1

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