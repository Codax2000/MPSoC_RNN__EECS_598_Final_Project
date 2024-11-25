'''
Alex Knowlton
11/24/2024

Consolidated Python functions for both CORDIC and general linear algebra
functions. 

Contained functions:
bbr_mac - compute y + x * z using BBR method from the paper
cordic_linear_divide - compute y / x using cordic linear mode
cordic_matrix_multiply - compute A * x using BBR method
cordic_vector_multiply - compute x * y using BBR method
get_matrix - get a fixed point matrix for testing
'''

import numpy as np
from fp_logic import fp_quantize
from write_mem_utils import int_to_signed_bits
import pdb


def bbr_mac(xin, yin, zin, nx=16, rx=12):
    '''
    Computes y_in + zin * xin where all three numbers are in (nx,rx) fixed
    point notation.

    Inputs:
        xin - fixed point vector in (nx, rx) notation
        yin - fixed point vector in (nx, rx) notation
        zin - fixed point vector in (nx, rx) notation, must be within [-1, 1)
        nx - number of binary bits
        rx - number of fractional bits, must be rx <= nx
    
    Outputs:
        y - output yin + zin * xin in (nx, rx) notation
    '''
    dir = np.zeros((rx))
    y = yin
    dir[0] = 1 if zin < 0 else 0
    zin = int_to_signed_bits(zin, nx)
    for i in range(1, rx):
        dir[i] = 1 if zin[rx - i] == 0 else 0
    for j in range(rx):
        xreg = np.floor(xin / 2**(j + 1))
        if dir[j] == 1:
            xreg = -xreg
        y += xreg
    return y


def cordic_linear_divide(xin, yin, n_rotations=10, is_tanh=True, N=16, R=8):
    '''
    Returns the linear division of yin / xin.

    Inputs:
        xin - x input array in (N, R) fixed point form
        yin - y input array in (N, R) fixed point form
        is_tanh - Boolean that if is tanh, does nothing to output, otherwise
        adds 1 and divides by 2
    
    Returns
        div_out - divided values after being adjusted for tanh in (N, R)
    '''
    div_out = np.zeros([n_rotations+2, xin.shape[0]])
    for i in range(1, n_rotations+1):
        filt = yin < 0
        delta = np.ones(filt.shape)
        delta[filt] = -1
        theta_i = 2**R / np.power(2, i)
        div_out[i, :] = div_out[i - 1, :] + np.trunc(delta * theta_i)
        yin = yin - np.trunc(xin * delta / (2**i))
    if is_tanh:
        div_out[-1, :] = div_out[-2, :]
    else:
        div_out[-1, :] = (div_out[-2, :] + 2**R) / 2
    return div_out


def cordic_matrix_multiply(x, A, nx=16, rx=12):
    '''
    Returns the matrix multiplication A * x in (nx, rx) notation.

    Inputs:
        x - input column vector in (nx, rx) notation
        A - input matrix in in (nx, rx) notation
        nx - number of binary bits, defaults to 16
        rx - number of fractional bits, defaults to 12, must be rx <= nx
    
    Outputs:
        outputs - output column vector in (nx, rx) notation
    '''
    m = A.shape[0]
    outputs = np.zeros((m))
    for i in range(m):
        outputs[i] = cordic_vector_multiply(x, A[i], nx, rx)
    return outputs


def cordic_vector_multiply(x, z, n=16, r=12):
    '''
    Return the dot product of x * z in (n, r) notation.

    Inputs:
        x - input vector in (n, r) notation, must be within [-1, 1)
        z - input vector in (n, r) notation
        n - number of binary bits, defaults to 16
        r - number of fractional bits, defaults to 12, must be rx <= nx

    Outputs: dot product x * z in (n, r) notation
    '''
    y = np.zeros(x.shape)
    for i in range(len(y)):
        y[i] = bbr_mac(z[i], y[i], x[i], n, r)
    print(f'X = {x}')
    print(f'Z = {z}')
    print(f'Y = {np.cumsum(y)}')
    return np.sum(y)


def get_matrix(m, n, nx=16, rx=12):
    '''
    Returns a fixed-point matrix

    Inputs:
        m - number of rows in output matrix
        n - number of columns in output matrix
        nx - number of binary bits in output matrix, default 16
        rx - number of fractional bits in output matrix, default 12, must be
             rx <= nx
    
    Outputs:
        A - m by n matrix in (nx, rx) notation drawn from a Gaussian
        distribution with mean 0 and standard deviation sqrt(2)
    '''
    A1 = 0.02 * np.random.randn(m, n)
    A1_fp = fp_quantize(A1, n=nx, r=rx)
    return A1_fp