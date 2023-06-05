import mne, os
import numpy as np
import matplotlib.pyplot as plt
from eeg_analysis_lib import psd_abs_n_rel

def psd_alltrials(mode= "Audio"):
    raw_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'mne_raw')
    raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]

    psd_rel = []
    psd_abs = []

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            psd_data_abs, psd_data_rel = psd_abs_n_rel(raw, chart=False)
            psd_rel.append(psd_data_rel)
            psd_abs.append(psd_data_abs)
    psd_rel = np.array(psd_rel)
    psd_abs = np.array(psd_abs)
    print(psd_rel.shape)
    print(psd_abs.shape)
    psd_rel =np.transpose(psd_rel)
    psd_abs =np.transpose(psd_abs)
    print(psd_rel.shape)
    print(psd_abs.shape)
    psd_rel_mean =np.mean(psd_rel)
    psd_abs_mean =np.mean(psd_abs)
    psd_rel_std =np.std(psd_rel)
    psd_abs_std =np.std(psd_abs)
    print("Mean and Std Relative Power:",psd_rel_mean, psd_rel_std )
    print("Mean and Std Absolute Power:",psd_abs_mean, psd_abs_std )



            


psd_alltrials(mode= "Audio")
# psd_alltrials(mode= "Vibro")
# psd_alltrials(mode= "Shape")

