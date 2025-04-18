import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import torch.nn as nn
import os
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report

class AudioClassifierCRNN(nn.Module):
    def __init__(self, num_genres, input_channels):
        super(AudioClassifierCRNN, self).__init__()
        
        # CNN Layers -used for feature extraction from spectrogram
        self.cnn_layers = nn.Sequential(
            nn.Conv2d(input_channels, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout(0.2), 
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout(0.3), 
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.MaxPool2d(2, 2),
            nn.Dropout(0.4), 
        )
        
        self.rnn_input_size = 256 * 16  
        
        # RNN layers - used for temporal analysis of features
        self.rnn = nn.LSTM(
            input_size=self.rnn_input_size,
            hidden_size=128,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.3
        )
        
        self.attention = nn.Sequential(
            nn.Linear(256, 32), 
            nn.Tanh(),
            nn.Linear(32, 1),
            nn.Softmax(dim=1)
        )
        
        # Classification layers
        self.classifier = nn.Sequential(
            nn.Linear(256, 64),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(64, num_genres)
        )
    
    def forward(self, x):
        batch_size = x.size(0)
        x = self.cnn_layers(x)
        x = x.permute(0, 3, 1, 2)
        x = x.reshape(batch_size, -1, self.rnn_input_size)
        
        rnn_out, _ = self.rnn(x)
        
        attention_weights = self.attention(rnn_out)
        x = torch.sum(attention_weights * rnn_out, dim=1)
        
        x = self.classifier(x)
        return x, attention_weights