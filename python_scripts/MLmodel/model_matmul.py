import sys
sys.path.insert(1, 'python_scripts/utils')
from textDataset import *
from inference import inference
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import torch.nn as nn
import torch
from quantize_tensor import *
import numpy as np
from model import model, model_q
# from bbr_mac import cordic_vector_multiply
from cordic_dnn_operations import *
from fp_logic import *
# from generate_cordic_fc_inputs import cordic_matrix_multiply, get_matrix
from tqdm import tqdm


def main():
    fixed_r = 12
    fixed_n = 16
    #varify model weights:
    modelPath_q = "python_scripts\\MLmodel\\weights\\epoch50q_manual.pth"
    modelPath = 'python_scripts\\MLmodel\\weights\\epoch50.pth'
    device = torch.device("cpu")
    net_q = model_q()
    net = model()

    infilepath_q = 'python_scripts\\MLmodel\\Dataset\\all_data_q\\data_q.txt'
    input_q = np.loadtxt(infilepath_q, delimiter=',')

    inference_data_dir_q = 'python_scripts\\MLmodel\\Dataset\\all_data_q'
    inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\all_key'
    test_dataset_q = TextDataset(data_dir=inference_data_dir_q, key_dir=inference_key_dir)
    test_loader_q = DataLoader(test_dataset_q)
    # weights_dir_q = 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth'
    criterion = nn.SmoothL1Loss() #use SmoothL1Loss loss to optimize

    layers = []
    weightsPath = 'python_scripts\\MLmodel\\weights\\layers\\'

    for i in range(8):
        fname = 'layer{}.csv'.format(i)
        layers.append(torch.tensor(np.loadtxt(weightsPath + fname, delimiter=',')).to(torch.int16))

    #inference
    gt, pred_q, loss = inference(net_q, modelPath_q, test_loader_q, criterion, device)
    gt, pred, loss = inference(net, modelPath, test_loader_q, criterion, device)
    # out_float = inference(net, modelPath, test_loader_q, criterion, device)
    out_ideal = ideal_matmul_model(input_q, layers, fixed_r = fixed_r)
    out_cordic = cordic_matmul_model(input_q, layers, fixed_n = fixed_n, fixed_r = fixed_r)

    for i in range(len(gt)):
        plt.figure()
        plt.plot(gt[i].squeeze().cpu())
        plt.plot(pred_q[i].squeeze().cpu())
        plt.plot(out_ideal, linestyle= ':', linewidth=3)
        plt.plot(range(0,300), out_cordic)
        plt.title("LSTM Temperature Prediction")
        plt.legend(["ground truth", "pred fixed", "pred fixed matmul", "pred cordic"]) 
        plt.xlabel("Time(steps)")
        plt.ylabel("Temperature(normalized)")

        plt.figure()
        plt.plot(pred_q[i].squeeze().cpu() - out_ideal)
        plt.plot(pred[i].squeeze().cpu() - out_ideal)
        plt.legend(["quantized - quantized matmul", "float - quantized matmul"])
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
        f1out = fixed_point_quantize(f1out, r = fixed_r)

        f2out = torch.tanh((layers[1].to(torch.float32) * 2**-fixed_r) @ f1out)
        f2out = torch.cat((f2out,one), dim=0)
        f2out = torch.cat((h_t,f2out), dim=0)
        f2out = fixed_point_quantize(f2out, r = fixed_r)

        lstm_i = torch.sigmoid((layers[4].to(torch.float32)* 2**-fixed_r) @ f2out)
        lstm_f = torch.sigmoid((layers[5].to(torch.float32)* 2**-fixed_r) @ f2out)
        lstm_g = torch.tanh((layers[6].to(torch.float32)* 2**-fixed_r)@ f2out)
        lstm_o = torch.sigmoid((layers[7].to(torch.float32)* 2**-fixed_r) @ f2out)

        c_t = lstm_f * c_t + lstm_i * lstm_g
        h_t = lstm_o * torch.tanh(c_t)
        c_t = fixed_point_quantize(c_t, r = fixed_r)
        h_t = fixed_point_quantize(h_t, r = fixed_r)

        h_t_1 = torch.cat((h_t,one), dim=0)
 
        f3out = torch.tanh((layers[2].to(torch.float32)* 2**-fixed_r) @ h_t_1)
        f3out = torch.cat((f3out,one), dim=0)
        f3out = fixed_point_quantize(f3out, r = fixed_r)
        

        f4out = torch.tanh((layers[3].to(torch.float32)* 2**-fixed_r) @ f3out)
        f4out = fixed_point_quantize(f4out, r = fixed_r).item()
        out = np.append(out, f4out)

    return out

def sigmoid(z):
    return 1/(1 + np.exp(-z))

