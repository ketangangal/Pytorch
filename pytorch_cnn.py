# -*- coding: utf-8 -*-
"""Pytorch_CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1L1SWQUdLwwGL0FTgsJhHr97BI_0cBJce

# Basic Things to remember Before CNN Training
"""

# Convolution Neural Networks
# Rotate kernals on i/p image to generate feature maps
# Kernal --> Feature extractor , image modifier, filters etc
# In cnn back propagation also happens in kernals so they are not static they are dynamic
# But CNN are more efficient than ANN as their we have less paramertes to train, no effect of translation invarience etc 
# In CNN we need to keep in mind about 
  # Image Size 
  # Image Augmentation 
  # Kernal(Filters) 
  # Pooling 
  # Padding 
  # Batch Normalization
  # Dropout 
  # stride
  # optimizer
  # No of layers
  # Flatten 
  # Different Types of Networks Architectures (lenet, alexnet, googlenet, Vgg16 , resnet )


# Mode 
# Valid -- > o/p size n-k+1
# same ---> n
# full ---> n+k-1


# Hyperparameters 
 # Inputsize
 # kernal size 
 # pooling 
 # stride 
 # hidden layers 
 # dense layer 
 # learning rate 
 # ++

# Guidelines 
  # Start with small filters or stick with 3*3
  # Repeat patterns (conv + pool repeat)
  # Increase feature map 
  # read papers
  
# Type of cnn 
  # Pure
  # mixed

# Necessary Imports 
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 


import torch 
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import torch.nn.functional as f
from sklearn.metrics import confusion_matrix, classification_report

plt.style.use('fivethirtyeight')

"""## Download and Load Data"""

train_data = datasets.FashionMNIST(
    root='Data',
    train=True,
    download = True,
    transform = transforms.ToTensor(),
    target_transform = None
)

test_data = datasets.FashionMNIST(
    root='Data',
    train=False,
    download = True,
    transform = transforms.ToTensor(),
    target_transform = None
)

label_map = {0: 'T-shirt/top',
1: 'Trouser',
2: 'Pullover',
3:' Dress',
4: 'Coat',
5: 'Sandal',
6: 'Shirt',
7: 'Sneaker',
8: 'Bag',
9: 'Ankle boot',
}

plt.imshow(train_data.data[1])
plt.xlabel(label_map[train_data.targets[1].item()])

# Lets create data loader 
# Loader will transform and rescale data automaticaly + reshape 
train_data_loader = DataLoader(dataset=train_data,
                               batch_size=64,
                               shuffle=True)

test_data_loader = DataLoader(dataset=test_data,
                               batch_size=64,
                               shuffle=False)

for x in test_data_loader:
  print(x[0].shape)
  print(x[1].shape)
  break

"""## Cnn model Creation with Image size calculation 

"""

device = 'cuda' if torch.cuda.is_available() else 'cpu'
class Neural_Network(nn.Module):
  def __init__(self,input,output):
    super(Neural_Network,self).__init__()
    self.layer1 = nn.Conv2d(in_channels=input,out_channels=64,kernel_size=(3,3),stride=1,padding=(1,1))   # Input(28,28) -- Output(28,28)
    self.pool1= nn.MaxPool2d(kernel_size=2)                                                               # Input(28,28) -- Output(14,14)
    self.layer2 = nn.Conv2d(in_channels=64,out_channels=32,kernel_size=(3,3),stride=1,padding=(1,1))      # Input(14,14) -- Output(14,14)
    self.pool2 = nn.MaxPool2d(kernel_size=2)                                                              # Input  (14,14) -- Output(7,7)
    self.layer3 = nn.Conv2d(in_channels=32,out_channels=32,kernel_size=(3,3),stride=1,padding=(0,0))      # Input  (7,7)   -- Output(5,5)
    self.layer4 = nn.Conv2d(in_channels=32,out_channels=32,kernel_size=(3,3),stride=1,padding=(0,0))      # Input  (5,5)   -- Output(3,3)

    self.flatten = nn.Flatten()
    self.dense1 = nn.Linear(3*3*32,64)
    self.dropout = nn.Dropout()
    self.dense2 = nn.Linear(64,output)

  def forward(self,x):
    x = f.relu(self.layer1(x))
    x = self.pool1(x)
    x = f.relu(self.layer2(x))
    x = self.pool2(x)
    x = f.relu(self.layer3(x))
    x = f.relu(self.layer4(x))
    x = self.flatten(x)
    x = f.relu(self.dense1(x))
    x = self.dropout(x)
    x = f.relu(self.dense2(x))
    return x

device

model = Neural_Network(1,10)
model.to(device)

"""# Total Trainable parameters """

from prettytable import PrettyTable

def count_parameters(model):
    table = PrettyTable(["Modules", "Parameters"])
    total_params = 0
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad: continue
        param = parameter.numel()
        table.add_row([name, param])
        total_params+=param
    print(table)
    print(f"Total Trainable Params: {total_params}")
    return total_params
    
count_parameters(model)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters())

def train_(n_epoch=5,train_data_loader=None,test_data_loader=None,criterion=None,optimizer=None,model=None):
    train_loss = []
    test_loss = []
    for epoch in range(n_epoch):
      model.train()
      for batch,data in enumerate(train_data_loader):
        x = data[0].to(device)
        y = data[1].to(device)
        
        optimizer.zero_grad()

        y_pred = model(x)
        loss = criterion(y_pred,y)
        loss.backward()
        optimizer.step()
      
      model.eval()

      for batch,data in enumerate(test_data_loader):
        with torch.no_grad():
          x  = data[0].to(device)
          y = data[1].to(device)
      
          y_pred = model(x)
          loss_ = criterion(y_pred,y)

      train_loss.append(loss.item()) 
      test_loss.append(loss_.item()) 
      print(f' Epoch {epoch+1}/{n_epoch} Train Loss {loss:.4f}  Test Loss {loss_:.4f}') 
    return train_loss, test_loss


train_loss, test_loss = train_(10,train_data_loader,test_data_loader,criterion,optimizer,model)

pd.DataFrame(data={'train_loss':train_loss,'test_loss':test_loss}).plot()

# Lets Evaluate Model 
# Accuracy Calculation 
model.eval()
for batch, data in enumerate(train_data_loader):
  with torch.no_grad():
     x = data[0].to(device)
     y = data[1].to(device)
     y_pred = model.forward(x)
     print((torch.argmax(y_pred,axis=1) == y))
     break
