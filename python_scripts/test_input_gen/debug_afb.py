import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

from write_mem_utils import write_mem_file, write_matrix_to_files
from fp_logic import fp_quantize
from cordic_dnn_operations import get_matrix, cordic_matrix_multiply, cordic_afb, bbr_mac
from generate_cordic_lstm_inputs import pointwise_mult
import numpy as np
import pdb


def test_pass1():
    xi = np.array([-4364], int)
    xu = np.array([-2240], int)
    xf = np.array([-2415], int)
    xo = np.array([5505], int)

    it = cordic_afb(xi, False, 16, 12)
    ut = cordic_afb(xu, True, 16, 12)
    ft = cordic_afb(xf, False, 16, 12)
    ot = cordic_afb(xo, False, 16, 12)
    
    mult1 = pointwise_mult(ut, it, 16, 12)
    mult2 = pointwise_mult(ft, np.array([0]), 16, 12)
    add1 = mult1 + mult2
    tan_out = cordic_afb(add1.astype(int), True, 16, 12)
    out = bbr_mac(ot[0], 0, tan_out[0])
    pdb.set_trace()


if __name__ == '__main__':
    test_pass1()