#include <Arduino.h>
#include <Wire.h>
#include "MAX30105.h"   // SparkFun lib class name is MAX30105; drives the MAX30102 too
#include "heartRate.h"

// Combined shared-bus test: MAX30102 heart rate (0x57) + BMI160 6-axis motion (0x68/0x69).
// Each sensor has its own ok-flag so a missing one doesn't stall the other.

// --- MAX30102 heart rate ---
MAX30105 particleSensor;
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;
int beatsThisSecond = 0;
bool max_ok = false;

// --- BMI160 motion (direct Wire — no library) ---
const uint8_t BMI160_ADDRS[] = {0x69, 0x68};
uint8_t bmi_addr = 0x00;
const uint8_t REG_CHIP_ID   = 0x00;
const uint8_t REG_DATA      = 0x0C;   // gyro X LSB; 12 bytes gyro(6)+accel(6) follow
const uint8_t REG_ACC_RANGE = 0x41;
const uint8_t REG_GYR_RANGE = 0x43;
const uint8_t REG_CMD       = 0x7E;
const uint8_t CHIP_ID_BMI160 = 0xD1;
const float ACC_LSB_PER_G   = 16384.0f;  // ±2g
const float GYR_LSB_PER_DPS = 16.4f;     // ±2000 dps
bool bmi_ok = false;

long lastPrint = 0;

bool bmiWrite(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(bmi_addr);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

bool bmiReadReg(uint8_t addr, uint8_t reg, uint8_t &out) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)addr, 1) != 1) return false;
  out = Wire.read();
  return true;
}

bool bmiReadMotion(float &ax, float &ay, float &az,
                   float &gx, float &gy, float &gz) {
  Wire.beginTransmission(bmi_addr);
  Wire.write(REG_DATA);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)bmi_addr, 12) != 12) return false;

  uint8_t b[12];
  for (int i = 0; i < 12; i++) b[i] = Wire.read();

  int16_t rgx = (int16_t)((b[1]  << 8) | b[0]);
  int16_t rgy = (int16_t)((b[3]  << 8) | b[2]);
  int16_t rgz = (int16_t)((b[5]  << 8) | b[4]);
  int16_t rax = (int16_t)((b[7]  << 8) | b[6]);
  int16_t ray = (int16_t)((b[9]  << 8) | b[8]);
  int16_t raz = (int16_t)((b[11] << 8) | b[10]);

  ax = rax / ACC_LSB_PER_G; ay = ray / ACC_LSB_PER_G; az = raz / ACC_LSB_PER_G;
  gx = rgx / GYR_LSB_PER_DPS; gy = rgy / GYR_LSB_PER_DPS; gz = rgz / GYR_LSB_PER_DPS;
  return true;
}

void setupBMI() {
  uint8_t id = 0;
  for (uint8_t a : BMI160_ADDRS) {
    if (bmiReadReg(a, REG_CHIP_ID, id) && id == CHIP_ID_BMI160) {
      bmi_addr = a;
      break;
    }
  }
  if (bmi_addr == 0x00) {
    Serial.println("BMI160 not found at 0x68/0x69 — check wiring / 3.3V");
    return;
  }
  Serial.print("BMI160 found at 0x");
  Serial.println(bmi_addr, HEX);

  bmiWrite(REG_CMD, 0x11); delay(5);    // accel normal mode
  bmiWrite(REG_CMD, 0x15); delay(80);   // gyro normal mode
  bmiWrite(REG_ACC_RANGE, 0x03);        // ±2g
  bmiWrite(REG_GYR_RANGE, 0x00);        // ±2000 dps
  delay(10);
  bmi_ok = true;
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Combined shared-bus test: MAX30102 heart rate + BMI160 motion");

  // MAX30102 begin() also inits Wire at 100kHz (I2C_SPEED_STANDARD) for the shared bus.
  if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    max_ok = true;
    particleSensor.setup();
    particleSensor.setPulseAmplitudeRed(0x0A);
    particleSensor.setPulseAmplitudeGreen(0);
    Serial.println("MAX30102 ready at 0x57.");
  } else {
    Serial.println("MAX30102 not found at 0x57 — check wiring.");
    Wire.begin();                // ensure Wire is up for the BMI160 even if MAX is absent
    Wire.setClock(100000);
  }

  setupBMI();

  if (!max_ok && !bmi_ok) {
    Serial.println("No sensors found on the bus — check shared power/ground and SDA/SCL.");
  }
}

void loop() {
  if (!max_ok && !bmi_ok) { delay(1000); return; }

  long irValue = 0;

  // --- heart rate ---
  if (max_ok) {
    irValue = particleSensor.getIR();
    if (checkForBeat(irValue)) {
      if (lastBeat != 0) {
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
    if (irValue < 50000) { beatsPerMinute = 0; beatAvg = 0; }
  }

  // --- one combined summary line per second ---
  if (millis() - lastPrint >= 1000) {
    lastPrint = millis();

    if (max_ok) {
      if (irValue < 50000) {
        Serial.print("HR: no finger");
      } else {
        Serial.print("HR: Avg BPM=");
        Serial.print(beatAvg);
        Serial.print(" (last=");
        Serial.print(beatsPerMinute, 0);
        Serial.print(", beats/s=");
        Serial.print(beatsThisSecond);
        Serial.print(", IR=");
        Serial.print(irValue);
        Serial.print(")");
      }
    } else {
      Serial.print("HR: --");
    }
    beatsThisSecond = 0;

    Serial.print("   |   ");

    if (bmi_ok) {
      float ax, ay, az, gx, gy, gz;
      if (bmiReadMotion(ax, ay, az, gx, gy, gz)) {
        Serial.print("MOTION: A[g]=");
        Serial.print(ax, 2); Serial.print(",");
        Serial.print(ay, 2); Serial.print(",");
        Serial.print(az, 2);
        Serial.print(" G[dps]=");
        Serial.print(gx, 0); Serial.print(",");
        Serial.print(gy, 0); Serial.print(",");
        Serial.println(gz, 0);
      } else {
        Serial.println("MOTION: read failed");
      }
    } else {
      Serial.println("MOTION: --");
    }
  }
}
