import mne, os
import numpy as np
import matplotlib.pyplot as plt
from eeg_analysis_lib import create_raw_object



def psd_abs_n_rel(raw, chart=False):
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
    fmin = 0.1
    fmax = 40
    freq_mask = (raw.copy().filter(fmin, fmax, fir_design='firwin')).get_data()
    psd_tot = np.abs(np.fft.fft(freq_mask, n_fft, axis=-1)) ** 2
    psd_tot_pow = np.sum(psd_tot, axis=1, keepdims=True)


    # Compute the absolute and relative PSD for each frequency band
    psd_data_abs = []#np.zeros((len(bands),num_channels))
    psd_data_rel = []#np.zeros((len(bands), num_channels))

    for key in bands.keys():
        (fmin, fmax) = bands[key]
        freq_mask = (raw.copy().filter(fmin, fmax, fir_design='firwin')).get_data()
        psd_band = np.abs(np.fft.fft(freq_mask, n_fft, axis=-1)) ** 2
        # print(psd_band)
        psd_band_mean = np.mean(psd_band, axis=-1)
        # print(psd_band_mean)
        # print(psd_tot)
        print(psd_tot_pow)
        psd_band_mean_rel = []
        for i in range(len(psd_band_mean)):
            psd_band_mean_rel.append(psd_band_mean[i]/psd_tot_pow[i])
        # print(psd_band_mean_rel)
        #psd_mean = np.mean(psd, axis=-1)
        #print(psd_mean.shape)
        #psd_total = np.sum(psd_mean, axis=0, keepdims=True)
        #print(psd_total.shape)
        #psd_relative = psd_mean / psd_total
        psd_data_abs.append(psd_band_mean)
        psd_data_rel.append(psd_band_mean_rel)
        # print("-------------BAND------------")

    psd_data_rel = np.array(psd_data_rel)
    psd_data_abs = np.array(psd_data_abs)
    print(psd_data_abs)
    print(psd_data_rel)


    #----------BARCHART
            
    if chart:
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
            # Bar chart of absolute and relative PSD

        fig, ax = plt.subplots()
        x = np.arange(len(psd_data_abs.flatten()))
        ax.bar(x, psd_data_abs.flatten(), align='center', color=color)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation='vertical')
        ax.set_xlabel('Features')
        ax.set_ylabel('Average Relative PSD')
        ax.set_title('Relative Power per channel per band')
        plt.tight_layout()
        plt.show()

        fig, ax = plt.subplots()
        x = np.arange(len(psd_data_rel.flatten()))
        ax.bar(x, psd_data_rel.flatten(), align='center', color=color)
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation='vertical')
        ax.set_xlabel('Features')
        ax.set_ylabel('Average Absolute PSD')
        ax.set_title('Absolute Power per channel per band')
        plt.tight_layout()
        plt.show()
    
    return psd_data_abs, psd_data_rel

#---------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_2.json')
# raw = create_raw_object(json_file_path)
# psd_asb, psd_rel = psd_abs_n_rel(raw)