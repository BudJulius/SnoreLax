import os
import torch
import librosa
import numpy as np
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import torch.nn as nn
import os
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from datetime import datetime
from CRNN_Arch import AudioClassifierCRNN
import DataTransfer
import math

    # Loads the trained model
def load_model(model_path):
    checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
    model = AudioClassifierCRNN(num_genres=2, input_channels=1)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    return model

    # Processes the audio files by creating a mel scalogram and normalizing it
def process_audio_file(file_path, sr=22050, duration=5):
    try:
        audio, sr = librosa.load(file_path, sr=sr, duration=duration)

            # Creates a mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio,
            sr=sr,
            n_mels=128,
            n_fft=2048,
            hop_length=512
        )
        mel_spec = librosa.power_to_db(mel_spec)
        
            # Since recordings can be of different lengths, it needs to be padded or truncated to match the model's input size
        target_length = 1292
        if mel_spec.shape[1] > target_length:
            mel_spec = mel_spec[:, :target_length]
        elif mel_spec.shape[1] < target_length:
            pad_width = target_length - mel_spec.shape[1]
            mel_spec = np.pad(mel_spec, ((0, 0), (0, pad_width)), mode='constant')
            
        mel_spec = (mel_spec - mel_spec.mean()) / (mel_spec.std() + 1e-8)
        mel_spec = torch.FloatTensor(mel_spec).unsqueeze(0).unsqueeze(0) 
        
        return mel_spec
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

    # Analyzes and processes the sleep recordings and classifies them as either snoring or talking
def analyze_sleep_recordings(filename):
    model_path = "model.pth" 
    model = load_model(model_path)
    results = []
    
    if filename.endswith(('.wav', '.WAV')):
        file_path = os.path.join(filename)
        print(f"Processing {filename}...")
        
        mel_spec = process_audio_file(file_path)
        if mel_spec is None:
            print(f"Skipping {filename} due to processing error.")
            return
            
            # This is where the model makes the prediction and classifies the recording
        with torch.no_grad():
            outputs, _ = model(mel_spec)
            _, predicted = torch.max(outputs, 1)
            
            class_name = "Snoring" if predicted.item() == 0 else "Talking"
            
            results.append({
                "filename": filename,
                "prediction": class_name,
                "timestamp": os.path.getmtime(file_path)
            })

            # Duration is substracted due to silence periods at the end of the recording
        duration = librosa.get_duration(path=file_path) - 5
        duration = math.ceil(duration)
        print(f"Recording has been classified as {class_name} with duration {duration} seconds.")
        DataTransfer.DataTransfer.save_to_database(filename, class_name, duration)
            
    return results