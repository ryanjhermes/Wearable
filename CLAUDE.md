# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Experimental wearable prototype using Seeed Studio XIAO ESP32S3. Collects body/environment signals via two I2C sensors. Not a medical device — readings are experimental.

**Current phase:** Phase 2 — I2C sensor detection (board bring-up complete).

## Toolchain

PlatformIO is installed in a local venv. Always use it via:

```bash
source .venv/bin/activate   # once per shell session
pio run                     # build
pio run -t upload           # upload
pio device monitor          # serial monitor (115200 baud), exit with Ctrl+C
pio device list             # check port if upload fails
```

Do not use `python3 -m pip install` system-wide — use the venv.

## Board

- **Board:** Seeed Studio XIAO ESP32S3
- **PlatformIO ID:** `seeed_xiao_esp32s3`
- **Framework:** Arduino (C++)
- **Port:** `/dev/cu.usbmodem1101` — can change after replug; update `upload_port` and `monitor_port` in `platformio.ini` if so

**If upload hangs at `Connecting...`:**
1. Hold B (BOOT), start upload, tap R (RESET) when it says Connecting, release B.

**After opening serial monitor:** tap RESET on the board to catch `setup()` output — the monitor connects after boot.

## Hardware & I2C

All sensors share one I2C bus (same SDA/SCL pins). Both powered from 3.3V.

| Sensor | Role | I2C address |
|---|---|---|
| MAX30102 | Heart rate / PPG | `0x57` |
| MLX90614 (GY-906) | Non-contact IR temperature | `0x5A` |

Wiring: `XIAO 3.3V → VIN`, `GND → GND`, `SDA → SDA`, `SCL → SCL` for both. Leave MAX30102 INT/RD/IRD unconnected unless needed.

## Known Toolchain Issues

- `toolchain-riscv32-esp` is a PlatformIO dependency that is not needed for ESP32S3 (Xtensa). A stub package lives at `~/.platformio/packages/toolchain-riscv32-esp/` to prevent download loops.
- PlatformIO mirrors occasionally fail SSL (`[SSL] record layer failure`). It retries other mirrors automatically — wait it out.
- The Arduino ESP32 framework (`framework-arduinoespressif32`) is ~3GB installed. Ensure at least 5GB free before first build.

## Firmware Architecture

Single-file firmware at `src/main.cpp`. Arduino framework: `setup()` runs once, `loop()` runs continuously. All sensor reads go in `loop()`. No RTOS, no threading currently.

Future sensor libraries to add via `platformio.ini` `lib_deps`:
- MAX30102: search for `sparkfun/SparkFun MAX3010x Pulse and Proximity Sensor Library`
- MLX90614: search for `adafruit/Adafruit MLX90614 Library`
