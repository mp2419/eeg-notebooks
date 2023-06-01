import copy
from typing import List
from time import time
import os, csv, json
import time
import mne
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
from graphics import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mne import create_info, concatenate_raws
from mne.io import RawArray
from mne.channels import make_standard_montage


def load_csv_as_raw(
    fnames: List[str],
    sfreq=256,
    ch_ind= [0,1,2,3, 4],
    aux_ind=None,
    replace_ch_names=None,
    verbose=1,
    resp_on_missing='warn'
) -> RawArray:
    """Load CSV files into an MNE Raw object.

    Args:
        fnames (array_like): list of filename(s) to load. Should end with
            ".csv".
        sfreq (float): sampling frequency of the data.
        ch_ind (array_like): column indices to keep from the CSV files.

    Keyword Args:
        aux_ind (array_like or None): list of indices for columns containing
            auxiliary channels.
        replace_ch_names (array_like or None): list of channel name mappings
            for the selected columns.
        verbose (int): verbose level.

    Returns:
        (mne.io.RawArray): concatenation of the specified filenames into a
            single Raw object.
    """


    print('\n\nLoading these files: \n')
    for f in fnames: print(f + '\n')
    print('\n\n')


    ch_ind = copy.deepcopy(ch_ind)
    n_eeg = len(ch_ind)
    if aux_ind is not None:
        n_aux = len(aux_ind)
        ch_ind += aux_ind
    else:
        n_aux = 0

    raw = []

    for fn in fnames:
        # Read the file
        data = pd.read_csv(fn)

        # Channel names and types
        ch_names = [list(data.columns)[i] for i in ch_ind] + ["stim"]
        print(ch_names)
        ch_types = ["eeg"] * n_eeg + ["misc"] * n_aux + ["stim"]

        if replace_ch_names is not None:
            ch_names = [
                c if c not in replace_ch_names.keys() else replace_ch_names[c]
                for c in ch_names
            ]
        print(ch_names)

        # Transpose EEG data and convert from uV to Volts
        data = data.values[:, ch_ind + [-1]].T
        data[:-1] *= 1e-6

        # create MNE object
        info = create_info(ch_names=ch_names, ch_types=ch_types, sfreq=sfreq, verbose=1)
        raw.append(RawArray(data=data, info=info, verbose=verbose))
    
    raws = concatenate_raws(raw, verbose=verbose)
    montage = make_standard_montage("standard_1005")
    raws.set_montage(montage,on_missing=resp_on_missing)

    return raws


# TODO FOR MORE CHECKS AND PLOT:
# https://mne.tools/1.0/generated/mne.time_frequency.psd_multitaper.html#footcite-slepian1978

def check_quality(duration = 10):

    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    # Set active EEG stream to inlet and apply time correction
    start_time = time.time()
    print("Start acquiring data at time ", start_time)
    inlet = StreamInlet(streams[0], max_chunklen=12)
    eeg_time_correction = inlet.time_correction()
    # Get the stream info, description, sampling frequency, number of channels
    info = inlet.info()
    description = info.desc()
    fs = int(info.nominal_srate())
    n_channels = info.channel_count()
    sfreq = 256  # Set the sampling rate
    # Get names of all channels
    ch = description.child('channels').first_child()
    ch_names = [ch.child_value('label')]
    for i in range(1, n_channels):
        ch = ch.next_sibling()
        ch_names.append(ch.child_value('label'))

    ch_types = ['eeg'] * len(ch_names)  # Set the channel types
    data = []

    while (time.time() - start_time) < duration:
        sample, _ = inlet.pull_sample()
        data.append(sample)

        # Convert the recorded data to a numpy array
    data = np.array(data)

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    # Create an MNE Raw object from the data
    raw = mne.io.RawArray(data.T, info)




    # Calculate the power spectral density of the EEG signal
    psds, freqs = mne.time_frequency.psd_multitaper(raw, fmax=30, n_jobs=1, verbose=0)
    psd_mean = psds.mean(axis=0)

    # Calculate the signal-to-noise ratio of the EEG signal
    signal_power = np.mean(psds[:, np.logical_and(freqs >= 1, freqs <= 30)], axis=1)
    noise_power = np.mean(psds[:, np.logical_or(freqs < 1, freqs > 30)], axis=1)
    snr = signal_power / noise_power

    # Print the EEG quality and noise sources
    print("EEG quality (signal-to-noise ratio):", snr)
    # EEG quality (signal-to-noise ratio): [ 0.34595192  0.38935046  0.42858711  0.6477837  38.99336141]
    # AT REST: EEG quality (signal-to-noise ratio): [0.149849   0.1306871  0.13169118 0.11753881 0.96839295]; EEG quality (signal-to-noise ratio): [0.15654753 0.34208071 0.2231241  0.16698169 1.16249644]
    # noise: EEG quality (signal-to-noise ratio): [0.19566665 0.46358032 0.56061054 0.22219707 1.04238929]


def plot_eeg_spectrum(file_name_raw):
    raw = load_csv_as_raw([file_name_raw ],256, [1,2,3, 4])
    raw.filter(1,30, method='iir')
    raw.plot_psd(fmin=1, fmax=30)


