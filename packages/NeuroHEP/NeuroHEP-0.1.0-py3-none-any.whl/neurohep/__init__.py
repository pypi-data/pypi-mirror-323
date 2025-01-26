from .preprocessing import resample_signal, preprocess_ecg_eeg, apply_bandpass_notch_filter
from .detection import detect_r_wave_peaks, extract_heps
from .visualization import plot_ecg_eeg_with_hep

__version__ = "0.1.0"
