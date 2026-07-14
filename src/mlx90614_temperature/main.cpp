#include <Arduino.h>
#include <Wire.h>

// MLX90614 read directly over Wire — no library (Adafruit lib won't build here, see CLAUDE.md)
const uint8_t MLX_ADDR  = 0x5A;
const uint8_t MLX_TA    = 0x06;   // ambient temperature register
const uint8_t MLX_TOBJ1 = 0x07;   // object (surface) temperature register

// Reads one temperature register. Returns true on success, writing degrees C into out.
bool readMLX(uint8_t reg, float &out) {
  Wire.beginTransmission(MLX_ADDR);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;   // repeated start, keep bus
  if (Wire.requestFrom((int)MLX_ADDR, 3) != 3) return false;

  uint8_t lsb = Wire.read();
  uint8_t msb = Wire.read();
  Wire.read();                                           // PEC checksum, ignored

  uint16_t raw = ((uint16_t)msb << 8) | lsb;
  if (raw & 0x8000) return false;                        // error flag set
  out = raw * 0.02f - 273.15f;                           // raw is in 0.02K steps
  return true;
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Wire.begin();
  Wire.setClock(100000);   // 100kHz standard speed
  Serial.println("MLX90614 temperature read");
}

void loop() {
  float object, ambient;
  bool okObj = readMLX(MLX_TOBJ1, object);
  bool okAmb = readMLX(MLX_TA, ambient);

  if (okObj && okAmb) {
    Serial.print("Ambient=");
    Serial.print(ambient, 2);
    Serial.print(" C,  Object=");
    Serial.print(object, 2);
    Serial.println(" C");
  } else {
    Serial.println("MLX read failed — check wiring / 0x5A");
  }
  delay(1000);
}
