import json, os
import numpy as np
import mne
import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft
from scipy.signal import butter, filtfilt
import basic_analysis_lib as analysis



def create_raw_object(json_file):
    with open(json_file, 'r') as file:
        eeg_data = json.load(file)

    eeg_data = np.array(eeg_data)  # Convert the data to a NumPy array

    # Extract the channel names
    channel_names = ['TP9', 'AF7', 'AF8', 'TP10']

    # Create the info structure needed for MNE
    info = mne.create_info(ch_names=channel_names, sfreq=256, ch_types='eeg')

    # Extract the relevant columns from the data
    timestamps = eeg_data[:, 0].astype(float)
    marker_strings = eeg_data[:, 5]
    marker_timestamps = eeg_data[:, 6]

    # OLD: Transform marker strings to numeric values, ignoring "n/a"
    # marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    # markers = [marker_mapping[marker] if marker != "n/a" and marker != "end" else next for marker in marker_strings]

    marker_list = []
    marker_timestamp_list = []

    for i in range(0, len(marker_strings)):
        marker = marker_strings[i]
        if marker != "n/a" and marker != "end":
            marker_list.append(marker)
            marker_timestamp_list.append(float(eeg_data[i,0])-30)
    # Reshape the data to match the MNE format: (n_channels, n_times)
    eeg_data = np.transpose(eeg_data[:, 1:5].astype(float))  # Select the EEG channel data and transpose it

    # Create the MNE Raw object
    raw = mne.io.RawArray(eeg_data, info, first_samp=30)

    # Add markers as annotations
    raw.set_annotations(mne.Annotations(onset=marker_timestamp_list, duration=[0] * len(marker_timestamp_list), description=marker_list))

    montage = mne.channels.make_standard_montage('standard_1005')  # Choose the appropriate montage for your data
    raw.set_montage(montage)
    return raw

def return_eventcount(raw_data):
    annotations = raw_data.annotations
    print(annotations[0])
    event_counts = {}
    for annotation in annotations:
        event_type = annotation['description']
        if event_type != '0':
            if event_type not in event_counts:
                event_counts[event_type] = 0
            event_counts[event_type] += 1

    for event_type, count in event_counts.items():
        print(f"Event Type: {event_type}, Count: {count}")
    
    return event_counts

#-------------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')

# raw_data = create_raw_object(json_file_path)
# count = return_eventcount(raw_data)

#-----------------------------------------------------------

