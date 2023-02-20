import threading
import time
import csv
import os
import random
from queue import Queue
import muselsl
from muselsl import stream
import argparse
import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data


# Define a function to record data with Muse and put it into a queue
def record_data(queue, duration, file_name):
    # Create a stream with Muse
    # muselsl.find_muse()
    # muse_stream = stream(address="00:55:da:b7:c5:d9")

    # Search for active LSL stream
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

    # Get names of all channels
    ch = description.child('channels').first_child()
    ch_names = [ch.child_value('label')]

    for i in range(1, n_channels):
        ch = ch.next_sibling()
        ch_names.append(ch.child_value('label'))

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        i = 0
        # Insert a header row
        writer.writerow(['Timestamp', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Other'])

        # Record data and put it into the queue
        while True:
            sample, timestamp = inlet.pull_sample()
            # print("--> into queue: ", [timestamp, sample], " at time: ", time.time() )
            queue.put([timestamp, sample])
            #print(timestamp, sample)
            writer.writerow([timestamp, sample[0],sample[1],sample[2],sample[3],sample[4]])  

            if time.time() - start_time > duration:
                print("Stopped acquiring data at time ", time.time())
                print("Data IN queue is size", queue.qsize())
                break

# Define a function to insert markers at random intervals into the data from the queue
def insert_markers(queue, duration, file_name):
    # Open a CSV file for writing
    lag = 10

    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        i = 0
        # Insert a header row
        writer.writerow(['Timestamp', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Other', 'Markers', 'Timestamp_stim'])
        
        start_time = time.time()
        print("Start writing data at time ", start_time)
        # Get the first sample from the queue
        sample = queue.get()
        # print("<-- from queue: ",  sample, " at time: ", time.time() )
        # Record the first sample in the CSV file
        writer.writerow([sample[0], sample[1][0],sample[1][1],sample[1][2],sample[1][3],sample[1][4], None])
        
        # Insert markers at random intervals into the data from the queue
        while True:
            
            # Insert a marker into the data
            # writer.writerow([sample.timestamp, 'Marker', '', '', ''])
            # Get the next sample from the queue
            sample = queue.get()
            if i  %  2 == 0:
                marker = ['Stimulus 1', time.time()]
            else:
                marker = ['No stimulus', time.time()]

            #print(i, "<-- from queue: ",  sample, " at time: ", time.time() )
            i = i + 1
            # Record the sample in the CSV file
            writer.writerow([sample[0], sample[1][0],sample[1][1],sample[1][2],sample[1][3],sample[1][4], marker])

            if (time.time() - start_time > duration) &  (queue.qsize() == 0):
                print("Stopped writing data at time ", time.time())
                print("Data OUT queue is size", queue.qsize())
                break

# Create a queue to hold the data from the recording thread
queue = Queue()
duration = 10
file_name_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_raw.csv'
file_name_marked = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_marked.csv' 

print("Experiment Started at time ", time.time())

# Start the recording thread
recording_thread = threading.Thread(target=record_data, args=(queue,duration,file_name_raw))
recording_thread.start()

# time.sleep(5)

# Start the marker insertion thread
stimulus_thread = threading.Thread(target=insert_markers, args=(queue,duration, file_name_marked))
stimulus_thread.start()

# Wait for both threads to finish
recording_thread.join()

stimulus_thread.join()

print("Experiment Completed at time ", time.time())
