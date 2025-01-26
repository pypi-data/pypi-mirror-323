# **NeuroHEP**

*A Python package for detecting and processing Heartbeat-Evoked Potentials (HEPs) from EEG signals.*

## **Overview**

The **Heartbeat-Evoked Potential (HEP)** is a brain response that occurs in synchronization with each heartbeat. These responses reflect **cardiac signaling** to central autonomic areas and are considered a **marker of internal body awareness** (*interoception*).

**NeuroHEP** facilitates the **detection, extraction, and visualization** of HEPs by aligning EEG signals with ECG events (e.g., **R-peak** or **T-wave**). This tool allows researchers to study the **brain-heart connection** and the role of the **autonomic nervous system** in bodily awareness.

---

## **Key Features** 🚀

✅ **Preprocessing**: Filter, clean, and align EEG and ECG signals.\
✅ **HEP Detection**: Extract HEPs by time-locking EEG to ECG events.\
✅ **Visualization**: Easily plot EEG, ECG, and HEPs for analysis.\
✅ **Interoception Research**: Supports studies on internal body awareness and cardiac-brain interactions.

---

## **Installation** ⚙️

You can install **NeuroHEP** directly from PyPI:

```bash
pip install NeuroHEP
```

Or install it manually from the source:

```bash
git clone https://github.com/mahsaalidadi/NeuroHEP.git
cd NeuroHEP
pip install .
```

---

## **Requirements** 📋

NeuroHEP requires **Python 3.7+** and the following dependencies:

- `numpy`
- `scipy`
- `matplotlib`
- `mne`
- `neurokit2`
- `pandas`

To install all dependencies:

```bash
pip install -r requirements.txt
```

---

## **Usage Example** 🧠

Here’s how to use **NeuroHEP** to process EEG and ECG data for HEP detection:

```python
import neurokit2 as nk
import numpy as np
import NeuroHEP as hep

# Generate synthetic ECG and EEG signals (5 subjects, 10s data, 250Hz)
num_subjects = 5
sampling_rate = 250  
duration = 10  

ecg_signals = np.array([nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, heart_rate=70) for _ in range(num_subjects)])
eeg_signals = np.array([nk.eeg_simulate(duration=duration, sampling_rate=sampling_rate, noise=0.1) for _ in range(num_subjects)])

# Preprocessing
filtered_ecg, filtered_eeg = hep.preprocessing.preprocess_ecg_eeg(
    ecg_signals, eeg_signals, sampling_rate,
    target_fs=128, notch_freq=60,
    low_cutoff=0.1, high_cutoff=35
)

# Extract HEPs
r_peak_indices = hep.detection.detect_r_wave_peaks(filtered_ecg[0], sampling_rate)
hep, hep_ecg = hep.detection.extract_heps(
    filtered_eeg[0], filtered_ecg[0], r_peak_indices,
    pre_window_ms=100, post_window_ms=300, sampling_rate=sampling_rate
)

# Visualization
hep.visualization.plot_ecg_eeg_with_hep()
```

---

## **Contributing** 🤝

We welcome contributions! To contribute:

1. **Fork** this repository
2. **Create a new branch** (`feature-branch`)
3. **Commit your changes**
4. **Submit a pull request**

---

## **License** 📜

**NeuroHEP** is licensed under the **MIT License**. See the [LICENSE](https://github.com/mahsaalidadi/NeuroHEP/blob/master/LICENSE.txt) file for details.

---

## **Links & Resources** 🔗

📌 **GitHub Repository**: [NeuroHEP](https://github.com/mahsaalidadi/NeuroHEP)\
📌 **Issue Tracker**: [Report Issues](https://github.com/mahsaalidadi/NeuroHEP/issues)

---

