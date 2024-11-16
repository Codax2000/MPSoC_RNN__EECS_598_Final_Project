from write_mem_utils import write_mem_file
import numpy as np
from model import model
import torch.nn as nn
import torch
from quantize_tensor import *
from textDataset import *
from inference import inference
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt


modelPath = "python_scripts\\MLmodel\\weights\\epoch50q_manual_int.pth"
outputPath = "hdl_design\\hdl_design.srcs\\design_sources\\mem_init\\"
fixed_r = 8


if __name__ == '__main__':
    #load model
    device = torch.device("cpu")
    net = model()
    checkpoint = torch.load(modelPath, map_location='cpu')
    net.load_state_dict(checkpoint)
    weights = net.state_dict()

    #get weights and bias
    layer0w = weights["fc1.0.weight"]
    layer0b = weights["fc1.0.bias"].unsqueeze(1)
    layer1w = weights["fc2.0.weight"]
    layer1b = weights["fc2.0.bias"].unsqueeze(1)
    layer2w = weights["fc3.0.weight"]
    layer2b = weights["fc3.0.bias"].unsqueeze(1)
    layer3w = weights["fc4.0.weight"]
    layer3b = weights["fc4.0.bias"].unsqueeze(1)
    ihw = weights["lstm.ih.weight"]
    hhw = weights["lstm.hh.weight"]
    lstmb = (weights["lstm.ih.bias"] + weights["lstm.hh.bias"]).unsqueeze(1)

    # check dim
    print("fc1 weight shape:    ", layer0w.shape)
    print("fc1 bias shape:      ", layer0b.shape)
    print("fc2 weight shape:    ", layer1w.shape)
    print("fc2 bias shape:      ", layer1b.shape)
    print("ih weight shape:     ", ihw.shape)
    print("hh weight shape:     ", hhw.shape)
    print("lstm bias shape:     ", lstmb.shape)
    print("fc3 weight shape:    ", layer2w.shape)
    print("fc3 bias shape:      ", layer2b.shape)
    print("fc4 weight shape:    ", layer3w.shape)
    print("fc4 bias shape:      ", layer3b.shape)

    #concatenate
    layer0 = torch.cat((layer0w, layer0b), dim=1).to(torch.int16)
    layer1 = torch.cat((layer1w, layer1b), dim=1).to(torch.int16)
    layer2 = torch.cat((layer2w, layer2b), dim=1).to(torch.int16)
    layer3 = torch.cat((layer3w, layer3b), dim=1).to(torch.int16)
    i_gate_i, f_gate_i, g_gate_i, o_gate_i = ihw.chunk(4, dim=0)
    i_gate_h, f_gate_h, g_gate_h, o_gate_h = hhw.chunk(4, dim=0)
    i_gate_b, f_gate_b, g_gate_b, o_gate_b = lstmb.chunk(4, dim=0)
    layer4 = torch.cat((i_gate_h, i_gate_i, i_gate_b), dim=1).to(torch.int16)
    layer5 = torch.cat((f_gate_h, f_gate_i, f_gate_b), dim=1).to(torch.int16)
    layer6 = torch.cat((g_gate_h, g_gate_i, g_gate_b), dim=1).to(torch.int16)
    layer7 = torch.cat((o_gate_h, o_gate_i, o_gate_b), dim=1).to(torch.int16)
    

    print("\n\n")
    print("fc1 shape:    ", layer0.shape)
    print("fc2 shape:    ", layer1.shape)
    print("fc3 shape:    ", layer2.shape)
    print("fc4 shape:    ", layer3.shape)
    print("i_gate shape: ", layer4.shape)
    print("f_gate shape: ", layer5.shape)
    print("g_gate shape: ", layer6.shape)
    print("o_gate shape: ", layer7.shape)

    #varify model weights:
    infilepath = 'python_scripts\\MLmodel\\Dataset\\all_data_q\\data_q.txt'
    input = np.loadtxt(infilepath, delimiter=',')
    one = torch.tensor([1]).unsqueeze(1)
    h_t = torch.zeros((40,1))
    c_t = torch.zeros((40,1))
    out = np.array([])

    inference_data_dir_q = 'python_scripts\\MLmodel\\Dataset\\all_data_q'
    inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\all_key'
    test_dataset_q = TextDataset(data_dir=inference_data_dir_q, key_dir=inference_key_dir)
    test_loader_q = DataLoader(test_dataset_q)
    weights_dir_q = 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth'
    criterion = nn.SmoothL1Loss() #use SmoothL1Loss loss to optimize
    gt, pred, loss = inference(net, weights_dir_q, test_loader_q, criterion, device)



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
        lstm_g = torch.tanh((layer6.to(torch.float32) * 2**-fixed_r)@ f2out)
        lstm_o = torch.sigmoid((layer7.to(torch.float32) * 2**-fixed_r)@ f2out)
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


    print(out)

    for i in range(len(gt)):
        plt.figure()
        plt.plot(gt[i].squeeze().cpu())
        plt.plot(pred[i].squeeze().cpu())
        plt.plot(out, linestyle= ':', linewidth=3)
        plt.title("LSTM Temperature Prediction")
        plt.legend(["ground truth", "prediction fixed", "prediction fixed matmul"])
        plt.xlabel("Time(steps)")
        plt.ylabel("Temperature(normalized)")

        plt.figure()
        plt.plot(pred[i].squeeze().cpu() - out)
        plt.title("Diff")

    plt.show()

        

    # print(inputline.shape)

    write_mem_file(layer0.numpy(), outputPath +"layer0", 16)
    write_mem_file(layer1.numpy(), outputPath +"layer1", 16)
    write_mem_file(layer2.numpy(), outputPath +"layer2", 16)
    write_mem_file(layer3.numpy(), outputPath +"layer3", 16)
    write_mem_file(layer4.numpy(), outputPath +"layer4", 16)
    write_mem_file(layer5.numpy(), outputPath +"layer5", 16)
    write_mem_file(layer6.numpy(), outputPath +"layer6", 16)
    write_mem_file(layer7.numpy(), outputPath +"layer7", 16)
    



    
        