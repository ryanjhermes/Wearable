# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Experimental wearable prototype on a Seeed Studio XIAO ESP32S3. Collects body/environment signals
via I2C sensors. Not a medical device — readings are experimental.

**Status:** Phase 3 (sensor reads) is **COMPLETE**. MAX30102 heart rate and BMI160 motion both
read live and are CONFIRMED simultaneously on the shared I2C bus. BLE HR streaming works
untethered on battery. Battery power CONFIRMED working. Open work: enclosure (target form factor
wristband/watch, module assembly in 3D-printed TPU — no custom PCB; min footprint ~57×24×11mm).

**Candidate application (exploratory, not committed):** replicate Kaczor et al., *"Detecting Ethanol
Intoxication and Impairment Using Wearable Biosensors"* (HICSS 2026) — a wrist HR + skin-temp + EDA +
accelerometry combo with an XGBoost model (~0.80 accuracy). Three of four channels map to existing
parts (MAX30102=HR, MLX90614=temp, BMI160=accel); the missing channel is **EDA/GSR**, which is
**analog, not I2C** — read as a voltage on an ADC pin (D0/A0) via oversampled `analogRead()`, gated on
BMI160 motion ≈ 0. Candidate module: Seeed Grove GSR. No unit ordered.

## Toolchain

PlatformIO runs in a local venv. `source .venv/bin/activate` once per shell, then use `pio`.
Do NOT `pip install` system-wide. Every `pio run`/`upload` MUST name an env with `-e`.

```bash
source .venv/bin/activate
pio run                                # build ALL envs
pio run -e <env> -t upload             # build + upload one env (close the monitor first)
pio device monitor -e <env>            # serial monitor, 115200 baud, Ctrl+C to exit
pio device list                        # find the port if upload fails (match 303A:1001)
```

### Environments (`platformio.ini`, one folder per env under `src/<env>/main.cpp`)

| Env | Purpose | Monitor filter → output |
|---|---|---|
| `max30102_heartrate` | Live HR read (SparkFun MAX3010x) | default |
| `mlx90614_temperature` | Non-contact IR temp (direct `Wire`, no lib) | default |
| `bmi160_motion` | BMI160 6-axis accel+gyro, 1 Hz | default |
| `bmi160_motion_log` | BMI160 ~50 Hz CSV logger | `motion_csv` → `data/motion_*.csv` |
| `i2c_scanner` | Shared-bus address scanner | default |
| `combined_hr_temp` | MAX30102 HR + MLX90614 temp | `csv_capture` → `data/run_*.csv` |
| `combined_hr_motion` | MAX30102 HR + BMI160 motion (watch live) | `csv_capture` (writes empty run_*.csv — see note) |
| `max30102_hr_log` | HR → LittleFS CSV logger | `flash_dump` → `data/hr_flash_*.csv` |
| `max30102_hr_ble` | HR → BLE stream (untethered) | — (use `scripts/ble_hr_stream.py`) |
| `battery_blink` | Onboard-LED blink, no serial dep — battery test | — |

**Filter gotcha:** the shared default filter `csv_capture` only matches HR/temp line format, so
`combined_hr_motion` writes an *empty* `run_*.csv` (header only). For motion charting use
`bmi160_motion_log`; `combined_hr_motion` is for watching both sensors live, not logging. Same
trap for `max30102_hr_ble` if you open the monitor on it: it inherits the `csv_capture` default but
prints the comma format `t_ms,avg_bpm,last_bpm,beats,ir,finger  ble=advertising`, which the filter
ignores → empty `run_*.csv`. Its ONLY data path is BLE (no flash logging) — capture via
`scripts/ble_hr_stream.py`; serial is watch-only.

## Repo Layout

- `src/<env>/main.cpp` — firmware, one folder per PlatformIO env (see table). Split from a single
  `src/main.cpp` on 2026-07-12 via `build_src_filter`; shared settings live under `[env]`.
- `platformio.ini` — build/upload/monitor config; **source of truth for the serial port**.
- `monitor/filter_*.py` — serial-monitor capture filters: `filter_csv_capture.py`,
  `filter_motion_csv.py`, `filter_flash_dump.py`. Wired per-env via `monitor_filters`.
- `scripts/ble_hr_stream.py` — Mac-side BLE client (`pip install bleak`); streams `Wearable-HR`
  to terminal and saves `data/ble_hr_*.csv`.
- `notebooks/` — plotters: `plot_combined_run.ipynb`, `plot_motion_run.ipynb`, `plot_ble_hr.ipynb`.
- `data/` — captured CSVs.
- `.claude/docs/*.md` — background docs (not authoritative; this file wins on conflict):
  `project_plan.md` (6-phase roadmap), `wearable_hardware.md` (component specs), `wiring.md`
  (I2C wiring tables + scanner troubleshooting), `development_setup.md` (PlatformIO/upload recovery),
  `hardware_debug_log.md` (historical bring-up narrative — battery, MLX, HR, bus sagas).
