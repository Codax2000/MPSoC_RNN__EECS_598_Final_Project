'''
Akash Shetty
11/25/24

Attempt to write AFB that does both tanh and sigmoid functions in fixed
point logic, comparing with sinh and cosh outputs for given theta inputs.
'''

import numpy as np
import matplotlib.pyplot as plt
from fp_logic import fp_quantize, fp_mult
from write_mem_utils import get_2s_complement_hex_string, write_mem_file
from CORDIC import CORDIC as cordic

def cordic_hyperbolic(theta,cb = cordic(n_rotations=16, n_x=16, r_x=8, n_z=16, r_z=8), n_rotations=11, N=16, R=8, is_hyperbolic=True):
    """
    Perform hyperbolic CORDIC computations.
    
    This implements the hyperbolic CORDIC pipeline for iterative
    computation of hyperbolic functions like sinh, cosh, and tanh.

    Args:
    - x, y, z: Input values.
    - cb: CORDIC block configuration.
    - is_vectoring: Whether to operate in vectoring mode (default False).
    - is_hyperbolic: Whether to use hyperbolic mode (default True).

    Returns:
    - x, y, z: Final computed values.
    - sigma: Rotation directions used during computation.
    """
    Kh = .2652
    #print(theta)
    x = fp_quantize(1 / Kh, N, R)
    y = 0
    x, y, z = cb._fix_types(x, y, theta)
    
    # create result arrays
    x_out = np.zeros((n_rotations + 5, x.shape[1]))
    y_out = np.zeros((n_rotations + 5, x.shape[1]))
    z_out = np.zeros((n_rotations + 5, x.shape[1]))
    sigma = np.zeros((n_rotations+2, x.shape[1]))
    x_out[0, :] = x[0, :]
    y_out[0, :] = y[0, :]
    z_out[0, :] = z[0, :]

    x_out[1, :] = x_out[0, :]
    y_out[1, :] = y_out[0, :]
    z_out[1, :] = z_out[0, :]
    
   
    # rename for readability, now that things are saved
    x = x_out
    y = y_out
    z = z_out

    # set appropriate lookup table for the operation
    lut, K, index, m = cb.get_rotation_constants(is_hyperbolic)

    M = 1
    K_extend = .2652
    Kh = fp_quantize(1 / K_extend, cb._n_x, cb._r_x)
    index_expand = [i for i in range(-M, 1)]
    index_expand = np.array(index_expand)
    lut_expand = np.arctanh(1-np.power(2.0, index_expand-2))
    lut_expand = fp_quantize(lut_expand, cb._n_z, cb._r_z)


    for i in range(M+1):
        j_current = index_expand[i]
        filt = z[i+1, :] < 0
        sigma[i, filt] = 1
        sigma[i, ~filt] = -1

        x[i+2, :] = x[i+1, :] - sigma[i, :] * (y[i+1, :] - np.trunc(y[i+1, :].astype(int)>>(-j_current+2)))
        y[i+2, :] = y[i+1, :] - sigma[i, :] * (x[i+1, :] - np.trunc(x[i+1, :].astype(int)>>(-j_current+2)))
        #print(np.trunc(y[i+1, :]* (2.0**(j_current-2))))
        #print(y[i+1, :]* (2.0**(j_current-2)))
        z[i+2, :] = z[i+1, :] + sigma[i, :] * lut_expand[i]
        #print(x[i+2, :], y[i+2, :], z[i+2,:],sigma[i, :], lut_expand[i],j_current )

        
       
    for i in range(n_rotations):
        j_current = index[i]
        
        filt = z[i+3, :] < 0
        sigma[i+2, filt] = 1
        sigma[i+2, ~filt] = -1

        x[i+4, :] = x[i+3, :] - sigma[i+2, :] * np.trunc(y[i+3, :].astype(int)>>j_current)
        y[i+4, :] = y[i+3, :] - sigma[i+2, :] * np.trunc(x[i+3, :].astype(int)>>j_current)
        z[i+4, :] = z[i+3, :] + sigma[i+2, :] * lut[i]
        #print(x[i+4, :], y[i+4, :], z[i+4,:],sigma[i+2, :],lut[i],j_current)
        
    x[-1, :] = fp_mult(x[-2, :], Kh, cb._n_x, cb._n_x, cb._r_x, \
                           cb._r_x, cb._n_x, cb._r_x)
    y[-1, :] = fp_mult(y[-2, :], Kh, cb._n_x, cb._n_x, cb._r_x, \
                           cb._r_x, cb._n_x, cb._r_x)
    z[-1, :] = z[-2, :]

    sinh = x[-2,:]
    cosh = y[-2,:]

    return sinh, cosh



