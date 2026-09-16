#include <Arduino.h>
#include <Wire.h>

// BMI160 motion LOGGER — fast CSV for spatial/motion charting (~50 Hz).
// MAX30102 may share the bus; this sketch only talks to the BMI160.
// Emits one line per sample:  M,<t_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>
// (accel in g, gyro in dps). The motion_csv monitor filter parses these.

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
const unsigned long SAMPLE_MS = 20;   // ~50 Hz
unsigned long lastSample = 0;

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

void setup() {
  Serial.begin(115200);
  delay(2000);
  Wire.begin();
  Wire.setClock(100000);
  Serial.println("BMI160 motion logger (~50 Hz CSV)");

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
  Serial.println("Logging... move the sensor. Ctrl+C to stop.");
}

void loop() {
  if (!bmi_ok) { delay(1000); return; }

  if (millis() - lastSample >= SAMPLE_MS) {
    lastSample = millis();
    float ax, ay, az, gx, gy, gz;
    if (bmiReadMotion(ax, ay, az, gx, gy, gz)) {
      Serial.print("M,");
      Serial.print(millis());        Serial.print(",");
      Serial.print(ax, 4);           Serial.print(",");
      Serial.print(ay, 4);           Serial.print(",");
      Serial.print(az, 4);           Serial.print(",");
      Serial.print(gx, 2);           Serial.print(",");
      Serial.print(gy, 2);           Serial.print(",");
      Serial.println(gz, 2);
    }
  }
}