- `.claude/docs/component_images/` — reference photos (`xiao_esp32s3/`, `max30102/`,
  `mlx90614_gy906/`, `lipo_402030/`, `bmi160/`).

Wi-Fi is out of scope; BLE (onboard antenna) is used for HR streaming.

## Board

- **Board:** Seeed Studio XIAO ESP32S3 — PlatformIO ID `seeed_xiao_esp32s3`, Arduino framework.
  ESP32-S3 (QFN56) rev v0.2, 8MB PSRAM, USB-Serial/JTAG (no drivers). Current board serial
  `SER=E0:72:A1:FC:4F:80` (swapped in fresh 2026-07-19 — see debug log).
- **Port:** `/dev/cu.usbmodem101` — the name flips on each replug. If upload/monitor fails with
  "No such file or directory," run `pio device list`, match the `303A:1001` entry, and update
  `upload_port`/`monitor_port` in `platformio.ini`.
- **Pin positions** (USB-C at top): left side top→bottom `D0, D1, D2, D3, D4/SDA, D5/SCL, TX`;
  right side `5V, GND, 3V3, D10, D9, D8, D7`. I2C: SDA=GPIO5, SCL=GPIO6 (`Wire.begin()` defaults).

**Upload/monitor procedure:**
- Close the serial monitor before uploading — else `esptool` fails with `[Errno 35] Resource
  temporarily unavailable` (port busy).
- If upload hangs at `Connecting...`: hold BOOT, start upload, tap RESET when it says Connecting,
  release BOOT.
- After opening the monitor, tap RESET to catch `setup()` output (monitor connects after boot;
  firmware has `delay(2000)` after `Serial.begin()` for a catch window).
- On reset, USB-Serial/JTAG briefly drops (`[Errno 6] Device not configured`) then reconnects —
  normal; wait for "Connected!" before tapping RESET.
- **USB+battery quirk:** enumeration fails when both are connected. Flash with the battery
  unplugged; BLE runs fine on battery alone afterward.

## Hardware & I2C

All sensors share one I2C bus (SDA=GPIO5, SCL=GPIO6). Power from **3.3V only — never 5V** (damages
sensors). Wiring: `3V3→VIN, GND→GND, SDA→SDA, SCL→SCL`. Headers are soldered on both breakouts.

| Sensor | Role | I2C address | State |
|---|---|---|---|
| MAX30102 | Heart rate / PPG | `0x57` | Healthy, HR CONFIRMED |
| BMI160 (GY-BMI160) | 6-axis accel + gyro | `0x69` (this HiLetgo unit; SDO/SA0 pull selects 0x68/0x69; chip ID `0xD1` at reg `0x00`) | CONFIRMED live |
| MLX90614 (GY-906) | Non-contact IR temp | `0x5A` | **Suspected dead** — last `Error -1` 2026-07-14; temp deprioritized |

BMI160: leave SDO/SA0, INT, CS unconnected. MAX30102: leave INT/RD/IRD unconnected; its edge
curvature only accepts the 4 middle pins (VIN/GND/SDA/SCL) — sufficient. BMI160 is Bosch EOL
(successor BMI270) — fine for a prototype.

