# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Experimental wearable prototype using Seeed Studio XIAO ESP32S3. Collects body/environment signals via two I2C sensors. Not a medical device — readings are experimental.

**Current phase:** Phase 2 — I2C sensor detection (board bring-up complete).

## Toolchain

PlatformIO is installed in a local venv. Always use it via:

```bash
source .venv/bin/activate            # once per shell session
pio run                              # build
pio run -e seeed_xiao_esp32s3        # build targeting the named env explicitly
pio run -t upload                    # build + upload
pio device monitor                   # serial monitor (115200 baud), exit with Ctrl+C
pio device list                      # check port if upload fails
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

All sensors share one I2C bus (same SDA/SCL pins). Both powered from 3.3V only — **never connect to 5V**, it will damage the sensors.

| Sensor | Role | I2C address |
|---|---|---|
| MAX30102 | Heart rate / PPG | `0x57` |
| MLX90614 (GY-906) | Non-contact IR temperature | `0x5A` |

Wiring: `XIAO 3.3V → VIN`, `GND → GND`, `SDA → SDA`, `SCL → SCL` for both. Leave MAX30102 INT/RD/IRD unconnected unless needed. XIAO I2C pins: SDA = GPIO5, SCL = GPIO6 — `Wire.begin()` uses these by default, no need to specify in code.

**MAX30102 physical note:** The breakout board's edge curvature only accepts 4 pins in the middle (VIN, GND, SDA, SCL) — this is sufficient. The INT/RD pins on the ends cannot be used without soldering directly to the board.

**MAX30102 header state:** No pins soldered. As of session 2026-06-21, 4 loose header pins were inserted into the breadboard (long side down, short side up) and the board was lowered onto them for pressure-only contact — but it was not yet fully flush (gap visible). Before running the I2C scanner, press the board down firmly. If the I2C scanner doesn't detect the sensor, press harder before concluding failure — loose contact is the #1 false negative with this method.

**MAX30102 breadboard placement:** Sits on one half of the breadboard only — its pins are all on one side, so it cannot and does not need to straddle the center gap.

**XIAO breadboard placement:** Must straddle the center gap with pins on both sides. Placing it on one side only would create internal shorts via the breadboard's horizontal row connections.

**MLX90614 header state:** Not yet verified as of session 2026-06-21 — user deferred wiring it. Check pin state before proceeding.

**XIAO header state:** Confirmed soldered from session photos (2026-06-21).

**Setup approach:** Using jumper wires on breadboard only — no soldering at this stage.

## Known Toolchain Issues

- `toolchain-riscv32-esp` is a PlatformIO dependency that is not needed for ESP32S3 (Xtensa). A stub package lives at `~/.platformio/packages/toolchain-riscv32-esp/` to prevent download loops.
- PlatformIO mirrors occasionally fail SSL (`[SSL] record layer failure`). It retries other mirrors automatically — wait it out.
- The Arduino ESP32 framework (`framework-arduinoespressif32`) is ~3GB installed. Ensure at least 5GB free before first build.

## Firmware Architecture

Single-file firmware at `src/main.cpp`. Arduino framework: `setup()` runs once, `loop()` runs continuously. All sensor reads go in `loop()`. No RTOS, no threading currently.

**Current state:** `src/main.cpp` is a Phase 1 blink/alive sketch only — no I2C or sensor code yet. As of 2026-06-21, the I2C scanner sketch has not been written to the file; the next step is to replace the blink sketch with an I2C scanner, wire MAX30102, and confirm `0x57` appears on the serial monitor.

**Phase 2 approach:** Write an I2C scanner sketch first to confirm both sensors ACK at `0x57` and `0x5A` before writing sensor-specific code.

Sensor libraries must be declared in `platformio.ini` under `lib_deps` before they can be `#include`d:
- MAX30102: `sparkfun/SparkFun MAX3010x Pulse and Proximity Sensor Library`
- MLX90614: `adafruit/Adafruit MLX90614 Library`

PlatformIO fetches and links them automatically on the next `pio run` after adding.
