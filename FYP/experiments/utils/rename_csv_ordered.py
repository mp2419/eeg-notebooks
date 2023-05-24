import os

# Define the path to the folder
folder_path = 'FYP/data_ordered'

# Get the list of files in the folder
file_list = os.listdir(folder_path)

# Iterate through each file in the folder
for file_name in file_list:
    if file_name.startswith('AudioVisual') and file_name.endswith('.csv'):
        # Extract the number from the file name
        file_number = file_name[len('AudioVisual'):].split('.')[0]
        if len(file_number) == 3:
            folder_number = file_number[:2]
            file_number = file_number[2:]
        else:
            folder_number = file_number[:1]
            file_number = file_number[1:]
        
        # Create the new file name
        new_file_name = f'AudioVisual_{folder_number}_{file_number}.csv'
        
        # Create the full paths for the source and destination files
        source_path = os.path.join(folder_path, file_name)
        destination_path = os.path.join(folder_path, new_file_name)
        
        # Rename the file
        os.rename(source_path, destination_path)
        
        print(f"File '{file_name}' renamed to '{new_file_name}'.")
