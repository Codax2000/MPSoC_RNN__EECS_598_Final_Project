# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

from write_mem_utils import write_mem_file, write_matrix_to_files
from fp_logic import fp_quantize
from cordic_dnn_operations import get_matrix, cordic_matrix_multiply
import numpy as np
import pdb


def main():
    inputs = get_matrix()


if __name__ == '__main__':
    main()