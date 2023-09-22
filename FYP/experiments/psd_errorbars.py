import numpy as np
from matplotlib import pyplot as plt
import mne, os
import json
mne.set_log_level("ERROR")

n_trials = 24


# Load the PSD data from the previously saved file
freqs = np.load('C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\experiments\\freqs.npy', allow_pickle=True)

psd_data = np.load('psd_data.npy', allow_pickle=True).item()

bands = {
    'δ': (0.1, 4),
    'θ': (4, 8),
    'α': (8, 13),
    'β': (13, 30),
    'γ': (30, 40)
}

# Initialize arrays to store the absolute and relative power for each channel and modality
abs_power = {modality: np.zeros((len(bands), len(psd_data[modality][0]), n_trials)) for modality in psd_data.keys()}
rel_power = {modality: np.zeros((len(bands), len(psd_data[modality][0]), n_trials)) for modality in psd_data.keys()}
# Convert psd_data from list to numpy array
psd_data = {modality: np.array(data) for modality, data in psd_data.items()}
# print(abs_power['Audio'][1,1].shape)
# print(psd_array[:, 1].shape)

# Compute the absolute and relative power for each frequency band and each channel and modality
for modality, psd_array in psd_data.items():
    for ch in range(len(psd_array[0])):
        for i, (fmin, fmax) in enumerate(bands.values()):
            freq_indices = np.where((freqs >= fmin) & (freqs <= fmax))[0]
            #print(freq_indices)
            band_psd = (psd_array[0:n_trials, ch, freq_indices])
            band = np.mean(band_psd, 1)
            #print(band.shape)

            abs_power[modality][i, ch] = 10*np.log10(band)
            rel_power[modality][i, ch] = 100*(band) / np.sum(psd_array[:, ch])

import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt


# -------Plot absolute OR relative:
absolute = True

# Plotting the mean and standard deviation of each channel as a bar chart
fig, axs = plt.subplots(1, 4, figsize=(20, 6), sharex=True)

#freq_labels = list(bands.keys())
# freq_labels = [f'{key}\n({bands[key][0]}-{bands[key][1]})' for key in bands.keys()]
freq_labels = [f'{key}' for key in bands.keys()]
x = np.arange(len(freq_labels))
bar_width = 0.2
opacity = 0.8
opacity_std = 0.4
colors = [ ['tab:red','tab:red','tab:red','tab:red','tab:red'], ['tab:green','tab:green','tab:green','tab:green','tab:green'], ['tab:blue','tab:blue','tab:blue','tab:blue','tab:blue']]
channel_names = ['TP9', 'AF7', 'AF8', 'TP10']
meanpointprops = dict(marker='D', markeredgecolor='black',
                      markerfacecolor='firebrick')
legend_labels = []
# After creating the box plots, determine which conditions are significant
significant_conditions = [[4,5],[4, 3],[4,3],[4,3],[4,3]]  # Replace with the indices of your significant conditions

for ch in range(len(psd_data['Audio'][0])):
    for i, modality in enumerate(psd_data.keys()):
        if absolute:
            power =(abs_power[modality][:, ch]).T 
            #axs[ch].set_ylim(-8,30)  
        else:
            power =((rel_power[modality][:, ch])).T
            #axs[ch].set_ylim(-3,12)
        boxprops = dict(linestyle='-', linewidth=1, color='black')
        boxplot= axs[ch].boxplot(power,  
                     vert=True, widths=bar_width,
                     patch_artist=True,boxprops=boxprops, meanline=False,
                    showmeans=False, positions=(x + i * bar_width),labels=bands.keys(), showfliers=False)
        for median_line in boxplot['medians']:
            median_line.set(color='black', linewidth=4)
        for patch, color in zip(boxplot['boxes'], colors[i]):
            patch.set_facecolor(color)
        if ch == 0:  # Only add one set of labels to the legend
            legend_labels.append(boxplot['boxes'][0])
        
        # TODO Check if the current condition is significant
        if i in significant_conditions[ch]:
            # Add a rectangle to highlight the significant condition
            significant_rect = plt.Rectangle((x[i] - bar_width / 1.8, np.min(power) - 2),
                                             bar_width*3.2, np.max(power) - np.min(power) + 4,
                                             linewidth=1, edgecolor='orange', facecolor='none')
            axs[ch].add_patch(significant_rect)

    axs[ch].yaxis.grid(True)
    #axs[ch].legend(loc='lower right')
    axs[0].set_ylabel('Power (dB)', fontsize=18)
    axs[ch].set_xlabel('Frequency Bands', fontsize=18)

    axs[ch].set_xticks(x + bar_width * (len(psd_data.keys()) - 1) / 2)
    axs[ch].set_xticklabels(freq_labels)
    axs[ch].tick_params(axis='both', which='both', labelsize=20)  # Increase tick label size for both x and y axes

    axs[ch].set_title(f'{channel_names[ch]}', fontsize=20)
    axs[ch].axhline(y=0, color='black', linestyle='-', linewidth=0.5)

axs[1].legend(legend_labels, [modality for modality in psd_data.keys()], fontsize=18)



if absolute:
    plt.suptitle("Power Distribution per Frequency Band", fontweight='bold', fontsize=24)
else:
    plt.suptitle("Mean Relative Power per Frequency Band")
plt.show()
plt.savefig('C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\results_data\\svg\\PSD_abs_try.eps', format='eps')