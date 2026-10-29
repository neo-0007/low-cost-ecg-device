import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================
# Configuration
# ============================================

OUTPUT_DIR = Path("./outputs")

ECG_FILE_NAME = input("Enter ECG Filename : ")
PEAK_FILE_NAME = input("Enter Corresponding peak filename: ")

ECG_FILE = OUTPUT_DIR / ECG_FILE_NAME
PEAK_FILE = OUTPUT_DIR / PEAK_FILE_NAME

# Which detected peak do you want to visualize?

PEAK_NUMBER = int(input("Enter peak number: "))

# Time window around the peak
# 0.5 seconds before and after
WINDOW_BEFORE = 0.5
WINDOW_AFTER = 0.5

# ============================================
# Load ECG
# ============================================

ecg_data = pd.read_csv(ECG_FILE)

time = ecg_data["time_seconds"].values
ecg = ecg_data["ecg"].values

# ============================================
# Load detected peaks
# ============================================

peak_data = pd.read_csv(PEAK_FILE)

selected = peak_data[
    peak_data["peak_number"] == PEAK_NUMBER
]

if selected.empty:
    print(f"Peak {PEAK_NUMBER} not found.")
    print(
        f"Available peaks: 1 to "
        f"{len(peak_data)}"
    )
    exit()

# Get peak information
peak_sample = int(
    selected.iloc[0]["sample"]
)

peak_time = float(
    selected.iloc[0]["time_seconds"]
)

peak_value = float(
    selected.iloc[0]["ecg_value"]
)

# ============================================
# Select ECG region around peak
# ============================================

start_time = peak_time - WINDOW_BEFORE
end_time = peak_time + WINDOW_AFTER

mask = (
    (time >= start_time)
    &
    (time <= end_time)
)

plot_time = time[mask]
plot_ecg = ecg[mask]

# ============================================
# Plot
# ============================================

plt.figure(figsize=(12, 6))

plt.plot(
    plot_time,
    plot_ecg,
    linewidth=1.5,
    label="Filtered ECG"
)

# Detected peak
plt.scatter(
    peak_time,
    peak_value,
    s=100,
    zorder=5,
    label="Detected R Peak"
)

# Vertical line through detected peak
plt.axvline(
    peak_time,
    linestyle="--",
    linewidth=1
)

# ============================================
# Formatting
# ============================================

plt.title(
    f"ECG Peak #{PEAK_NUMBER}"
)

plt.xlabel("Time (seconds)")
plt.ylabel("ECG Amplitude (ADC)")

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.show()

# ============================================
# Print information
# ============================================

print()
print(f"Peak number : {PEAK_NUMBER}")
print(f"Sample      : {peak_sample}")
print(f"Time        : {peak_time:.4f} s")
print(f"ECG value   : {peak_value:.2f}")
