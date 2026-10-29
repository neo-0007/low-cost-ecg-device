/*
 * AD8232 ECG Acquisition + Moving Average Filter
 * Board: Arduino Due
 *
 * AD8232 OUT  -> A0
 * LO+         -> D10
 * LO-         -> D11
 *
 * Sampling frequency: 250 Hz
 * ADC resolution: 12-bit (0-4095)
 * Moving average window: 5 samples
 */

const int ECG_PIN = A0;
const int LO_PLUS = 10;
const int LO_MINUS = 11;

const unsigned long SAMPLE_INTERVAL_US = 4000; // 250 Hz

const int MA_WINDOW = 5;
int buffer[MA_WINDOW];
long bufferSum = 0;
int bufferIndex = 0;
int samplesInBuffer = 0;

void setup() {
    Serial.begin(115200);

    // Arduino Due ADC: 12-bit -> 0 to 4095
    analogReadResolution(12);

    pinMode(LO_PLUS, INPUT);
    pinMode(LO_MINUS, INPUT);

    // Initialize moving average buffer
    for (int i = 0; i < MA_WINDOW; i++) {
        buffer[i] = 0;
    }

    delay(1000);
}

void loop() {

    static unsigned long lastSampleTime = micros();

    unsigned long currentTime = micros();

    if ((unsigned long)(currentTime - lastSampleTime) >= SAMPLE_INTERVAL_US) {

        lastSampleTime += SAMPLE_INTERVAL_US;

        // Check electrode connection
        if (digitalRead(LO_PLUS) || digitalRead(LO_MINUS)) {
            Serial.println("!");
            return;
        }

        // Read ECG signal
        int rawECG = analogRead(ECG_PIN);

        // Safety check for 12-bit ADC
        if (rawECG < 0 || rawECG > 4095) {
            return;
        }

        // Remove oldest value from sum
        if (samplesInBuffer == MA_WINDOW) {
            bufferSum -= buffer[bufferIndex];
        } else {
            samplesInBuffer++;
        }

        // Add new sample
        buffer[bufferIndex] = rawECG;
        bufferSum += rawECG;

        // Move circular buffer index
        bufferIndex++;

        if (bufferIndex >= MA_WINDOW) {
            bufferIndex = 0;
        }

        // Calculate moving average
        float filteredECG =
            (float)bufferSum / samplesInBuffer;

        // Print filtered ECG value
        Serial.println(filteredECG);
    }
}