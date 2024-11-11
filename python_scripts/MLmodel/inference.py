from model import model
from torch.utils.data import Dataset, DataLoader
import torch
import os
from torchinfo import summary
import torch.optim as optim
import torch.nn as nn
from tqdm import tqdm
import matplotlib.pyplot as plt



# Custom dataset class
class TextDataset(Dataset):
    def __init__(self, data_dir, key_dir, transform=None):
        self.data_dir = data_dir
        self.key_dir = key_dir
        self.data_files = sorted(os.listdir(data_dir))
        self.key_files = sorted(os.listdir(key_dir))
        self.transform = transform

    def __len__(self):
        return len(self.data_files)

    def __getitem__(self, idx):
        # Load input data
        data_path = os.path.join(self.data_dir, self.data_files[idx])
        with open(data_path, 'r') as f:
            data = []
            for line in f:
                values = line.strip().split(',')  # Split by tab character
                data.append([float(value) for value in values])  # Convert each value to float
        
        # Load corresponding label/target
        key_path = os.path.join(self.key_dir, self.key_files[idx])
        with open(key_path, 'r') as f:
            key = []
            for line in f:
                values = line.strip().split(',')  # Split by tab character
                key.append([float(value) for value in values])  # Convert each value to float

        # Optionally apply any transformation
        if self.transform:
            data = self.transform(data)
            key = self.transform(key)

        # Convert data and key to tensors
        data_tensor = torch.tensor(data, dtype=torch.float32)
        # data_tensor = data_tensor.view(-1, input_len)
        key_tensor = torch.tensor(key, dtype=torch.float32)
        # key_tensor = key_tensor.view(-1, input_len)
        
        return data_tensor, key_tensor

def inference(model, weight_path, inference_loader, criterion):
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

    #dynamic quantization
    # net = torch.quantization.quantize_dynamic(net, {nn.Linear}, dtype=torch.qint8)

    criterion = nn.SmoothL1Loss() #use MSE loss to optimize for closest abs val to target

    # Define file paths
    # inference_data_dir = 'python_scripts\\MLmodel\\Dataset\\Split\\test_data'
    # inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\Split\\test_key'
    inference_data_dir = 'python_scripts\\MLmodel\\Dataset\\all_data'
    inference_key_dir = 'python_scripts\\MLmodel\\Dataset\\all_key'
    weights_dir = 'python_scripts\\MLmodel\\weights\\epoch50.pth'
    weights_dir_q = 'python_scripts\\MLmodel\\weights\\epoch50q_manual.pth'

    # Instantiate the dataset and DataLoader
    test_dataset = TextDataset(data_dir=inference_data_dir, key_dir=inference_key_dir)
    test_loader = DataLoader(test_dataset)

    gt, pred, loss = inference(net, weights_dir, test_loader, criterion)
    gt_q, pred_q, loss_q = inference(net, weights_dir_q, test_loader, criterion)

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
