import json, os
import numpy as np
from scipy.fft import fft, ifft
from scipy.signal import butter, filtfilt

# Load the epoch data from JSON file
json_file_path = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'epochs', 'AudioVisual_01_1.json')
with open(json_file_path, "r") as json_file:
    epoch_data = json.load(json_file)

# Constants for filtering and outlier detection
sampling_rate = 256 # Hz
low_pass_cutoff = 0.1  # Hz
high_pass_cutoff = 40  # Hz
threshold = 70  # µV

# Function to apply a combined low-pass and high-pass filter to the epoch data
def apply_filter(epoch):
    electrodes = ['TP9', 'AF7', 'AF8', 'TP10']
    # Extract the columns to be filtered (TP9, AF7, AF8, TP10)
    data = np.array([epoch[(i, j)] for i in range(1,epoch_length) for j in range(1, 5)])

    # Calculate the FFT of the data
    fft_data = fft(data, axis=0)
    
    # Define the filter parameters
    nyquist_freq = 0.5 * sampling_rate
    low = low_pass_cutoff / nyquist_freq
    high = high_pass_cutoff / nyquist_freq
    
    # Create the filter coefficients
    b, a = butter(4, [low, high], btype='band')
    
    # Apply the filter to the FFT data
    filtered_fft_data = filtfilt(b, a, fft_data, axis=0)
    
    # Transform the filtered FFT data back to the time domain
    filtered_data = ifft(filtered_fft_data, axis=0).real

    # Update the epoch dictionary with the filtered data
    for i in range(epoch_length):
        for j, channel in enumerate(["TP9", "AF7", "AF8", "TP10"]):
            epoch[(i, j + 1, channel)] = filtered_data[i, j].tolist()

    return epoch

# ------ OUTLIERS -----

# Function to calculate the percentage of outliers in the filtered epoch data
def calculate_outlier_percentage(epoch):
    total_timestamps = epoch_length * 4  # 4 channels
    
    outlier_counts = {channel: 0 for channel in ["TP9", "AF7", "AF8", "TP10"]}
    
    # Count the number of outliers for each channel
    for i in range(epoch_length):
        for j, channel in enumerate(["TP9", "AF7", "AF8", "TP10"]):
            values = epoch.get((i, j + 1, channel), [])
            outliers = sum(1 for value in values if abs(value) > threshold)
            outlier_counts[channel] += outliers

    # Calculate the percentage of outliers for each channel
    outlier_percentages = {channel: (count / total_timestamps) * 100 for channel, count in outlier_counts.items()}

    return outlier_percentages

# Iterate over each epoch in the data
epoch_length = len(epoch_data.values())
outlier_epochs = 0
print(epoch_data.keys())
for epoch_key in epoch_data.keys():
    # Get the epoch dictionary
    epoch = epoch_data[epoch_key, 1:5, :]
    
    #print(epoch.shape)
    # print(epoch)
    # Apply the combined low-pass and high-pass filter to the epoch data
    filtered_epoch = apply_filter(epoch)
    
    # Calculate the percentage of outliers in the filtered epoch data
    outlier_percentages = calculate_outlier_percentage(filtered_epoch)
    
    # Check if any channel has a percentage of outliers exceeding 30%
    if any(percentage > 30 for percentage in outlier_percentages.values()):
        outlier_epochs += 1

# Calculate the percentage of epochs containing more than 30% outliers
outlier_percentage = (outlier_epochs / epoch_length) * 100

print(f"Percentage of epochs containing more than 30% outliers: {outlier_percentage:.2f}%")
