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

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG

__title__ = "Audio Visual"


def present(duration=120, eeg: EEG=None, save_fn=None,
            iti = 0.4, soa = 0.3, jitter = 0.2):
    
    record_duration = np.float32(duration)
    markernames = ['left', 'right', 'blue', 'red', 'key pressed']

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    # Show the instructions screen
    show_instructions(duration)

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "audio_visual", random_id, random_id, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)

    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()

    # Iterate through the events
    while True:
        # Chose between visual and audio
        if random.random() < 0.8:
            next_event_type = 'visual'
        else:
            next_event_type = 'audio'

        # --- Visual Stimulus - Update screen
        if next_event_type == 'visual':

            # Inter trial interval
            core.wait(iti + np.random.rand() * jitter)

            # Select colour 
            colour = random.randint(1, 2)
            if colour == 1:
                label = 'blue'
            else:
                label = 'red'

            # If new colour, update
            if label != current_colour: 
                # get the center point of the window
                center_point = Point(mywin.getWidth()/2, mywin.getHeight()/2)
                # create a circle with a radius of 50 and a red color
                circle = Circle(center_point, 50)
                circle.setFill(label)
                # draw the circle to the window
                circle.draw(mywin)
                mywin.flip()
                current_colour = label
                new = True
            else:
                new = False

            # Push sample of visual stimulus
            if eeg & new:
                timestamp = time()
                if eeg.backend == "muselsl":
                    marker = [markernames[label]]
                else:
                    marker = markernames[label]
                eeg.push_sample(marker=marker, timestamp=timestamp)


        # --- Audio Stimulus - Directional Command
        elif next_event_type == 'audio':

            # Inter trial interval
            core.wait(iti + np.random.rand() * jitter)
            direction = random.randint(1, 2)
            if direction == 1:
                label = 'right'
            else:
                label = 'left'

            key = perform_audio_stimulus(label)

            # Push sample of audio stimulus
            if eeg:
                timestamp = time()
                if eeg.backend == "muselsl":
                    marker = [markernames[label]]
                else:
                    marker = markernames[label]
                eeg.push_sample(marker=marker, timestamp=timestamp)
            
            # Wait for key input
            event.waitKeys(keyList=key)

            # Push sample of pressed key
            if eeg:
                timestamp = time()
                if eeg.backend == "muselsl":
                    marker = [markernames['key pressed']]
                else:
                    marker = markernames['key pressed']
                eeg.push_sample(marker=marker, timestamp=timestamp)


        # offset
        core.wait(soa)
        mywin.flip()

        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


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

    mywin.mouseVisible = True
    mywin.close()

def perform_audio_stimulus(command):
    # Direction
    if command =='right':
        key='right arrow'
        playsound.playsound("right_audio.wav", True)
    else:
        key='left arrow'
        playsound.playsound("left_audio.wav", True)
    return key
