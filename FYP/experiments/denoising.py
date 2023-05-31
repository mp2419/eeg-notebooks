import matplotlib.pyplot as plt
import mne, os
from mne.preprocessing import ICA
import json_to_mne

json_file_path = os.path.join(os.path.expanduser('~/'), 'Desktop', 'FYP', 'code_env', 'eeg-notebooks', 'FYP', 'data_ordered', 'data_json', 'AudioVisual_01_1.json')

raw = json_to_mne.create_raw_object(json_file_path)
# count = json_to_mne.return_eventcount(raw_data)

filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')

n_components = min(len(filtered_raw.info['ch_names']), 20)  # Maximum of 20 components or number of channels
ica = ICA(n_components=n_components, random_state=0)  # Adjust the number of components as needed
ica.fit(filtered_raw)

# Extract the ICAs
ica_sources = ica.get_sources(filtered_raw)

# Reconstruct the data using the 10th most relevant ICA
ica_reconstructed = ica_sources.copy()
ica_reconstructed._data = ica_reconstructed._data[:2]  # Select the 10th ICA

#--- Plot 
# Plot raw PSD
raw.plot_psd()
plt.title('Raw PSD')
plt.show(block=False)

# Plot filtered PSD
filtered_raw.plot_psd()
plt.title('Filtered PSD')
plt.show(block=False)

# Plot ICA fit
ica.plot_components(picks=range(n_components))
plt.title('ICA Fit')
plt.show(block=False)

# Plot reconstructed data
ica_reconstructed.plot()
plt.title('Reconstructed Data (ICA 2)')
plt.show(block=False)