**Off-breadboard build:** the current XIAO uses a direct-wired MAX30102 (30 AWG, no headers,
CONFIRMED HR live). Decision: skip a perfboard bus and **daisy-chain** solder the shared
3V3/GND/SDA/SCL point-to-point (I2C is a bus — device order doesn't matter). Reversible but each
reheat stresses the pad. Keep the USB-C port reachable in the enclosure (charging + reflashing).

**Battery:** LiPo 402030 (3.7V 250mAh) solders to the XIAO underside `BAT`/`GND` pads (independent
of the I2C bus). Runtime ~3–6h. Path (B) chosen: removable matching JST 1.25mm pigtail.
**Installed polarity — do NOT "correct" by wire color:** board-side **black → silkscreen `+`
(BAT+)**, board-side **red → silkscreen `−` (GND)**. Looks backwards, but the pigtail housing is
mirrored relative to the battery, so after the connector the battery's red lands on BAT+.
CONFIRMED working; board stays cool; charge IC survived an earlier reverse-polarity episode.
Full saga in `hardware_debug_log.md`.

**Verifying the battery — the serial monitor CANNOT do it** (serial rides USB; unplugging USB
always kills the monitor regardless of battery state). Use USB-independent signals:
- **Charge LED** (BAT joints conduct): battery + USB-C plugged → small charge LED near USB lights.
- **Discharge** (cell powers the board): flash `battery_blink`, unplug USB → LED keeps blinking
  = on battery ✅; goes dark = flat cell or open BAT joint.
- **Rapid heating with battery + USB = reverse polarity or a short (SAFETY, LiPo fire risk).**
  STOP, unplug both, let cool, inspect the cell. It is NOT an open-joint symptom.

**I2C diagnostic heuristics:**
- Random/shifting addresses each scan = floating bus = power/ground fault (not contact, not firmware).
- A real device ACKs at the same address every scan. Clean `(none)` = device unpowered or dead
  (not a floating-bus fault).
- MAX30102 `Error -1` (SparkFun lib) = device stopped ACKing mid-read = physical I2C contact lost,
  not a firmware bug.

## Firmware Architecture

Arduino: `setup()` once, `loop()` continuously; all sensor reads in `loop()`. No RTOS/threading.

**Non-blocking failure pattern (required on ESP32-S3):** never block in `setup()` on sensor failure.
`while(1);` — and even `while(1) delay(1);` inside `setup()` — starves the FreeRTOS loop-task watchdog
and triggers a reset loop (symptom: repeated `Disconnected → Connected!` after upload). Instead set a
`bool sensor_ok = false;` flag, let `setup()` return, and have `loop()` early-return on the flag.

**I2C speed:** use `I2C_SPEED_STANDARD` (100kHz). `I2C_SPEED_FAST` (400kHz) is too aggressive over
jumper/breadboard wiring and causes read errors.

**Direct-`Wire` sensors (no library):** MLX90614 and BMI160 are read via raw `Wire` register calls —
deliberately, to dodge a build trap (see Known Toolchain Issues), and the pattern is reusable.
- MLX90614: write reg addr, `endTransmission(false)` (repeated start), `requestFrom(addr,3)` → LSB/MSB/PEC,
  `°C = raw*0.02 − 273.15` (high bit set = error, skip). Regs `0x06`=ambient(Ta), `0x07`=object(Tobj1).
  Non-contact IR is surface temp — drifts with distance/angle/airflow, reads below core body temp.
  If revived: log **both** `0x06` and `0x07` from the start (Ta = die temp, used to regress out
  enclosure self-heating drift), gate reads on BMI160 motion ≈ 0, prefer a contact sensor (TMP117/
  MAX30205) for real temperature.
- BMI160: auto-detect at `0x68`/`0x69` via chip ID `0xD1` (reg `0x00`), power accel+gyro to normal mode
  with datasheet start-up delays, set ±2g / ±2000 dps, read the 12-byte block (gyro `0x0C`, accel `0x12`).
  Update `ACC_LSB_PER_G` / `GYR_LSB_PER_DPS` if the ranges change.
- **3D-trajectory caveat:** `plot_motion_run.ipynb`'s path is de-trended double-integrated accel — IMU
  bias drifts quadratically, so it's trustworthy for gesture *shape* only, not absolute position. The
  per-axis accel/gyro time series are the trustworthy signals.

**HR beat detection:** SparkFun `checkForBeat` + 4-beat rolling `beatAvg`, kept as-is. It needs the small
AC pulse ripple riding on the DC — a flat high steady DC (~119–122k, "pressing too hard") defeats it.
Skip the first beat until `lastBeat != 0` (else a phantom frozen `BPM=4.6`). Serial throttled to one
summary line/sec.

**BLE HR (`max30102_hr_ble`):** broadcasts as `Wearable-HR` — standard Heart Rate service (0x180D) for
generic apps + a custom telemetry notify with CSV `t_ms,avg_bpm,last_bpm,beats,ir,finger`. Untethered
workflow: flash over USB (battery out), unplug USB, power from battery, run `scripts/ble_hr_stream.py`.

**HR flash logger (`max30102_hr_log`):** 1 Hz CSV `t_ms,avg_bpm,last_bpm,beats,ir,finger` appended to
LittleFS (`/hr_log.csv`, capped 512 KB). Serial commands: `d`=dump (`---FLASH_DUMP_BEGIN/END---`),
`e`=erase, `i`=size.

## Known Toolchain Issues

- **Do NOT use `adafruit/Adafruit MLX90614 Library`** — it pulls in Adafruit BusIO, which fails to
  compile under this toolchain (`fatal error: SPI.h: No such file or directory`) even though MLX90614
  is I2C-only. Read the MLX directly via `Wire` instead. `robtillaart/MLX90614` is not a valid registry
  name either. Only `sparkfun/SparkFun MAX3010x` is declared in `lib_deps`.
- `toolchain-riscv32-esp` is a PlatformIO dep not needed for ESP32-S3 (Xtensa); a stub at
  `~/.platformio/packages/toolchain-riscv32-esp/` prevents download loops.
- PlatformIO mirrors occasionally fail SSL (`[SSL] record layer failure`) — it retries other mirrors,
  wait it out. `framework-arduinoespressif32` is ~3GB installed (need ≥5GB free before first build).