def extract_epoch(file_path, new_file_path):
    with open(file_path, "r") as file:
        csv_reader = csv.reader(file)

        # Read the header row
        header = next(csv_reader)

        # Get the initial timestamp
        first_row = next(csv_reader)
        initial_timestamp = datetime.fromtimestamp(float(first_row[0]))

        # Reset the file pointer to the beginning of the file
        file.seek(0)

        # Skip the header row
        next(csv_reader)

        # Initialize the dictionary for storing epoch data
        epoch_data = {}

        # Convert timestamp and extract epochs
        prev_time = None
        first_epoch = True
        for row in csv_reader:
            timestamp = datetime.fromtimestamp(float(row[0]))

            # Skip the first epoch
            if first_epoch:
                prev_time = timestamp
                first_epoch = False
                continue

            # Check if any column value is 'n/a' except Marker_timestamp
            if 'n/a' in row[:-2]:
                continue

            # Calculate the difference between timestamps
            time_diff = (timestamp - initial_timestamp).total_seconds()

            # Check if the epoch is 30 seconds or more
            if time_diff >= 30:
                # Calculate the epoch index
                epoch = int(time_diff // 30)

                # Update the timestamp as relative time
                relative_time = (timestamp - prev_time).total_seconds()

                # Store the data in the dictionary
                epoch_matrix = []
                for value in row[:-2]:
                    epoch_matrix.append(float(value))
                
                # Preserve the Marker column as a string
                epoch_matrix.append(str(row[-2]))
                
                # Preserve the Marker_timestamp column as a string
                epoch_matrix.append(str(row[-1]))

                epoch_data.setdefault(str(epoch), []).append(epoch_matrix)

                # Update the previous timestamp
                prev_time = timestamp

    # Write the epoch data to a JSON file
    with open(new_file_path, "w") as json_file:
        json.dump(epoch_data, json_file)

    print(f"Epochs file '{new_file_path}' created successfully.")

#--------------

# csv_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
# epochs_folder = os.path.join(csv_folder, "epochs")
# os.makedirs(epochs_folder, exist_ok=True)
# csv_files = [file for file in os.listdir(csv_folder) if file.endswith(".csv")]

# for csv_file in csv_files:
#     file_path = os.path.join(csv_folder, csv_file)
#     new_file_path = os.path.join(epochs_folder, csv_file.replace(".csv", ".json"))
#     extract_epoch(csv_file, new_file_path)
# print("Epochs files created successfully in the 'epochs' folder.")

#------------------------------------------

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

    with open(erp_file, 'w') as file:
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

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')
# erp_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'erp','AudioVisual_01_1.json')

# data = extract_marker_data(json_file_path, erp_file_path)
# plot_erps(data)

#----------------------------------

def csv_to_json(csv_file, json_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader) #leave
        first_row = next(reader)
        data = []
        initial_timestamp = float(first_row[0])

        for row in reader:
            timestamp = float(row[0])
            time_diff = (timestamp - initial_timestamp)
            if time_diff >= 30:
                data.append([time_diff] + row[1:])
        
    json_data = json.dumps(data, indent=4)

    with open(json_file, 'w') as file:
        file.write(json_data)

#---------

# csv_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
# epochs_folder = os.path.join(csv_folder, "data_json")
# os.makedirs(epochs_folder, exist_ok=True)

# csv_files = [os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'AudioVisual_01_1.csv' )]
# #csv_files = [file for file in os.listdir(csv_folder) if file.endswith(".csv")]

# for csv_file in csv_files:
#     file_path = os.path.join(csv_folder, csv_file)
#     new_file_path = os.path.join(epochs_folder, 'AudioVisual_01_1.json' )
#     csv_to_json(file_path, new_file_path)

#---------------------------------

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
    percentages = []
    print("Percentage of epochs containing more than", percentage, "% outliers (above", threshold, "microV)")
    for channel in range(0,4):
        channel_outlier_percentage[channel] = (outlier_epochs[channel] / epoch_length) * 100
        print(ch[channel], f": {channel_outlier_percentage[channel]:.2f}%")
        percentages.append((outlier_epochs[channel] / epoch_length) * 100)
        
    return percentages

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

#-------------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'epochs', 'AudioVisual_01_1.json')
# extract_outliers(json_file_path)

#---------------------------------------------

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

#--------------------------------------------

def extract_direction_evoked(raw, plot_display=False, tmin=-0.3, tmax=0.7):
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
    filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
    duration = 30.0  # Duration of each epoch (seconds)

    # Extract epochs
    epochs = mne.Epochs(filtered_raw, events, event_id=event_id, tmin=tmin, tmax=tmax, baseline=None, preload=True, event_repeated='merge')
    # fig = epochs.plot(events=events)

    # #TODO 
    # reject_criteria = dict(eeg=100e-6)  # 100 µV, 200 µV
    # epochs.drop_bad(reject=reject_criteria)
    # or directly 
    # reject_threshold = 200.0  # Threshold for epoch rejection (microvolts)
    # # reject=dict(eeg=reject_threshold)
    # epochs.plot_drop_log()

    # Get unique event types from annotations
    event_types = np.unique(events[:, -1])

    l = epochs["left"].average()
    r = epochs["right"].average()
    # fig1 = l.plot(titles="Left event")
    # fig2 = r.plot(titles="Right event")
    
    # Mean and Std across epochs, both left and right
    evokeds = dict(
        left=list(epochs["left"].iter_evoked()),
        right=list(epochs["right"].iter_evoked()),
    )

    if plot_display:
        #l.plot_topomap(times=[-0.2, 0.3, 0.5], average=0.05, title="Left event")
        l.plot_joint(title="Left event")
        #r.plot_topomap(times=[-0.2, 0.3, 0.5], average=0.05, title="Right event")
        r.plot_joint(title="Right event")


        l.plot(gfp=True, spatial_colors=True, titles="Left event")
        r.plot(gfp=True, spatial_colors=True, titles="Right event")

        mne.viz.plot_compare_evokeds(evokeds, combine="mean")

    return epochs["left"], epochs["right"]

#----------------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_1.json')
# raw = create_raw_object(json_file_path)
# epochs["left"], epochs["right"] = extract_direction_evoked(raw, plot_display=False)

#---------------------------------------

import mne, os
import numpy as np
import matplotlib.pyplot as plt

def erp_alltrials(raw_files, mode= "Audio", rejection_th =7000000, show_trials=True, arrow=False):

    #----------PROCESSING DATA

    raw_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'mne_raw')
    #raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    duration = 30.0  # Duration of each epoch (seconds)
    if arrow:
        event_ids = {"right arrow": 5, "left arrow": 6} 
    else:
        event_ids = {'left': 4, 'right': 3}  
    tmin, tmax = -0.3, 0.7
    evokeds_left = {}
    evokeds_right = {}

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=30, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)
            if arrow:
                epochs_left = mne.Epochs(filtered_raw, events, event_id=event_ids['left arrow'], tmin=tmin, tmax=tmax,
                                baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

                epochs_right = mne.Epochs(filtered_raw, events, event_id=event_ids['right arrow'], tmin=tmin, tmax=tmax,
                                    baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))
            else:
                epochs_left = mne.Epochs(filtered_raw, events, event_id=event_ids['left'], tmin=tmin, tmax=tmax,
                                    baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

                epochs_right = mne.Epochs(filtered_raw, events, event_id=event_ids['right'], tmin=tmin, tmax=tmax,
                                        baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))
            
            # Compute the average evoked response for left events
            evoked_left = epochs_left.average()
            evokeds_left[file] = evoked_left

            # Compute the average evoked response for right events
            evoked_right = epochs_right.average()
            evokeds_right[file] = evoked_right

    # Combine the evoked responses from different trials for left and right events
    combined_evoked_left = mne.combine_evoked(list(evokeds_left.values()), weights='nave')
    combined_evoked_right = mne.combine_evoked(list(evokeds_right.values()), weights='nave')

    #-----------PLOTS------------

    # # Plot the average evoked responses for left events
    # fig, ax = plt.subplots()
    # for evoked in evokeds_left.values():
    #     ax.plot(evoked.times, evoked.data[0], color='blue', alpha=0.3)
    # ax.plot(combined_evoked_left.times, combined_evoked_left.data[0], color='blue', label='Left')
    # ax.set(xlabel='Time (s)', ylabel='Amplitude (uV)', title='Average Evoked Response for Left Events')
    # ax.legend(loc='upper right')
    # plt.show()

    
    # Plot the average evoked response, individual trials, and standard deviation for each channel for left events
    fig, axs = plt.subplots(2, 2, figsize=(10, 6))
    fig.suptitle(f'ERP for {mode} Modality - Left Event')
    for ch_idx, ch_name in enumerate(evoked_left.ch_names):
        row_idx = ch_idx // 2
        col_idx = ch_idx % 2

        if show_trials:
            for raw_file, evoked in evokeds_left.items():
                if raw_file == list(evokeds_left.keys())[0]:
                    axs[row_idx, col_idx].plot(evoked.times, evoked.data[ch_idx], color='red', alpha=0.5, label=f"Trial")
                else:
                    axs[row_idx, col_idx].plot(evoked.times, evoked.data[ch_idx],color='red', alpha=0.5)
        
        axs[row_idx, col_idx].plot(evoked_left.times, np.mean([evoked.data[ch_idx] for evoked in evokeds_left.values()], axis=0), color='black', linewidth=2, label='Mean')
        axs[row_idx, col_idx].set_title(ch_name)
        axs[row_idx, col_idx].fill_between(evoked_left.times,
                                        np.mean([evoked.data[ch_idx] for evoked in evokeds_left.values()], axis=0) - np.std([evoked.data[ch_idx] for evoked in evokeds_left.values()], axis=0),
                                        np.mean([evoked.data[ch_idx] for evoked in evokeds_left.values()], axis=0) + np.std([evoked.data[ch_idx] for evoked in evokeds_left.values()], axis=0),
                                        color='orange', alpha=0.3, label='Std')
        axs[row_idx, col_idx].legend(loc='upper right')
        axs[row_idx, col_idx].axvline(x=0, color='black', linestyle='--')
        axs[row_idx, col_idx].set_xlabel("Time (s)")
        axs[row_idx, col_idx].set_ylabel("Amplitude (uV)")
    plt.axvline(x=0, color='black', linestyle='--')
    plt.tight_layout()
    plt.show()

    # Plot the average evoked response, individual trials, and standard deviation for each channel for right events
    fig, axs = plt.subplots(2, 2, figsize=(10, 6))
    fig.suptitle(f'ERP for {mode} Modality - Right Event')
    for ch_idx, ch_name in enumerate(evoked_right.ch_names):
        row_idx = ch_idx // 2
        col_idx = ch_idx % 2

        if show_trials:
            for raw_file, evoked in evokeds_right.items():
                if raw_file == list(evokeds_right.keys())[0]:
                    axs[row_idx, col_idx].plot(evoked.times, evoked.data[ch_idx], color='blue', alpha=0.5, label=f"Trial")
                else:
                    axs[row_idx, col_idx].plot(evoked.times, evoked.data[ch_idx],color='blue', alpha=0.5)

        axs[row_idx, col_idx].plot(evoked_right.times, np.mean([evoked.data[ch_idx] for evoked in evokeds_right.values()], axis=0), color='black', linewidth=2, label='Mean')
        axs[row_idx, col_idx].set_title(ch_name)
        axs[row_idx, col_idx].fill_between(evoked_right.times,
                                        np.mean([evoked.data[ch_idx] for evoked in evokeds_right.values()], axis=0) - np.std([evoked.data[ch_idx] for evoked in evokeds_right.values()], axis=0),
                                        np.mean([evoked.data[ch_idx] for evoked in evokeds_right.values()], axis=0) + np.std([evoked.data[ch_idx] for evoked in evokeds_right.values()], axis=0),
                                        color='green', alpha=0.3, label='Std')
        axs[row_idx, col_idx].legend(loc='upper right')
        axs[row_idx, col_idx].axvline(x=0, color='black', linestyle='--')
        axs[row_idx, col_idx].set_xlabel("Time (s)")
        axs[row_idx, col_idx].set_ylabel("Amplitude (uV)")
    plt.axvline(x=0, color='black', linestyle='--')
    plt.tight_layout()
    plt.show()

