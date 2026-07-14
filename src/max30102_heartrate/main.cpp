#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"   // SparkFun lib class name is MAX30105; drives the MAX30102 too
#include "heartRate.h"

MAX30105 particleSensor;

const byte RATE_SIZE = 4;   // BPM averaging window
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;          // ms timestamp of the last detected beat
float beatsPerMinute = 0;
int beatAvg = 0;

bool sensor_ok = false;     // non-blocking failure flag (see CLAUDE.md watchdog note)

long lastPrint = 0;         // throttles serial output to once per second
int beatsThisSecond = 0;    // beats counted in the current print window

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("MAX30102 heart rate test");

  // 100kHz (I2C_SPEED_STANDARD) per project notes — 400kHz was unreliable over jumpers
  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    sensor_ok = true;
    particleSensor.setup();                       // default config
    particleSensor.setPulseAmplitudeRed(0x0A);    // dim red LED as a "powered" indicator
    particleSensor.setPulseAmplitudeGreen(0);     // MAX30102 has no green LED
    Serial.println("Ready. Rest a fingertip on the sensor with light, steady pressure.");
  } else {
    Serial.println("MAX30102 not found at 0x57 — check wiring.");
  }
}

void loop() {
  if (!sensor_ok) {          // let loop() return so the watchdog stays fed
    delay(1000);
    return;
  }

  long irValue = particleSensor.getIR();
  bool beat = checkForBeat(irValue);

  if (beat) {
    if (lastBeat != 0) {                    // skip the phantom first beat at startup
      long delta = millis() - lastBeat;
      beatsPerMinute = 60 / (delta / 1000.0);

      if (beatsPerMinute < 255 && beatsPerMinute > 20) {
        rates[rateSpot++] = (byte)beatsPerMinute;   // store this reading
        rateSpot %= RATE_SIZE;

        beatAvg = 0;
        for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
        beatAvg /= RATE_SIZE;
      }
    }
    lastBeat = millis();
    beatsThisSecond++;
  }

  if (irValue < 50000) {                    // finger lifted — reset stale state
    beatsPerMinute = 0;
    beatAvg = 0;
  }

  // Print one summary line per second so a long run stays readable
  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();

    if (irValue < 50000) {
      Serial.println("No finger — rest fingertip lightly on the sensor");
    } else {
      Serial.print("Avg BPM=");
      Serial.print(beatAvg);
      Serial.print("  (last=");
      Serial.print(beatsPerMinute, 0);
      Serial.print(", beats this sec=");
      Serial.print(beatsThisSecond);
      Serial.print(", IR=");
      Serial.print(irValue);
      Serial.println(")");
    }
    beatsThisSecond = 0;
  }
}
