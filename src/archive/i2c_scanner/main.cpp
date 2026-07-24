#include <Arduino.h>
#include <Wire.h>

void setup() {
  Serial.begin(115200);
  delay(2000);
  Wire.begin();
  Wire.setClock(100000);   // 100kHz — same as the sensor sketches
  Serial.println("I2C scanner — expect 0x57 (MAX) and 0x5A (MLX)");
}

void loop() {
  int found = 0;
  Serial.print("scan: ");
  for (uint8_t addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {
      Serial.print("0x");
      if (addr < 16) Serial.print("0");
      Serial.print(addr, HEX);
      Serial.print(" ");
      found++;
    }
  }
  if (found == 0) Serial.print("(none)");
  Serial.println();
  delay(1000);
}
