import os
import csv
import json
from datetime import datetime, timedelta

def extract_epoch(file_path, new_file_path):
    with open(file_path, "r") as file:
        csv_reader = csv.reader(file)

        # Read the header row
        header = next(csv_reader)

        # Get the initial timestamp
        first_row = next(csv_reader)
        initial_timestamp = datetime.fromtimestamp(float(first_row[0]))

        # Reset the file pointer to the beginning of the file
        file.seek(0)

        # Skip the header row
        next(csv_reader)

        # Initialize the dictionary for storing epoch data
        epoch_data = {}

        # Convert timestamp and extract epochs
        prev_time = None
        first_epoch = True
        for row in csv_reader:
            timestamp = datetime.fromtimestamp(float(row[0]))

            # Skip the first epoch
            if first_epoch:
                prev_time = timestamp
                first_epoch = False
                continue

            # Check if any column value is 'n/a' except Marker_timestamp
            if 'n/a' in row[:-2]:
                continue

            # Calculate the difference between timestamps
            time_diff = (timestamp - initial_timestamp).total_seconds()

            # Check if the epoch is 30 seconds or more
            if time_diff >= 30:
                # Calculate the epoch index
                epoch = int(time_diff // 30)

                # Update the timestamp as relative time
                relative_time = (timestamp - prev_time).total_seconds()

                # Store the data in the dictionary
                epoch_matrix = []
                for value in row[:-2]:
                    epoch_matrix.append(float(value))
                
                # Preserve the Marker column as a string
                epoch_matrix.append(str(row[-2]))
                
                # Preserve the Marker_timestamp column as a string
                epoch_matrix.append(str(row[-1]))

                epoch_data.setdefault(str(epoch), []).append(epoch_matrix)

                # Update the previous timestamp
                prev_time = timestamp

    # Write the epoch data to a JSON file
    with open(new_file_path, "w") as json_file:
        json.dump(epoch_data, json_file)

    print(f"Epochs file '{new_file_path}' created successfully.")

#--------------

# csv_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
# epochs_folder = os.path.join(csv_folder, "epochs")
# os.makedirs(epochs_folder, exist_ok=True)
# csv_files = [file for file in os.listdir(csv_folder) if file.endswith(".csv")]

# for csv_file in csv_files:
#     file_path = os.path.join(csv_folder, csv_file)
#     new_file_path = os.path.join(epochs_folder, csv_file.replace(".csv", ".json"))
#     extract_epoch(csv_file, new_file_path)
# print("Epochs files created successfully in the 'epochs' folder.")

#----------------all files

import os
import basic_analysis_lib
import eeg_analysis_lib as analysis

csv_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
epochs_folder = os.path.join(csv_folder, "epochs")
os.makedirs(epochs_folder, exist_ok=True)
csv_files = [file for file in os.listdir(csv_folder) if file.endswith(".csv")]

for csv_file in csv_files:
    file_path = os.path.join(csv_folder, csv_file)
    new_file_path = os.path.join(epochs_folder, csv_file.replace(".csv", ".json"))
    analysis.extract_epoch(file_path, new_file_path)
print("Epochs files created successfully in the 'epochs' folder.")