# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Experimental wearable prototype using Seeed Studio XIAO ESP32S3. Collects body/environment signals via two I2C sensors. Not a medical device — readings are experimental.

**Current phase:** Phase 3 — sensor reads — is **COMPLETE (2026-07-13)**. Both sensors read live data: MAX30102 heart-rate is done and confirmed, and the MLX90614 temperature read is now done and confirmed (see Firmware Architecture). MLX90614 detection at 0x5A is also confirmed.

**Target form factor:** Wristband/watch. Planned build approach: module assembly (XIAO + breakout boards in a 3D-printed TPU enclosure — no custom PCB). Sensors go skin-facing; XIAO on top. Minimum enclosure footprint: ~57 × 24 × 11mm (battery + XIAO + MAX30102 side-by-side).

## Repo Layout & Background Docs

- `src/<sensor>/main.cpp` — firmware, one folder per sensor: `src/max30102_heartrate/main.cpp` (heart rate) and `src/mlx90614_temperature/main.cpp` (temperature). Each folder is its own PlatformIO build environment. **This split superseded the earlier single `src/main.cpp` on 2026-07-12** (uncommitted at time of writing — the two committed sketches on `phase3-heart-rate` still live at `src/main.cpp`). See Firmware Architecture below.
- `platformio.ini` — build/upload/monitor config; the source of truth for the serial port.
- `.claude/docs/*.md` — background planning docs (not authoritative — this CLAUDE.md wins on any conflict):
  - `project_plan.md` — 6-phase roadmap (currently Phase 2) and MVP definition.
  - `wearable_hardware.md` — component spec sheets for the XIAO, MAX30102, and MLX90614.
  - `wiring.md` — I2C wiring tables and scanner-troubleshooting steps.
  - `development_setup.md` — PlatformIO/VS Code setup, boot/reset upload recovery, minimal blink sketch.
- `.claude/docs/component_images/` — reference photos (paths cited inline in the Board/Hardware sections).

Note: the docs mention BLE/Wi-Fi and MicroPython as *possible future* directions. For this prototype those are explicitly out of scope (no RF/BLE — see Board section).

## Toolchain

PlatformIO is installed in a local venv. Always use it via:

```bash
source .venv/bin/activate                     # once per shell session
pio run                                       # build ALL environments
pio run -e max30102_heartrate                 # build just the heart-rate sketch
pio run -e mlx90614_temperature               # build just the temperature sketch
pio run -e i2c_scanner                         # build the shared-bus I2C scanner
pio run -e combined_hr_temp                    # build the combined HR + temperature sketch
pio run -e combined_hr_motion                  # build the combined HR + BMI160 motion sketch
pio run -e bmi160_motion                       # build the BMI160 6-axis motion sketch
pio run -e bmi160_motion_log                    # build the ~50Hz BMI160 motion CSV logger
pio run -e max30102_heartrate -t upload       # build + upload — MUST name the env now
pio device monitor                            # serial monitor (115200 baud), exit with Ctrl+C
pio device monitor -e bmi160_motion_log       # MUST name the env for its capture filter (see note)
pio device list                               # check port if upload fails
```

Do not use `python3 -m pip install` system-wide — use the venv.

## Board

**Component images:** `.claude/docs/component_images/xiao_esp32s3/` — `top_view.png`, `angled_front.png`, `pinout_back.png`, `pinout_back_angled.png`, `size_reference.png`, `with_antenna_connected.png`, `with_antenna_disconnected.png`

- **Board:** Seeed Studio XIAO ESP32S3
- **PlatformIO ID:** `seeed_xiao_esp32s3`
- **Framework:** Arduino (C++)
- **Port:** `/dev/cu.usbmodem101` (as of 2026-07-13; was `/dev/cu.usbmodem1101` before a replug) — the name changes after replug; `platformio.ini` is the source of truth. If upload/monitor fails with "No such file or directory," run `pio device list` and match the `303A:1001` entry, then update `upload_port` and `monitor_port` in `platformio.ini`
- **Chip (confirmed by esptool):** ESP32-S3 (QFN56) revision v0.2, Embedded PSRAM 8MB (AP_3v3), Crystal 40MHz, USB mode: USB-Serial/JTAG
- **Antenna:** Not used — no RF/BLE features planned for this prototype.

