import sys
sys.path.insert(1, 'python_scripts/utility_functions')
from generate_lstm_inputs import write_matrix_to_files
import numpy as np
from model import model
import torch
from quantize_tensor import *
from model_matmul import *


modelPath = "python_scripts\\MLmodel\\weights\\epoch50q_manual_int.pth"
outputPath = "hdl_design\\hdl_design.srcs\\design_sources\\mem_init\\"
csvOutPath = 'python_scripts\\MLmodel\\weights\\layers\\'

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

    # print(layer0)

    np.savetxt(csvOutPath + "layer0.csv", layer0, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer1.csv", layer1, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer2.csv", layer2, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer3.csv", layer3, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer4.csv", layer4, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer5.csv", layer5, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer6.csv", layer6, delimiter=",", fmt="%d")
    np.savetxt(csvOutPath + "layer7.csv", layer7, delimiter=",", fmt="%d")

    
    

    # print(inputline.shape)

    # write_matrix_to_files(layer0.numpy(), outputPath, 16, 0)
    # write_matrix_to_files(layer1.numpy(), outputPath, 16, 1)
    # write_matrix_to_files(layer2.numpy(), outputPath, 16, 2)
    # write_matrix_to_files(layer3.numpy(), outputPath, 16, 3)
    # write_matrix_to_files(layer4.numpy(), outputPath, 16, 4)
    # write_matrix_to_files(layer5.numpy(), outputPath, 16, 5)
    # write_matrix_to_files(layer6.numpy(), outputPath, 16, 6)
    # write_matrix_to_files(layer7.numpy(), outputPath, 16, 7)


    # torch_matmul(layer0, layer1, layer2, layer3, layer4, layer5, layer6, layer7)
    



    
        