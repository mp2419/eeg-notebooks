import mne
import os
from eeg_analysis_lib import create_raw_object

#TODO https://mne.tools/0.12/auto_tutorials/plot_artifacts_correction_ica.html#tut-artifacts-correct-ica

folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered')
json_folder = os.path.join(os.path.expanduser('~/'),'Desktop', 'FYP', 'code_env', 'eeg-notebooks','FYP', 'data_ordered', 'data_json')

raw_folder = os.path.join(folder, "mne_raw")
file = os.path.join(raw_folder, "AudioVisual_04_1.fif")
# Load raw data
raw = mne.io.read_raw_fif(file, preload=True)

# Set up ICA parameters
n_components = 4  # Number of components for ICA decomposition
method = 'fastica'  # ICA algorithm to use
decim = 3  # Decimation factor for ICA (reduces computational burden)

# Define EOG channel(s) (can be a list if multiple EOG channels)
eog_channels = ['EOG1', 'EOG2']

# Apply ICA for artifact removal
ica = mne.preprocessing.ICA(n_components=n_components, method=method)
ica.fit(raw, decim=decim)

# Identify eyeblink-related components
eog_epochs = mne.preprocessing.create_eog_epochs(raw)
eog_indices, eog_scores = ica.find_bads_eog(eog_epochs)

# Exclude eyeblink-related components
ica.exclude = eog_indices
file_clean = os.path.join(raw_folder, "AudioVisual_04_1_raw_clean.fif")
# Apply inverse ICA transformation to obtain clean data
raw_clean = ica.apply(raw.copy(), exclude=ica.exclude)

# Save the cleaned raw data to a new file
raw_clean.save(file_clean, overwrite=True)
