# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Experimental wearable prototype using Seeed Studio XIAO ESP32S3. Collects body/environment signals via two I2C sensors. Not a medical device — readings are experimental.

**Current phase:** Phase 2 — I2C sensor detection (board bring-up complete).

**Target form factor:** Wristband/watch. Planned build approach: module assembly (XIAO + breakout boards in a 3D-printed TPU enclosure — no custom PCB). Sensors go skin-facing; XIAO on top. XIAO's built-in LiPo connector and charging IC eliminates a separate charging board.

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

**Component images:** `.claude/docs/component_images/xiao_esp32s3/` — `top_view.png`, `angled_front.png`, `pinout_back.png`, `pinout_back_angled.png`, `size_reference.png`, `with_antenna_connected.png`, `with_antenna_disconnected.png`

- **Board:** Seeed Studio XIAO ESP32S3
- **PlatformIO ID:** `seeed_xiao_esp32s3`
- **Framework:** Arduino (C++)
- **Port:** `/dev/cu.usbmodem1101` — can change after replug; update `upload_port` and `monitor_port` in `platformio.ini` if so
- **Chip (confirmed by esptool):** ESP32-S3 (QFN56) revision v0.2, Embedded PSRAM 8MB (AP_3v3), Crystal 40MHz, USB mode: USB-Serial/JTAG

**If upload hangs at `Connecting...`:**
1. Hold B (BOOT), start upload, tap R (RESET) when it says Connecting, release B.

**After opening serial monitor:** tap RESET on the board to catch `setup()` output — the monitor connects after boot.

**Serial monitor disconnect on reset:** USB-Serial/JTAG briefly drops (`[Errno 6] Device not configured`) when the board resets via RTS, then reconnects automatically. This is normal — wait for "Connected!" before tapping RESET to catch output.

## Hardware & I2C

**Component images:**
- MAX30102: `.claude/docs/component_images/max30102/` — `breakout_front_with_headers.png`, `breakout_front_back.png`, `schematic_redboard.png`
- MLX90614: `.claude/docs/component_images/mlx90614_gy906/` — `breakout_front_with_headers.png`, `breakout_front_no_headers.png`, `breakout_back.png`
- LiPo battery (402030, 3.7V 250mAh, 30×20×4mm): `.claude/docs/component_images/lipo_402030/` — `dimensions_diagram.png`, `product_photo.png`, `polarity_labels.png`

All sensors share one I2C bus (same SDA/SCL pins). Both powered from 3.3V only — **never connect to 5V**, it will damage the sensors.

| Sensor | Role | I2C address |
|---|---|---|
| MAX30102 | Heart rate / PPG | `0x57` |
| MLX90614 (GY-906) | Non-contact IR temperature | `0x5A` |

Wiring: `XIAO 3.3V → VIN`, `GND → GND`, `SDA → SDA`, `SCL → SCL` for both. Leave MAX30102 INT/RD/IRD unconnected unless needed. XIAO I2C pins: SDA = GPIO5, SCL = GPIO6 — `Wire.begin()` uses these by default, no need to specify in code.

**XIAO physical pin positions (left side, USB-C end at top, counting down):** D0, D1, D2, D3, D4/SDA, D5/SCL, TX. **Right side (counting down):** 5V, GND, 3V3, D10, D9, D8, D7. For breadboard wiring: SDA is the 5th pin down on the left, SCL is the 6th pin down on the left.

**MAX30102 physical note:** The breakout board's edge curvature only accepts 4 pins in the middle (VIN, GND, SDA, SCL) — this is sufficient. The INT/RD pins on the ends cannot be used without soldering directly to the board.

**MAX30102 header state:** No pins soldered. Contact is currently established via **header pins inserted through MAX30102 PCB holes into the breadboard, with jumper wires on the same breadboard rows connecting to the XIAO** — confirmed ACKing at 0x57 as of 2026-06-24. This approach produces intermittent contact; slight movement causes connection loss (see Error -1 below). Soldering the 4 pins (VIN, GND, SDA, SCL) is the only reliable fix. Earlier breadboard approaches (pressure-fit, header-pins-long-side-down without PCB hole insertion) also failed — PCB hole insertion is what makes row contact viable at all.

**I2C speed:** `I2C_SPEED_FAST` (400kHz) was too aggressive for breadboard wiring and contributed to read errors. Use `I2C_SPEED_STANDARD` (100kHz) in firmware for reliable operation over jumper wires.

**MAX30102 `Error -1`:** The SparkFun library returns -1 when the device stops ACKing mid-read. This means physical I2C contact was lost (breadboard connection shifted), not a firmware bug. If it appears in a flood after valid reads, re-stabilize the breadboard connections or solder the header pins.

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

**Current state (2026-06-24):** MAX30102 confirmed at `0x57` via header pins through PCB holes into breadboard rows. `src/main.cpp` is the I2C scanner running in `loop()` with a 3 s delay — repeatedly prints all discovered I2C addresses. SparkFun library (`MAX30105.h`) is installed (`SparkFun MAX3010x Pulse and Proximity Sensor Library@1.1.2`) and available for the next step. The PPG sketch (reads Red and IR; IR >50,000 indicates finger contact) was tested during session 2026-06-24 but the file was reverted to the scanner for continued bus validation.

**Remaining Phase 2:** MLX90614 (0x5A) not yet wired as of 2026-06-22. Wire it and re-run the I2C scanner (or extend the PPG sketch) to confirm it ACKs before adding Adafruit MLX90614 library code.

Sensor libraries must be declared in `platformio.ini` under `lib_deps` before they can be `#include`d:
- MAX30102: `sparkfun/SparkFun MAX3010x Pulse and Proximity Sensor Library`
- MLX90614: `adafruit/Adafruit MLX90614 Library`

PlatformIO fetches and links them automatically on the next `pio run` after adding.