#---------------

# erp_alltrials(mode= "Audio", rejection_th =70)
# erp_alltrials(mode= "Vibro", rejection_th =70)
# erp_alltrials(mode= "Shape", rejection_th =70)

#-----------------------------------

from mne.time_frequency import tfr_morlet

def morlet_alltrials(raw_files, mode= "Audio", rejection_th =7000000):

    #----------PROCESSING DATA

    raw_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'mne_raw')
    #raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    duration = 30.0  # Duration of each epoch (seconds)
    event_ids = {'left': 4, 'right': 3}  # Replace with your event IDs
    tmin, tmax = -0.3, 0.7
    evokeds_left = {}
    evokeds_right = {}

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)

            epochs_left = mne.Epochs(filtered_raw, events, event_id=event_ids['left'], tmin=tmin, tmax=tmax,
                                baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            # Compute the average evoked response for left events
            evoked_left = epochs_left.average()
            evokeds_left[file] = evoked_left

            # Create epochs based on the events and desired time window for right events
            epochs_right = mne.Epochs(filtered_raw, events, event_id=event_ids['right'], tmin=tmin, tmax=tmax,
                                    baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            # Compute the average evoked response for right events
            evoked_right = epochs_right.average()
            evokeds_right[file] = evoked_right

    # Combine the evoked responses from different trials for left and right events
    combined_evoked_left = mne.combine_evoked(list(evokeds_left.values()), weights='nave')
    combined_evoked_right = mne.combine_evoked(list(evokeds_right.values()), weights='nave')

    
    freqs = np.arange(0.1, 30, 2)  # Frequency range for the wavelet transform
    n_cycles = freqs / 2.0  # Number of cycles in each frequency range

    #--------LEFT EVENT

    # Perform the Morlet wavelet transform LEFT
    power = tfr_morlet(combined_evoked_left, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    # Flatten the axs array for easier iteration
    axs = axs.flatten()

    # Define the frequency range of interest
    freq_min = 0  # Minimum frequency (Hz)
    freq_max = 30  # Maximum frequency (Hz)

    # Iterate over each channel and plot the power
    for i, channel in enumerate(power.ch_names):
        # Create a new subplot for the current channel
        ax = axs[i]

        # Plot the power for the current channel with dB scaling
        tfr_plot = power.copy().pick_channels([channel])
        tfr_data = np.mean(np.abs(tfr_plot.data), axis=0)  # Compute average power
        im = ax.imshow(10 * np.log10(tfr_data), aspect='auto', origin='lower', cmap='jet',
                    extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max])  # Create dummy image plot

        # Add colorbar
        cbar = plt.colorbar(im, orientation='vertical', pad=0.1, ax=ax)
        cbar.set_label('Power (dB)')

        # Set labels and title
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"{channel}")

    # Remove any extra subplots if there are fewer channels than subplots
    if len(power.ch_names) < 4:
        for i in range(len(power.ch_names), 4):
            fig.delaxes(axs[i])

    # Set common labels and title for the figure
    # fig.text(0.5, 0.04, 'Time (s)', ha='center')
    # fig.text(0.04, 0.5, 'Frequency (Hz)', va='center', rotation='vertical')
    fig.suptitle(f"Time-frequency response to 'left' command - {mode} Stimulation")

    # Adjust spacing between subplots
    fig.tight_layout()

    # Show the figure
    plt.show()


    #-------RIGHT EVENT
    # Perform the Morlet wavelet transform RIGHT
    power = tfr_morlet(combined_evoked_right, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)

 
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    # Flatten the axs array for easier iteration
    axs = axs.flatten()

    # Define the frequency range of interest
    freq_min = 0  # Minimum frequency (Hz)
    freq_max = 30  # Maximum frequency (Hz)

    # Iterate over each channel and plot the power
    for i, channel in enumerate(power.ch_names):
        # Create a new subplot for the current channel
        ax = axs[i]

        # Plot the power for the current channel with dB scaling
        tfr_plot = power.copy().pick_channels([channel])
        tfr_data = np.mean(np.abs(tfr_plot.data), axis=0)  # Compute average power
        im = ax.imshow(10 * np.log10(tfr_data), aspect='auto', origin='lower', cmap='jet',
                    extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max])  # Create dummy image plot

        # Add colorbar
        cbar = plt.colorbar(im, orientation='vertical', pad=0.1, ax=ax)
        cbar.set_label('Power (dB)')

        # Set labels and title
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"{channel}")

    # Remove any extra subplots if there are fewer channels than subplots
    if len(power.ch_names) < 4:
        for i in range(len(power.ch_names), 4):
            fig.delaxes(axs[i])

    # Set common labels and title for the figure
    # fig.text(0.5, 0.04, 'Time (s)', ha='center')
    # fig.text(0.04, 0.5, 'Frequency (Hz)', va='center', rotation='vertical')
    fig.suptitle(f"Time-frequency response to 'Right' command - {mode} Stimulation")

    # Adjust spacing between subplots
    fig.tight_layout()

    # Show the figure
    plt.show()