**Before uploading:** close the serial monitor first (Ctrl+C). If the monitor is open, `esptool` fails with `[Errno 35] Resource temporarily unavailable` (port busy).

**If upload hangs at `Connecting...`:**
1. Hold B (BOOT), start upload, tap R (RESET) when it says Connecting, release B.

**After opening serial monitor:** tap RESET on the board to catch `setup()` output — the monitor connects after boot. Note: `pio run -t upload` auto-resets the board on completion, running `setup()` before the monitor can open. The firmware includes `delay(2000)` after `Serial.begin()` to create a window; open the monitor promptly after upload and press RESET once.

**Serial monitor disconnect on reset:** USB-Serial/JTAG briefly drops (`[Errno 6] Device not configured`) when the board resets via RTS, then reconnects automatically. This is normal — wait for "Connected!" before tapping RESET to catch output.

## Hardware & I2C

**Component images:**
- MAX30102: `.claude/docs/component_images/max30102/` — `breakout_front_with_headers.png`, `breakout_front_back.png`, `schematic_redboard.png`
- MLX90614: `.claude/docs/component_images/mlx90614_gy906/` — `breakout_front_with_headers.png`, `breakout_front_no_headers.png`, `breakout_back.png`
- LiPo battery (402030, 3.7V 250mAh, 30×20×4mm): `.claude/docs/component_images/lipo_402030/` — `dimensions_diagram.png`, `product_photo.png`, `polarity_labels.png`
- BMI160 (GY-BMI160): `.claude/docs/component_images/bmi160/` — folder created 2026-07-13, currently **empty** (no reference images yet)

**Battery wiring:** The XIAO has a `BAT` pad on the underside (visible in `pinout_back.png`) plus a charging IC. This unit has **bare pads only — no pre-installed JST connector** (confirmed from board images 2026-06-27). **The battery cell itself already ships with a 2-pin JST pigtail (red = +, black = −) — confirmed from `lipo_402030/product_photo.png` and `polarity_labels.png` (2026-07-12).** So the only work is the XIAO side: either (A) cut the JST off and solder red→`BAT`, black→`GND` directly (2 joints, battery no longer unplugs), or (B) solder a *matching* JST pigtail to the pads so the battery plugs/unplugs (removable; measure the pitch — JST 1.25mm vs PH 2.0mm — before ordering the mate). **Polarity is critical: red = BAT+, black = GND; reversing it can damage the board or vent the cell.** USB-C charges via the onboard IC regardless. Est. effort ~30–45 min. Runtime: 250mAh vs ~40–80mA active draw ≈ 3–6 h.

All sensors share one I2C bus (same SDA/SCL pins). All powered from 3.3V only — **never connect to 5V**, it will damage the sensors.

| Sensor | Role | I2C address |
|---|---|---|
| MAX30102 | Heart rate / PPG | `0x57` |
| MLX90614 (GY-906) | Non-contact IR temperature | `0x5A` |
| BMI160 (GY-BMI160) | 6-axis accel + gyro | `0x68` or `0x69` (SDO pull) |
| BMI160 | 6-axis motion (accel + gyro) | `0x68` or `0x69` (SDO/SA0 pull selects; chip ID `0xD1` at reg `0x00`) |

Wiring: `XIAO 3.3V → VIN`, `GND → GND`, `SDA → SDA`, `SCL → SCL` for all three (BMI160: leave SDO/SA0, INT, CS unconnected). Leave MAX30102 INT/RD/IRD unconnected unless needed. XIAO I2C pins: SDA = GPIO5, SCL = GPIO6 — `Wire.begin()` uses these by default, no need to specify in code.

**XIAO physical pin positions (left side, USB-C end at top, counting down):** D0, D1, D2, D3, D4/SDA, D5/SCL, TX. **Right side (counting down):** 5V, GND, 3V3, D10, D9, D8, D7. For breadboard wiring: SDA is the 5th pin down on the left, SCL is the 6th pin down on the left.

**MAX30102 physical note:** The breakout board's edge curvature only accepts 4 pins in the middle (VIN, GND, SDA, SCL) — this is sufficient. The INT/RD pins on the ends cannot be used without soldering directly to the board.

