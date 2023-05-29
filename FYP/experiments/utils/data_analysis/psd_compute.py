import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def psd_eeg(file_path):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)

    # Extract the time values (first column) and data (other columns)
    time = df.iloc[:, 0].values
    data = df.iloc[:, 1:].values

    # Compute the PSD for each column of the data
    fs = 1 / (time[1] - time[0])  # Sampling frequency
    n = len(time)  # Number of samples
    frequencies = np.fft.fftfreq(n, 1 / fs)
    psd = np.zeros((len(frequencies), data.shape[1]))

    for i in range(data.shape[1]):
        fft = np.fft.fft(data[:, i])
        psd[:, i] = np.abs(fft) ** 2 / (n * fs)

    # Plot the PSD for each column of the data
    for i in range(data.shape[1]):
        plt.plot(frequencies, psd[:, i], label=f"Column {i+1}")

    plt.xlabel('Frequency')
    plt.ylabel('Power Spectral Density')
    plt.legend()
    plt.show()

