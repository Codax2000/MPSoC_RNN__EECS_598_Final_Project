'''
Alex Knowlton
10/24

Fixed point logic using numpy
'''

import numpy as np


def fp_quantize(x, n=16, r=8):
    '''
    Quantizes inpu x to mantissa values in Q(n,r) format of the same
    shape as x

    inputs:
    x - input numpy array/matrix
    n - number of bits overall, default 16
    r - number of fractional bits, default 8

    outputs:
    x_fp - quantized mantissa values of x
    '''
    pass


def fp_mult(x, y, n_x=16, n_y=16, r_x=8, r_y=8, n_z=16, r_z=8):
    '''
    Multiplies fixed-point arrays x and y in fixed point form
    and outputs z in fixed point
    Inputs:
    x - array 1
    y - array 2
    n_x - number of bits in x, default 16
    r_x - number of fractional bits in x, default 8
    n_y - number of bits in y, default 16
    r_x - number of fractional bits in y, default 8
    n_z - number of bits in output, default 16
    r_z - number of fractional bits in output, default 8

    Outputs:
    z: x * y quantized to Q(n_z, r_z)
    '''
    pass


def fp_add(x, y, n_x=16, n_y=16, r_x=8, r_y=8, n_z=16, r_z=8):
    '''
    Adds fixed-point arrays x and y in fixed point form
    and outputs z in fixed point
    Inputs:
    x - array 1
    y - array 2
    n_x - number of bits in x, default 16
    r_x - number of fractional bits in x, default 8
    n_y - number of bits in y, default 16
    r_x - number of fractional bits in y, default 8
    n_z - number of bits in output, default 16
    r_z - number of fractional bits in output, default 8

    Outputs:
    z: x * y quantized to Q(n_z, r_z)
    '''
    pass