**MAX30102 header state:** Header pins **soldered by user (2026-07-12)**, superseding the earlier bare-holes/breadboard-insertion state. Detection at 0x57 post-solder is **CONFIRMED (2026-07-12)** — scanner returned a stable `0x57` on every scan (12+ consecutive, no drops, no `Error -1`), wired via **breadboard with the soldered header pins** (not the planned direct-female-jumper path). Soldering was the fix, as predicted; the breadboard is reliable once the sensor has soldered headers. Prior (pre-solder) history: intermittent breadboard contact via header pins inserted through the PCB holes ACKed at 0x57 on 2026-06-24 but dropped on movement (see Error -1 below); earlier pressure-fit approaches failed entirely. Soldering was chosen as the only reliable fix.

**I2C speed:** `I2C_SPEED_FAST` (400kHz) was too aggressive for breadboard wiring and contributed to read errors. Use `I2C_SPEED_STANDARD` (100kHz) in firmware for reliable operation over jumper wires.

**ESP32 watchdog + bare `while(1)` halt:** On ESP32S3, `while(1);` with no yield starves the FreeRTOS task watchdog and causes the board to reset, producing the same disconnect/reconnect flood as a boot loop. **Correction (2026-07-01): `while(1) delay(1);` inside `setup()` still triggers this reset loop** — the loop task watchdog needs `loop()` itself to return periodically, not just a yielding delay inside `setup()`. The reliable pattern is to let `setup()` return normally on failure (set a `bool sensor_ok = false;` flag) and have `loop()` check the flag and early-return instead of blocking. Symptom: serial monitor shows repeated `Disconnected → Connected!` cycles immediately after upload.

**MAX30102 `Error -1`:** The SparkFun library returns -1 when the device stops ACKing mid-read. This means physical I2C contact was lost (breadboard connection shifted), not a firmware bug. If it appears in a flood after valid reads, re-stabilize the breadboard connections or solder the header pins.

**MAX30102 breadboard placement:** Sits on one half of the breadboard only — its pins are all on one side, so it cannot and does not need to straddle the center gap.

**XIAO breadboard placement:** Must straddle the center gap with pins on both sides. Placing it on one side only would create internal shorts via the breadboard's horizontal row connections.

**MLX90614 header state:** Headers soldered by user (2026-07-01), superseding the earlier bare-holes/insertion-trick state. Now plugs directly into the breadboard. Pinout is **VIN GND SCL SDA** left-to-right on the breakout edge. Board has onboard 4.7kΩ pull-ups — no external pull-ups needed. **Detection at 0x5A is now CONFIRMED (2026-07-13):** wired alone (MAX disconnected) with the soldered headers, the scanner returned a **stable `0x5A` on every scan**. This closes the long detection saga — the MLX now works. Earlier in the same session it had first shown the floating/noisy-bus signature (random shifting addresses each cycle: `0x8`, then nothing, then `0x3`/`0xD`, then `0x27–0x39`) caused by a power/ground contact fault via the new header pins; re-wiring to solid contact (MLX alone, direct jumpers) fixed it and it ACKed cleanly. Confirmed heuristic: random shifting addresses = floating bus / power-ground fault; a working MLX ACKs at a stable 0x5A every scan.

**I2C scanner diagnostic heuristic:** changing/random addresses each scan = floating bus = power/ground fault (not contact, not firmware). A real device ACKs at the same address identically every scan.

**XIAO header state:** Confirmed soldered from session photos (2026-06-21).

**Setup approach:** Soldering is now the agreed path (user has iron, header pins, electrical wire, flux as of 2026-07-12) — breadboard jumper contact was too intermittent to proceed. Decision: solder **header pins** (not wires directly) to the MAX30102's 4 pins (VIN/GND/SDA/SCL), matching the MLX90614, to keep swap-in/swap-out flexibility during debugging; direct-wire soldering is deferred to the enclosure phase. Planned wiring is **female-female jumpers direct from XIAO to the soldered sensor headers, eliminating the breadboard**. Debug one sensor at a time. **This plan is fully executed and succeeded (2026-07-13):** both header sets are soldered (MLX90614 2026-07-01, MAX30102 2026-07-12) and the per-sensor scans confirmed 0x57 and 0x5A individually via direct female-jumper contact. What remains is verifying both together on the shared bus (see Firmware Architecture).

