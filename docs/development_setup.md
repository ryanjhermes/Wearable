# Development Setup

This document tracks the current setup for developing the wearable firmware from VS Code.

---

## Current Development Choice

Use:

```text
VS Code + PlatformIO + Arduino framework
```

Avoid using Arduino IDE unless needed for emergency testing.

Reasons:

- Cleaner project folders.
- Better editing experience in VS Code.
- Easier to use with AI coding agents.
- Good library support for ESP32 and sensors.
- PlatformIO CLI can be used even if the PlatformIO Home UI gets stuck.

---

## Board

Main board:

```text
Seeed Studio XIAO ESP32S3
```

PlatformIO board ID:

```ini
seeed_xiao_esp32s3
```

Framework:

```ini
arduino
```

Known macOS serial port:

```text
/dev/cu.usbmodem1101
```

Note: this port can change after unplugging/replugging the board.

---

## Useful Terminal Commands

Check whether PlatformIO is installed:

```bash
pio --version
```

List connected serial devices:

```bash
ls /dev/cu.*
```

List devices PlatformIO can see:

```bash
pio device list
```

Build firmware:

```bash
pio run
```

Upload firmware:

```bash
pio run -t upload
```

Open serial monitor:

```bash
pio device monitor
```

Exit serial monitor:

```text
Control + ]
```

---

## Recommended `platformio.ini`

Use this as the starting configuration:

```ini
[env:seeed_xiao_esp32s3]
platform = espressif32
board = seeed_xiao_esp32s3
framework = arduino

upload_port = /dev/cu.usbmodem1101
monitor_port = /dev/cu.usbmodem1101
monitor_speed = 115200
```

If the port changes, update both:

```ini
upload_port = ...
monitor_port = ...
```

---

## Minimal Test Program

Use this first to prove board upload and serial output:

```cpp
#include <Arduino.h>

void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);

  delay(1000);
  Serial.println("XIAO ESP32S3 is alive from PlatformIO");
}

void loop() {
  Serial.println("blink");

  digitalWrite(LED_BUILTIN, LOW);
  delay(500);

  digitalWrite(LED_BUILTIN, HIGH);
  delay(500);
}
```

Note: on many XIAO/ESP boards, the onboard LED is active-low, so `LOW` may mean LED on and `HIGH` may mean LED off.

---

## Boot / Reset Upload Recovery

The board has two relevant buttons:

```text
B = BOOT
R = RESET
```

If upload gets stuck at `Connecting...`, try:

1. Hold `B / BOOT`.
2. Start upload.
3. When PlatformIO says `Connecting...`, tap `R / RESET`.
4. Release `B / BOOT`.

Alternative:

1. Hold `B / BOOT`.
2. Tap `R / RESET`.
3. Release `B / BOOT`.
4. Run upload again.

---

## If the Board Does Not Appear

Run:

```bash
ls /dev/cu.*
```

Expected current device:

```text
/dev/cu.usbmodem1101
```

If it does not appear:

- Try a known data-capable USB-C cable.
- Avoid a hub if possible.
- Plug directly into the Mac.
- Try the boot/reset sequence.
- Check macOS System Report → USB.
- Confirm the board receives power.

---

## Python / MicroPython Direction

Python is still possible later through MicroPython or CircuitPython.

However, for this project, Arduino/C++ through PlatformIO is currently the safer first path because:

- MAX30102 libraries are easier to find.
- ESP32 BLE/Wi-Fi examples are more mature.
- Battery and sleep-mode behavior is better documented.
- Long-running firmware is more common in C++.

Possible future Python use cases:

- Simple I2C scan.
- Simple sensor tests.
- Quick scripts.
- Early logic experiments.

Likely C++ use cases:

- Final firmware.
- BLE.
- MAX30102 processing.
- Battery optimization.
- Reliable long-running wearable behavior.
