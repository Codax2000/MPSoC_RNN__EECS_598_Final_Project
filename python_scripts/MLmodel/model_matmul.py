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

def torch_matmul(layer0, layer1, layer2, layer3, layer4, layer5, layer6, layer7, fixed_r = 8):
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

    #inference
    gt, pred, loss = inference(net, weights_dir_q, test_loader_q, criterion, device)
    out_ideal = ideal_matmul_model(input, layer0, layer1, layer2, layer3, layer4, layer5, layer6, layer7, fixed_r)
    print(input.shape)

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


def ideal_matmul_model(input, layer0, layer1, layer2, layer3, 
                       layer4, layer5, layer6, layer7, fixed_r = 8):
    
    one = torch.tensor([1]).unsqueeze(1)
    h_t = torch.zeros((40,1))
    c_t = torch.zeros((40,1))
    out = np.array([])
    for i in range(len(input)):        
        inputline = torch.cat((torch.tensor(input[i]).unsqueeze(1),one), dim=0)
        inputline = inputline.to(torch.float32)
        
        f1out = torch.tanh((layer0.to(torch.float32) * 2**-fixed_r) @ inputline)
        f1out = torch.cat((f1out,one), dim=0)
        f1out = fixed_point_quantize(f1out)

        f2out = torch.tanh((layer1.to(torch.float32) * 2**-8) @ f1out)
        f2out = torch.cat((f2out,one), dim=0)
        f2out = torch.cat((h_t,f2out), dim=0)
        f2out = fixed_point_quantize(f2out)

        lstm_i = torch.sigmoid((layer4.to(torch.float32)* 2**-fixed_r) @ f2out)
        lstm_f = torch.sigmoid((layer5.to(torch.float32)* 2**-fixed_r) @ f2out)
        lstm_g = torch.tanh((layer6.to(torch.float32)* 2**-fixed_r)@ f2out)
        lstm_o = torch.sigmoid((layer7.to(torch.float32)* 2**-fixed_r) @ f2out)
        c_t = lstm_f * c_t + lstm_i * lstm_g
        h_t = lstm_o * torch.tanh(c_t)
        c_t = fixed_point_quantize(c_t)
        h_t = fixed_point_quantize(h_t)

        h_t_1 = torch.cat((h_t,one), dim=0)

        f3out = torch.tanh((layer2.to(torch.float32)* 2**-fixed_r) @ h_t_1)
        f3out = torch.cat((f3out,one), dim=0)
        f3out = fixed_point_quantize(f3out)

        f4out = torch.tanh((layer3.to(torch.float32)* 2**-fixed_r) @ f3out)
        f4out = fixed_point_quantize(f4out).item()

        out = np.append(out, f4out)
    return out

def cordic_matmul_model(input, layer0, layer1, layer2, layer3, layer4, layer5, 
                        layer6, layer7, fixed_n = 16, fixed_r = 8):
    
    layer0_q = fp_quantize(layer0, fixed_n, fixed_r)
    layer1_q = fp_quantize(layer1, fixed_n, fixed_r)
    layer2_q = fp_quantize(layer2, fixed_n, fixed_r)
    layer3_q = fp_quantize(layer3, fixed_n, fixed_r)
    layer4_q = fp_quantize(layer4, fixed_n, fixed_r)
    layer5_q = fp_quantize(layer5, fixed_n, fixed_r)
    layer6_q = fp_quantize(layer6, fixed_n, fixed_r)
    layer7_q = fp_quantize(layer7, fixed_n, fixed_r)
    return

function 