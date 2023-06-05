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


def extract_outliers(json_file_path, threshold = 70, percentage = 30):
    with open(json_file_path, "r") as json_file:
        epoch_data = json.load(json_file)

    # Iterate over each epoch in the data
    epoch_length = len(epoch_data.keys())
    outlier_epochs = np.zeros(4)
    channel_outlier_percentage = np.zeros(4)
    for epoch_key in epoch_data.keys():
        epoch = np.array(epoch_data[epoch_key])
        outlier_percentages = calculate_outlier_percentage(epoch)
        # Check if any channel has a percentage of outliers exceeding 30%
        for channel in range(0,4):
            if outlier_percentages[channel] > percentage:
                outlier_epochs[channel] += 1

    # Calculate the percentage of epochs containing more than 30% outliers
    ch = ["TP9", "AF7", "AF8", "TP10"]
    print("Percentage of epochs containing more than", percentage, "% outliers (above", threshold, "microV)")
    for channel in range(0,4):
        channel_outlier_percentage[channel] = (outlier_epochs[channel] / epoch_length) * 100
        print(ch[channel], f": {channel_outlier_percentage[channel]:.2f}%")


# Auxiliary function to calculate the percentage of outliers in the filtered epoch data
def calculate_outlier_percentage(epoch, threshold = 70):
    total_timestamps = epoch.shape[0]
    outlier_percentage = [0,0,0,0]
    for channel in [0,1,2,3]:
        values = epoch[:,channel+1]
        outliers = 0
        for i in values:
            if abs(float(i)) > threshold:
                outliers +=1   
        outlier_percentage[channel] = (outliers / total_timestamps)*100
    return outlier_percentage

extract_outliers(json_file_path)

#-------------------all files

import eeg_analysis_lib as analysis
import json, os
import numpy as np

csv_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
json_folder = os.path.join(csv_folder, "epochs")
json_files = [file for file in os.listdir(json_folder) if file.endswith(".json")]
# json_files = [ os.path.join(json_folder,  'AudioVisual_01_1.json')]
outliers_matrix = {}

for file in json_files:
    json_file = os.path.join(json_folder, file)
    print("Computing outlier percentage for experiement: ", file)
    percentages = analysis.extract_outliers(json_file, threshold = 70, percentage = 30)
    outliers_matrix[file] = percentages

json_data = json.dumps(outliers_matrix, indent=4)

results_folder = os.path.join(csv_folder, "results_data")
os.makedirs(results_folder, exist_ok=True)

json_file = os.path.join(results_folder, "Outliers_7030.json")
with open(json_file, 'w') as file:
    file.write(json_data)