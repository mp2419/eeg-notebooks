import os
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne.time_frequency import tfr_morlet
from eeg_analysis_lib import json_to_mne

json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_2.json')
raw = json_to_mne.create_raw_object(json_file_path)

filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
channel_names = ['TP9', 'AF7', 'AF8', 'TP10']
events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
duration = 30.0  # Duration of each epoch (seconds)


# Extract epochs
epochs = mne.Epochs(filtered_raw, events, event_id=event_id, tmin=-0.3, tmax=0.7, baseline=None, preload=True, event_repeated='merge')
# Set the parameters for the Morlet wavelet transform
freqs = np.arange(0.1, 30, 2)  # Frequency range for the wavelet transform
n_cycles = freqs / 2.0  # Number of cycles in each frequency range

# Perform the Morlet wavelet transform
power = tfr_morlet(epochs, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)

# Plot the wavelet power
power.plot(title=channel_names)
plt.show()
