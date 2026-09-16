# Wearable Hardware List

This document tracks the main hardware components used in the wearable prototype, including the microcontroller, sensors, interfaces, and notes for wiring/software.

---

## 1. Main Microcontroller

### Seeed Studio XIAO ESP32S3

**Role:** Main wearable controller. Handles sensor reads, local processing, wireless communication, and battery-powered operation.

### Key specs

| Feature | Value |
|---|---|
| Chip | ESP32-S3 |
| CPU | Dual-core, up to 240 MHz |
| Wireless | 2.4 GHz Wi-Fi, BLE 5.0 |
| Flash | 8 MB |
| PSRAM | 8 MB |
| USB | USB-C |
| Supported frameworks | Arduino, MicroPython, ESP-IDF |
| Battery support | LiPo battery charging supported, depending on board version |
| Logic voltage | 3.3V |

### Why we are using it

The XIAO ESP32S3 is small enough for a wearable while still having Wi-Fi, BLE, enough memory for sensor processing, and support for both C++/Arduino and MicroPython.

### Notes

- macOS currently detects the board at:

```text
/dev/cu.usbmodem1101
```

- PlatformIO board ID:

```ini
seeed_xiao_esp32s3
```

- Best early development path:

```text
VS Code + PlatformIO + Arduino framework
```

- Possible future Python path:

```text
MicroPython or CircuitPython
```

---

## 2. Heart Rate / Blood Oxygen Sensor

### MAX30102 Pulse Oximeter and Heart Rate Sensor Module

**Role:** Optical sensor for measuring pulse-related signals using PPG. Potentially usable for heart rate, pulse waveform, and rough blood oxygen experiments.

### Key specs

| Feature | Value |
|---|---|
| Sensor | MAX30102 |
| Signal type | Optical reflection / PPG |
| LEDs | Red + infrared |
| LED wavelengths | ~660 nm red, ~880 nm infrared |
| Interface | I2C |
| Main power input | 1.8V–5V depending on breakout |
| Logic/interface voltage | Typically 1.8V–3.3V, module may tolerate 5V depending on breakout |
| Interrupt pin | Available as `INT` |

### Pins

| Pin | Purpose | Connects to XIAO ESP32S3 |
|---|---|---|
| VIN | Power input | 3.3V preferred |
| GND | Ground | GND |
| SCL | I2C clock | XIAO SCL |
| SDA | I2C data | XIAO SDA |
| INT | Interrupt output | Optional GPIO |
| RD | Red LED ground terminal | Usually not connected |
| IRD | IR LED ground terminal | Usually not connected |

### Notes

- Use **3.3V** with the XIAO unless the exact breakout documentation says otherwise.
- The MAX30102 is sensitive to placement, movement, and pressure against the skin.
- For a wearable, physical mounting matters almost as much as code.
- Good early test: confirm it appears in an I2C scan.
- Avoid describing this as a medical-grade blood oxygen sensor. In this project, it should be treated as an experimental PPG/pulse oximetry module.

---

## 3. Non-Contact Temperature Sensor

### HiLetgo GY-906 / MLX90614ESF Infrared Temperature Sensor Module

**Role:** Non-contact infrared temperature sensor. Measures object temperature without direct contact. Could be used for skin-surface temperature experiments, ambient/object temperature comparisons, or environment-aware wearable behavior.

### Key specs

| Feature | Value |
|---|---|
| Sensor | MLX90614ESF |
| Measurement type | Non-contact infrared temperature |
| Interface | I2C / SMBus |
| Sensor temperature range | -40°C to +125°C |
| Object temperature range | -70°C to +380°C |
| Accuracy | Around ±0.5°C in common calibrated ranges |
| Resolution | 0.02°C |
| Pull-ups | Module includes I2C pull-up resistors |
| Low power support | Sleep mode available |

### Pins

Typical GY-906 module pins:

| Pin | Purpose | Connects to XIAO ESP32S3 |
|---|---|---|
| VIN / VCC | Power input | 3.3V preferred |
| GND | Ground | GND |
| SCL | I2C clock | XIAO SCL |
| SDA | I2C data | XIAO SDA |

### Notes

- This sensor measures **surface/object temperature**, not true internal body temperature.
- For skin measurements, readings can be affected by distance, angle, sweat, airflow, and ambient temperature.
- It shares the same I2C bus as the MAX30102, so both can connect to the same SDA/SCL lines.
- Good early test: confirm it appears in an I2C scan.

---

## 4. Motion Sensor (Accelerometer + Gyroscope)

### HiLetgo BMI160 6-axis IMU Module (GY-BMI160)

