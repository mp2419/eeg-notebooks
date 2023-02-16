# #packages abd libraries
# from muselsl import stream, list_muses, view, record
# from multiprocessing import Process
# from mne import Epochs, find_events
# from time import time, strftime, gmtime
# import os
# from collections import OrderedDict
import sys
sys.path.append("..\\")
print(sys.path)

import warnings
warnings.filterwarnings('ignore')

# from scipy.io import loadmat
# import numpy as np, pandas as pd
# import h5py
# from psychopy import prefs
#prefs.hardware['audioLib'] = ['PTB']
#prefs.hardware['audioLib'] = ['pyo'] # PTB']

from eegnb.experiments.auditory_oddball import auditory_erp_arrayin
from eegnb.analysis import utils

from experiment import audio_visual
from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG

# Define some variables
board_name = "muse2"
experiment = "audio_visual"
subject_id = 1
session_nb = 1
record_duration = 120

# Start EEG device
eeg_device = EEG(device=board_name)

# Create save file name
save_fn = generate_save_fn(board_name, experiment, subject_id, session_nb)
print(save_fn)
 
# Run experiment
audio_visual.present(duration=record_duration, eeg=eeg_device, save_fn=save_fn)
