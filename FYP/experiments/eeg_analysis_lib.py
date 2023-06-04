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

    return evokeds 

#----------------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_1.json')
# raw = create_raw_object(json_file_path)
# evoked = extract_direction_evoked(raw, plot_display=False)