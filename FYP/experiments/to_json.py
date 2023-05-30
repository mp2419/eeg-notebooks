import csv, os
import json
from datetime import datetime

def csv_to_json(csv_file, json_file):
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        header = next(reader) #leave
        first_row = next(reader)
        data = []
        initial_timestamp = float(first_row[0])

        for row in reader:
            timestamp = float(row[0])
            time_diff = (timestamp - initial_timestamp)
            if time_diff >= 30:
                data.append([time_diff] + row[1:])
        
    json_data = json.dumps(data, indent=4)

    with open(json_file, 'w') as file:
        file.write(json_data)


csv_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
epochs_folder = os.path.join(csv_folder, "data_json")
os.makedirs(epochs_folder, exist_ok=True)

csv_files = [os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'AudioVisual_01_1.csv' )]
#csv_files = [file for file in os.listdir(csv_folder) if file.endswith(".csv")]

for csv_file in csv_files:
    file_path = os.path.join(csv_folder, csv_file)
    new_file_path = os.path.join(epochs_folder, 'AudioVisual_01_1.json' )
    csv_to_json(file_path, new_file_path)
