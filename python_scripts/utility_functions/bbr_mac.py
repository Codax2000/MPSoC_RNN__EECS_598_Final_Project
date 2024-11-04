import numpy as np
import pdb
from fp_logic import fp_quantize
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def int_to_signed_bits(xin, bit_width=16):
    '''
    Given a signed number n, return an array representing the bits of n
    '''
    if xin < 0:
        xin = (1 << bit_width) + xin  # Add 2^bit_width to get the 2's complement representation
    
    # Convert to binary string and pad with leading zeros
    binary_str = format(xin, '0{}b'.format(bit_width))[-bit_width:]
    
    # Convert the binary string to a numpy array of integers (0 and 1)
    bits_array = np.array([int(bit) for bit in binary_str], dtype=int)
    
    return bits_array[::-1]


def bbr_mac(xin, yin, zin, n=12):
    '''
    Computes y_in + zin * xin where all three numbers are in (16,n) fixed
    point notation
    '''
    dir = np.zeros((n + 1))
    y = yin
    dir[0] = 1 if zin < 0 else -1
    zin = int_to_signed_bits(zin)
    for i in range(1, n):
        dir[i] = 1 if zin[n - i] == 0 else -1
    for j in range(n):
        xreg = np.floor(xin / 2**(j + 1))
        if dir[j] == 1:
            xreg = -xreg
        y += xreg
    return y


def plot_heatmap():
    '''
    Plot heatmap of results
    '''
    result_list = []
    z = np.arange(-1, 1, 0.02)
    x = np.linspace(-7, 7, num=700)
    z_fp = fp_quantize(z, 16, 12)
    x_fp = fp_quantize(x, 16, 12)
    results = np.zeros((len(z), len(x)))
    ideal_results = z.reshape((len(z), 1)) * x
    for i in range(len(z)):  # row indexer
        for j in range(len(x)):  # column indexer
            results[i, j] = bbr_mac(x_fp[j], 0, z_fp[i]) / 2**12
            diff = np.abs(results[i, j] - ideal_results[i, j])
            result_list.append({'X': np.round(x_fp[j] / 2**12, 2), 'Z': np.round(z_fp[i] / 2**12, 2), 'Product': diff})
    results = pd.DataFrame(result_list)
    results_pivot = results.pivot(index='Z', columns='X', values='Product')
    sns.heatmap(results_pivot)
    plt.title('CORDIC MAC Heatmap')
    print(np.max(diff))
    print(np.min(diff))
    plt.show()



def main():
    z = fp_quantize(-1, 16, 12)
    x = fp_quantize(1.615, 16, 12)
    y = 0
    print(f'z = {z}\nx = {x}, y = {y}')
    plot_heatmap()


if __name__ == '__main__':
    main()