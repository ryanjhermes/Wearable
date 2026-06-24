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

### Physical dimensions

| Dimension | Value |
|---|---|
| Length | 21.5 mm |
| Width | 17.5 mm |
| Thickness | 3.5 mm |

The PCB fits within a roughly 22 × 18 mm footprint — comfortably inside a 38 mm watch case diameter.

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

### Physical dimensions

Two common breakout variants exist:

| Variant | PCB size | Notes |
|---|---|---|
| HiLetgo (in use) | 14 mm × 14 mm | Compact; the one we have |
| Generic large variant | ~25 mm × 20 mm | Common on Amazon/AliExpress, avoid for enclosure work |
| IC bare die | 5.6 mm × 3.3 mm × 1.6 mm | Could be used on a custom PCB later |

The HiLetgo board's 14 × 14 mm footprint is well-suited for a watch enclosure. Module height (components + PCB) is approximately 3–4 mm.

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

### Physical dimensions

| Dimension | Value |
|---|---|
| PCB length | ~17 mm |
| PCB width | ~15 mm |
| Module height | ~3–4 mm (estimated, varies by supplier) |

The GY-906 footprint is similar in size to the HiLetgo MAX30102, making them roughly stackable or placeable side by side in an enclosure.

### Notes

- This sensor measures **surface/object temperature**, not true internal body temperature.
- For skin measurements, readings can be affected by distance, angle, sweat, airflow, and ambient temperature.
- It shares the same I2C bus as the MAX30102, so both can connect to the same SDA/SCL lines.
- Good early test: confirm it appears in an I2C scan.

---

## 4. Battery

### OXWINOU 402030 LiPo — 3.7V 250mAh (2-pack)

**Role:** Primary power source for the wearable. The XIAO ESP32S3 includes onboard LiPo charging, so this connects directly to the XIAO battery connector.

### Key specs

| Feature | Value |
|---|---|
| Model | 402030 |
| Chemistry | Lithium Polymer (LiPo) |
| Nominal voltage | 3.7V |
| Capacity | 250 mAh |
| Energy | 0.92 Wh |
| Connector | JST-style 2-pin with red/black leads |
| Comes in | 2-pack |

### Physical dimensions

The model number directly encodes the size: **4 mm thick × 20 mm wide × 30 mm long**.

| Dimension | Value |
|---|---|
| Thickness | 4 mm |
| Width | 20 mm |
| Length | 30 mm |

At 4 mm thick, this is well-suited for a slim watch profile. The 20 × 30 mm footprint is smaller than the XIAO and fits within a 38 mm case.

### Notes

- The XIAO ESP32S3 has a JST 1.25mm 2-pin battery connector — verify the OXWINOU connector pitch matches before plugging in. If needed, the connector can be swapped.
- Never charge above 4.2V or discharge below 3.0V. The XIAO's onboard charger handles this if wired correctly.
- The 2-pack means one spare — keep the second cell for a backup or a parallel wiring experiment.
- LiPo cells are sensitive to puncture and over-compression. Enclosure design must not apply pressure directly to the cell body.

---

## Shared Communication Bus

Both the MAX30102 and MLX90614 use **I2C**, meaning they can share the same two data wires:

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

---

## Enclosure Planning (Watch Form Factor)

### Component footprint summary

| Component | Length | Width | Height/Thickness |
|---|---|---|---|
| XIAO ESP32S3 | 21.5 mm | 17.5 mm | 3.5 mm |
| MAX30102 (HiLetgo) | 14 mm | 14 mm | ~3–4 mm |
| OXWINOU 402030 LiPo | 30 mm | 20 mm | 4 mm |

> MLX90614 excluded from current layout — Phase 1 module is XIAO + MAX30102 + battery only.

### Committed layout

```
Side view (cross-section):
┌─────────────────────────────────┐
│   Battery  30 × 20 × 4 mm      │  ← top layer
├──────────────────┬──────────────┤
│  XIAO            │  MAX30102    │  ← bottom layer
│  21.5 × 17.5mm   │  14 × 14mm  │
└──────────────────┴──────────────┘
        wrist side (skin-facing)
```

**Bottom layer:** XIAO and MAX30102 placed side by side.
- Combined width: 17.5 + 14 = **31.5 mm**
- Combined depth: XIAO drives this at **21.5 mm**

**Top layer:** Battery lies flat across both bottom components.
- Battery length (30 mm) ≈ combined bottom width (31.5 mm) — **1.5 mm delta**, negligible
- Battery width (20 mm) ≈ XIAO depth (21.5 mm) — near-full coverage

**Total module footprint:** ~31.5 mm × 21.5 mm × 11–12 mm thick

| Layer | Thickness |
|---|---|
| Bottom (XIAO / MAX30102) | ~3.5–4 mm |
| Top (battery) | 4 mm |
| Enclosure walls (top + bottom) | ~2.4–4 mm (1.2–2 mm per wall) |
| **Total estimated** | **~10–12 mm** |

This lands in Apple Watch SE territory (~10.7 mm) at the thin end.

### Watch case sizing context

Consumer smartwatch cases typically run 38–46 mm in diameter and 10–14 mm thick. Reference points:

| Reference device | Case size | Thickness |
|---|---|---|
| Apple Watch SE | 40 mm | ~10.7 mm |
| Apple Watch Ultra | 49 mm | ~14.4 mm |
| Garmin Forerunner 265 | 46 mm | ~13.4 mm |
| **This module (estimated)** | **~35 mm diagonal** | **~10–12 mm** |

### Enclosure design considerations

- **Sensor placement:** MAX30102 must face the skin (wrist-side of enclosure) with an optical window cut-out aligned to the sensor's LED/photodetector.
- **Custom PCB path:** Replacing breakout boards with bare ICs on a single PCB would collapse the bottom layer to ~1.6 mm and allow a much thinner final enclosure.
- **3D printing:** Plan for 1.2–2 mm wall thickness minimum. Bottom wall needs a precise optical window for MAX30102.
- **Strap attachment:** Standard 20–22 mm lug width is common for DIY wearables and compatible with off-the-shelf bands.
