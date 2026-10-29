import numpy as np
import pandas as pd

from scipy.signal import butter, filtfilt
from pathlib import Path

# ============================================
# Configuration
# ============================================

OUTPUT_DIR = Path("./outputs")

INPUT_FILE_NAME = input("Enter ecg csv filename to detect peaks: ")
OUTPUT_FILE_NAME = input("Enter filename to store peaks: ")

INPUT_FILE = OUTPUT_DIR / INPUT_FILE_NAME
OUTPUT_FILE = OUTPUT_DIR / OUTPUT_FILE_NAME

FS = 250                  # Sampling frequency
INTEGRATION_WINDOW = 30   # ~120 ms at 250 Hz

# Minimum distance between two detected R peaks
# 200 ms = 50 samples
MIN_PEAK_DISTANCE = int(0.20 * FS)


# ============================================
# Load ECG
# ============================================

data = pd.read_csv(INPUT_FILE)

ecg = data["ecg"].values.astype(float)

print(f"Loaded {len(ecg)} ECG samples.")


# ============================================
# Step 1: Band-pass filtering
# ============================================

def bandpass_filter(signal, fs):

    low_cutoff = 5.0
    high_cutoff = 15.0

    nyquist = fs / 2

    low = low_cutoff / nyquist
    high = high_cutoff / nyquist

    b, a = butter(
        2,
        [low, high],
        btype="band"
    )

    filtered = filtfilt(
        b,
        a,
        signal
    )

    return filtered


filtered = bandpass_filter(
    ecg,
    FS
)


# ============================================
# Step 2: Derivative
# ============================================

derivative = np.zeros_like(filtered)

for i in range(1, len(filtered)):

    derivative[i] = (
        filtered[i]
        - filtered[i - 1]
    )


# ============================================
# Step 3: Squaring
# ============================================

squared = derivative ** 2


# ============================================
# Step 4: Moving Window Integration
# ============================================

window = np.ones(
    INTEGRATION_WINDOW
) / INTEGRATION_WINDOW

integrated = np.convolve(
    squared,
    window,
    mode="same"
)


# ============================================
# Step 5: Threshold / Peak Detection
# ============================================

# Initial threshold based on signal statistics

threshold = (
    np.mean(integrated)
    +
    0.5 * np.std(integrated)
)

candidate_peaks = []

for i in range(1, len(integrated) - 1):

    # Local maximum
    if (
        integrated[i] > integrated[i - 1]
        and
        integrated[i] >= integrated[i + 1]
        and
        integrated[i] > threshold
    ):

        candidate_peaks.append(i)


# ============================================
# Enforce minimum distance between peaks
# ============================================

peaks = []

for peak in candidate_peaks:

    if len(peaks) == 0:

        peaks.append(peak)

    else:

        previous_peak = peaks[-1]

        if peak - previous_peak >= MIN_PEAK_DISTANCE:

            peaks.append(peak)

        else:

            # Keep the stronger peak
            if integrated[peak] > integrated[previous_peak]:
                peaks[-1] = peak


# ============================================
# Locate actual R peak in original ECG
# ============================================

refined_peaks = []

SEARCH_RADIUS = int(0.08 * FS)

for peak in peaks:

    start = max(
        0,
        peak - SEARCH_RADIUS
    )

    end = min(
        len(ecg),
        peak + SEARCH_RADIUS + 1
    )

    # Find maximum ECG value around detected QRS
    local_region = ecg[start:end]

    local_peak = start + np.argmax(
        local_region
    )

    refined_peaks.append(
        local_peak
    )


# ============================================
# Remove duplicate peaks
# ============================================

final_peaks = []

for peak in refined_peaks:

    if len(final_peaks) == 0:

        final_peaks.append(peak)

    elif peak - final_peaks[-1] >= MIN_PEAK_DISTANCE:

        final_peaks.append(peak)


# ============================================
# Save detected peaks
# ============================================

peak_data = []

for number, peak in enumerate(
    final_peaks,
    start=1
):

    timestamp = peak / FS

    peak_data.append([
        number,
        peak,
        timestamp,
        ecg[peak]
    ])


output = pd.DataFrame(
    peak_data,
    columns=[
        "peak_number",
        "sample",
        "time_seconds",
        "ecg_value"
    ]
)


output.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================
# Results
# ============================================

print()
print("Pan-Tompkins processing complete.")
print(f"Detected peaks: {len(final_peaks)}")
print(f"Output file: {OUTPUT_FILE}")
