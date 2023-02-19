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


mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
text = visual.TextStim(win=mywin, text="Starting the test...", color=[-1, -1, -1])
text.draw()
mywin.flip()
current_colour = None
i = 0
time.sleep(2)
# Iterate through the events
while True:
    time.sleep(2)

    next_event_type = 'visual'

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
            circle = Circle(mywin, radius=7, fillColor=label, lineColor=None)
            circle.pos = (1,1)
            circle.draw()
            mywin.flip()
            current_colour = label
            new = True
        else:
            new = False

        i = i+1
        print(label, new)
    if i > 10:
        break

mywin.close()

# #  win = visual.Window(monitor=monitor)
# from psychopy import core, visual, monitors
# import psychopy.visual.circle


# class Circle(psychopy.visual.circle.Circle):
#     def __init__(self, win, lineColor='black', fillColor='red'):
#         super(Circle, self).__init__(
#             win=win, lineColor=lineColor, fillColor=fillColor, units='deg',
#             pos=(1,1), radius=7)
# win = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True, color='black')
# colors = ('red', 'green', 'blue')
# circles = [Circle(win=win, fillColor=color) for color in colors]

# for circle in circles:
#     circle.draw()
#     win.flip()
#     core.wait(1)

# core.quit()
