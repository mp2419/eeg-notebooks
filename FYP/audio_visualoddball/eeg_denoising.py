import mne
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mne import (io, compute_raw_covariance, read_events, pick_types, Epochs)
from mne.datasets import sample
from mne.preprocessing import Xdawn
from mne.viz import plot_epochs_image

print(__doc__)

df = pd.read_csv('C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse__raw.csv')
data=df.to_numpy()
channel_names=df.columns.tolist()
channel_types=len(channel_names)*['eeg']
sfreq = 256  # in Hertz
#montage = 'standard_1005'
info = mne.create_info(channel_names, sfreq, channel_types)
raw = mne.io.RawArray(data, info)



# data_path = sample.data_path()
# meg_path = data_path / 'MEG' / 'sample'
# raw_fname = meg_path / 'sample_audvis_filt-0-40_raw.fif'
# event_fname = meg_path / 'sample_audvis_filt-0-40_raw-eve.fif'
# tmin, tmax = -0.1, 0.3
# event_id = dict(vis_r=4)

# Setup for reading the raw data
# raw = io.read_raw_fif(raw_fname, preload=True)
events = mne.find_events(raw, stim_channel='AF7')
print(events)

# raw.filter(1, 20, fir_design='firwin')  # replace baselining with high-pass
# events = read_events(event_fname)

# raw.info['bads'] = ['MEG 2443']  # set bad channels
# picks = pick_types(raw.info, meg=True, eeg=False, stim=False, eog=False,
#                    exclude='bads')
# # Epoching
# epochs = Epochs(raw, events, event_id, tmin, tmax, proj=False,
#                 picks=picks, baseline=None, preload=True,
#                 verbose=False)

# # Plot image epoch before xdawn
# plot_epochs_image(epochs['vis_r'], picks=[230], vmin=-500, vmax=500)