from model import model, model_q
from torch.utils.data import DataLoader
import torch
import os
from torchinfo import summary
import torch.optim as optim
import torch.nn as nn
from tqdm import tqdm
import matplotlib.pyplot as plt
from textDataset import *


def inference(model, weight_path, inference_loader, criterion, device):
    ground_truth = []
    prediction = []
    inference_loss = 0
    check_point = torch.load(weight_path, map_location=torch.device(device))
    model.load_state_dict(check_point)

    with torch.no_grad():
        for data, key in tqdm(inference_loader):
            data = data.to(device)
            key = key.to(device)

            output = model(data)
            loss = criterion(output, key)
            inference_loss += loss.item()
            ground_truth.append(key)
            prediction.append(output)
    return ground_truth, prediction, inference_loss/len(inference_loader)
        



if __name__ == "__main__":

    # Quantized can only run on cpu, else check GPU
    device = torch.device("cpu")
    # device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    # if torch.cuda.is_available():
    #     print("Using the GPU!")
    # else:
    #     print("WARNING: Could not find GPU! Using CPU only.")
    
    #define model
    net = model()
    net_q = model_q(16,8)

    #dynamic quantization
    # net = torch.quantization.quantize_dynamic(net, {nn.Linear}, dtype=torch.qint8)

    criterion = nn.SmoothL1Loss() #use SmoothL1Loss loss to optimize

    # Define file paths
    # inference_data_dir = 'python_scripts\\MLmodel\\Dataset\\Split\\test_data'
    # inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\Split\\test_key'
    inference_data_dir = 'python_scripts\\MLmodel\\Dataset\\all_data'
    inference_data_dir_q = 'python_scripts\\MLmodel\\Dataset\\all_data_q'
    inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\all_key'
    weights_dir = 'python_scripts\\MLmodel\\weights\\epoch50.pth'
    weights_dir_q = 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth'

    # Instantiate the dataset and DataLoader
    test_dataset = TextDataset(data_dir=inference_data_dir, key_dir=inference_key_dir)
    test_dataset_q = TextDataset(data_dir=inference_data_dir_q, key_dir=inference_key_dir)

    test_loader = DataLoader(test_dataset)
    test_loader_q = DataLoader(test_dataset_q)

    gt, pred, loss = inference(net, weights_dir, test_loader, criterion, device)
    gt_q, pred_q, loss_q = inference(net_q, weights_dir_q, test_loader_q, criterion, device)

    for i in range(len(gt)):
        plt.figure()
        plt.plot(gt[i].squeeze().cpu())
        plt.plot(pred[i].squeeze().cpu())
        plt.plot(pred_q[i].squeeze().cpu(), linestyle= ':')
        plt.title("LSTM Temperature Prediction")
        plt.legend(["ground truth", "prediction float", "prediction fixed"])
        plt.xlabel("Time(steps)")
        plt.ylabel("Temperature(normalized)")

        plt.figure()
        plt.plot(pred[i].squeeze().cpu() - pred_q[i].squeeze().cpu())
        plt.title("Fixed Point Error")

    plt.show()
    print(loss)

    

    # for data, key in train_loader:
    #     print("Data Batch:", data.shape)
    #     print("Key Batch:", key.shape)
    #     break
