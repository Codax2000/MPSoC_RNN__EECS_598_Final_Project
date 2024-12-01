# add utils to path
import sys
import os
utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utils_path)

import numpy as np
from fp_logic import fp_quantize
from write_mem_utils import write_mem_file, get_2s_complement_hex_string
from cordic_dnn_operations import cordic_vector_multiply, bbr_mac
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


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
    plt.savefig('./pictures/cordic_mac_heatmap.png')


<<<<<<< HEAD:python_scripts/utility_functions/bbr_mac.py
def cordic_vector_multiply(x, z, n=12):
    y = np.zeros(x.shape)
    for i in range(len(y)):
        y[i] = bbr_mac(z[i], y[i], x[i], n)
    # print(f'X = {x}')
    # print(f'Z = {z}')
    # print(f'Y = {np.cumsum(y)}')
    return np.sum(y)


=======
>>>>>>> main:python_scripts/test_input_gen/generate_mac_inputs.py
def write_mac_input(x, z, path, n=16):
    with open(path, 'w') as fd:
        for i in range(x.shape[0]):
            x_string = get_2s_complement_hex_string(x[i], n)
            z_string = get_2s_complement_hex_string(z[i], n)
            print(f'{x_string}_{z_string}', file=fd)


def main():
    plot_heatmap()
    x1 = np.random.uniform(-1, 1, 6)
    x2 = np.random.uniform(-1, 1, 6)
    z = np.random.randn(6)
    x1_fp = fp_quantize(x1, 16, 12)
    x2_fp = fp_quantize(x2, 16, 12)
    z_fp = fp_quantize(z, 16, 12)
    y1_fp = cordic_vector_multiply(x1_fp, z_fp, 12)
    y2_fp = cordic_vector_multiply(x2_fp, z_fp, 12)
    y1 = np.sum(x1 * z)
    y2 = np.sum(x2 * z)
    path = './hdl_design/hdl_design.srcs/cordic_mac_tb/mem'
    print(f'y1 = {y1_fp / 2**12} = {y1} (ideal)')
    print(f'y2 = {y2_fp / 2**12} = {y2} (ideal)')
    x_inputs = np.hstack((x1_fp, x2_fp))
    y_outputs = np.hstack((y1_fp, y2_fp)).astype(int)
    z_inputs = np.hstack((z_fp, z_fp))
    write_mac_input(x_inputs, z_inputs, f'{path}/cordic_mac_input.mem', 16)
    write_mem_file(y_outputs, f'{path}/cordic_mac_output', 16)


if __name__ == '__main__':
    main()