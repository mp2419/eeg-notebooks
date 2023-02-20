import sys
sys.path.append("..\\")
# print(sys.path)
import warnings
import os
warnings.filterwarnings('ignore')
import audio_visual_lib as audiovisual

# Define some variables
experiment = "audio_visual"
# subject_id = "1"
# session_nb = 1
#TODO update name generation
data_path = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data', 'AudioVisual')


file_name_raw = os.path.join(data_path, '3_recording.csv')
file_name_marked = os.path.join(data_path, '3_markers.csv')
record_duration = 100


audiovisual.run_experiment(duration = record_duration, file_name_raw = file_name_raw, file_name_marked = file_name_marked)

#TODO synch data finish function
