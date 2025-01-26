import numpy as np
import matplotlib.pyplot as plt


def plot_ecg_eeg_with_hep(clean_ecg_signal, clean_eeg_signal, r_peak_indices, pre_window_ms, post_window_ms, sampling_rate):
    """
    Plot ECG and EEG signals, highlighting R-wave peak windows, along with Heart-Evoked Potential (HEP) and 
    average ECG around R-wave peaks, computed from the given data.

    Parameters:
        clean_ecg_signal (array): ECG signal data.
        clean_eeg_signal (array): EEG signal data.
        r_peak_indices (array): Indices of detected R-wave peaks.
        pre_window_ms (int): Time window before the R-peak (ms).
        post_window_ms (int): Time window after the R-peak (ms).
        sampling_rate (int): Sampling rate of the signals (Hz).
    """
    if len(clean_ecg_signal) != len(clean_eeg_signal):
        print("Error: ECG and EEG must have the same duration after resampling.")
        return None

    try:
        pre_window_samples = int((pre_window_ms / 1000) * sampling_rate)
        post_window_samples = int((post_window_ms / 1000) * sampling_rate)

        # Extract segments around R-peaks
        ecg_segments = []
        eeg_segments = []

        for r_idx in r_peak_indices:
            start_idx, end_idx = r_idx - pre_window_samples, r_idx + post_window_samples
            if 0 <= start_idx < len(clean_ecg_signal) and 0 < end_idx < len(clean_ecg_signal):
                ecg_segments.append(clean_ecg_signal[start_idx:end_idx])
                eeg_segments.append(clean_eeg_signal[start_idx:end_idx])

        # Convert lists to arrays for averaging
        ecg_segments = np.array(ecg_segments)
        eeg_segments = np.array(eeg_segments)

        # Compute averages
        avg_ecg = np.mean(ecg_segments, axis=0)
        avg_eeg = np.mean(eeg_segments, axis=0)

        # Define color and style settings
        ecg_color = "#1f77b4"    # Blue for ECG
        eeg_color = "#ff7f0e"    # Orange for EEG
        hep_color = "#007acc"    # Dark blue for HEP
        avg_pqrs_color = "#2ca02c" # Green for average ECG
        peak_color = "#d62728"   # Red for R-peaks
        window_color = "#c7c7c7" # Light gray for time windows

        # Create subplots with a 2-row, 5-column layout
        fig = plt.figure(figsize=(14, 8))
        gs = fig.add_gridspec(2, 5)  # 2 rows, 5 columns

        # ECG Signal (3 columns)
        ax1 = fig.add_subplot(gs[0, 0:3])  
        ax1.plot(clean_ecg_signal, color=ecg_color, linewidth=1.5, label="ECG Signal")
        ax1.scatter(r_peak_indices, clean_ecg_signal[r_peak_indices], color=peak_color, edgecolors='black', 
                    label="R-wave Peaks", zorder=3)
        ax1.set_title("ECG Signal with R-wave Peaks", fontsize=14, fontweight='bold')
        ax1.set_ylabel("Amplitude (µV)", fontsize=12)
        ax1.legend(loc="upper right")
        ax1.grid(True, linestyle="--", alpha=0.5)

        # Average ECG (2 columns) with all segments in gray
        ax2 = fig.add_subplot(gs[0, 3:5])  
        for segment in ecg_segments:
            ax2.plot(segment, color="gray", linewidth=0.8, alpha=0.7)  # gray for individual segments
        ax2.plot(avg_ecg, color=avg_pqrs_color, linewidth=2, label="Average ECG")  # Bold color for average
        ax2.set_title("Average ECG Around R-wave Peaks", fontsize=14, fontweight='bold')
        ax2.set_xlabel("Time (samples)", fontsize=12)
        ax2.set_ylabel("Amplitude (µV)", fontsize=12)
        ax2.legend(loc="upper right")
        ax2.grid(True, linestyle="--", alpha=0.5)

        # EEG Signal (3 columns)
        ax3 = fig.add_subplot(gs[1, 0:3])  
        ax3.plot(clean_eeg_signal, color=eeg_color, linewidth=1.5, label="EEG Signal")
        for r_idx in r_peak_indices:
            start_idx, end_idx = r_idx - pre_window_samples, r_idx + post_window_samples
            if 0 <= start_idx < len(clean_eeg_signal) and 0 < end_idx < len(clean_eeg_signal):
                ax3.axvspan(start_idx, end_idx, color=window_color, alpha=0.3, 
                            label="R-peak Window" if r_idx == r_peak_indices[0] else "")
        ax3.set_title(f"EEG Signal with {pre_window_ms} ms Before and {post_window_ms} ms After R-wave Peaks", 
                      fontsize=14, fontweight='bold')
        ax3.set_ylabel("Amplitude (µV)", fontsize=12)
        ax3.legend(loc="upper right")
        ax3.grid(True, linestyle="--", alpha=0.5)

        # Heart-Evoked Potential (HEP) (2 columns) with all segments in light
        ax4 = fig.add_subplot(gs[1, 3:5])  
        for segment in eeg_segments:
            ax4.plot(segment, color="gray", linewidth=0.8, alpha=0.7)  # Light for individual segments
        ax4.plot(avg_eeg, color=hep_color, linewidth=2, label="Heart-Evoked Potential (EEG)")  # Bold for average
        ax4.set_title("Average Heart-Evoked Potential (EEG)", fontsize=14, fontweight='bold')
        ax4.set_xlabel("Time (samples)", fontsize=12)
        ax4.set_ylabel("Amplitude (µV)", fontsize=12)
        ax4.legend(loc="upper right")
        ax4.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Error plotting signals: {e}")