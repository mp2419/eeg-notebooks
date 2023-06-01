import mne, os
import numpy as np
import matplotlib.pyplot as plt
import json_to_mne


json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')

raw = json_to_mne.create_raw_object(json_file_path)
# Define the frequency bands of interest
bands = {'delta': (0.1, 4),
         'theta': (4, 8),
         'alpha': (8, 13),
         'beta': (13, 30),
         'gamma': (30, 40)}

# Define the number of features extracted per epoch
num_channels = len(raw.info['ch_names'])
num_features = len(bands) * num_channels

# Set the FFT parameters
n_fft = 1024

# Compute the absolute and relative PSD for each frequency band
psd_data = np.zeros((len(raw), num_features))
for i, (band_name, (fmin, fmax)) in enumerate(bands.items()):
    freq_mask = (raw.copy().filter(fmin, fmax, fir_design='firwin')).get_data()
    psd = np.abs(np.fft.fft(freq_mask, n_fft, axis=-1)) ** 2
    psd_mean = np.mean(psd, axis=-1)
    psd_total = np.sum(psd_mean, axis=0, keepdims=True)
    psd_relative = psd_mean / psd_total
    psd_data[:, i*num_channels:(i+1)*num_channels] = psd_relative

# psd_data now contains the computed relative PSD for each epoch and frequency band

# # Print the shape of psd_data
# print(psd_data.shape)

#TODO change so works with variation between epochs
# Plot line plot of all features across epochs
fig, ax = plt.subplots()
for i, (band_name, (fmin, fmax)) in enumerate(bands.items()):
    for j in range(num_channels):
        feature_idx = i * num_channels + j
        label = f'Relative PSD ({band_name}) / Ptot ({raw.info["ch_names"][j]})'
        ax.plot(psd_data[:, feature_idx], label=label)
ax.set_xlabel('Epochs')
ax.set_ylabel('Relative PSD')
ax.set_title('Line Plot of All Features')
ax.legend()
plt.show(block=False)

# Compute the average across all epochs for each feature
average_psd = np.mean(psd_data, axis=0)

# Reshape average_psd for plotting
average_psd = average_psd.reshape(len(bands), num_channels)

# Create x-axis labels for the bar chart
x_labels = []
color = []
color_bands_dic = {'delta': "orange",
         'theta': "red",
         'alpha': "purple",
         'beta': "blue",
         'gamma': "green"}

for band_name in bands.keys():
    for channel_name in raw.info['ch_names']:
        x_labels.append(f'{band_name} - {channel_name}')
        color.append(color_bands_dic[band_name])
        

# Plot bar chart of average relative PSD
fig, ax = plt.subplots()
x = np.arange(len(average_psd.flatten()))
ax.bar(x, average_psd.flatten(), align='center', color=color)
ax.set_xticks(x)
ax.set_xticklabels(x_labels, rotation='vertical')
ax.set_xlabel('Features')
ax.set_ylabel('Average Relative PSD')
ax.set_title('Bar Chart of Average Relative PSD')
plt.tight_layout()
plt.show()