## Known Toolchain Issues

- `toolchain-riscv32-esp` is a PlatformIO dependency that is not needed for ESP32S3 (Xtensa). A stub package lives at `~/.platformio/packages/toolchain-riscv32-esp/` to prevent download loops.
- PlatformIO mirrors occasionally fail SSL (`[SSL] record layer failure`). It retries other mirrors automatically — wait it out.
- The Arduino ESP32 framework (`framework-arduinoespressif32`) is ~3GB installed. Ensure at least 5GB free before first build.
- **`adafruit/Adafruit MLX90614 Library` is unusable with this toolchain.** It pulls in `Adafruit BusIO`, which fails to compile (`fatal error: SPI.h: No such file or directory`) under PlatformIO's LDF chain mode — even though MLX90614 is I2C-only. Adding a bare `SPI` entry to `lib_deps` does not fix it. `robtillaart/MLX90614` is not a valid PlatformIO registry package name either (confirmed via failed install, 2026-07-01). Read the MLX90614 directly via `Wire` register calls instead of any library.

## Firmware Architecture

Arduino framework: `setup()` runs once, `loop()` runs continuously. All sensor reads go in `loop()`. No RTOS, no threading currently.

**Layout reorg (2026-07-12, uncommitted):** the single `src/main.cpp` was split into one folder per sensor — `src/max30102_heartrate/main.cpp` (the working heart-rate sketch) and `src/mlx90614_temperature/main.cpp` (the temperature sketch, `git mv`-d from the old `src/main.cpp`) — each wired to its own PlatformIO environment via `build_src_filter` (shared settings now live under `[env]` in `platformio.ini`; `lib_deps` is shared there too). Build/flash with `-e max30102_heartrate` or `-e mlx90614_temperature`. **Both env builds are green.** The historical narrative below predates this move and still says `src/main.cpp` — read those references as "the sketch that is now in the per-sensor folder." The heart-rate code no longer needs recovering from git — it is back in the working tree at `src/max30102_heartrate/main.cpp`.

**Current state (2026-07-12):** `src/main.cpp` is now a **MAX30102 heart-rate read sketch** (SparkFun `MAX30105`/`heartRate.h`, `checkForBeat`, 4-beat rolling `beatAvg`, non-blocking `sensor_ok` pattern), which **overwrote the I2C scanner** after 0x57 was confirmed. **Live-read status (2026-07-12): the PPG signal path is CONFIRMED working** — with a fingertip on the optical window, `IR` climbs from a ~500 baseline to a stable **~118,000** (the `< 50000` "No finger detected" threshold correctly clears), proving soldered sensor → I2C → live optical data end-to-end. **Beat detection / `Avg BPM` is still UNVERIFIED** — the first sketch had a phantom-first-beat bug (`lastBeat` initialized to 0 produced a frozen bogus `BPM=4.6`, `Avg BPM=0`); the fix now in `main.cpp` skips the first beat until `lastBeat != 0`, prints a `<-- beat!` marker per detected pulse, and zeroes the rate when the finger lifts. **The fix is CONFIRMED (2026-07-13): live reads now show `BPM=0.0` throughout, no more frozen `4.6`.** **Beat detection is now CONFIRMED working (2026-07-13):** `checkForBeat` *does* fire once a fingertip is held long enough — the earlier zero-beat captures were too short (finger settled for only ~1.5s) and/or too hard (a flat, high, steady DC level ~119,000–122,000 with no visible ripple = the "pressing too hard" signature — beat detection needs the small **AC pulse ripple** riding on the DC, e.g. IR wiggling 118500→118900→118400). The planned `checkForBeat`-replacement / custom-AC-detector rewrite was **considered but NOT applied** — the user got real beats first, so the SparkFun `checkForBeat` is kept as-is. Only the *output* was changed: `main.cpp` now **throttles serial to one summary line per second** (`Avg BPM=X  (last=Y, beats this sec=Z, IR=W)`, via `lastPrint`/`beatsThisSecond`), replacing the per-sample `<-- beat!` flood, so a 60s hold is ~60 readable lines. **Heart rate is now fully CONFIRMED end-to-end (2026-07-13):** a ~60s single-finger hold produced `Avg BPM` locking on after ~7s and then parked at a stable **74–82** (IR steady ~115–116k, `beats this sec` 1–2) for the better part of a minute — a plausible resting rate. Occasional wild `last=` values (12, 124, 25) are single-beat artifacts from micro-movement that the rolling average shrugs off; one brief dip to `Avg BPM=34` was a detection gap that self-recovered. Phase 3 heart-rate is done. **The heart-rate sketch is committed on branch `phase3-heart-rate` (commit "Add working MAX30102 heart-rate firmware").** After that commit, `main.cpp` was overwritten with a plain I2C scanner (1s interval) to confirm the MLX at 0x5A, and then — once confirmed — with the **MLX90614 temperature read** (see below). **So the current uncommitted `src/main.cpp` is the MLX90614 temperature-read sketch, not the heart-rate sketch nor the scanner; recover the heart-rate code from the committed branch when needed.**

