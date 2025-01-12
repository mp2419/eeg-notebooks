import sys
sys.path.append("..\\")
sys.path.append("C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP")
sys.path.append("C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\experiments")
#print(sys.path)
import warnings  
import os
warnings.filterwarnings('ignore')
import experiment_lib as experiment
import utils.data_analysis.synch_data as synch
import utils.data_analysis.trim_data as trim

# Parameters
type = "AudioVisual"
subject_id = "1"
session_n = "1"

data_path = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data', type, subject_id, session_n)

file_name_raw = os.path.join(data_path, 'eeg.csv')
file_name_marked = os.path.join(data_path, 'markers.csv')
file_name_synched = os.path.join(data_path, 'synched_data.csv')
record_duration = 300


experiment.run_trial(type= "audio", duration = record_duration, file_name_raw = file_name_raw, file_name_marked = file_name_marked, file_name_synched = file_name_synched)



