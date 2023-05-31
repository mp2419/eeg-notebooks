import mne, os
from mne.preprocessing import ICA
import matplotlib.pyplot as plt
import json_to_mne
import numpy as np

json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')

raw = json_to_mne.create_raw_object(json_file_path)

# Step 2: Bandpass filter the EEG data (if not already done)
filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')

# Step 3: Run ICA to identify eyeblink-related components
n_components = 4  # Number of ICA components
ica = ICA(n_components=n_components, random_state=0)  # Adjust the number of components as needed
ica.fit(filtered_raw)

# Step 4: Identify eyeblink-related components
eog_inds, eog_scores = ica.find_bads_eog(filtered_raw, ch_name='TP9')

# Step 5: Plot and inspect the identified eyeblink components
picks=np.array(eog_inds).tolist()
ica.plot_components()

# Step 6: Remove eyeblink-related components from the data
ica.exclude = eog_inds
cleaned_raw = filtered_raw.copy()
ica.apply(cleaned_raw)

#--------- clean vs raw signal per component
# Applying ICA to Raw instance
#     Transforming to ICA space (4 components)
#     Zeroing out 1 ICA component
#     Projecting back using 4 PCA components

ica.plot_overlay(filtered_raw, exclude=[0], picks="eeg")
ica.plot_overlay(filtered_raw, exclude=[1], picks="eeg")
ica.plot_overlay(filtered_raw, exclude=[2], picks="eeg")
ica.plot_overlay(filtered_raw, exclude=[3], picks="eeg")

#------- Plot the raw and cleaned data in time

# raw.plot()
# plt.title('Raw Data')
# plt.show()

# cleaned_raw.plot()
# plt.title('Cleaned Data')
# plt.show()

#----------diagnostic of each IC

ica.plot_properties(filtered_raw, picks=[0, 1, 2, 3])