**MLX90614 temperature read — DONE and CONFIRMED (2026-07-13).** `main.cpp` now reads the MLX directly over `Wire` (no library): write the register address, `endTransmission(false)` for a repeated start, `requestFrom(addr, 3)` to read LSB/MSB/PEC, then `°C = raw × 0.02 − 273.15` (raw is 0.02K steps; high bit set = error, skip). Registers: `0x06` = ambient (Ta), `0x07` = object (Tobj1). Prints `Ambient=X C,  Object=Y C` once per second. **Live-verified end-to-end:** ambient sat at room temp (~25–30°C); object tracked what the sensor was aimed at — ~35°C at skin/forehead, ~20°C at a cold target, 100°C+ when pointed near the hot soldering iron. Object temp is surface/non-contact, drifts with distance/angle/airflow, and reads below core body temp — an experimental signal, not a fever thermometer.

**BMI160 6-axis motion sketch — ADDED 2026-07-13, hardware-verified on the shared bus (enumerated at `0x69`).** `src/bmi160_motion/main.cpp` reads the BMI160 directly over `Wire` (no library — same reason as the MLX): auto-detects the chip at `0x68`/`0x69` via chip-ID `0xD1`, powers accel+gyro to normal mode with datasheet start-up delays, sets ±2g / ±2000 dps ranges, then reads the 12-byte data block (gyro 0x0C, accel 0x12) and prints one throttled line/sec (`A[g]=…  G[dps]=…`). Uses the non-blocking `sensor_ok` guard. Env: `pio run -e bmi160_motion`. **Live reads are now CONFIRMED on the shared bus (2026-07-13) — see the `combined_hr_motion` note below.** BMI160 is Bosch EOL (successor BMI270). Firmware defaults to whichever range constants (`ACC_LSB_PER_G`, `GYR_LSB_PER_DPS`) match the configured ranges — update both if the ranges change.

**BMI160 motion logger + spatial charting — ADDED 2026-07-13, uncommitted.** For motion capture/plotting (not just the 1 Hz combined test), `src/bmi160_motion_log/main.cpp` (env `bmi160_motion_log`) logs BMI160-only at **~50 Hz** as CSV lines `M,<t_ms>,<ax>,<ay>,<az>,<gx>,<gy>,<gz>` (MAX may share the bus but this sketch ignores it). Its env **overrides `monitor_filters`** to use `monitor/filter_motion_csv.py`, which writes `data/motion_*.csv` — deliberately separate from the HR `run_*.csv` files so the empty non-HR lines don't corrupt the HR notebook. `notebooks/plot_motion_run.ipynb` loads the latest `motion_*.csv` and plots per-axis accel/gyro time series plus an estimated 3D trajectory. **Caveat: the 3D path is de-trended double integration — trustworthy for gesture *shape* only; IMU bias drifts quadratically so absolute position/distance is not reliable.** Capture with `pio run -e bmi160_motion_log -t upload && pio device monitor`, move the sensor 10–20s, Ctrl+C to flush the CSV.

