import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def main():
    path = './hdl_design/hdl_design.sim/toplevel_tb/behav/xsim/'
    df = pd.read_csv(f'{path}output.csv')
    expected = df['expected']
    actual = df['received']
    diff = expected - actual
    diff = diff / 2**12
    bins = np.linspace(-0.05, 0.05, num=50)
    plt.hist(diff, bins=bins)
    plt.grid()
    plt.xlabel('LSTM Error')
    plt.title('Quantization Error, with 80000 Samples')
    plt.tight_layout()
    plt.savefig('./pictures/lstm_quant_error.png')


if __name__ == '__main__':
    main()
