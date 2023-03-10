import time
import eegnb
from eegnb.devices.eeg import EEG
import mne
import threading
import csv
import random
from queue import Queue
import muselsl
from muselsl import stream
import argparse
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
from psychopy import prefs
from graphics import *


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
    
check_quality()