def cordic_matmul_model(input, layers, fixed_n = 16, fixed_r = 6):
    layers_q = []

    #quantize all layers
    for i in range(8):
        layers_q.append(np.array(layers[i]).astype(int))#)* 2**-fixed_r, fixed_n, fixed_r

    one_q = fp_quantize(np.array([1]), fixed_n, fixed_r) - 1
    h_t = np.zeros((40)).astype(int)
    c_t = np.zeros((40)).astype(int)
    out = np.array([])
    
    for i in tqdm(range(len(input))):
        input_q = fp_quantize(input[i], fixed_n, fixed_r)
        inputline = np.append(input_q, one_q)

        macOut1 = cordic_matrix_multiply(inputline, layers_q[0], fixed_r)#/2**fixed_r
        macOut1 = cordic_afb(macOut1, is_tanh=True, N=fixed_n, R=fixed_r)
        # macOut1 = fp_quantize(macOut1, fixed_n, fixed_r)

        macOut1 = np.append(macOut1, one_q)

        macOut2 = cordic_matrix_multiply(macOut1, layers_q[1],fixed_r)#/2**fixed_r
        macOut2 = cordic_afb(macOut2, is_tanh=True, N=fixed_n, R=fixed_r)
        # macOut2 = fp_quantize(macOut2, fixed_n, fixed_r)
        macOut2 = np.append(macOut2, one_q)
        macOut2 = np.append(h_t, macOut2)

        lstm_i = cordic_matrix_multiply(macOut2, layers_q[4],fixed_r)#/2**fixed_r
        lstm_f = cordic_matrix_multiply(macOut2, layers_q[5],fixed_r)#/2**fixed_r
        lstm_g = cordic_matrix_multiply(macOut2, layers_q[6],fixed_r)#/2**fixed_r
        lstm_o = cordic_matrix_multiply(macOut2, layers_q[7],fixed_r)#/2**fixed_r
        lstm_i = cordic_afb(lstm_i, is_tanh=False, N=fixed_n, R=fixed_r)
        lstm_f = cordic_afb(lstm_f, is_tanh=False, N=fixed_n, R=fixed_r)
        lstm_g = cordic_afb(lstm_g, is_tanh=True, N=fixed_n, R=fixed_r)
        lstm_o = cordic_afb(lstm_o, is_tanh=False, N=fixed_n, R=fixed_r)

        # c_t = lstm_f * c_t + lstm_i * lstm_g #replace with fixed point mul later
        # h_t = lstm_o * np.tanh(c_t)
        c_t_intermediate1 = fp_mult(lstm_f, c_t, n_x=fixed_n, n_y=fixed_n, r_x=fixed_r, r_y=fixed_r, n_z=fixed_n, r_z=fixed_r)
        c_t_intermediate2 = fp_mult(lstm_i, lstm_g, n_x=fixed_n, n_y=fixed_n, r_x=fixed_r, r_y=fixed_r, n_z=fixed_n, r_z=fixed_r)
        # print(c_t_intermediate1.dtype)
        # print(c_t_intermediate2.dtype)
        c_t = fp_add(c_t_intermediate1, c_t_intermediate2, n_x=fixed_n, n_y=fixed_n, r_x=fixed_r, r_y=fixed_r, n_z=fixed_n, r_z=fixed_r)
        # print(h_t.dtype)
        # print(h_t)
        c_t_tanh = cordic_afb(c_t, is_tanh=True, N=fixed_n, R=fixed_r)
        h_t = fp_mult(lstm_o, c_t_tanh, n_x=fixed_n, n_y=fixed_n, r_x=fixed_r, r_y=fixed_r, n_z=fixed_n, r_z=fixed_r)
        # c_t = fp_quantize(c_t, fixed_n, fixed_r) /2**fixed_r
        # h_t = fp_quantize(h_t, fixed_n, fixed_r)
        h_t_1 = np.append(h_t, one_q)

        # print(h_t.dtype)
        # print(h_t)
        # print(h_t_1)

        macOut3 = cordic_matrix_multiply(h_t_1, layers_q[2],fixed_r)#/2**fixed_r
        macOut3 = cordic_afb(macOut3, is_tanh=True, N=fixed_n, R=fixed_r)
        # macOut3 = fp_quantize(macOut3, fixed_n, fixed_r)
        macOut3 = np.append(macOut3, one_q)



        macOut4 = cordic_vector_multiply(macOut3, layers_q[3],fixed_r)#/2**fixed_r
        macOut4 = cordic_afb(macOut4, is_tanh=True, N=fixed_n, R=fixed_r)
        # macOut4 = fp_quantize(macOut4, fixed_n, fixed_r)

        out = np.append(out, macOut4)
        

        if i == 299:
            return out /2**fixed_r
    return out



if __name__ == '__main__':
    main()