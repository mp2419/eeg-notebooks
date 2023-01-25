"""
Generate Visual
=============

Face vs. house paradigm stimulus presentation for evoking present.

"""

from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

from time import time
from optparse import OptionParser
import os
from glob import glob
import random

import numpy as np
from pandas import DataFrame, read_csv
from psychopy import visual, core, event
from pylsl import StreamInfo, StreamOutlet

from eegnb import stimuli, experiments

# stim_dir = os.path.split(stimuli.__file__)[0]
# exp_dir = os.path.split(experiments.__file__)[0]

# fixed stim order list file
#fso_list_file = os.path.join(exp_dir, "visual_n170", "n170_fixedstimorder_list.csv")


def present(duration=120):

    # Create markers stream outlet
    # info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
    info = StreamInfo("Visual_Markers", "Markers", 1, 0, "int32", "source_visual2000")
    outlet = StreamOutlet(info)

    # markernames = [1, 2]
    start = time()

    # Set up trial parameters
    # n_trials = 2010
    iti = 0.8
    soa = 0.2
    jitter = 0.2
    record_duration = np.float32(duration)
    red = (255, 0, 0)
    blue = (0, 0, 255)

    #-----------pyshopy game 

    win = visual.Window([1600, 900], monitor="testMonitor", units="deg", winType="pygame", fullscr=True)
    running = True
    
    prev_color = red

    while running:
        running = True
        # trialnum, filename, facehouse, girlboy = trial.values
        # filename = os.path.join(stim_dir, filename)
        new_blue = 1
        # Intertrial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select circle to display
        color = random.choice([red, blue])
        circle = visual.Circle(win=win,units="pix",radius=150,fillColor=color,lineColor=[-1, -1, -1])
        circle.draw()

        if prev_color == red & color == blue:
            # Send marker
            timestamp = time()
            # outlet.push_sample([markernames[label]], timestamp)
            outlet.push_sample([new_blue], timestamp)

        prev_color = color

        win.flip()

        # offset
        core.wait(soa)
        win.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            running=False
        event.clearEvents()

    # Cleanup
    win.close()


def main():
    parser = OptionParser()

    parser.add_option(
        "-d",
        "--duration",
        dest="duration",
        type="int",
        default=120,
        help="duration of the recording in seconds.",
    )

    (options, args) = parser.parse_args()
    present(options.duration)


if __name__ == "__main__":
    main()