**Build is fixed and green (2026-07-01):** the `SPI.h` failure was caused by `adafruit/Adafruit MLX90614 Library`'s transitive dependency on `Adafruit BusIO`, which fails to compile under this toolchain (see Known Toolchain Issues). Removing that lib_dep entirely resolved it — `platformio.ini` currently declares only the SparkFun MAX3010x library. Do not re-add the Adafruit MLX90614 library.

**Both sensors are now individually proven:** MAX30102 at a stable 0x57 (2026-07-12, heart-rate reads confirmed) and MLX90614 at a stable 0x5A (2026-07-13, temperature reads confirmed — see above). Both were tested **one sensor at a time** (the other disconnected). The long detection saga is closed; soldering the headers + solid direct-jumper contact was the fix, exactly as predicted. **Caveat (2026-07-13): the MLX90614 has since STOPPED responding and is now suspected dead — see the isolation test in the Firmware Architecture "Shared-bus progress" note below. The MAX30102 remains healthy (stable 0x57).**

**BMI160 6-axis motion sensor added (2026-07-13, uncommitted):** the user is adding a BMI160 accelerometer/gyroscope as a **third** I2C sensor. New sketch `src/bmi160_motion/main.cpp` reads it directly over `Wire` (no library — same pattern as the MLX, dodges the Adafruit BusIO build trap): auto-detects the chip at `0x68`/`0x69` by verifying chip ID `0xD1` (reg `0x00`), powers up accel+gyro to normal mode with datasheet start-up delays, configures ±2g / ±2000 dps, and prints one throttled line/sec (`A[g]=…  G[dps]=…`) using the non-blocking `bmi_ok` guard. New `bmi160_motion` PlatformIO env added to `platformio.ini`. **Bring-up approach changed (2026-07-13): the user explicitly chose to wire the BMI160 onto the SHARED bus in tandem with the MAX30102 (NOT one-sensor-at-a-time), since the MLX is being set aside** — "lets do this with the bus to do it in tandem with the HR sensor. First, lets make sure the HR sensor still works." **This was executed and CONFIRMED live (2026-07-13):** the MAX30102 heart-rate read was re-flashed and reconfirmed, the BMI160 was wired onto the shared bus ("Accelerometer and MAX plugged in"), and a new combined sketch `src/combined_hr_motion/main.cpp` (env `combined_hr_motion`, distinct from `combined_hr_temp`) produced real simultaneous data — "we are getting data!" **This is the first confirmed simultaneous multi-sensor read on the shared I2C bus (MAX30102 + BMI160 coexisting live).** **Serial output now captured (2026-07-13, later same session):** the BMI160 enumerates at **`0x69`** (SDO/SA0 high on this HiLetgo unit) alongside the MAX at `0x57` — both printed at boot (`MAX30102 ready at 0x57.` / `BMI160 found at 0x69`). Rest values are healthy: lying flat, `A[g]≈0.0,-0.1,1.0` (gravity on Z) with X/Y near 0, gyro near 0, and both accel (±0.3–0.5g) and gyro (spikes to ~110 dps) respond live to tilt/rotation. So the exact address and rest values are no longer unrecorded. (The BMI160 hardware is a HiLetgo GY-BMI160, 13×18mm.) Note: **BMI160 is Bosch end-of-life** (BMI270 is the successor) — fine for a prototype.

