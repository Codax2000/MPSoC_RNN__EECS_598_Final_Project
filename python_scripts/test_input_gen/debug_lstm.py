# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

from fp_logic import fp_quantize
from cordic_dnn_operations import bbr_mac, cordic_vector_multiply
import numpy as np
import pdb

N = 16
R = 12
out1 = bbr_mac(58, 0, 0)
print(out1)

input = np.array([0, 0, 0, 0, 0, -3123,  2193, -1744,  4095])
A_vac = np.array([58, 85, 25, 80, 87,-32, 69, 87, -3])
print(cordic_vector_multiply(input, A_vac))