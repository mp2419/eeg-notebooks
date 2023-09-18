import json, os
import numpy as np
import mne

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

json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_12_1.json')

raw_data = create_raw_object(json_file_path)
count = return_eventcount(raw_data)