#------------

# keys_below_30 = ['AudioVisual_04_1.fif', 'AudioVisual_04_2.fif', 'AudioVisual_06_1.fif', 'AudioVisual_06_2.fif',  'ShapeVisual_03_1.fif', 'ShapeVisual_03_2.fif', 'ShapeVisual_04_1.fif', 'ShapeVisual_04_2.fif', 'ShapeVisual_06_2.fif', 'VibroVisual_06_1.fif', 'VibroVisual_02_2.fif', 'VibroVisual_03_1.fif', 'VibroVisual_03_2.fif']

# morlet_alltrials(keys_below_30, mode= "Audio", rejection_th =70)
# morlet_alltrials(keys_below_30, mode= "Vibro", rejection_th =70)
# morlet_alltrials(keys_below_30, mode= "Shape", rejection_th =70)

#--------------------------------------


def compute_amplitude_rms(epochs, event_id, sfreq, pre_init=-0.2, pre_end=0, post_init=0.2, post_end=0.4):
    rms_values = []
    std_error_values = []
    
    # Convert pre_duration and post_duration to samples
    pre_samples_init = int((pre_init+0.5) * sfreq)
    pre_samples_end = int((0.5+pre_end) * sfreq)
    post_samples_init = int((0.5+post_init) * sfreq)
    post_samples_end = int((0.5+post_end) * sfreq)
    
    # Load the epochs data into memory
    epochs.load_data()
    
    # Iterate over each channel
    for ch_idx, ch_name in enumerate(epochs.info['ch_names']):
        channel_rms = []
        channel_std_error = []
        
        # Iterate over each event type
        for event_name, event_code in event_id.items():
            event_rms = []
            
            # Get the epochs for the current event type
            event_epochs = epochs[event_name]
            
            # Iterate over each epoch
            for epoch in event_epochs:
                # Compute the average amplitude in the pre and post durations
                pre_amplitude = np.mean(np.abs(epoch[ch_idx, pre_samples_init:pre_samples_end]))
                post_amplitude = np.mean(np.abs(epoch[ch_idx, post_samples_init:post_samples_end]))
                
                # Compute the RMS between the pre and post amplitudes
                rms = np.sqrt(np.mean((pre_amplitude - post_amplitude) ** 2))
                event_rms.append(rms)
            
            channel_rms.append(np.mean(event_rms))
            channel_std_error.append(np.std(event_rms, ddof=1) / np.sqrt(len(event_rms)))
        
        rms_values.append(channel_rms)
        std_error_values.append(channel_std_error)
    
    # Convert rms_values and std_error_values to numpy arrays
    rms_values = np.array(rms_values)
    std_error_values = np.array(std_error_values)
    
    return rms_values, std_error_values

