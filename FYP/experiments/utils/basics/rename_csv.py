import os
import shutil

# Define the paths
source_parent_folder = 'FYP\data'
external_folder = 'FYP\data_ordered'

for experiement_type in [ "ShapeVisual", "VibroVisual"]:
    for sbj in range(9, 12):                  
        # Iterate through the folder names from "01" to "13"
        for session in range(2, 3):
            session = str(session)
            sbj = str(sbj).zfill(2)  # Pad with leading zeros if necessary
            
            # Create the full paths for the source and destination folders
            source_folder = os.path.join(source_parent_folder, experiement_type, sbj, session)
            destination_folder = external_folder
            
            file_name = 'synched_data.csv'
            # Get the new name for the file
            new_name = experiement_type + '_' +  sbj + '_' + session + '.csv'
            
            # Create the full paths for the source and destination files
            source_path = os.path.join(source_folder, file_name)
            destination_path = os.path.join(destination_folder, new_name)
            
            # Rename and move the file
            os.makedirs(destination_folder, exist_ok=True)  # Create the destination folder if it doesn't exist
            shutil.move(source_path, destination_path)
            
            print(f"File '{file_name}' renamed and moved to '{destination_path}'.")
