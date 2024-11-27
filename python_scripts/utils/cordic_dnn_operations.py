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


def cordic_afb(theta, is_tanh=True, N=16, R=8):
    '''
    Returns the activation function of the inputs using the CORDIC
    algorithm in (N, R) notation.

    Inputs:
        theta - value or 1D numpy array of input values
        is_tanh - if True, computes tanh. Else, computes sigmoid
        N - number of binary bits in (N, R)
        R - number of fractional bits, must satisfy R <= N
    '''
    cosh, sinh = cordic_hyperbolic(theta, is_tanh, N, R)
    div = cordic_linear_divide(cosh, sinh, is_tanh=is_tanh, N=N, R=R)
    return div.astype(int)


def cordic_linear_divide(xin, yin, n_rotations=12, is_tanh=True, N=16, R=8):
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


def cordic_hyperbolic(theta, is_tanh=True, N=16, R=8):
    """
    Perform hyperbolic CORDIC computations.
    
    This implements the hyperbolic CORDIC pipeline for iterative
    computation of hyperbolic functions like sinh, cosh, and tanh.

    Args:
        theta - float or 1D numpy array of values to rotate by, in (N, R)
                fixed point format
        is_tanh - if True, computes cordic rotation for tanh AFB value
        N - total number of bits in fixed point
        R - number of fractional bits, must satisfy R <= N

    Returns:
        sinh - 1D numpy array of sinh values corresponding to sinh(theta)
        cosh - 1D numpy array of cosh values corresponding to cosh(theta)
    """
    n_rotations = 13
    # account for sigmoid if necessary
    if not is_tanh:
        theta = np.trunc(theta / 2)
    
    # set rotation constants in fixed point
    M = 1
    Kh_fp, index_expand, index_standard, lut_expand, lut_standard = \
        get_hyperbolic_constants(M, n_rotations, N, R)

    # set inputs to be arrays
    theta = fix_type(theta)
    x = Kh_fp + np.zeros(theta.shape)
    y = np.zeros(theta.shape)   
    z = theta

    # create output arrays (helps with debugging)
    x_out = np.zeros((1 + len(lut_standard) + len(lut_expand), len(theta)))
    y_out = np.zeros((1 + len(lut_standard) + len(lut_expand), len(theta)))
    z_out = np.zeros((1 + len(lut_standard) + len(lut_expand), len(theta)))
    x_out[0, :] = x
    y_out[0, :] = y
    z_out[0, :] = z
    sigma = np.zeros(z_out.shape)
    x = x_out
    y = y_out
    z = z_out

    for i in range(M+1):
        j_current = index_expand[i]
        filt = z[i, :] < 0
        sigma[i, filt] = 1
        sigma[i, ~filt] = -1

        x[i+1, :] = x[i, :] - sigma[i, :] * (y[i, :] - np.trunc(y[i, :].astype(int)>>(-j_current+2)))
        y[i+1, :] = y[i, :] - sigma[i, :] * (x[i, :] - np.trunc(x[i, :].astype(int)>>(-j_current+2)))
        z[i+1, :] = z[i, :] + sigma[i, :] * lut_expand[i]
    
    for i in range(len(lut_standard)):
        j_current = index_standard[i]
        
        filt = z[i+(M+1), :] < 0
        sigma[i+(M+1),  filt] =  1
        sigma[i+(M+1), ~filt] = -1

        x[i+(M+1)+1, :] = x[i+(M+1), :] - sigma[i+(M+1), :] * \
            np.trunc(y[i+(M+1), :].astype(int)>>j_current)
        y[i+(M+1)+1, :] = y[i+(M+1), :] - sigma[i+(M+1), :] * \
            np.trunc(x[i+(M+1), :].astype(int)>>j_current)
        z[i+(M+1)+1, :] = z[i+(M+1), :] + sigma[i+(M+1), :] * lut_standard[i]

    sinh = y[-1,:]
    cosh = x[-1,:]

    return cosh, sinh


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


def fix_type(x):
    '''
    Ensures that the input is a numpy array.

    Input - x, either numpy array, iterable
    '''
    if type(x) != type(np.zeros(1)):
        x = np.array([x])
    if len(x.shape) == 2:
        x = x[0]
    return x


def get_hyperbolic_constants(M, n_rotations, N=16, R=8):
    '''
    Returns fixed point constants for rotation in (N, R) notation.

    Outputs:
    Kh - actually the inverse, 1 / Kh, that x should be initialized to
    index_expand - rotation indices of expanded range
    index_standard - rotation indices of standard hyperbolic range
    lut_expand - rotation LUT values of expanded range
    lut_standard - rotation LUT values of standard range
    '''
    # set appropriate lookup table for the operation
    
    index = np.arange(n_rotations)
    m = -1
    index += 1
    extra_numbers = []
    extra = 4
    while(extra < n_rotations):
        extra_numbers.append(extra)
        extra = 3 * extra + 1
    extra = np.array(extra_numbers)
    index = np.concatenate((index, extra))
    index = np.sort(index)
    index_standard = index[:n_rotations]
    index_expand = np.arange(-M, 1, dtype=int)
    lut = np.arctanh(np.power(2.0, -index))
    lut_standard = fp_quantize(lut, N, R)
    lut_standard = lut_standard[:n_rotations]
    lut_expand = np.arctanh(1-np.power(2.0, index_expand-2))
    lut_expand = fp_quantize(lut_expand, N, R)
    Kh = Kh_extended_calc(1, n_rotations)
    Kh = fp_quantize(1 / Kh, N, R)
    return Kh, index_expand, index_standard, lut_expand, lut_standard


def Kh_extended_calc(M, N):
    '''
    Calculate the extended constant Kh for hyperbolic CORDIC.
    
    This function computes the product of scaling factors for 
    hyperbolic iterations. It combines negatively and positively
    indexed iterations to achieve better convergence.

    Args:
    - M: Number of negatively indexed iterations.
    - N: Number of positively indexed iterations.

    Returns:
    - Kh: The extended constant for hyperbolic scaling.
    '''
    product_neg = np.prod([np.sqrt(1 - (1 - 2**(i-2))**2) for i in range(-M, 1)])
    product_pos = np.prod([np.sqrt(1 - (2**-i)**2) for i in range(1, N+1)])
    return product_neg * product_pos