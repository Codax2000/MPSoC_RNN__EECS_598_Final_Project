import sys
sys.path.insert(1, 'python_scripts/utility_functions')
from textDataset import *
from inference import inference
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import torch.nn as nn
import torch
from quantize_tensor import *
import numpy as np
from model import model, model_q
from bbr_mac import cordic_vector_multiply
from fp_logic import fp_quantize
from generate_cordic_fc_inputs import cordic_matrix_multiply, get_matrix


def main():
    fixed_r = 6
    fixed_n = 16
    #varify model weights:
    modelPath = "python_scripts\\MLmodel\\weights\\epoch50q_manual_int.pth"
    device = torch.device("cpu")
    net = model_q()
    checkpoint = torch.load(modelPath, map_location='cpu')
    net.load_state_dict(checkpoint)

    infilepath = 'python_scripts\\MLmodel\\Dataset\\all_data_q\\data_q.txt'
    input = np.loadtxt(infilepath, delimiter=',')

    inference_data_dir_q = 'python_scripts\\MLmodel\\Dataset\\all_data_q'
    inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\all_key'
    test_dataset_q = TextDataset(data_dir=inference_data_dir_q, key_dir=inference_key_dir)
    test_loader_q = DataLoader(test_dataset_q)
    weights_dir_q = 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth'
    criterion = nn.SmoothL1Loss() #use SmoothL1Loss loss to optimize

    layers = []
    weightsPath = 'python_scripts\\MLmodel\\weights\\layers\\'

    for i in range(8):
        fname = 'layer{}.csv'.format(i)
        layers.append(torch.tensor(np.loadtxt(weightsPath + fname, delimiter=',')).to(torch.int16))

    #inference
    # gt, pred, loss = inference(net, weights_dir_q, test_loader_q, criterion, device)
    # out_ideal = ideal_matmul_model(input, layers)
    out_cordic = cordic_matmul_model(input, layers, fixed_n = fixed_n, fixed_r = fixed_r)

    for i in range(len(gt)):
        plt.figure()
        plt.plot(gt[i].squeeze().cpu())
        plt.plot(pred[i].squeeze().cpu())
        plt.plot(out_ideal, linestyle= ':', linewidth=3)
        plt.title("LSTM Temperature Prediction")
        plt.legend(["ground truth", "prediction fixed", "prediction fixed matmul"])
        plt.xlabel("Time(steps)")
        plt.ylabel("Temperature(normalized)")

        plt.figure()
        plt.plot(pred[i].squeeze().cpu() - out_ideal)
        plt.title("Diff")

    plt.show()



def ideal_matmul_model(input, layers, fixed_r = 6):
    min_max = []
    one = torch.tensor([1]).unsqueeze(1)
    h_t = torch.zeros((40,1))
    c_t = torch.zeros((40,1))
    out = np.array([])
    for i in range(len(input)):        
        inputline = torch.cat((torch.tensor(input[i]).unsqueeze(1),one), dim=0)
        inputline = inputline.to(torch.float32)
        
        f1out = torch.tanh((layers[0].to(torch.float32) * 2**-fixed_r) @ inputline)
        f1out = torch.cat((f1out,one), dim=0)
        f1out = fixed_point_quantize(f1out)
        print(inputline * 2**fixed_r) #
        print(layers[0])
        print(layers[0].to(torch.float32) @ (inputline* 2**fixed_r))
        break

        f2out = torch.tanh((layers[1].to(torch.float32) * 2**-8) @ f1out)
        f2out = torch.cat((f2out,one), dim=0)
        f2out = torch.cat((h_t,f2out), dim=0)
        f2out = fixed_point_quantize(f2out)

        lstm_i = torch.sigmoid((layers[4].to(torch.float32)* 2**-fixed_r) @ f2out)
        lstm_f = torch.sigmoid((layers[5].to(torch.float32)* 2**-fixed_r) @ f2out)
        lstm_g = torch.tanh((layers[6].to(torch.float32)* 2**-fixed_r)@ f2out)
        lstm_o = torch.sigmoid((layers[7].to(torch.float32)* 2**-fixed_r) @ f2out)

        c_t = lstm_f * c_t + lstm_i * lstm_g
        h_t = lstm_o * torch.tanh(c_t)
        c_t = fixed_point_quantize(c_t)
        h_t = fixed_point_quantize(h_t)

        h_t_1 = torch.cat((h_t,one), dim=0)

        f3out = torch.tanh((layers[2].to(torch.float32)* 2**-fixed_r) @ h_t_1)
        f3out = torch.cat((f3out,one), dim=0)
        f3out = fixed_point_quantize(f3out)

        f4out = torch.tanh((layers[3].to(torch.float32)* 2**-fixed_r) @ f3out)
        f4out = fixed_point_quantize(f4out).item()
        out = np.append(out, f4out)
    return out

def cordic_matmul_model(input, layers, fixed_n = 16, fixed_r = 6):
    layers_q = []

    #quantize all layers
    for i in range(8):
        layers_q.append(np.array(layers[i]).astype(int))#)* 2**-fixed_r, fixed_n, fixed_r

    one_q = fp_quantize(np.array([1]), fixed_n, fixed_r) - 1
    

    # print(input_q[0].shape)
    # print(one_q.shape)
    # print(layers_q[0].shape)
    # print(np.append(input_q[0], one_q).shape)

    for i in range(len(input)):
        input_q = fp_quantize(input[i], fixed_n, fixed_r)
        inputline = np.append(input_q, one_q)
        print("quantized input")
        print(inputline)
        print(inputline.shape)
        print("quantized weights")
        print(layers_q[i]*5)
        print(layers_q[i].shape)
        print("ideal output")
        ideal = (layers_q[i]*5/ 2**fixed_r) @ (inputline/2**fixed_r)
        print(ideal)
        macOut1 = cordic_matrix_multiply(inputline, layers_q[i]*5,6)/2**fixed_r
        print("CORDIC output")
        print(macOut1)
        print("diff")
        print(sum(abs(ideal-macOut1)))

        # print("test vec")
        # vout = cordic_vector_multiply(layers_q[i][1], inputline, 12)
        # print(vout/2**fixed_r)
        # print(get_matrix(60,91,16,6).shape)

        # print(layers_q[i][0].shape)
        # print(inputline.shape)

        # vout = cordic_vector_multiply(inputline,layers_q[i][0])
        # print(vout)
        # print(np.sum(layers_q[i][0] * inputline))
        break





    # cordic_matrix_multiply(np.expand_dims(np.append(input_q,one_q), axis=0).transpose(), layer0_q.transpose(), fixed_r)



    # cordic_matrix_multiply()
    return


if __name__ == '__main__':
    main()