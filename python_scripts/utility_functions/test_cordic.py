from CORDIC import CORDIC
from fp_logic import *
import numpy as np
import matplotlib.pyplot as plt
import pdb

def main():
    cord = CORDIC(12, 16, 14, 18, 14)
    a = 1
    theta = -3 * np.pi / 4
    theta = np.linspace(-np.pi, np.pi)
    theta_fp = fp_quantize(theta, 18, 14)
    a_fp = fp_quantize(a, 16, 14)
    result = cord.vector(-a_fp, -a_fp, 0)

    # uncomment to look at the iterations of a single value
    xo, yo, zo, sigo = result
    result = np.zeros([xo.shape[0], 4])
    print(xo.shape)
    result[:, 0] = xo[:, 0] / 2**14
    result[:, 1] = yo[:, 0] / 2**14
    result[:, 2] = zo[:, 0] / 2**14
    result[1:(1+sigo.shape[0]), 3] = sigo[:, 0]
    print(result)

    # uncomment to do the datapath of HW3 P2
    fs = 735e3
    f_inst = np.linspace(-75e3, 75e3, 256) * 2 * np.pi / fs
    angle = np.cumsum(f_inst)
    angle_wrapped = np.arctan2(np.sin(angle), np.cos(angle))
    angle_wrapped_fp = fp_quantize(angle_wrapped, 18, 14)
    one = fp_quantize(1, 16, 14)
    result = cord.rotate(one, 0, angle_wrapped_fp)
    x = result[0][-1, :] / 2.0**14
    y = result[1][-1, :] / 2.0**14
    plt.figure()
    plt.plot(x)
    plt.plot(y)
    plt.grid()
    plt.show()

    # back to HW3 P1
    x, y, z, sigma = cord.vector(result[0][-1, :], result[1][-1, :], 0)
    theta = z[-1, :] / 2.0 ** 14
    delta_theta = np.diff(theta)
    f_inst = np.arctan2(np.sin(delta_theta), np.cos(delta_theta)) * fs / (1e3 * 2 * np.pi)
    plt.figure()
    plt.plot(f_inst)
    plt.ylabel('Frequency [kHz]')
    plt.grid()
    plt.show()




if __name__ == '__main__':
    main()