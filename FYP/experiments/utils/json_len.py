import os
import json

json_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'data_json')


# Get the list of JSON files in the folder
json_files = [file for file in os.listdir(json_folder) if file.endswith('.json')]

if len(json_files) == 0:
    print("No JSON files found in the folder.")
else:
    max_length = float('-inf')
    longest_file = None

    min_length = float('inf')
    shortest_file = None
    lengths = []
    # Iterate through the JSON files
    for file in json_files:
        file_path = os.path.join(json_folder, file)
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
            data_length = len(json_data)
            lengths.append(data_length)
            if data_length > max_length:
                max_length = data_length
                longest_file = file
            if data_length < min_length:
                min_length = data_length
                shortest_file = file

    if shortest_file:
        print(f"The JSON file with the minimum length is: {shortest_file}")
        print(f"Length: {min_length}")
    else:
        print("No JSON files found in the folder.")
    if longest_file:
        print(f"The JSON file with the maximum length is: {longest_file}")
        print(f"Length: {max_length}")
    else:
        print("No JSON files found in the folder.")
    print("Lengths are:", lengths)