def analyze_hyperbolic_results():
    '''
    Compares the results of CORDIC sinh and cosh with ideal floating-point sinh and cosh.
    '''

    N = 16
    R = 8
    inputs = np.linspace(-3, 3, num=500)

    # Ideal floating-point values
    sinh_ideal = np.sinh(inputs)
    cosh_ideal = np.cosh(inputs)
    
    sinh_fp, cosh_fp = np.zeros(500), np.zeros(500)

    # Fixed-point values using CORDIC
    theta_fp = fp_quantize(inputs)
    #print(theta_fp)
    for i,theta in enumerate(theta_fp):
        cosh_fp[i], sinh_fp[i] = cordic_hyperbolic(theta)
       

    # Convert fixed-point results back to float
    sinh_cordic = sinh_fp / (2 ** R)
    cosh_cordic = cosh_fp / (2 ** R)
   

    # Quantization error
    sinh_error = np.abs(sinh_ideal - sinh_cordic)
    cosh_error = np.abs(cosh_ideal - cosh_cordic)

    # Plot results
    plt.figure(figsize=(12, 10))

    # Quantization error
    plt.subplot(3, 1, 1)
    plt.title('CORDIC Hyperbolic Function Results')
    plt.plot(inputs, sinh_error, label='sinh quantization error')
    plt.plot(inputs, cosh_error, label='cosh quantization error')
    plt.ylabel('Quantization Error')
    plt.legend()
    plt.grid()

    # sinh comparison
    plt.subplot(3, 1, 2)
    plt.plot(inputs, sinh_ideal, label='Ideal sinh')
    plt.plot(inputs, sinh_cordic, '--', label='CORDIC sinh')
    plt.ylabel('sinh')
    plt.legend()
    plt.grid()

    # cosh comparison
    plt.subplot(3, 1, 3)
    plt.plot(inputs, cosh_ideal, label='Ideal cosh')
    plt.plot(inputs, cosh_cordic, '--', label='CORDIC cosh')
    plt.xlabel('Input ($\\theta$)')
    plt.ylabel('cosh')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.show()


def main():
    
    N = 16
    R = 8
    inputs = np.linspace(-3, 3, num=500)

    # Generate hyperbolic function values using CORDIC
    theta_fp = fp_quantize(inputs)
    
    cb = cordic(n_rotations=16, n_x=16, r_x=8, n_z=16, r_z=8)
    sinh_fp, cosh_fp = cordic_hyperbolic(theta_fp, cb)

    # Convert fixed-point results to output for HDL testing

    path = './hdl_design/hdl_design.srcs/cordic_hyperbolic_tb/mem/'
    write_mem_file((theta_fp).astype(int), f'{path}cordic_hyperbolic_inputs', N)

    with open(f'{path}cordic_hyperbolic_outputs.mem', 'w') as f:
        for i in range(len(cosh_fp)):
            cos_str = get_2s_complement_hex_string((cosh_fp[i]).astype(int), N)
            sin_str = get_2s_complement_hex_string((sinh_fp[i]).astype(int), N)
            print(f'{sin_str}_{cos_str}', file=f)
    
    # Analyze and plot the results
    analyze_hyperbolic_results()


if __name__ == '__main__':
    main()

