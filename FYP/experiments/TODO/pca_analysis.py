import mne
from mne.decoding import Vectorizer
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt


raw = "C:\\Users\\matil\\Desktop\\FYP\\code_env\\eeg-notebooks\\FYP\\data_ordered\\mne_raw\\AudioVisual_04_1.fif"
# Load the EEG data into an MNE Epochs object or Raw object
epochs = mne.read_epochs(raw)
marker_mapping = {"blue": 1, "red": 2, "right": 3, "left": 4, "right arrow": 5, "left arrow": 6}
events, event_id= mne.events_from_annotations(raw, event_id=marker_mapping)
filtered_raw = raw.copy().filter(l_freq=0.1, h_freq=40, fir_design='firwin')
duration = 30.0  # Duration of each epoch (seconds)
epochs = mne.Epochs(filtered_raw, events, event_id=event_id, tmin=-0.3, tmax=0.7, baseline=None, preload=True, event_repeated='merge')
event_types = np.unique(events[:, -1])

# Apply Vectorizer to reshape the data into a 2D array
if isinstance(epochs, mne.Epochs):
    X = Vectorizer().fit_transform(epochs.get_data())
else:
    X = Vectorizer().fit_transform(raw.get_data())

# Perform PCA on the data
n_components = 3  # Number of components to keep
pca = PCA(n_components=n_components)
X_pca = pca.fit_transform(X)

# Access the explained variance ratio
explained_var_ratio = pca.explained_variance_ratio_

# Visualize the explained variance ratio
plt.plot(np.arange(1, n_components + 1), np.cumsum(explained_var_ratio))
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance Ratio')
plt.show()