#-----------

# raw_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'mne_raw', 'AudioVisual_04_1.fif')
# raw = mne.io.read_raw_fif(raw_path, preload=True)
# marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
# filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
# events, event_id= mne.events_from_annotations(filtered_raw, event_id=marker_mapping)
# event_id = {'left': 4, 'right': 3}
# #event_timestamps = filtered_raw.times[events[:, 0]]
# epochs = mne.Epochs(filtered_raw, events, event_id=event_id, tmin=-0.5, tmax=0.5, baseline=(None, 0))
# sfreq = raw.info['sfreq']


# mean_rms, std_error_rms = compute_amplitude_rms(epochs, event_id, sfreq)

# for event_idx, event_name in enumerate(event_id.keys()):
#     print(f"Event: {event_name}")
#     for ch_idx, ch_name in enumerate(epochs.info['ch_names']):
#         print(f"Channel: {ch_name}")
#         print(f"Mean RMS: {mean_rms[ch_idx, event_idx]:.2f}")
#         print(f"Std Error of RMS: {std_error_rms[ch_idx, event_idx]:.2f}")
#     print()

#-------------------------------------------

def erp_rsm_alltrials(raw_files, mode= "Audio", rejection_th =7000000):

    #----------PROCESSING DATA
    raw_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'mne_raw')
    #raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    event_ids = {'left': 4, 'right': 3}  
    tmin, tmax = -0.5, 0.5
    mean_rms_trial = {'left': [], 'right': []} 
    std_error_rms_trial = {'left': [], 'right': []}

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, _ = mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=30, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)
            sfreq = raw.info['sfreq']

            epochs = mne.Epochs(filtered_raw, events, event_id=event_ids, tmin=tmin, tmax=tmax,
                                baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            mean_rms, std_error_rms = compute_amplitude_rms(epochs, event_ids, sfreq,pre_init=-0.4, pre_end=-0.2, post_init=0.3, post_end=0.4)
            mean_rms_trial['left'].append(mean_rms[:,0])
            mean_rms_trial['right'].append(mean_rms[:,1])  
            std_error_rms_trial['left'].append(std_error_rms[:,0])
            std_error_rms_trial['right'].append(std_error_rms[:,1])    
            
    mean_rms_trial['left'] = np.array(mean_rms_trial['left'])
    mean_rms_trial['right'] = np.array(mean_rms_trial['right'])
    
    return mean_rms_trial, std_error_rms_trial

#----------

# mne.set_log_level("ERROR")
# keys_below_30 = ['AudioVisual_04_1.fif', 'AudioVisual_04_2.fif', 'AudioVisual_06_1.fif', 'AudioVisual_06_2.fif',  'ShapeVisual_03_1.fif', 'ShapeVisual_03_2.fif', 'ShapeVisual_04_1.fif', 'ShapeVisual_04_2.fif', 'ShapeVisual_06_2.fif', 'VibroVisual_06_1.fif', 'VibroVisual_02_2.fif', 'VibroVisual_03_1.fif', 'VibroVisual_03_2.fif']
# raw_files = keys_below_30

# mean_rsm_audio, std_error_rms_audio = erp_rsm_alltrials(raw_files, mode= "Audio", rejection_th =70)
# mean_rms_vibro,std_error_rms_vibro = erp_rsm_alltrials(raw_files, mode= "Vibro", rejection_th =70)
# mean_rsm_shape, std_error_rms_shape = erp_rsm_alltrials(raw_files, mode= "Shape", rejection_th =70)

#-------------------------------
