import numpy as np
from fp_logic import fp_quantize
from write_mem_utils import int_to_signed_bits


def bbr_mac(xin, yin, zin, n=12):
    '''
    Computes y_in + zin * xin where all three numbers are in (16,n) fixed
    point notation
    '''
    dir = np.zeros((n))
    y = yin
    dir[0] = 1 if zin < 0 else 0
    zin = int_to_signed_bits(zin)
    for i in range(1, n):
        dir[i] = 1 if zin[n - i] == 0 else 0
    for j in range(n):
        xreg = np.floor(xin / 2**(j + 1))
        if dir[j] == 1:
            xreg = -xreg
        y += xreg
    return y


def cordic_linear_divide(xin, yin, n_rotations=10, is_tanh=True, N=16, R=8):
    '''
    Returns the linear division of yin / xin.

    Inputs:
        xin - x input array in fixed point form
        yin - y input array in fixed point form
        is_tanh - Boolean that if is tanh, does nothing to output, otherwise
        adds 1 and divides by 2
    
    Returns
        div_out - divided values after being adjusted for tanh
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


def cordic_matrix_multiply(x, A, r=12):
    m, n = A.shape
    outputs = np.zeros((m))
    for i in range(m):
        outputs[i] = cordic_vector_multiply(x, A[i])
    return outputs


def cordic_vector_multiply(x, z, n=12):
    y = np.zeros(x.shape)
    for i in range(len(y)):
        y[i] = bbr_mac(z[i], y[i], x[i], n)
    print(f'X = {x}')
    print(f'Z = {z}')
    print(f'Y = {np.cumsum(y)}')
    return np.sum(y)


def get_matrix(m, n, nx=16, rx=12):
    A1 = 2 * np.random.randn(m, n)
    A1_fp = fp_quantize(A1, n=nx, r=rx)
    return A1_fp