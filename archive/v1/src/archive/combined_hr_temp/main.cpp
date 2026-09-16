#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"   // SparkFun lib class name is MAX30105; drives the MAX30102 too
#include "heartRate.h"

// --- MAX30102 heart rate ---
MAX30105 particleSensor;

const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;
bool max_ok = false;

long lastPrint = 0;
int beatsThisSecond = 0;
long irValue = 0;

// --- MLX90614 temperature (direct Wire — no library) ---
const uint8_t MLX_ADDR  = 0x5A;
const uint8_t MLX_TA    = 0x06;
const uint8_t MLX_TOBJ1 = 0x07;
bool mlx_ok = false;

bool readMLX(uint8_t reg, float &out) {
  Wire.beginTransmission(MLX_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)MLX_ADDR, 3) != 3) return false;

  uint8_t lsb = Wire.read();
  uint8_t msb = Wire.read();
  Wire.read();   // PEC, ignored

  uint16_t raw = ((uint16_t)msb << 8) | lsb;
  if (raw & 0x8000) return false;
  out = raw * 0.02f - 273.15f;
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Combined HR + temperature");

  // 100kHz — 400kHz was unreliable over jumpers
  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    max_ok = true;
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
    Serial.println("MAX30102 ready at 0x57");
  } else {
    Serial.println("MAX30102 not found at 0x57");
    Wire.begin();
    Wire.setClock(100000);
  }

  float probe;
  if (readMLX(MLX_TA, probe)) {
    mlx_ok = true;
    Serial.println("MLX90614 ready at 0x5A");
  } else {
    Serial.println("MLX90614 not found at 0x5A");
  }

  if (max_ok || mlx_ok) {
    Serial.println("Ready. Finger on MAX; aim MLX at a target.");
  }
}

void loop() {
  // Heart rate needs continuous IR samples — never block this path
  if (max_ok) {
    irValue = particleSensor.getIR();
    bool beat = checkForBeat(irValue);

    if (beat) {
      if (lastBeat != 0) {   // skip phantom first beat
        long delta = millis() - lastBeat;
        beatsPerMinute = 60 / (delta / 1000.0);

        if (beatsPerMinute < 255 && beatsPerMinute > 20) {
          rates[rateSpot++] = (byte)beatsPerMinute;
          rateSpot %= RATE_SIZE;

          beatAvg = 0;
          for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
          beatAvg /= RATE_SIZE;
        }
      }
      lastBeat = millis();
      beatsThisSecond++;
    }

    if (irValue < 50000) {
      beatsPerMinute = 0;
      beatAvg = 0;
    }
  }

  // One summary line per second (HR + temps)
  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();

    // HR portion
    if (!max_ok) {
      Serial.print("MAX=missing");
    } else if (irValue < 50000) {
      Serial.print("Avg BPM=-- (no finger, IR=");
      Serial.print(irValue);
      Serial.print(")");
    } else {
      Serial.print("Avg BPM=");
      Serial.print(beatAvg);
      Serial.print("  (last=");
      Serial.print(beatsPerMinute, 0);
      Serial.print(", beats=");
      Serial.print(beatsThisSecond);
      Serial.print(", IR=");
      Serial.print(irValue);
      Serial.print(")");
    }

    Serial.print("  |  ");

    // Temp portion
    float object = 0, ambient = 0;
    if (!mlx_ok) {
      Serial.println("MLX=missing");
    } else if (readMLX(MLX_TOBJ1, object) && readMLX(MLX_TA, ambient)) {
      Serial.print("Ambient=");
      Serial.print(ambient, 1);
      Serial.print(" C, Object=");
      Serial.print(object, 1);
      Serial.println(" C");
    } else {
      Serial.println("MLX read failed");
    }

    beatsThisSecond = 0;
  }

  if (!max_ok && !mlx_ok) {
    delay(1000);   // both missing — idle without starving the watchdog forever
  }
}
