from time import sleep
from threading import Thread
import sys
import time
import logging
from time import sleep
from multiprocessing import Process

import numpy as np
import pandas as pd

from brainflow.board_shim import BoardShim, BoardIds, BrainFlowInputParams
from muselsl import stream, list_muses, record, constants as mlsl_cnsts
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_byprop

from eegnb.devices.utils import (
    get_openbci_usb,
    create_stim_array,
    SAMPLE_FREQS,
    EEG_INDICES,
    EEG_CHANNELS,
)


class MuseThread(Thread):

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def get_data(self):
        return self.count

    # second thread
    def run(self):
        # Connect to Muse device
        muses = list_muses()
        if not muses:
            print('No Muses found')
            exit()
        stream_name = muses[0]['name']
        print(f'Connecting to {stream_name}')
        stream_inlet = stream(stream_name)
        
        while True:
            # block for a moment
            sleep(1)
            self.count += 1
            if self.count > 11:
                break


muse_thread = MuseThread()
muse_thread.start()

# main thread
while True:
    print(muse_thread.get_data())
    sleep(1)
    if muse_thread.get_data() > 10:
        break

# pause main thread adn wait for the second thread to finish
muse_thread.join()