def psd_eeg(file_path, n=4):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Extract the time values (first column) and data (other columns)
    time = df.iloc[:, 0].values
    data = df.iloc[:, 1:(1+n)].values

    # Compute the PSD for each column of the data
    fs = 1 / (time[1] - time[0])  # Sampling frequency
    n = len(time)  # Number of samples
    frequencies = np.fft.fftfreq(n, 1 / fs)
    psd = np.zeros((len(frequencies), data.shape[1]))

    for i in range(data.shape[1]):
        fft = np.fft.fft(data[:, i])
        psd[:, i] = np.abs(fft) ** 2 / (n * fs)

    # Plot the PSD for each column of the data
    for i in range(data.shape[1]):
        plt.plot(frequencies, psd[:, i], label=f"Column {i+1}")

    plt.xlabel('Frequency')
    plt.ylabel('Power Spectral Density')
    plt.legend()
    plt.show()

#----------------------------------------

def extract_arrow_stats(json_file_path):
    with open(json_file_path, 'r') as file:
        eeg_data = json.load(file)
        eeg_data = np.array(eeg_data)
        marker_strings = eeg_data[:, 5]
        marker_timestamp = eeg_data[:, 0]

        left_arrow_delay = []
        right_arrow_delay = []
        stats = {'Dir_Missed_pcg':0, 'Dir_Wrong_pcg':0, 'Dir_empty_call':0, 'L_correct': 0, 'L_missed': 0, 'L_wrong': 0, 'R_correct': 0, 'R_missed': 0, 'R_wrong': 0, 'L_delay_avg': 0, 'R_delay_avg':0, 'L_delay_std': 0, 'R_delay_std':0}
        prev_left = False
        prev_right = False

        for i in range(len(marker_strings)):
            value = marker_strings[i]
           
            timestamp = float(marker_timestamp[i])

            if value == "left arrow":
                if prev_left:
                    left_arrow_delay.append(timestamp - prev_left_timestamp)
                    prev_left = False
                elif prev_right:
                    stats['R_wrong'] += 1
                else:
                    stats['Dir_empty_call'] += 1

            elif value == "right arrow":
                if prev_right:
                    right_arrow_delay.append(timestamp - prev_right_timestamp)
                    prev_right = False
                elif prev_left:
                    stats['L_wrong'] += 1
                else:
                    stats['Dir_empty_call'] += 1

            elif value == "left":
                if prev_left:
                    stats['L_missed'] += 1
                if prev_right:
                    stats['R_missed'] += 1
                
                prev_left = True
                prev_right = False
                prev_left_timestamp = timestamp

            elif value == "right":
                if prev_left:
                    stats['L_missed'] += 1
                if prev_right:
                    stats['R_missed'] += 1
                
                prev_right = True
                prev_left = False
                prev_right_timestamp = timestamp

        if prev_left:
            stats['L_missed'] += 1
        if prev_right:
            stats['R_missed'] += 1

        stats['L_correct'] = len(left_arrow_delay)
        stats['R_correct'] = len(right_arrow_delay)
        tot_correct = stats['L_correct'] + stats['R_correct']

        stats['L_delay_avg'] = np.mean(left_arrow_delay)
        stats['R_delay_avg'] = np.mean(right_arrow_delay)

        stats['L_delay_std'] = np.std(left_arrow_delay)
        stats['R_delay_std'] = np.std(right_arrow_delay)

        stats['Dir_Missed_pcg'] = (stats['L_missed'] + stats['R_missed']) / tot_correct *100
        stats['Dir_Wrong_pcg'] = (stats['L_wrong'] + stats['R_wrong']) / tot_correct *100

    return left_arrow_delay, right_arrow_delay, stats

#-------------

# json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_2.json')
# left_arrow_delay, right_arrow_delay, stats = extract_arrow_stats(json_file_path)
# print(stats)

#----------------------------

def merge_obj_performance(circles_file_path, eeg_json_path):

    with open(circles_file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader) #leave
        first_row = next(reader)
        true = float(first_row[0])
        reported = float(first_row[1])
        error = reported-true
        error_pcg = error/true *100

        left_arrow_delay, right_arrow_delay, stats = extract_arrow_stats(eeg_json_path)

        performance = {}
        performance['Cir_Error_pcg'] = error_pcg
        performance['Cir_Error'] = error
        for key in stats.keys():
            performance[key] = stats[key]
        performance['L_delay_array'] = left_arrow_delay
        performance['R_delay_array'] = right_arrow_delay


    
    return performance

#--------------

# circles_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data', 'AudioVisual', '04', '2', 'blue_circles.csv')
# eeg_json_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_04_2.json')
# new_file_json = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'results_data', 'Arrow_Circles_performance.json')


# performance = merge_obj_performance(circles_file_path, eeg_json_path)
# all_performances = {}
# all_performances['AudioVisual_04_2'] = performance

# json_data = json.dumps(all_performances, indent=4)

# with open(new_file_json, 'w') as file:
#     file.write(json_data)
#     print("New file at ", new_file_json)
