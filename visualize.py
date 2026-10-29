import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
# ============================================
# Configuration
# ============================================

OUTPUT_DIR = Path("./outputs")

ECG_FILE_NAME = input("Enter ecg csv filename: ")
PEAK_FILE_NAME = input("Enter corresponding detected peaks file: ")

ECG_FILE = OUTPUT_DIR / ECG_FILE_NAME
PEAK_FILE = OUTPUT_DIR / PEAK_FILE_NAME

# ============================================
# Load ECG data
# ============================================

if not os.path.exists(ECG_FILE):
    print(f"Error: {ECG_FILE} not found.")
    exit()

ecg_data = pd.read_csv(ECG_FILE)

time = ecg_data["time_seconds"]
ecg = ecg_data["ecg"]

# ============================================
# Load detected peaks
# ============================================

peaks_exist = os.path.exists(PEAK_FILE)

if peaks_exist:
    peak_data = pd.read_csv(PEAK_FILE)

    peak_time = peak_data["time_seconds"]
    peak_ecg = peak_data["ecg_value"]

    print(f"Detected peaks: {len(peak_data)}")

else:
    print(f"{PEAK_FILE} not found.")
    print("Plotting ECG without detected peaks.")

# ============================================
# Plot ECG
# ============================================

plt.figure(figsize=(14, 6))

plt.plot(
    time,
    ecg,
    linewidth=1,
    label="Filtered ECG"
)

# Overlay Pan-Tompkins peaks
if peaks_exist:

    plt.scatter(
        peak_time,
        peak_ecg,
        marker="o",
        s=40,
        label="Detected R Peaks"
    )

# ============================================
# Plot formatting
# ============================================

plt.title("ECG Signal with Pan-Tompkins R-Peak Detection")

plt.xlabel("Time (seconds)")
plt.ylabel("ECG Amplitude (ADC)")

plt.grid(True, alpha=0.3)

plt.legend()

plt.tight_layout()

plt.show()
