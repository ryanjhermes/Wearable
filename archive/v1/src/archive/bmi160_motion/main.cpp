#include <Arduino.h>
#include <Wire.h>

// BMI160 read directly over Wire — no library (avoids the Adafruit BusIO build trap, see CLAUDE.md).
// 6-axis raw accel + gyro. SDO pull sets the address: 0x68 (low) or 0x69 (high) — we auto-detect both.

const uint8_t BMI160_ADDRS[] = {0x69, 0x68};
uint8_t bmi_addr = 0x00;                 // resolved in setup()

// Registers
const uint8_t REG_CHIP_ID  = 0x00;       // reads 0xD1 on a real BMI160
const uint8_t REG_PMU      = 0x03;       // power-mode status
const uint8_t REG_DATA     = 0x0C;       // gyro X LSB; 12 bytes gyro(6) + accel(6) follow
const uint8_t REG_ACC_RANGE = 0x41;
const uint8_t REG_GYR_RANGE = 0x43;
const uint8_t REG_CMD      = 0x7E;

const uint8_t CHIP_ID_BMI160 = 0xD1;

// Ranges chosen below: accel ±2g, gyro ±2000 dps
const float ACC_LSB_PER_G  = 16384.0f;   // ±2g
const float GYR_LSB_PER_DPS = 16.4f;     // ±2000 dps

bool bmi_ok = false;
long lastPrint = 0;

bool writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(bmi_addr);
  Wire.write(reg);
  Wire.write(val);
  return Wire.endTransmission() == 0;
}

bool readReg(uint8_t addr, uint8_t reg, uint8_t &out) {
  Wire.beginTransmission(addr);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;   // repeated start, keep bus
  if (Wire.requestFrom((int)addr, 1) != 1) return false;
  out = Wire.read();
  return true;
}

// Reads the 12-byte data block into six int16 values.
bool readMotion(int16_t &gx, int16_t &gy, int16_t &gz,
                int16_t &ax, int16_t &ay, int16_t &az) {
  Wire.beginTransmission(bmi_addr);
  Wire.write(REG_DATA);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom((int)bmi_addr, 12) != 12) return false;

  uint8_t b[12];
  for (int i = 0; i < 12; i++) b[i] = Wire.read();

  gx = (int16_t)((b[1]  << 8) | b[0]);
  gy = (int16_t)((b[3]  << 8) | b[2]);
  gz = (int16_t)((b[5]  << 8) | b[4]);
  ax = (int16_t)((b[7]  << 8) | b[6]);
  ay = (int16_t)((b[9]  << 8) | b[8]);
  az = (int16_t)((b[11] << 8) | b[10]);
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Wire.begin();
  Wire.setClock(100000);   // 100kHz standard speed — matches the shared-bus sensors
  Serial.println("BMI160 6-axis motion read");

  // Find the chip at 0x69 or 0x68 by verifying the chip ID.
  uint8_t id = 0;
  for (uint8_t a : BMI160_ADDRS) {
    if (readReg(a, REG_CHIP_ID, id) && id == CHIP_ID_BMI160) {
      bmi_addr = a;
      break;
    }
  }
  if (bmi_addr == 0x00) {
    Serial.println("BMI160 not found (no 0xD1 at 0x68/0x69) — check wiring / 3.3V");
    return;                // leave bmi_ok = false; loop() will early-return
  }
  Serial.print("BMI160 found at 0x");
  Serial.println(bmi_addr, HEX);

  // Power up: accel then gyro to normal mode, with datasheet start-up delays.
  writeReg(REG_CMD, 0x11);   // accel normal mode
  delay(5);                  // accel start-up ~3.8ms
  writeReg(REG_CMD, 0x15);   // gyro normal mode
  delay(80);                 // gyro start-up ~80ms

  writeReg(REG_ACC_RANGE, 0x03);   // ±2g
  writeReg(REG_GYR_RANGE, 0x00);   // ±2000 dps
  delay(10);

  bmi_ok = true;
}

void loop() {
  if (!bmi_ok) { delay(1000); return; }   // non-blocking halt — keeps the watchdog fed

  int16_t gx, gy, gz, ax, ay, az;
  if (readMotion(gx, gy, gz, ax, ay, az)) {
    if (millis() - lastPrint >= 1000) {    // throttle to 1 line/sec
      lastPrint = millis();
      Serial.print("A[g]=");
      Serial.print(ax / ACC_LSB_PER_G, 2); Serial.print(",");
      Serial.print(ay / ACC_LSB_PER_G, 2); Serial.print(",");
      Serial.print(az / ACC_LSB_PER_G, 2);
      Serial.print("   G[dps]=");
      Serial.print(gx / GYR_LSB_PER_DPS, 1); Serial.print(",");
      Serial.print(gy / GYR_LSB_PER_DPS, 1); Serial.print(",");
      Serial.println(gz / GYR_LSB_PER_DPS, 1);
    }
  } else {
    Serial.println("BMI160 read failed — check contact on the shared bus");
    delay(1000);
  }
}
