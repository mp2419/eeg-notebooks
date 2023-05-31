import mne, os
import json_to_mne
import numpy as np


json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')

raw = json_to_mne.create_raw_object(json_file_path)

events = mne.events_from_annotations(raw)[0]


filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')

duration = 30.0  # Duration of each epoch (seconds)
reject_threshold = 200.0  # Threshold for epoch rejection (microvolts)

# Extract epochs
epochs = mne.Epochs(filtered_raw, events, tmin=0, tmax=duration, baseline=None, reject=dict(eeg=reject_threshold), preload=True, event_repeated='merge')
epochs.plot_drop_log()

# Get unique event types from annotations
#event_types = np.unique(raw.annotations.description)
event_types = np.unique(events[:, -1])

# Create evoked objects for each event type and channel
evokeds = {}
for event_type in event_types:
    evokeds[event_type] = {}
    for ch_name in raw.info['ch_names']:
        evokeds[event_type][ch_name] = epochs[event_type].average(picks=ch_name)

# Plot evoked potentials (ERPs) for each event type and channel
for event_type in event_types:
    for ch_name in raw.info['ch_names']:
        evokeds[event_type][ch_name].plot()
