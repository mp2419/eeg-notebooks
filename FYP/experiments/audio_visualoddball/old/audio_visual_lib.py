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
import utils.data_analysis.synch_data as synch

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

    file_folder = os.path.dirname(file_name)
    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

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
def present_experiment(trial, duration, file_name,  mywin,  iti = 0.7, soa = 0.3, jitter = 0.2):

    file_folder = os.path.dirname(file_name)

    if not os.path.exists(file_folder):
        os.makedirs(file_folder)

    # Open a CSV file for writing
    with open(file_name, 'w', newline='') as file:
        start_time = time.time()
        writer = csv.writer(file)
        i = 0
        # Insert a header row
        writer.writerow(['Timestamp', 'Marker'])
        print("Start writing data at time ", start_time)

        # Start UI 
        # mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
        instruction_text = "Starting trial number %s..." % trial
        text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        current_colour = None
        blue_n = 0 

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
                    if label == 'blue':
                        blue_n += 1


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

            if  (time.time() - start_time) > duration:
                print("Stopped writing data at time ", time.time())
                break

            event.clearEvents()

        text = visual.TextStim(win=mywin, text="Trial completed", color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        # mywin.close()

    return blue_n

def run_trial(duration, file_name_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_raw.csv',
file_name_marked = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_marked.csv', file_name_synched ='C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_synched.csv'):
    
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    show_instructions(duration, mywin)
    
    print("Experiment Started at time ", time.time())

    # - Start the recording thread
    recording_thread = threading.Thread(target=record_data, args=(duration+5,file_name_raw))
    recording_thread.start()
    trial = 1
    # time.sleep(5)
    blue_n = present_experiment(trial, duration, file_name_marked, iti = 0.4, soa = 0.3, jitter = 0.2, mywin = mywin)

    # # - Start the marker insertion thread
    # # stimulus_thread = threading.Thread(target=present_experiment, args=(duration, file_name_marked))
    # # stimulus_thread.start()

    # - Wait for both threads to finish
    recording_thread.join()
    # # stimulus_thread.join()
    blue_n_reported = return_blue_number(mywin)
    mywin.close()
    print("Experiment Completed at time ", time.time())
    print("Number of blue cirlces reported is: ", blue_n_reported, "Number of actual blue circles is: ", blue_n )
    synch.merge_data(filename_raw = file_name_raw, filename_marked = file_name_marked, filename_union = file_name_synched)

def show_instructions(duration,  mywin ):

    instruction_text = """
    Welcome to the Audio Visual experiment! 

    You will see displayed circles of different colours, please COUNT the BLUE circles.

    Occasionally, you will hear a left or right indicator, please PRESS the LEFT or RIGHT arrow key accordingly.
     
 
    Stay still, focus on the centre of the screen, and try not to blink. 

    This test will run for %s seconds.

    Press spacebar to continue. 
    
    """
    instruction_text = instruction_text % duration

    # graphics
    # mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    mywin.mouseVisible = False

    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")
    # mywin.close()

def perform_audio_stimulus(command):
    # Direction
    if command =='right':
        key='right arrow'
        playsound.playsound("FYP\\audio_visualoddball\\audio_data\\right_only_beep.wav", True)
    else:
        key='left arrow'
        playsound.playsound("FYP\\audio_visualoddball\\audio_data\\left_only_beep.wav", True)
    return key

def return_blue_number( mywin ):

    # graphics
     # mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    mywin.mouseVisible = False

    key_number = ''

    while True:
        instruction_text = """
        Well Done! 

        Please report the number of BLUE circles 
        
        you have counted and press SPACE.

        Number of blue circles: %s
        
        """
        instruction_text = instruction_text % key_number

        # Instructions
        text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        keys = event.waitKeys()  # wait for a key to be pressed

        if 'space' in keys:  # check if the escape key was pressed
            break

        if keys[0].isdigit():  # check if the key pressed is a number
            key_number += keys[0]  # append the number to key_number


    # mywin.close()
    
    return key_number

def run_experiement(duration, file_name_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_raw.csv',
file_name_marked = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_marked.csv', file_name_synched ='C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\data_muse_synched.csv'):
    
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    show_instructions(duration, mywin)
    for trial in range([1, 3]):
        
        print("Experiment Started at time ", time.time())

        # - Start the recording thread
        recording_thread = threading.Thread(target=record_data, args=(duration+5, file_name_raw))
        recording_thread.start()

        # time.sleep(5)
        blue_n = present_experiment(trial, duration, file_name_marked, iti = 0.4, soa = 0.3, jitter = 0.2, mywin = mywin)

        # # - Start the marker insertion thread
        # # stimulus_thread = threading.Thread(target=present_experiment, args=(duration, file_name_marked))
        # # stimulus_thread.start()

        # - Wait for both threads to finish
        recording_thread.join()
        # # stimulus_thread.join()
        blue_n_reported = return_blue_number(mywin)
        mywin.close()
        print("Experiment Completed at time ", time.time())
        print("Number of blue cirlces reported is: ", blue_n_reported, "Number of actual blue circles is: ", blue_n )
    
    synch.merge_data(filename_raw = file_name_raw, filename_marked = file_name_marked, filename_union = file_name_synched)

