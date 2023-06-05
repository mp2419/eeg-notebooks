import mne
from mne.decoding import Vectorizer
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt

# Load the EEG data into an MNE Epochs object or Raw object
epochs = mne.read_epochs('your_epochs_file-epo.fif')
# or
# raw = mne.io.read_raw_fif('your_raw_file.fif')

# Apply Vectorizer to reshape the data into a 2D array
if isinstance(epochs, mne.Epochs):
    X = Vectorizer().fit_transform(epochs.get_data())
else:
    X = Vectorizer().fit_transform(raw.get_data())

# Perform PCA on the data
n_components = 10  # Number of components to keep
pca = PCA(n_components=n_components)
X_pca = pca.fit_transform(X)

# Access the explained variance ratio
explained_var_ratio = pca.explained_variance_ratio_

# Visualize the explained variance ratio
plt.plot(np.arange(1, n_components + 1), np.cumsum(explained_var_ratio))
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Explained Variance Ratio')
plt.show()
