import os
from eeg_analysis_lib import create_raw_object

folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
json_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'data_json')

raw_folder = os.path.join(folder, "mne_raw")
os.makedirs(raw_folder, exist_ok=True)
json_files = [file for file in os.listdir(json_folder) if file.endswith(".json")]

for json_file in ["ShapeVisual_12_1.json","ShapeVisual_12_2.json","ShapeVisual_14_1.json","ShapeVisual_14_2.json","ShapeVisual_15_1.json","ShapeVisual_15_2.json","ShapeVisual_17_1.json","ShapeVisual_17_2.json"]:
    file_path = os.path.join(json_folder, json_file)
    new_file_path = os.path.join(raw_folder, json_file.replace(".json", ".fif"))
    raw = create_raw_object(file_path)
    raw_filtered = raw.copy().filter(0.1, 40, fir_design='firwin')
    raw_filtered.save(new_file_path, overwrite=True)
    print(new_file_path)
print("All raw object converted")