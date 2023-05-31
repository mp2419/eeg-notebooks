import json
import os
import matplotlib.pyplot as plt
import numpy as np

def extract_marker_data(json_file, erp_file):
    with open(json_file, 'r') as file:
        eeg_data = json.load(file)

    eeg_data = np.array(eeg_data)
    print(eeg_data.shape)

    extracted_data = {}
    marker_list = ["blue", "red", "right", "left", "right arrow", "left arrow"]
    window = int(0.6*256) #window samples of 600ms @ 256Hz 
    for marker in marker_list:
        event_timestamp_list = []
        erp_windows = []
        # Find events of marker type
        for sample in range(0,len(eeg_data)):
            if eeg_data[sample,5] == marker: 
                if sample+window > len(eeg_data):
                    break
                else:
                    event_timestamp_list.append(eeg_data[sample,0])
                    erp_windows.append(eeg_data[sample:sample+window,1:5])

        extracted_data[marker] = erp_windows
    # save in new json file
    data_converted = {}
    for marker, erp_data in extracted_data.items():
        erp_data_converted = [erp.tolist() for erp in erp_data]
        data_converted[marker] = erp_data_converted

    with open(erp_file_path, 'w') as file:
        json.dump(data_converted, file)

    return extracted_data

def plot_erps(extracted_data):
    # Plot ERPs for each marker type
    for marker_type, erp_data in extracted_data.items():
        erp_data = np.array(erp_data, dtype=np.float64)  # Convert the data to a numeric data type
        erp_data_channel = erp_data[:, :, 0]  # Select the specified channel
        num_windows, num_samples = erp_data_channel.shape

        # Plot all windows and their mean
        plt.figure()
        for window in range(num_windows):
            plt.plot(np.arange(num_samples), erp_data_channel[window, :], alpha=0.4, label=f'Window {window+1}')
        mean_erp = np.mean(erp_data_channel, axis=0)
        plt.plot(np.arange(num_samples), mean_erp, 'k', linewidth=2, label='Mean ERP')
        plt.xlabel('Sample')
        plt.ylabel('Amplitude')
        plt.title(f'ERP - Marker Type: {marker_type}')
        plt.legend()
        plt.grid(True)
        plt.show()

#--------

json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')
erp_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'erp','AudioVisual_01_1.json')

data = extract_marker_data(json_file_path, erp_file_path)
plot_erps(data)
