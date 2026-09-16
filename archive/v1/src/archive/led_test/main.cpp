#include <Arduino.h>
#include <driver/gpio.h>

// External LED test on GPIO4 (the D3 pad on the XIAO ESP32S3), with diagnostics.
//
// Wiring: GPIO4 -> LED anode (long leg); LED cathode (short leg / flat rim) -> GND.
//
// NO series resistor is used, so the pad drive strength is capped (see below).
// A bare 3.3 V pad into a 2.0-2.2 V Vf yellow LED would otherwise pull ~40 mA,
// at/over the ESP32-S3 per-pad limit. CAP_1 is ~10 mA: visible, still in spec.
//
// Three signals, so a dark external LED tells you WHICH thing is broken:
//   1. onboard LED blinks in ANTI-PHASE  -> firmware is running at all
//   2. serial prints the pin state       -> loop() is actually cycling
//   3. GPIO4 toggles                     -> the pin under test
// Onboard lit but external dark = wiring, polarity, wrong pad, or a dead LED.

const gpio_num_t LED = GPIO_NUM_4;

void setup() {
  Serial.begin(115200);
  delay(2000);  // catch window: monitor connects after boot

  pinMode(LED, OUTPUT);
  gpio_set_drive_capability(LED, GPIO_DRIVE_CAP_1);  // ~10 mA, resistor-free

  pinMode(LED_BUILTIN, OUTPUT);  // active-LOW on the XIAO ESP32S3

  Serial.println("led_test: GPIO4 (D3 pad), no series resistor, drive cap 1 (~10mA)");
  Serial.println("onboard LED blinks anti-phase; if it blinks, firmware is running.");
}

void loop() {
  digitalWrite(LED, HIGH);          // external on
  digitalWrite(LED_BUILTIN, HIGH);  // onboard off (active-LOW)
  Serial.println("GPIO4=HIGH  (external LED should be ON, onboard OFF)");
  delay(500);

  digitalWrite(LED, LOW);           // external off
  digitalWrite(LED_BUILTIN, LOW);   // onboard on
  Serial.println("GPIO4=LOW   (external LED should be OFF, onboard ON)");
  delay(500);
}
