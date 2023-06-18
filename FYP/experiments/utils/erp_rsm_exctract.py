import numpy as np
import mne, os

def compute_amplitude_rms(epochs, event_id, sfreq, pre_init=-0.2, pre_end=0, post_init=0.2, post_end=0.4):
    rms_values = []
    std_error_values = []
    
    # Convert pre_duration and post_duration to samples
    pre_samples_init = int((pre_init+0.5) * sfreq)
    pre_samples_end = int((0.5+pre_end) * sfreq)
    post_samples_init = int((0.5+post_init) * sfreq)
    post_samples_end = int((0.5+post_end) * sfreq)
    
    # Load the epochs data into memory
    epochs.load_data()
    
    # Iterate over each channel
    for ch_idx, ch_name in enumerate(epochs.info['ch_names']):
        channel_rms = []
        channel_std_error = []
        
        # Iterate over each event type
        for event_name, event_code in event_id.items():
            event_rms = []
            
            # Get the epochs for the current event type
            event_epochs = epochs[event_name]
            
            # Iterate over each epoch
            for epoch in event_epochs:
                # Compute the average amplitude in the pre and post durations
                pre_amplitude = np.mean(np.abs(epoch[ch_idx, pre_samples_init:pre_samples_end]))
                post_amplitude = np.mean(np.abs(epoch[ch_idx, post_samples_init:post_samples_end]))
                
                # Compute the RMS between the pre and post amplitudes
                rms = np.sqrt(np.mean((pre_amplitude - post_amplitude) ** 2))
                event_rms.append(rms)
            
            channel_rms.append(np.mean(event_rms))
            channel_std_error.append(np.std(event_rms, ddof=1) / np.sqrt(len(event_rms)))
        
        rms_values.append(channel_rms)
        std_error_values.append(channel_std_error)
    
    # Convert rms_values and std_error_values to numpy arrays
    rms_values = np.array(rms_values)
    std_error_values = np.array(std_error_values)
    
    return rms_values, std_error_values

#-----------

# raw_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'mne_raw', 'AudioVisual_04_1.fif')
# raw = mne.io.read_raw_fif(raw_path, preload=True)
# marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
# filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
# events, event_id= mne.events_from_annotations(filtered_raw, event_id=marker_mapping)
# event_id = {'left': 4, 'right': 3}
# #event_timestamps = filtered_raw.times[events[:, 0]]
# epochs = mne.Epochs(filtered_raw, events, event_id=event_id, tmin=-0.5, tmax=0.5, baseline=(None, 0))
# sfreq = raw.info['sfreq']


# mean_rms, std_error_rms = compute_amplitude_rms(epochs, event_id, sfreq)

# for event_idx, event_name in enumerate(event_id.keys()):
#     print(f"Event: {event_name}")
#     for ch_idx, ch_name in enumerate(epochs.info['ch_names']):
#         print(f"Channel: {ch_name}")
#         print(f"Mean RMS: {mean_rms[ch_idx, event_idx]:.2f}")
#         print(f"Std Error of RMS: {std_error_rms[ch_idx, event_idx]:.2f}")
#     print()

#-------------------------------------------

def erp_rsm_alltrials(raw_files, mode= "Audio", rejection_th =7000000):

    #----------PROCESSING DATA

    raw_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'mne_raw')
    #raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    event_ids = {'left': 4, 'right': 3}  
    tmin, tmax = -0.5, 0.5
    mean_rms_trial = {'left': [], 'right': []} 
    std_error_rms_trial = {'left': [], 'right': []}

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, _ = mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=30, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)
            sfreq = raw.info['sfreq']

            epochs = mne.Epochs(filtered_raw, events, event_id=event_ids, tmin=tmin, tmax=tmax,
                                baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            mean_rms, std_error_rms = compute_amplitude_rms(epochs, event_ids, sfreq)
            mean_rms_trial['left'].append(mean_rms[:,0])
            mean_rms_trial['right'].append(mean_rms[:,1])  
            std_error_rms_trial['left'].append(std_error_rms[:,0])
            std_error_rms_trial['right'].append(std_error_rms[:,1])    
    
    return mean_rms_trial, std_error_rms_trial

#----------

# mne.set_log_level("ERROR")
# keys_below_30 = ['AudioVisual_04_1.fif', 'AudioVisual_04_2.fif', 'AudioVisual_06_1.fif', 'AudioVisual_06_2.fif',  'ShapeVisual_03_1.fif', 'ShapeVisual_03_2.fif', 'ShapeVisual_04_1.fif', 'ShapeVisual_04_2.fif', 'ShapeVisual_06_2.fif', 'VibroVisual_06_1.fif', 'VibroVisual_02_2.fif', 'VibroVisual_03_1.fif', 'VibroVisual_03_2.fif']
# raw_files = keys_below_30

# mean_rsm_audio, std_error_rms_audio = erp_rsm_alltrials(raw_files, mode= "Audio", rejection_th =70)
# mean_rms_vibro,std_error_rms_vibro = erp_rsm_alltrials(raw_files, mode= "Vibro", rejection_th =70)
# mean_rsm_shape, std_error_rms_shape = erp_rsm_alltrials(raw_files, mode= "Shape", rejection_th =70)

#-------------------------------


