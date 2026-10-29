import serial
import csv
import time
from pathlib import Path

# ==============================
# Configuration
# ==============================

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

SAMPLE_RATE = 250
DURATION = 30

OUTPUT_DIR = Path("./outputs")
FILE_NAME = input("Enter filename of the CSV: ")

OUTPUT_FILE = OUTPUT_DIR / FILE_NAME

EXPECTED_SAMPLES = SAMPLE_RATE * DURATION


# ==============================
# Open Serial Port
# ==============================

ser = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)

# Allow Arduino to reset after serial connection
time.sleep(2)

print("Starting ECG recording...")
print(f"Expected samples: {EXPECTED_SAMPLES}")
print(f"Duration: {DURATION} seconds")


# ==============================
# Record ECG
# ==============================

samples = []

while len(samples) < EXPECTED_SAMPLES:

    line = ser.readline().decode(
        "utf-8",
        errors="ignore"
    ).strip()

    if not line:
        continue

    # Ignore electrode disconnect message
    if line == "!":
        print("Electrodes disconnected!")
        continue

    try:
        value = float(line)
    except ValueError:
        continue

    # Arduino Due 12-bit ADC range
    if value < 0 or value > 4095:
        continue

    samples.append(value)

    if len(samples) % 250 == 0:
        print(
            f"Collected {len(samples)}/"
            f"{EXPECTED_SAMPLES} samples"
        )


ser.close()


# ==============================
# Save CSV
# ==============================

with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    # CSV header
    writer.writerow([
        "sample",
        "time_seconds",
        "ecg"
    ])

    for i, value in enumerate(samples):

        timestamp = i / SAMPLE_RATE

        writer.writerow([
            i,
            f"{timestamp:.4f}",
            f"{value:.4f}"
        ])


print()
print("Recording complete.")
print(f"Saved {len(samples)} samples.")
print(f"File: {OUTPUT_FILE}")
