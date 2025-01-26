import mne
import pandas as pd
import numpy as np
from scipy.signal import resample, medfilt, detrend


def apply_bandpass_notch_filter(signal_matrix, sampling_rate, notch_freq=None, low_cutoff=None, high_cutoff=None):
    """
    Apply a notch filter (to remove powerline noise) and a bandpass filter (to retain relevant frequency components)
    to a multi-subject signal matrix.

    Parameters:
        signal_matrix: 2D NumPy array (subjects × time points), where each row is a signal from a subject.
        sampling_rate: int, the sampling rate of the signal in Hz.
        notch_freq: float, frequency to apply the notch filter (e.g., 60 Hz, optional).
        low_cutoff: float, low cutoff frequency for the bandpass filter (optional).
        high_cutoff: float, high cutoff frequency for the bandpass filter (optional).

    Returns:
        2D NumPy array of filtered signals.
    """
    try:
        if isinstance(signal_matrix, pd.DataFrame):
            signal_matrix = signal_matrix.to_numpy()
        signal_matrix = signal_matrix.astype(float)

        if notch_freq:
            signal_matrix = mne.filter.notch_filter(signal_matrix, sampling_rate, freqs=notch_freq, verbose=False)
        if low_cutoff and high_cutoff:
            signal_matrix = mne.filter.filter_data(signal_matrix, sampling_rate, l_freq=low_cutoff, h_freq=high_cutoff, verbose=False)
        
        return signal_matrix
    except Exception as e:
        print(f"Error in filtering: {e}")
        return signal_matrix


def resample_signal(signal_matrix, original_rate, target_rate):
    """
    Resample a multi-subject signal matrix to a new sampling rate.

    Parameters:
        signal_matrix: 2D NumPy array (subjects × time points), where each row is a signal from a subject.
        original_rate: int, original sampling rate.
        target_rate: int, desired sampling rate.

    Returns:
        2D NumPy array of resampled signals.
    """
    try:
        num_subjects, num_samples = signal_matrix.shape
        new_sample_count = int(num_samples * target_rate / original_rate)
        resampled_matrix = np.array([resample(signal_matrix[i, :], new_sample_count) for i in range(num_subjects)])
        return resampled_matrix
    except Exception as e:
        print(f"Error in resampling: {e}")
        return signal_matrix


def preprocess_ecg_eeg(ecg_matrix, eeg_matrix, fs, target_fs=None, notch_freq=None, low_cutoff=None, high_cutoff=None):
    """
    Preprocess ECG and EEG signals by resampling, filtering, and artifact removal, ensuring both have the same duration.

    Parameters:
        ecg_matrix: 2D NumPy array (subjects × time points), ECG signals.
        eeg_matrix: 2D NumPy array (subjects × time points), EEG signals.
        fs: int, original sampling rate.
        target_fs: int, desired resampling rate (optional).
        notch_freq: float, frequency for notch filtering (e.g., 50 or 60 Hz, optional).
        low_cutoff: float, low cutoff frequency for bandpass filter (optional).
        high_cutoff: float, high cutoff frequency for bandpass filter (optional).

    Returns:
        Tuple of 2D NumPy arrays: (Filtered ECG, Filtered EEG)
    """
    try:
        # Resample if needed
        if target_fs:
            ecg_matrix = resample_signal(ecg_matrix, fs, target_fs)
            eeg_matrix = resample_signal(eeg_matrix, fs, target_fs)
            fs = target_fs

        if ecg_matrix.shape[1] != eeg_matrix.shape[1]:
            print("Error: ECG and EEG must have the same duration after resampling.")
            return None

        # Apply filters if provided
        if notch_freq or (low_cutoff and high_cutoff):
            filtered_ecg = apply_bandpass_notch_filter(ecg_matrix, fs, notch_freq, low_cutoff, high_cutoff)
            filtered_eeg = apply_bandpass_notch_filter(eeg_matrix, fs, notch_freq, low_cutoff, high_cutoff)

            # Apply median filter for baseline correction
            baseline_eeg = medfilt(filtered_eeg, kernel_size=501)
            filtered_eeg = filtered_eeg - baseline_eeg

            # Remove linear trends
            filtered_ecg = detrend(filtered_ecg)
            return filtered_ecg, filtered_eeg
        else:
            return ecg_matrix, eeg_matrix
    except Exception as e:
        print(f"Error in preprocessing: {e}")
        return ecg_matrix, eeg_matrix