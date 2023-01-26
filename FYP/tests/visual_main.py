import sys; sys.path.append("")

import os
# import importlib.util
# sys.path.append('/../../eegnb')
# # Considering your module contains a function called my_func, you could import it:
from FYP.visualoddbal_simple import visualoddbal, visualoddbal_stim

import eegnb

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.experiments.visual_n170 import n170
#from eegnb.experiments.test import test
#from eegnb.visualoddbal_simple import visualoddbal_stim
#import eegnb.experiments.visualoddbal_simple

# Define some variables
board_name = "muse2"
experiment = "visual_n170"
subject_id = 0
session_nb = 0
record_duration = 10
eeg_device = EEG(device=board_name)

# Create save file name
save_fn = generate_save_fn(board_name, experiment, subject_id, session_nb)
print(save_fn)

visualoddbal_stim.present(duration=record_duration)