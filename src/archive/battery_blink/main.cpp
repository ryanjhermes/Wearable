#include <Arduino.h>

// Battery power-check: blinks the XIAO's onboard user LED with no USB/serial
// dependency. If it keeps blinking after USB is unplugged, the board is running
// on battery. LED_BUILTIN on the XIAO ESP32S3 is active-LOW (LOW = on).

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  digitalWrite(LED_BUILTIN, LOW);   // on
  delay(300);
  digitalWrite(LED_BUILTIN, HIGH);  // off
  delay(300);
}
