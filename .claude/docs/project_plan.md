# Wearable Project Plan

## Goal

Build a small experimental wearable using the Seeed Studio XIAO ESP32S3 that can collect basic body/environment signals and eventually display, store, or transmit useful information.

This is an experimental prototype, not a medical device.

---

## Current Prototype Scope

The first version should prove that the board, sensors, wiring, and firmware work reliably.

Initial hardware:

- Seeed Studio XIAO ESP32S3
- MAX30102 heart rate / PPG sensor
- MLX90614 / GY-906 non-contact infrared temperature sensor

Likely later hardware:

- Button
- Battery
- 3D printed enclosure or wrist mount
- BLE phone connection

---

## What This Project Is Not

This project is not trying to be a finished commercial wearable yet.

It is also not a medical device. Heart rate, SpO2-like estimates, and temperature readings should be treated as experimental signals, not medically reliable measurements.

---

## Development Approach

Start with:

```text
VS Code + PlatformIO + Arduino framework
```

Reason:

- Better library support for sensors than starting with pure MicroPython.
- Cleaner project structure than Arduino IDE.
- Works well with AI-assisted development inside VS Code.
- Still keeps the option open to test MicroPython later.

Possible later path:

```text
MicroPython or CircuitPython
```

This may be useful for simple experiments, but C++/Arduino is likely better for reliable sensor libraries, BLE, battery behavior, and long-running firmware.

---

## Phase 1: Board Bring-Up

Goal: confirm that the XIAO ESP32S3 can build, upload, and print serial output from VS Code.

Tasks:

- Confirm macOS sees the board.
- Confirm PlatformIO CLI works.
- Create a minimal PlatformIO project.
- Upload a blink/serial sketch.
- Confirm serial monitor output.
- Document boot/reset upload process.

Known board port:

```text
/dev/cu.usbmodem1101
```

Success criteria:

- `pio run` succeeds.
- `pio run -t upload` succeeds.
- Serial monitor prints live output.
- LED blink works.

---

## Phase 2: I2C Sensor Detection

Goal: confirm sensors are wired correctly and visible on the I2C bus.

Tasks:

- Wire MAX30102 to 3.3V, GND, SDA, and SCL.
- Wire MLX90614 to 3.3V, GND, SDA, and SCL.
- Run an I2C scanner.
- Confirm expected addresses.

Expected I2C addresses:

| Component | Expected address |
|---|---|
| MAX30102 | `0x57` |
| MLX90614 | `0x5A` |

Success criteria:

- I2C scanner detects the MAX30102.
- I2C scanner detects the MLX90614.
- No unstable wiring/disconnect behavior.

---

## Phase 3: Basic Sensor Readings

Goal: print simple live readings from each sensor.

Tasks:

- Read raw red/IR values from MAX30102.
- Read ambient/object temperature from MLX90614.
- Print values to serial monitor.
- Observe whether readings change when touched, moved, covered, or aimed at different surfaces.

Success criteria:

- Serial monitor shows live PPG-related values.
- Serial monitor shows live temperature values.
- Sensor values respond when the physical environment changes.

---

## Phase 4: Basic Wearable Logic

Goal: turn raw sensor readings into basic device behavior.

Possible outputs:

- Heart-rate estimate.
- PPG signal quality estimate.
- Temperature trend.
- Basic status messages.
- Simple alerts.

Success criteria:

- Firmware loop reads sensors consistently.
- Output is understandable.
- Bad readings can be identified or filtered out instead of treated as accurate.

---

## Phase 5: User Output Modules

Goal: add simple ways for the user to interact with the device.

Possible modules:

- OLED display
- Button
- Vibration motor

Possible behaviors:

- OLED shows sensor values.
- Button switches modes.
- Vibration motor gives an alert.
- Device can show connection/status/debug info.

Success criteria:

- OLED, button, and vibration motor can each be tested independently.
- Combined code remains understandable and stable.

---

## Phase 6: Battery and Wearable Form Factor

Goal: move from desk prototype to actual wearable prototype.

Tasks:

- Test battery power.
- Estimate runtime.
- Reduce power usage.
- Decide whether to keep OLED always off, occasionally on, or removed.
- Design a simple enclosure.
- Design mounting for the MAX30102 so it maintains usable skin contact.
- Design mounting for MLX90614 so it has a consistent view of the target surface.

Success criteria:

- Device can run untethered, even briefly.
- Components fit into a rough wearable form factor.
- Sensor mounting is stable enough for testing.

---

## MVP Definition

The MVP is complete when the device can:

- Power on reliably.
- Run firmware uploaded from VS Code.
- Detect at least one body-related signal.
- Detect at least one temperature/environment signal.
- Print or display useful live data.
- Run from battery, even if runtime is short.
- Fit into a rough wearable prototype.

---

## Long-Term Ideas

- BLE phone dashboard.
- Web dashboard.
- Data logging.
- OLED UI.
- Haptic alerts.
- Better heart rate calculation.
- PPG signal quality scoring.
- Recovery/stress score experiments.
- Skin/object temperature trend tracking.
- Sleep tracking experiments.
- 3D printed enclosure.
- TPU wristband.
- Lower-power firmware.
