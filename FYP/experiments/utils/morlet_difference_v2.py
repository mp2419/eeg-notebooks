import os
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne.time_frequency import tfr_morlet

def morlet_difference(raw_files, mode1="Audio", mode2="Vibro", rejection_th=7000000):

    # ----------PROCESSING DATA

    raw_folder = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP',
                              'data_ordered', 'mne_raw')
    # raw_files = [file for file in os.listdir(raw_folder) if file.endswith(".fif")]
    marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
    duration = 30.0  # Duration of each epoch (seconds)
    event_ids = {'left': 4, 'right': 3}  # Replace with your event IDs
    tmin, tmax = -0.3, 0.7
    evokeds_mode1_left = []
    evokeds_mode1_right = []
    evokeds_mode2_left = []
    evokeds_mode2_right = []

    # Process each raw file and extract evoked response
    for file in raw_files:
        if mode1 in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, event_id = mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)

            epochs_left = mne.Epochs(filtered_raw, events, event_id=event_ids['left'], tmin=tmin, tmax=tmax,
                                      baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            epochs_right = mne.Epochs(filtered_raw, events, event_id=event_ids['right'], tmin=tmin, tmax=tmax,
                                       baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            # Separate the evoked responses for left and right events
            evokeds_mode1_left.append(epochs_left.average())
            evokeds_mode1_right.append(epochs_right.average())

        if mode2 in file:
            raw_path = os.path.join(raw_folder, file)
            raw = mne.io.read_raw_fif(raw_path, preload=True)
            events, event_id = mne.events_from_annotations(raw, event_id=marker_mapping)
            filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
            reject_threshold = rejection_th  # Threshold for epoch rejection (microvolts)

            epochs_left = mne.Epochs(filtered_raw, events, event_id=event_ids['left'], tmin=tmin, tmax=tmax,
                                      baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            epochs_right = mne.Epochs(filtered_raw, events, event_id=event_ids['right'], tmin=tmin, tmax=tmax,
                                       baseline=(None, 0), preload=True, reject=dict(eeg=reject_threshold))

            evokeds_mode2_left.append(epochs_left.average())
            evokeds_mode2_right.append(epochs_right.average())

    # Combine the evoked responses for left and right events for each mode
    combined_evoked_mode1_left = mne.combine_evoked(evokeds_mode1_left, weights='nave')
    combined_evoked_mode1_right = mne.combine_evoked(evokeds_mode1_right, weights='nave')
    combined_evoked_mode2_left = mne.combine_evoked(evokeds_mode2_left, weights='nave')
    combined_evoked_mode2_right = mne.combine_evoked(evokeds_mode2_right, weights='nave')

    # Compute the point-to-point difference between mode1 and mode2 evoked responses for each channel
    evoked_diff_left = combined_evoked_mode1_left.copy()
    evoked_diff_left.data = combined_evoked_mode1_left.data - combined_evoked_mode2_left.data

    evoked_diff_right = combined_evoked_mode1_right.copy()
    evoked_diff_right.data = combined_evoked_mode1_right.data - combined_evoked_mode2_right.data

    # Compute the Morlet transform of the difference for event_id 'left'
    freqs = np.arange(0.1, 30, 2)  # Frequency range for the wavelet transform
    n_cycles = freqs / 2.0  # Number of cycles in each frequency range

    power_left1 = tfr_morlet(combined_evoked_mode1_left, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)
    power_left2 = tfr_morlet(combined_evoked_mode2_left, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)
    power_left = power_left1 - power_left2

    fig, axs = plt.subplots(2, 2, figsize=(5, 5))

    # Flatten the axs array for easier iteration
    axs = axs.flatten()

    # Define the frequency range of interest
    freq_min = 0  # Minimum frequency (Hz)
    freq_max = 30  # Maximum frequency (Hz)

    # Iterate over each channel and plot the power for event_id 'left'
    for i, channel in enumerate(power_left.ch_names):
        # Create a new subplot for the current channel
        ax = axs[i]

        # Plot the power for the current channel with dB scaling
        tfr_plot = power_left.copy().pick_channels([channel])
        tfr_data = np.mean(np.abs(tfr_plot.data), axis=0)  # Compute average power
        im = ax.imshow(10*np.log10(tfr_data), aspect='auto', origin='lower', cmap='jet',
                       extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max])  # Create dummy image plot

        # Add colorbar
        cbar = plt.colorbar(im, orientation='vertical', pad=0.1, ax=ax)
        cbar.set_label('Power')

        # Set labels and title
        ax.set_xlabel('Time from the Event (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"{channel}")

    # Remove any extra subplots if there are fewer channels than subplots
    if len(power_left.ch_names) < 4:
        for i in range(len(power_left.ch_names), 4):
            fig.delaxes(axs[i])


    fig.suptitle(f"Morlet Transform of Point-to-Point Difference for event 'left' between {mode1} and {mode2}")

    # Adjust spacing between subplots
    fig.tight_layout()

    # Show the figure
    plt.show(block=False)

    # Compute the Morlet transform of the difference for event_id 'right'
    power_right1 = tfr_morlet(combined_evoked_mode1_right, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)
    power_right2 = tfr_morlet(combined_evoked_mode2_right, freqs=freqs, n_cycles=n_cycles, use_fft=True, return_itc=False)
    power_right = power_right1 - power_right2

    fig, axs = plt.subplots(2, 2, figsize=(5, 5))

    # Flatten the axs array for easier iteration
    axs = axs.flatten()

    # Define the frequency range of interest
    freq_min = 0  # Minimum frequency (Hz)
    freq_max = 30  # Maximum frequency (Hz)

    # Iterate over each channel and plot the power for event_id 'right'
    for i, channel in enumerate(power_right.ch_names):
        # Create a new subplot for the current channel
        ax = axs[i]
        # Create the color map with the middle color at 0
        # cmap = plt.cm.get_cmap('coolwarm')
        # cmap.set_over('red')
        # cmap.set_under('blue')
        # cmap.set_bad('gray')
        # Plot the power for the current channel with dB scaling
        tfr_plot = power_right.copy().pick_channels([channel])
        tfr_data = np.mean(np.abs(tfr_plot.data), axis=0)  # Compute average power
        im = ax.imshow(10*np.log10(tfr_data), aspect='auto', origin='lower', cmap='jet',extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max])  # Create dummy image plot
        #im = ax.imshow((tfr_data), aspect='auto', origin='lower', cmap='jet',extent=[tfr_plot.times[0], tfr_plot.times[-1], freq_min, freq_max], )  # Create dummy image plot

        #vmin=-max_abs_rms, vmax=max_abs_rms
        # Add colorbar
        cbar = plt.colorbar(im, orientation='vertical', pad=0.1, ax=ax)
       # cbar.set_label('Power (dB)')
        cbar.set_label('Power')


        # Set labels and title
        ax.set_xlabel('Time from the Event (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(f"{channel}")

    # Remove any extra subplots if there are fewer channels than subplots
    if len(power_right.ch_names) < 4:
        for i in range(len(power_right.ch_names), 4):
            fig.delaxes(axs[i])

    fig.suptitle(f"Morlet Transform of Point-to-Point Difference for event 'right' between {mode1} and {mode2}")

    # Adjust spacing between subplots
    fig.tight_layout()

    # Show the figure
    plt.show()

keys_below_30 = ['AudioVisual_04_1.fif', 'AudioVisual_04_2.fif', 'AudioVisual_06_1.fif', 'AudioVisual_06_2.fif',  'ShapeVisual_03_1.fif', 'ShapeVisual_03_2.fif', 'ShapeVisual_04_1.fif', 'ShapeVisual_04_2.fif', 'ShapeVisual_06_2.fif', 'VibroVisual_06_1.fif', 'VibroVisual_02_2.fif', 'VibroVisual_03_1.fif', 'VibroVisual_03_2.fif']

morlet_difference(keys_below_30, mode1="Audio", mode2="Shape")
morlet_difference(keys_below_30, mode1="Vibro", mode2="Shape")
morlet_difference(keys_below_30, mode1="Audio", mode2="Vibro")