import neurokit2 as nk
import numpy as np
from . import visualization

def detect_r_wave_peaks(ecg_signal, sampling_rate):
    """
    Detect R-wave peaks in ECG signals using the Pan-Tompkins algorithm.

    Parameters:
        ecg_signal (array): ECG signal data.
        sampling_rate (int): Sampling rate of the ECG signal in Hz.

    Returns:
        array: Indices of detected R-wave peaks.
    """
    try:
        signals, info = nk.ecg_peaks(ecg_signal, sampling_rate, correct_artifacts=True, show=False)
        return info['ECG_R_Peaks']
    except Exception as e:
        print(f"Error detecting R-wave peaks: {e}")
        return []


def extract_heps(clean_eeg_signal, clean_ecg_signal, r_peak_indices, pre_window_ms, post_window_ms, sampling_rate, show_plots=False):
    """
    Extract and compute Heart-Evoked Potentials (HEP) and corresponding ECG segments.

    Parameters:
        clean_eeg_signal (array): Clean EEG signal data.
        clean_ecg_signal (array): Clean ECG signal data.
        r_peak_indices (array): Indices of detected R-wave peaks.
        pre_window_ms (int): Time window before the R-peak (ms).
        post_window_ms (int): Time window after the R-peak (ms).
        sampling_rate (int): Sampling rate of the signals (Hz).
        show_plots (bool): Whether to plot the windows and signals.

    Returns:
        tuple: (HEP, HEP_ECG), representing average EEG and ECG segments.
    """
    try:
        pre_window_samples = int((pre_window_ms / 1000) * sampling_rate)
        post_window_samples = int((post_window_ms / 1000) * sampling_rate)
        eeg_segments, ecg_segments = [], []

        for i in range(1, len(r_peak_indices) - 1):
            start_idx, end_idx = r_peak_indices[i] - pre_window_samples, r_peak_indices[i] + post_window_samples

            if 0 <= start_idx < len(clean_eeg_signal) and 0 < end_idx < len(clean_eeg_signal) and start_idx > r_peak_indices[i - 1] and end_idx < r_peak_indices[i + 1]:
                baseline_eeg = np.mean(clean_eeg_signal[start_idx:r_peak_indices[i]])
                baseline_ecg = np.mean(clean_ecg_signal[start_idx:r_peak_indices[i]])
                eeg_segments.append(clean_eeg_signal[start_idx:end_idx] - baseline_eeg)
                ecg_segments.append(clean_ecg_signal[start_idx:end_idx] - baseline_ecg)

        hep = np.mean(eeg_segments, axis=0) if eeg_segments else None
        avg_pqrs = np.mean(ecg_segments, axis=0) if ecg_segments else None

        if show_plots:
            visualization.plot_ecg_eeg_with_hep(clean_ecg_signal, clean_eeg_signal, r_peak_indices, pre_window_ms, post_window_ms, sampling_rate)

        return hep, avg_pqrs
    except Exception as e:
        print(f"Error extracting Heart-Evoked Potentials: {e}")
        return None, None