file_list = [
    file for file in os.listdir(folder_path)
    if file.endswith("_1.json")
]
 vs
 file_list = [
    file for file in os.listdir(folder_path)
    if file.endswith("_2.json")
]

#ERP

#PSD

#ICA

#------------------------

import mne
import numpy as np
import matplotlib.pyplot as plt

# Load the epochs data
epochs = mne.read_epochs('epochs_data.fif')

# Define the conditions and their corresponding event IDs
conditions = {'Condition1': 1, 'Condition2': 2, 'Condition3': 3}

# Create epochs for each condition
condition_epochs = {}
for condition, event_id in conditions.items():
    condition_epochs[condition] = epochs[event_id]

# Calculate the average ERP for each condition
average_erps = {}
for condition, condition_epochs in condition_epochs.items():
    average_erps[condition] = condition_epochs.average()

# Plot the ERPs for each condition
for condition, average_erp in average_erps.items():
    average_erp.plot_joint(title=condition)

# Compare the ERPs between conditions
# Perform statistical tests, such as t-tests or ANOVA, to compare the ERPs between conditions
# Extract relevant ERP features or time windows for further analysis

# Plot the trend between conditions
# Visualize the trend between conditions using appropriate visualization methods (e.g., line plot, bar plot, etc.)

# Additional analysis or post-processing steps can be performed based on specific research objectives

plt.show()
