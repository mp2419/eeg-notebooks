# ----------- ANOVA across participants for each electrode 
import glob
import os
import pandas as pd
from scipy.stats import f_oneway

# Define the directory path where the CSV files are located
data_path = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')

# Get the list of files in the folder
file_list = os.listdir(data_path)

# Filter for CSV files
csv_files = [file_name for file_name in file_list if file_name.endswith('.csv')]

print(csv_files)
# Load the data from the CSV files
groups = []
electrodes = ['TP9','AF7','AF8','TP10']

for file_path in csv_files:
    name = os.path.join(data_path,file_path)
    print(name)
    df = pd.read_csv(name)
    data = []
    print(df.shape)
    for i in electrodes:  # Assuming electrode columns are named 'electrode1', 'electrode2', 'electrode3', 'electrode4'
        data.append(df[1:][i])
    groups.append(data)

# Perform the ANOVA test
# f_value, p_value = f_oneway(*groups)

# # Print the results
# print("ANOVA Results:")
# print("F-value:", f_value)
# print("p-value:", p_value)
print(groups)

#Perform the ANOVA test
f_value, p_value = f_oneway(*groups)

# Print the results
print("ANOVA Results:")
print("F-value:", f_value)
print("p-value:", p_value)