**Role:** 6-axis inertial measurement — 3-axis accelerometer + 3-axis gyroscope. For the wearable: motion/activity detection, orientation, and (via the chip's hardware pedometer) step counting.

### Key specs

| Feature | Value |
|---|---|
| Sensor | Bosch BMI160 |
| Axes | 3-axis accel + 3-axis gyro (6 DOF) |
| Interface | I2C / SPI (we use **I2C**) |
| ADC | 16-bit per axis |
| Accel range | ±2 / ±4 / ±8 / ±16 g |
| Gyro range | ±125 / ±250 / ±500 / ±1000 / ±2000 °/s |
| Module supply (VIN) | 3–5V per listing — **use 3.3V** to keep bus logic at 3.3V |
| Logic voltage | 3.3V (chip VDDIO) |
| Module size | 13 × 18 mm |
| Upper temp rating | 85°C |
| I2C address | `0x68` (SDO low) or `0x69` (SDO high) |
| Sourcing | HiLetgo, ASIN B082KQ7L97, model BMI160, purchased 2026-06-30 |

### Pins

| Pin | Purpose | Connects to XIAO ESP32S3 |
|---|---|---|
| VIN | Power input | **3.3V** (never 5V — see note) |
| GND | Ground | GND |
| SCL | I2C clock | XIAO SCL |
| SDA | I2C data | XIAO SDA |
| SDO / SA0 | I2C address select | Leave unconnected (sets 0x68/0x69) |
| CS | Interface select (I2C when high) | Usually not connected |
| INT1 / INT2 | Interrupt outputs | Optional GPIO |

### Notes

- **Power at 3.3V, not 5V.** The listing rates VIN up to 5V, but this module shares an I2C bus with the MAX30102 and MLX90614 (3.3V parts). If VIN has no level shifting, 5V would put 5V logic on SDA/SCL and could damage the other two sensors. Keep the whole bus at 3.3V.
- Address does not conflict with 0x57 (MAX30102) or 0x5A (MLX90614).
- Firmware reads registers directly over `Wire` (no library) to avoid the Adafruit BusIO build failure documented for the MLX90614.
- The BMI160 is **Bosch end-of-life** (successor: BMI270). Fine for a prototype; note it if the design heads toward anything durable.
- Good early test: confirm it appears in an I2C scan at 0x68 or 0x69.

**Reference images:** `.claude/docs/component_images/bmi160/` (empty — to be populated).

---

## Shared Communication Bus

The MAX30102, MLX90614, and BMI160 all use **I2C**, meaning they can share the same two data wires:

```text
XIAO SDA → Sensor SDA
XIAO SCL → Sensor SCL
XIAO 3.3V → Sensor VIN/VCC
XIAO GND → Sensor GND
```

Each sensor has its own I2C address, so the XIAO can talk to them separately over the same bus.

### Expected I2C devices

| Component | Typical I2C address |
|---|---|
| MAX30102 | 0x57 |
| MLX90614 | 0x5A |
| BMI160 | 0x68 or 0x69 |

---

## Initial Wiring Plan

```text
XIAO ESP32S3 3.3V  → MAX30102 VIN
XIAO ESP32S3 GND   → MAX30102 GND
XIAO ESP32S3 SDA   → MAX30102 SDA
XIAO ESP32S3 SCL   → MAX30102 SCL

XIAO ESP32S3 3.3V  → MLX90614 VCC/VIN
XIAO ESP32S3 GND   → MLX90614 GND
XIAO ESP32S3 SDA   → MLX90614 SDA
XIAO ESP32S3 SCL   → MLX90614 SCL

XIAO ESP32S3 3.3V  → BMI160 VIN   (3.3V only — not 5V)
XIAO ESP32S3 GND   → BMI160 GND
XIAO ESP32S3 SDA   → BMI160 SDA
XIAO ESP32S3 SCL   → BMI160 SCL
```

---

## Development Notes

### Current software direction

Start with:

```text
VS Code + PlatformIO + Arduino framework
```

Reason:

- Better library support for sensors.
- Easier upload/debug path than pure ESP-IDF.
- Cleaner project structure than Arduino IDE.
- Still compatible with AI-assisted development in VS Code.

### Possible later direction

Use MicroPython for simpler iteration if the sensor support is good enough.

Potential MicroPython use cases:

- Simple I2C scan
- Button testing
- OLED display testing
- Basic temperature readings
- Simple wearable logic

Potential C++/Arduino use cases:

- More reliable MAX30102 readings
- BLE communication
- Battery optimization
- Long-running wearable firmware
- Lower-power sleep behavior

---

## Project Goal

Build a small wearable prototype that can collect basic body/environment signals, such as:

- Heart-rate-related PPG data
- Possible SpO2 experiments
- Skin/object temperature
- Motion or button inputs later
- BLE/Wi-Fi data transfer later
- Optional vibration/display output later

This is an experimental prototype, not a medical device.
