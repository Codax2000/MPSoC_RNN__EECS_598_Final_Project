import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def main():
    path = './hdl_design/hdl_design.sim/pytorch_tb/behav/xsim/'
    df = pd.read_csv(f'{path}output.csv')
    t = np.arange(2000)
    received = df['received'] / 2**12
    plt.figure()
    plt.plot(t, received)
    plt.xlabel('Time Index')
    plt.ylabel('Temperature (Normalized)')
    plt.title('Received HDL Time-series plot')
    plt.tight_layout()
    plt.savefig('./pictures/hdl_predictions.png')
    df.to_csv('./python_scripts/eval/output.csv', index=False)


if __name__ == '__main__':
    main()