**Remaining Phase-3-and-beyond work:** the two original sensors have been proven **individually** on the confirmed hardware; whether they run **together on the shared I2C bus** (now potentially three devices with the BMI160) still needs verifying. Scaffolding for the merge already exists in the working tree (uncommitted as of 2026-07-13): `src/i2c_scanner/main.cpp` (shared-bus scanner, `i2c_scanner` env) and `src/combined_hr_temp/main.cpp` (combined MAX30102 HR + MLX90614 temperature read, `combined_hr_temp` env) — plus CSV-capture tooling (`monitor/filter_csv_capture.py`, wired via `monitor_filters = default, csv_capture` in `platformio.ini`, writing `data/run_*.csv`) and a `notebooks/plot_combined_run.ipynb` plotter. So a single sketch reading both **does** now exist; what's unconfirmed is a clean simultaneous read on the shared bus. **Shared-bus progress (2026-07-13):** the `i2c_scanner` env was run on the shared bus for the first time — with the MAX30102 wired it returns a **stable `0x57` every scan** (bus is healthy, MAX solid; not a power/ground fault), and the CSV-capture tooling is confirmed working (wrote `data/run_20260713_212542.csv`). But the **MLX90614 dropped off (0x5A absent) after breadboard components were shifted** — a mechanical contact fault (a jumper/row moved), not a bus-wide fault, since the MAX stayed stable; fix is re-seating the MLX's four jumpers on the shared 3V3/GND rails and checking its reversed `VIN GND SCL SDA` pin order. **Update (2026-07-13, later same session): re-seating and correct re-wiring did NOT restore it** — the scanner still returns a stable `0x57` only, with `0x5A` absent, so the MLX may now be damaged rather than just miscontacted. **Damage heuristic for the MLX: only reverse polarity (VIN↔GND swapped) can fry it; a swapped SDA↔SCL is harmless (no comms, no damage), and it has been on 3V3 throughout.** Dead-or-not test: wire the MLX alone, power on, and touch the metal can — a reverse-powered/shorted chip runs warm/hot within seconds; a healthy one stays cool. If it stays cool but never ACKs at 0x5A, reflow the header joints before concluding it's dead. **Isolation test run (2026-07-13, later same session): the MLX wired ALONE, direct female-jumpers to the XIAO (no breadboard), on the exact D4/D5 pins that had just returned a rock-solid `0x57` from the MAX, scanned clean `(none)` on every scan.** This localizes the fault to the MLX itself (XIAO I2C proven good on those same pins) and, because the scan was clean `(none)` — NOT random shifting addresses — it is not a floating-bus/ground fault on the data lines; the MLX is either unpowered (broken VIN/GND joint) or dead. Likely reverse-polarity damage. Final confirmation still pending: multimeter VIN→GND at the MLX pins should read ~3.3V (no 3.3V = power-joint fault, reseat/reflow; 3.3V present but still `(none)` = dead chip), or the touch test above. **Treat the MLX as suspected-dead until a fresh unit or a passing solo scan says otherwise. Decision (2026-07-13): the user has NO multimeter, so that confirmation test cannot be run; the user has chosen to move on WITHOUT the MLX for now (temperature is deprioritized, not abandoned — may retry once the sensors are direct-wired in the enclosure phase).** BMI160 (0x68/0x69) was not yet wired during that scan — but it was wired later the same session and the MAX30102 + BMI160 shared-bus combined read was CONFIRMED live (see the `combined_hr_motion` note above), so simultaneous multi-sensor operation is no longer unconfirmed for those two. **Motion-logging tooling added (2026-07-13):** a dedicated ~50Hz BMI160-only CSV logger `src/bmi160_motion_log/main.cpp` (env `bmi160_motion_log`), a capture filter `monitor/filter_motion_csv.py` that matches the `M,…` line format and writes `data/motion_*.csv`, and a `notebooks/plot_motion_run.ipynb` plotter (per-axis accel/gyro time series + an estimated 3D trajectory). **Gotcha:** the `combined_hr_motion` env keeps the shared `csv_capture` filter, which only matches the HR/temp line format — so running it writes an **empty** `data/run_*.csv` (header only). For spatial/motion charting you must use `bmi160_motion_log` (its `monitor_filters` is overridden to `motion_csv`, writing `motion_*.csv`); `combined_hr_motion` is for watching both sensors live, not for logging motion. **3D-trajectory caveat:** position from a 6-axis IMU is double-integrated accel — bias errors compound quadratically and the path drifts within seconds; treat the trajectory as illustrative gesture shape, not real coordinates. The per-axis accel/gyro time series are the trustworthy signals. Next steps: commit the uncommitted working-tree sketches; proceed to later phases (enclosure/battery). Historical note: the pre-solder full-bus scanner (2026-07-01) found nothing at any address — a power/ground contact issue, not firmware; a third sensor (distance/VL53L0X-type) was considered and rejected for the same root cause.

Sensor libraries must be declared in `platformio.ini` under `lib_deps` before they can be `#include`d:
- MAX30102: `sparkfun/SparkFun MAX3010x Pulse and Proximity Sensor Library`
- MLX90614: no library — read registers directly via `Wire` (see Known Toolchain Issues)

PlatformIO fetches and links added libraries automatically on the next `pio run`.
