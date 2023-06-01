import json
import os
import numpy as np
from scipy.fft import fft, ifft
from scipy.signal import butter, filtfilt
import analysis_lib as analysis
import matplotlib.pyplot as plt

# Load the epoch data from JSON file
json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP',
                              'data_ordered', 'epochs', 'AudioVisual_01_1.json')
with open(json_file_path, "r") as json_file:
    epoch_data = json.load(json_file)

# Constants for filtering and outlier detection
sampling_rate = 256  # Hz
low_pass_cutoff = 0.1  # Hz
high_pass_cutoff = 40  # Hz
threshold = 70  # µV
percentage = 30 # 30 %

# Function to apply a combined low-pass and high-pass filter to the epoch data
def apply_filter(epoch):
    filtered_epoch = np.copy(epoch)
    # Extract the columns to be filtered (TP9, AF7, AF8, TP10)
    data = epoch[:, 1:-2]
    print(data[1,1:-2])
    # Calculate the FFT of the data
    fft_data = fft(data, axis=0)
    print(fft_data[1,1:-2])
    # Define the filter parameters
    nyquist_freq = 0.5 * sampling_rate
    low = low_pass_cutoff / nyquist_freq
    high = high_pass_cutoff / nyquist_freq

    # Create the filter coefficients
    b, a = butter(4, [low, high], btype='band')

    # Apply the filter to the FFT data
    filtered_fft_data = filtfilt(b, a, fft_data, axis=0)
    print(filtered_fft_data[1,1:-2])
    # Transform the filtered FFT data back to the time domain
    filtered_data = ifft(filtered_fft_data, axis=0).real
    print(filtered_data[1,1:-2])
    # Update the epoch dictionary with the filtered data
    

    filtered_epoch[:,1:-2] = filtered_data.tolist()
    print(filtered_epoch[1,1:-2])
    return filtered_epoch

# Function to calculate the percentage of outliers in the filtered epoch data
def calculate_outlier_percentage(epoch):
    total_timestamps = epoch.shape[0]
    # Count the number of outliers for each channel
    outlier_percentage = [0,0,0,0]

    for channel in [0,1,2,3]:
        values = epoch[:,channel+1]
        outliers = 0
        for i in values:
            if abs(float(i)) > threshold:
                outliers +=1   
        outlier_percentage[channel] = (outliers / total_timestamps)*100
    return outlier_percentage

# Iterate over each epoch in the data
epoch_length = len(epoch_data.keys())
outlier_epochs = np.zeros(4)
channel_outlier_percentage = np.zeros(4)

for epoch_key in epoch_data.keys():
    # Get the epoch dictionary
    epoch = np.array(epoch_data[epoch_key])
    # print(epoch)
    #print(epoch.shape)
    # Apply the combined low-pass and high-pass filter to the epoch data
    filtered_epoch = apply_filter(epoch)
    # Calculate the percentage of outliers in the filtered epoch data
    outlier_percentages = calculate_outlier_percentage(epoch) #TODO change
    
    # Check if any channel has a percentage of outliers exceeding 30%
    for channel in range(0,4):
        if outlier_percentages[channel] > percentage:
            outlier_epochs[channel] += 1

# Calculate the percentage of epochs containing more than 30% outliers
ch = ["TP9", "AF7", "AF8", "TP10"]
for channel in range(0,4):
    channel_outlier_percentage[channel] = (outlier_epochs[channel] / epoch_length) * 100
    print("Percentage of epochs containing more than 30% outliers for channel", ch[channel], f": {channel_outlier_percentage[channel]:.2f}%")

    # Plot the data in the frequency and time domains
    num_channels = epoch.shape[1] - 3  # Excluding epoch number, marker, and timestamp columns

# Frequency domain plot
# plt.figure(figsize=(10, 6))
# plt.plot(np.abs(fft(epoch[:, 1])) ** 2, label='Unfiltered')
# plt.plot(np.abs(fft(filtered_epoch[:, 1])) ** 2, label='Filtered')
# plt.xlabel('Frequency')
# plt.ylabel('Power Spectral Density')
# plt.xlim([0, 100])
# plt.title(f'Channel 1')
# plt.legend()
# plt.tight_layout()
# plt.show()

# Time domain plot
plt.figure()
plt.plot(epoch[7000:7200, 0], epoch[7000:7200, 1], label='Unfiltered')
plt.plot(filtered_epoch[7000:7200, 0], filtered_epoch[7000:7200, 1], label='Filtered')
plt.xlabel('Time')
plt.legend()
plt.show()
