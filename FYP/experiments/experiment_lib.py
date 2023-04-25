import time, serial, random, playsound
import numpy as np
import csv, os
import threading
from pylsl import StreamInlet, resolve_byprop 
from psychopy import visual, core, event
from psychopy.visual.circle import Circle
import utils.data_analysis.synch_data as synch
import utils.data_analysis.trim_data as trim

__title__ = "MultiSensory"

# ----------- run trial or experiement ----------

def run_experiement(type, trials, duration, file_name_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\test\\data_muse_raw.csv',
    file_name_marked = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\test\\data_muse_marked.csv', file_name_synched ='C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\test\\data_muse_synched.csv'):
    
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    show_instructions(duration, mywin)
    for trial in range(trials):
        
        print("Experiment Started at time ", time.time())

        # - Start the recording thread
        recording_thread = threading.Thread(target=record_data, args=(duration+5, file_name_raw))
        recording_thread.start()

        # time.sleep(5)
        blue_n = present_experiment(type, trial, duration, file_name_marked, iti = 0.4, soa = 0.3, jitter = 0.2, mywin = mywin)

        # # - Start the marker insertion thread
        # # stimulus_thread = threading.Thread(target=present_experiment, args=(duration, file_name_marked))
        # # stimulus_thread.start()

        # - Wait for both threads to finish
        recording_thread.join()
        # # stimulus_thread.join()
        blue_n_reported = return_blue_number(mywin)
        print("Experiment Completed at time ", time.time())
        print("Number of blue circles reported is: ", blue_n_reported, "Number of actual blue circles is: ", blue_n )

    mywin.close()
    synch.merge_data(filename_raw = file_name_raw, filename_marked = file_name_marked, filename_union = file_name_synched)

def run_trial(type, duration, file_name_raw = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\test\\data_muse_raw.csv',
file_name_marked = 'C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\test\\data_muse_marked.csv', file_name_synched ='C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data\\test\\data_muse_synched.csv'):
    
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    show_instructions(duration, mywin)
    
    print("Experiment Started at time ", time.time())
    # - Start the recording thread
    recording_thread = threading.Thread(target=record_data, args=(duration+5,file_name_raw))
    recording_thread.start()
    # time.sleep(5)
    blue_n = present_experiment(type, 1, duration, file_name_marked, iti = 0.4, soa = 0.3, jitter = 0.2, mywin = mywin)

    # # - Start the marker insertion thread
    # # stimulus_thread = threading.Thread(target=present_experiment, args=(duration, file_name_marked))
    # # stimulus_thread.start()

    # - Wait for both threads to finish
    recording_thread.join()
    # # stimulus_thread.join()
    return_blue_number(mywin, blue_n, file_name_marked)
    print("Experiment Completed at time ", time.time())
    
    
    mywin.close()
    synch.merge_data(filename_raw = file_name_raw, filename_marked = file_name_marked, filename_union = file_name_synched)

# ------------ core exmperiement ----------------

def present_experiment(type, trial, duration, file_name,  mywin,  iti = 0.7, soa = 0.3, jitter = 0.2):
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
        exit = False
        key = None

        time.sleep(2)
        writer.writerow([time.time(), 'start'])

        # Iterate through the events
        while True:
            # Inter trial interval
            core.wait(iti + np.random.rand() * jitter)

            # Chose between visual and tactile
            if random.random() < 0.8:
                next_event_type = 'visual'
            else:
                next_event_type = 'direction'

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

            # --- Haptic/Auditory Stimulus - Directional Command
            elif next_event_type == 'direction':

                direction = random.randint(1, 2)
                if direction == 1:
                    label = 'right'
                else:
                    label = 'left'

                key = perform_stimulus(label, type)

                # Push sample of audio stimulus
                timestamp = time.time()
                writer.writerow([timestamp, label])

                #old
                # Wait for key input
                #event.waitKeys(keyList=key)

            keys = event.getKeys(keyList=None, modifiers=False, timeStamped=True)
            #print(keys)
            if keys != []:
                for i in range(len(keys)):
                    current_key = keys[i]
                    #print(current_key)
                    print(current_key[0])
                    if current_key[0] == 'left':
                        print('arrow')
                        writer.writerow([time.time(), 'left arrow'])                
                    elif current_key[0] == 'right':
                        print('arrow')
                        writer.writerow([time.time(), 'right arrow'])
                    elif current_key[0] == 'escape':
                        exit = True
                        print("exit")


            # offset
            core.wait(soa)
            #mywin.flip()

            if ((time.time() - start_time) > duration) | (exit == True):
                writer.writerow([time.time(), 'end'])
                print("Stopped writing data at time ", time.time())
                break

            event.clearEvents()

        text = visual.TextStim(win=mywin, text="Trial completed", color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        # mywin.close()

    return blue_n

# ------------ auxiliary functions --------------

# --- eeg

def record_data(duration, file_name):

    # Search for active LSL stream
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    #TODO if no eeg stop experiment
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

# --- stimulation

def perform_stimulus(command, type):
    # Direction
    if command =='right':
        key='right arrow'
    else:
        key='left arrow'

    if type == "vibro":  
        vibrate(command)
    elif type == "shape":
        change_shape(command)
    elif type == "audio":
        if command =='right':
            playsound.playsound("FYP\\experiments\\audio_visualoddball\\audio_data\\right_only_beep.wav", True)
        else:
            playsound.playsound("FYP\\experiments\\audio_visualoddball\\audio_data\\left_only_beep.wav", True)

    return key

def vibrate(direction):
    # - connect to Arduino -
    ser = serial.Serial('COM9', 9600,  timeout=10)
    start_time = time.time()
    print("Vibrate ", direction)

    # - RUN -
    while time.time() - start_time < 2:
        if direction == "left":
            ser.write(b'9\n')
        elif direction == "right":
            ser.write(b'5\n')
        # bytesToRead = ser.inWaiting()
        # data=ser.read(bytesToRead)
        # print(data, " Vibrate")
        time.sleep(0.5)

    # - STOP -
    while time.time() - (start_time) < 3:
        ser.write(b'1\n')
        # bytesToRead = ser.inWaiting()
        # ser.read(bytesToRead)
        # print(data, " Done")
    ser.close()

def change_shape(direction):
    # - connect to Arduino -
    ser = serial.Serial('COM9', 9600,  timeout=10)
    start_time = time.time()
    print("Move ", direction)

    start_time = time.time()
    while time.time() - start_time < 2:
        if direction == "left":
            ser.write(b'1\n')
        elif direction == "right":
            ser.write(b'2\n')

        # bytesToRead = ser.inWaiting()
        # data=ser.read(bytesToRead)
        # print(data, " Translation")

    # - STOP -
    while time.time() - start_time < 4:
        ser.write(b'0\n')

        bytesToRead = ser.inWaiting()
        ser.read(bytesToRead)
        #print(data, " Done")
    ser.close()

# --- visual

def return_blue_number(mywin, blue_n, file_name_marked):

    # graphics
     # mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    mywin.mouseVisible = False

    key_number = ''

    while True:
        instruction_text = """
        Well Done! 

        Please report the number of BLUE circles you have counted and press SPACE.

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
        if keys[0] == 'backspace':  # check if the key pressed is delete
            key_number = ''  # 
    
    file = file_name_marked[:-11] + 'blue_circles.csv'

    with open(file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['True', 'Reported'])
        writer.writerow([blue_n, key_number])

    print("Number of blue circles reported is: ", key_number, "Number of actual blue circles is: ", blue_n )

def show_instructions(duration,  mywin ):

    instruction_text = """
    Welcome to the Multisensory experiment! 

    1. You will see circles of different colours, please COUNT the BLUE circles.

    2. You will perceive directional indications, please PRESS the LEFT or RIGHT arrow key accordingly.
     
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
