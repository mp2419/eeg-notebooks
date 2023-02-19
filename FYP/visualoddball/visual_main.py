import sys; sys.path.append("")

import os
import eegnb
from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.experiments.visual_n170 import n170
from FYP.visualoddball import visualoddbal_utils, z_visualoddball

# -- Define variables
board_name = "muse2"
experiment = "visual_n170"
subject_id = 0
session_nb = 0
record_duration = 10

# -- Setup EEG stream
# eeg_device = EEG(device=board_name)
# save_fn = generate_save_fn(board_name, experiment, subject_id, session_nb)
#print(save_fn)

# -- Start Visual Experiment
visualoddbal_utils.present(duration=record_duration)