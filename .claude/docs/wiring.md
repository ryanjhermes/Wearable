# Wiring Guide

This document tracks the initial wiring plan for the wearable prototype.

---

## Core Rule

The XIAO ESP32S3 uses 3.3V logic.

For this project, prefer powering sensors from:

```text
3.3V
```

unless the exact module documentation clearly says otherwise.

---

## Shared I2C Bus

Both initial sensors use I2C:

- MAX30102 heart rate / PPG sensor
- MLX90614 / GY-906 infrared temperature sensor

I2C uses two shared signal wires:

```text
SDA = data
SCL = clock
```

Multiple I2C devices can share the same SDA and SCL lines as long as they have different addresses.

---

## Expected I2C Addresses

| Component | Expected address |
|---|---|
| MAX30102 | `0x57` |
| MLX90614 | `0x5A` |

---

## Basic I2C Wiring Pattern

```text
XIAO 3.3V  → Sensor VIN/VCC
XIAO GND   → Sensor GND
XIAO SDA   → Sensor SDA
XIAO SCL   → Sensor SCL
```

Both sensors can connect to the same SDA and SCL pins.

---

## MAX30102 Wiring

| MAX30102 pin | Purpose | Connect to XIAO ESP32S3 |
|---|---|---|
| VIN | Power input | 3.3V preferred |
| GND | Ground | GND |
| SCL | I2C clock | SCL |
| SDA | I2C data | SDA |
| INT | Interrupt | Optional GPIO |
| RD | Red LED ground terminal | Usually not connected |
| IRD | IR LED ground terminal | Usually not connected |

Notes:

- Start with only VIN, GND, SCL, and SDA.
- Leave INT disconnected until needed.
- Leave RD and IRD disconnected unless a specific library/module guide says otherwise.
- Sensor placement and skin contact matter a lot for useful readings.

---

## MLX90614 / GY-906 Wiring

| MLX90614 / GY-906 pin | Purpose | Connect to XIAO ESP32S3 |
|---|---|---|
| VIN / VCC | Power input | 3.3V preferred |
| GND | Ground | GND |
| SCL | I2C clock | SCL |
| SDA | I2C data | SDA |

Notes:

- The sensor reads object/surface temperature, not core body temperature.
- Readings can change based on distance, angle, airflow, sweat, and ambient conditions.
- Keep the sensor pointed consistently during tests.

---

## Initial Full Wiring Plan

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

## Breadboard Notes

If using a breadboard:

- Power rails usually run vertically along the side.
- Regular rows usually connect horizontally in groups of 5.
- The center gap separates the two sides of the breadboard.
- Multiple sensors can share the same 3.3V and GND rails.
- Multiple I2C sensors can share SDA and SCL.

---

## I2C Scanner Test

Before writing real sensor code, run an I2C scanner.

Expected successful result:

```text
I2C device found at 0x57
I2C device found at 0x5A
```

If neither appears:

- Check 3.3V and GND.
- Check SDA/SCL are not swapped.
- Check loose jumper wires.
- Test one sensor at a time.
- Confirm the board is running the scanner firmware.

If only one appears:

- Test the missing sensor alone.
- Check whether the missing sensor has a different address.
- Check solder joints/header pins.
