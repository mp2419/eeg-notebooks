import os
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne.time_frequency import tfr_morlet
from eeg_analysis_lib import create_raw_object


def morlet_alltrials(raw_files, mode= "Audio", rejection_th =7000000):

    #----------PROCESSING DATA

    raw_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'mne_raw')
    #raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    duration = 30.0  # Duration of each epoch (seconds)
    event_ids = {'left': 4, 'right': 3}  # Replace with your event IDs
    tmin, tmax = -0.3, 0.7
    evokeds_left = {}
    evokeds_right = {}

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)

            epochs_left = mne.Epochs(filtered_raw, events, event_id=event_ids['left'], tmin=tmin, tmax=tmax,
                                baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            # Compute the average evoked response for left events
            evoked_left = epochs_left.average()
            evokeds_left[file] = evoked_left

            # Create epochs based on the events and desired time window for right events
            epochs_right = mne.Epochs(filtered_raw, events, event_id=event_ids['right'], tmin=tmin, tmax=tmax,
                                    baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            # Compute the average evoked response for right events
            evoked_right = epochs_right.average()
            evokeds_right[file] = evoked_right

    # Combine the evoked responses from different trials for left and right events
    combined_evoked_left = mne.combine_evoked(list(evokeds_left.values()), weights='nave')
    combined_evoked_right = mne.combine_evoked(list(evokeds_right.values()), weights='nave')

    
    freqs = np.arange(0.1, 30, 2)  # Frequency range for the wavelet transform
    n_cycles = freqs / 2.0  # Number of cycles in each frequency range

    #--------LEFT EVENT

    # Perform the Morlet wavelet transform LEFT
    power = tfr_morlet(combined_evoked_left, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    # Flatten the axs array for easier iteration
    axs = axs.flatten()

    # Define the frequency range of interest
    freq_min = 0  # Minimum frequency (Hz)
    freq_max = 30  # Maximum frequency (Hz)

    # Iterate over each channel and plot the power
    for i, channel in enumerate(power.ch_names):
        # Create a new subplot for the current channel
        ax = axs[i]

        # Plot the power for the current channel with dB scaling
        tfr_plot = power.copy().pick_channels([channel])
        tfr_data = np.mean(np.abs(tfr_plot.data), axis=0)  # Compute average power
        im = ax.imshow(10 * np.log10(tfr_data), aspect='auto', origin='lower', cmap='jet',
                    extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max])  # Create dummy image plot

        # Add colorbar
        cbar = plt.colorbar(im, orientation='vertical', pad=0.1, ax=ax)
        cbar.set_label('Power (dB)')

        # Set labels and title
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"{channel}")

    # Remove any extra subplots if there are fewer channels than subplots
    if len(power.ch_names) < 4:
        for i in range(len(power.ch_names), 4):
            fig.delaxes(axs[i])

    # Set common labels and title for the figure
    # fig.text(0.5, 0.04, 'Time (s)', ha='center')
    # fig.text(0.04, 0.5, 'Frequency (Hz)', va='center', rotation='vertical')
    fig.suptitle(f"Time-frequency response to 'left' command - {mode} Stimulation")

    # Adjust spacing between subplots
    fig.tight_layout()

    # Show the figure
    plt.show()


    #-------RIGHT EVENT
    # Perform the Morlet wavelet transform RIGHT
    power = tfr_morlet(combined_evoked_right, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)

 
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    # Flatten the axs array for easier iteration
    axs = axs.flatten()

    # Define the frequency range of interest
    freq_min = 0  # Minimum frequency (Hz)
    freq_max = 30  # Maximum frequency (Hz)

    # Iterate over each channel and plot the power
    for i, channel in enumerate(power.ch_names):
        # Create a new subplot for the current channel
        ax = axs[i]

        # Plot the power for the current channel with dB scaling
        tfr_plot = power.copy().pick_channels([channel])
        tfr_data = np.mean(np.abs(tfr_plot.data), axis=0)  # Compute average power
        im = ax.imshow(10 * np.log10(tfr_data), aspect='auto', origin='lower', cmap='jet',
                    extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max])  # Create dummy image plot

        # Add colorbar
        cbar = plt.colorbar(im, orientation='vertical', pad=0.1, ax=ax)
        cbar.set_label('Power (dB)')

        # Set labels and title
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"{channel}")

    # Remove any extra subplots if there are fewer channels than subplots
    if len(power.ch_names) < 4:
        for i in range(len(power.ch_names), 4):
            fig.delaxes(axs[i])

    # Set common labels and title for the figure
    # fig.text(0.5, 0.04, 'Time (s)', ha='center')
    # fig.text(0.04, 0.5, 'Frequency (Hz)', va='center', rotation='vertical')
    fig.suptitle(f"Time-frequency response to 'Right' command - {mode} Stimulation")

    # Adjust spacing between subplots
    fig.tight_layout()

    # Show the figure
    plt.show()

#------------

# keys_below_30 = ['AudioVisual_04_1.fif', 'AudioVisual_04_2.fif', 'AudioVisual_06_1.fif', 'AudioVisual_06_2.fif',  'ShapeVisual_03_1.fif', 'ShapeVisual_03_2.fif', 'ShapeVisual_04_1.fif', 'ShapeVisual_04_2.fif', 'ShapeVisual_06_2.fif', 'VibroVisual_06_1.fif', 'VibroVisual_02_2.fif', 'VibroVisual_03_1.fif', 'VibroVisual_03_2.fif']

# morlet_alltrials(keys_below_30, mode= "Audio", rejection_th =70)
# morlet_alltrials(keys_below_30, mode= "Vibro", rejection_th =70)
# morlet_alltrials(keys_below_30, mode= "Shape", rejection_th =70)