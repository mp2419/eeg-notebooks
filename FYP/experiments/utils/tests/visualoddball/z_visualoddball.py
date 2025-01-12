"""  eeg-notebooks/eegnb/experiments/visual_n170/n170.py """

from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

import os
from time import time
from glob import glob
from random import choice
from optparse import OptionParser
import random

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb.devices.eeg import EEG
from eegnb.stimuli import FACE_HOUSE
from eegnb.experiments import Experiment


class VisualOddball(Experiment.BaseExperiment):

    def __init__(self, duration=10, eeg: EEG=None, save_fn=None,
            n_trials = 2010, iti = 0.4, soa = 0.3, jitter = 0.2):

        # Set experiment name        
        exp_name = "Visual "
        # Calling the super class constructor to initialize the experiment variables
        super(VisualOddball, self).__init__(exp_name, duration, eeg, save_fn, n_trials, iti, soa, jitter)

    def load_stimulus(self):
        
        # Loading Images from the folder
        load_image = lambda fn: visual.ImageStim(win=self.window, image=fn)

        # Setting up images for the stimulus
        self.faces = list(map(load_image, glob(os.path.join(FACE_HOUSE, "faces", "*_3.jpg"))))
        self.houses = list(map(load_image, glob(os.path.join(FACE_HOUSE, "houses", "*.3.jpg"))))

        # Return the list of images as a stimulus object
        return [self.houses, self.faces]
        
    def present_stimulus(self, idx : int, trial):
        
        # Get the label of the trial
        label = self.trials["parameter"].iloc[idx]
        # Get the image to be presented
        image = choice(self.faces if label == 1 else self.houses)
        # Draw the image
        image.draw()

        # Pushing the sample to the EEG
        if self.eeg:
            timestamp = time()
            if self.eeg.backend == "muselsl":
                marker = [self.markernames[label]]
            else:
                marker = self.markernames[label]
            self.eeg.push_sample(marker=marker, timestamp=timestamp)
        
        self.window.flip()