import os
from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from FYP.initial_test.visualoddbal_simple import visualoddbal, visualoddbal_stim
# Define some variables
board_name = "muse2"
experiment = "visual_n170"
subject_id = 0
session_nb = 0
record_duration = 120

eeg_device = EEG(device=board_name)

# Create save file name
save_fn = generate_save_fn(board_name, experiment, subject_id, session_nb)
print(save_fn)

###################################################################################################  
# Run experiment
# ---------------------  
#  
visualoddbal.present(duration=record_duration, eeg=eeg_device, save_fn=save_fn)