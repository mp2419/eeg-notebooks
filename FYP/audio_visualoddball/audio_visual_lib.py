import threading
import time
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
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3
import os
from time import time
from glob import glob
from random import choice
from optparse import OptionParser
import random
import playsound
import random
import time
import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from psychopy.visual.circle import Circle
from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG

__title__ = "Audio Visual"

# Define a function to record data with Muse and put it into a queue
def record_data(duration, file_name):

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

    # Save data
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        # Insert a header row
        #TODO change names of channels
        writer.writerow(['Timestamp', 'Channel 1', 'Channel 2', 'Channel 3', 'Channel 4', 'Other'])
        # Record data and put it into the queue
        while True:
            sample, timestamp = inlet.pull_sample()
            writer.writerow([timestamp, sample[0],sample[1],sample[2],sample[3],sample[4]])  

            # Stop recording
            if time.time() - start_time > duration:
                print("Stopped acquiring data at time ", time.time())
                break

# Define a function to insert markers at random intervals into the data from the queue
def present_experiment(duration, file_name, iti = 0.4, soa = 0.3, jitter = 0.2):
    
    # Open a CSV file for writing
    with open(file_name, 'w', newline='') as file:
        start_time = time.time()
        writer = csv.writer(file)
        i = 0
        # Insert a header row
        writer.writerow(['Timestamp', 'Marker'])
        print("Start writing data at time ", start_time)

        # Start UI 
        mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
        text = visual.TextStim(win=mywin, text="Starting the test...", color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        current_colour = None

        time.sleep(2)
        # Iterate through the events
        while True:
            # Inter trial interval
            core.wait(iti + np.random.rand() * jitter)

            # Chose between visual and audio
            if random.random() < 0.8:
                next_event_type = 'visual'
            else:
                next_event_type = 'audio'

            # --- Visual Stimulus - Update screen

            if next_event_type == 'visual':
                # Select colour 
                colour = random.randint(1, 2)
                if colour == 1:
                    label = 'blue'
                else:
                    label = 'red'

                # If new colour, update
                if label != current_colour: 
                    # Define the circle stimulus
                    circle = Circle(mywin, radius=7, fillColor=label, lineColor=None, pos = (1,1))
                    circle.draw()
                    mywin.flip()
                    current_colour = label
                    new = True
                else:
                    new = False

                # Push sample of visual stimulus
                if new:
                    timestamp = time.time()
                    writer.writerow([timestamp, label])


            # --- Audio Stimulus - Directional Command
            elif next_event_type == 'audio':

                direction = random.randint(1, 2)
                if direction == 1:
                    label = 'right'
                else:
                    label = 'left'

                key = perform_audio_stimulus(label)

                # Push sample of audio stimulus
                timestamp = time.time()
                writer.writerow([timestamp, label])

                # Wait for key input
                event.waitKeys(keyList=key)

                # Push sample of audio stimulus
                timestamp = time.time()
                writer.writerow([timestamp, key])

            # offset
            core.wait(soa)
            #mywin.flip()

            if len(event.getKeys()) > 0 or (time.time() - start_time) > duration:
                print("Stopped writing data at time ", time.time())
                break

            event.clearEvents()

        mywin.close()


def run_experiment(duration, file_name_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_raw.csv',
file_name_marked = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_marked.csv'):

    show_instructions(duration)
    
    print("Experiment Started at time ", time.time())

    # - Start the recording thread
    recording_thread = threading.Thread(target=record_data, args=(duration,file_name_raw))
    recording_thread.start()

    # time.sleep(5)

    present_experiment(60, file_name_marked, iti = 0.4, soa = 0.3, jitter = 0.2)

    # # - Start the marker insertion thread
    # # stimulus_thread = threading.Thread(target=present_experiment, args=(duration, file_name_marked))
    # # stimulus_thread.start()

    # - Wait for both threads to finish
    recording_thread.join()
    # # stimulus_thread.join()

    print("Experiment Completed at time ", time.time())


def show_instructions(duration):

    instruction_text = """
    Welcome to the Audio Visual experiment! 

    You will see displayed circles of different colours, please count the blue ones.

    Occasionally, you will hear a left or right indicator, please press the appropriate arrow key to continue the test. 
 
    Stay still, focus on the centre of the screen, and try not to blink. 

    This test will run for %s seconds.

    Press spacebar to continue. 
    
    """
    instruction_text = instruction_text % duration

    # graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    mywin.mouseVisible = False

    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")
    mywin.close()

def perform_audio_stimulus(command):
    # Direction
    if command =='right':
        key='right arrow'
        playsound.playsound("FYP\\audio_visualoddball\\audio_data\\right_only_beep.wav", True)
    else:
        key='left arrow'
        playsound.playsound("FYP\\audio_visualoddball\\audio_data\\left_only_beep.wav", True)
    return key
