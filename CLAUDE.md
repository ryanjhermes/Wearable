# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Experimental wearable prototype on a Seeed Studio XIAO ESP32S3. Collects body/environment signals
via I2C sensors. Not a medical device — readings are experimental.

**Status:** Phase 3 (sensor reads) is **COMPLETE**. MAX30102 heart rate and BMI160 motion both
read live and are CONFIRMED simultaneously on the shared I2C bus. BLE HR streaming works
untethered on battery. Battery power CONFIRMED working. Open work: enclosure — a first
**simple two-part box** design exists as `.3mf` in `archive/v1/enclosure/` (see its `README.md`);
`enclosure/` now holds only the v2 placeholder, blocked on the fab PCB outline. Target
form factor is wristband/watch in 3D-printed TPU; the assembled electronics measure ~57×24×11mm.
Not yet confirmed printed/fitted against the assembled electronics.

**Direction change — miniaturization is the binding blocker (user, 2026-09-12):** firmware is
treated as done/clean-slate; the hardest open problem is **physical size/comfort** — the current
~57×24×11mm packing is too bulky (a volume audit found ~60% of it is air + jumper wire; the LiPo and
XIAO, not the sensors, dominate). Working direction: a **custom carrier PCB**, skin-facing optical
side, **externally assembled/fabbed**; target ≈Whoop-class (~32×24×11mm). **Form-factor constraint
(user, 2026-09-12):** **ONE double-sided PCB, NOT a board stack**, and **cannot be significantly
taller** — sensors on the skin side, MCU + LiPo on the top side; height budget ~11mm, pinned by the
LiPo. **The `pcb/` folder was DELETED 2026-09-14** at the user's request — it was an abandoned rough
start (schematic + PCB empty, one stale breakout footprint) and is not a basis for anything. It is
recoverable from commit `ebf99dc` if ever needed. The new board starts from scratch.

**Physical constraints (user, 2026-09-14):**
- **No status LEDs and no screen** — both cut to save space. Caveat worth remembering: the
  `battery_blink` and `led_test` envs exist precisely because an LED is the only diagnostic that works
  when USB won't enumerate (a recurring failure in `archive/v1/docs/hardware_debug_log.md`). Losing that costs
  bring-up visibility; a single DNP-able 0402 LED footprint would keep the option for ~1mm².
- **Recovery path — expose BOOT (GPIO9) + RESET as test pads (assistant recommendation, 2026-09-15).**
  No LEDs + no buttons + a sealed enclosure means a firmware failure could leave NO way in. The
  ESP32-C3 needs BOOT (GPIO9) pulled low to enter download mode (the "hold BOOT, tap RESET" fix that
  recurs throughout `archive/v1/docs/hardware_debug_log.md`). Two exposed pads cost ~0 and preserve the escape hatch.
- **Battery sits on TOP of the double-sided board** (over the top-side components), not beside it —
  confirmed as the plan. Stack: sensors 1.55 + PCB 1.0 + MINI-1 2.4 + LiPo 4.0 + walls ≈ **10.5mm**.
  Beside-mounting is thinner (~8mm) but makes the footprint far too long for a wrist.
- **Antenna keepout vs battery:** if an ESP32-C3-MINI-1 is used, the LiPo's metal pouch must NOT sit
  over the module's PCB trace antenna — it detunes/blocks it. Battery goes over the opposite end;
  the antenna end needs clear copper and no metal above it.
- **Optical isolation deprioritized (user's call).** Not being designed as a PCB-level feature. The
  cheap fallback if wrist PPG is weak: an opaque ring printed into the enclosure between LED and
  photodiode, and no air gap to skin — costs nothing at the PCB level, so this stays reversible.
- **Thermal-isolation slot is an UNVALIDATED hypothesis, not a finding.** The claim that board
  self-heat corrupted the MLX90614 readings was inference from `archive/v1/docs/hardware_debug_log.md`, never
  measured. Treat as optional cheap insurance at layout time, not a requirement.

### Part selection — NOTHING IS FINAL (user, 2026-09-14)

**Every row below is a CANDIDATE under evaluation, not a decision.** An earlier revision of this file
wrote these up as "DECIDED" — that was wrong and has been reverted. Two unresolved questions gate the
whole BOM; neither is answered:

1. **Prototyping track or fab track?** Breakout modules (bought on Amazon, hand-wireable) and bare
   chips (bought via LCSC/Mouser, machine-assembled by the fab) are *different supply channels,
   different sizes, and different skill requirements*. Which track this project is on is NOT decided,
   and the answer changes every row below. Bare LGA/OLGA chips cannot be hand-soldered.
2. **Wrist PPG wavelength is UNDIAGNOSED.** The green-LED argument for MAX30101 rests on commercial
   practice (Apple/Fitbit/Whoop use green on the wrist), NOT on any measurement from this project.
   The one on-wrist attempt (2026-07-24) ran on known-bad firmware and is inconclusive. **The
   diagnostic to settle it already exists and has NEVER been run** — `archive/v1/src/max30102_raw_ir/` +
   `archive/v1/scripts/raw_ir_capture.py` + `archive/v1/scripts/plot_raw_ir.py` were built 2026-07-23 and `data/` contains
   **zero** raw-IR captures. Run that on the wrist before spending money on either sensor.

| Function | Currently owned | Candidate | Why considered | Status |
|---|---|---|---|---|
| PPG / HR | MAX30102 (MH-ET LIVE breakout, ~20.5×15.5mm) | MAX30101 | Adds a **green** LED (red/IR is a fingertip/SpO₂ combo); wrist PPG in commercial devices is green | **OPEN** — blocked on the wavelength test above; on the prototyping/Amazon track user leans to buying **another MAX30102 breakout** (small MAX30101 breakouts aren't available on Amazon, 2026-09-14). **Fab track sourcing CONFIRMED (2026-09-14):** `MAX30101EFD+T` = LCSC **C2859066**, in stock ~319, Extended, ~$8.34@qty1 — the biggest BOM sourcing risk, now resolved |
| Temp | MLX90614 GY-906 (suspected dead, tall TO-39 can) | TMP117 or MAX30205 | Contact temp beats non-contact IR for body temp; kills the tallest part | **OPEN** — TMP117 leads, not committed. Both <1mm tall (no height impact). Decider is power: TMP117 ~3.5µA active (WSON-6 2.0×2.0mm, ±0.1°C over −20…50°C); MAX30205 **~600µA active** (TDFN-8 3.0×3.0mm, ±0.1°C only in 37–39°C) — the 600µA matters on the 250mAh cell. **Fab stock (2026-09-14):** MAX30205 (C2917019/C476171) is **pre-order only, 0 stock**. **TMP117AIDRVR now sourced & filed (2026-09-15):** LCSC **C699536**, WSON-6 2.0×2.0×0.75mm, datasheet in `parts/tmp117/` |
| IMU | BMI160 (GY-BMI160 breakout) | Keep BMI160 | Only needs to subtract activity from HR; existing driver works | **BMI160 confirmed DEAD on fab track (2026-09-14):** LCSC **C94021** is **consign-only, 0 stock** (the Bosch-EOL outcome) — not machine-placeable by JLCPCB. So on the fab track the accel is **LSM6DS3TR-C** (near-identical footprint; port ≈ axis-remap + register-address changes, ~a day of firmware). Keeping BMI160 only remains viable on the prototype/breakout track. User declined an upgrade to LIS2DH12 (2026-09-14) unless it's a large improvement. **LSM6DS3TR-C now sourced & filed (2026-09-15):** LCSC **C967633**, datasheet in `parts/lsm6ds3tr-c/`. It is **6-axis — the gyro is free**; use it for sway/tremor/gait-instability BAC features, not only activity-subtraction |
| MCU | XIAO ESP32S3 (dev board) | ESP32-C3-MINI-1 (module) | A dev board on a carrier = two stacked PCBs, violating the one-board constraint | **OPEN** — see MCU note below. **`-N4` variant (4MB flash) now sourced & filed (2026-09-15):** LCSC **C2838502**, datasheet in `parts/esp32-c3-mini-1/` |
| Battery | LiPo 402030 (30×20×4, 250mAh) | unchanged for now | Pins the height budget | Owned |
| EDA/GSR | none | analog front end | 4th Kaczor channel; see Application section | **OPEN** |
| Ambient temp+humidity | none | SHT40-AD1B-R3 | **De-confounds skin temp/EDA** — a hot/humid room raises skin temp and sweat with no alcohol, corrupting the BAC signal; needed to regress out environment | **New candidate (2026-09-15), filed** — LCSC **C2848306**, ~2×2mm I2C, datasheet in `parts/sht40/`. User chose the R3 sub-variant; R2-vs-R3 question resolved to R3 (suffix = tape-and-reel qty only, electrically identical) |

**Fab-track I2C bus has no address collisions (2026-09-15):** the four selected sensors sit at
distinct addresses — SHT40 `0x44`, TMP117 `0x48` (strappable 0x48–0x4B), MAX30101 `0x57`,
LSM6DS3TR-C `0x6A/0x6B` — so they share one bus cleanly. Note this differs from the prototype
breakouts' map in **Hardware & I2C**: the fab accel is `0x6A/0x6B`, not the GY-BMI160's `0x69`.

**Sizes are chip-vs-breakout, not chip-vs-chip — do not conflate them.** The bare MAX30101 and bare
MAX30102 are the **same size** (5.6×3.3×1.55mm OLGA-14, same `0x57` address, same SparkFun MAX3010x
library). An earlier revision of this file claimed MAX30101 was "smaller" — **that is false.** Any
size win comes from going breakout→bare chip, which is available with either sensor. Amazon sells
breakouts only; bare chips come from LCSC/Mouser and are placed by the fab.

**Bare-chip power trap — MAX30101/MAX30102 VDD is 1.8V, NOT 3.3V (from JLCPCB listing, 2026-09-14).**
The breakout you own hides this behind an onboard regulator (why it accepts 3.3V today). On a bare-chip
board you must supply **1.8V yourself** (a second LDO) **plus a separate higher VLED rail** — the power
design goes from one rail to **three**. The I2C pins are spec'd to tolerate a 3.3V bus even with 1.8V
VDD, so the shared bus is fine. **All three now datasheet-verified (2026-09-15, filed in
`parts/max30101/`):** VDD 1.7–2.0V (abs max **+2.2V** — 3.3V destroys it); SDA/SCL abs max +6.0V so the
3.3V bus needs **no level shifting**; and **VLED+ is 3.1–5.0V and runs straight off the LiPo (3.0–4.2V)
— NO boost converter needed**, so the "third rail" is just a direct LiPo tap, not extra silicon. This breakout→bare-chip
"the breakout was doing work you didn't know about" trap must be re-checked for every part picked.
**Concrete instance already known: I2C pull-ups.** The prototype breakouts each carry their own
SDA/SCL pull-ups; the bare chips do NOT, so the carrier board must add **one pair of ~4.7k pull-ups**
for the whole bus.

**"You have sensors, not a BOM" (assistant, 2026-09-15).** Part *selection* is settled pending the
EDA call, but a schematic needs **~25–30 more support parts** the XIAO + breakouts were silently
providing: 3.3V LDO + the 1.8V LDO above + LiPo charger (MCP73831/TP4054) + program resistor + bulk/
decoupling caps (~8); mid-mount USB-C + 2× 5.1k CC resistors (mandatory or it won't draw power) + ESD
array (~4); EN pull-up + RC + BOOT/RESET access + decoupling (~6); the 2 I2C pull-ups above; EDA front
end if included (~5). Most are Basic (no setup fee), but each is a chance to get something wrong. No
RTC chip needed — the `#now` BLE clock-anchor + phone time already cover timestamps.
**Support-part sourcing started, not finalized (2026-09-15):** first-pass candidates are
**ME6211C33M5G-N** (3.3V LDO) and **USBLC6-2SC6** (USB ESD array) — "look right," not yet
datasheet-verified or filed in `parts/`. The **mid-mount USB-C connector is still unpicked.** These
do not close the support-part gap; the schematic stays blocked until they (and the rest) are chosen.

**MCU — "ESP32-C3" names three different things:** the bare **chip** (QFN 5×5mm, needs crystal/
antenna/flash support circuitry); the **ESP32-C3-MINI-1 module** (13.2×16.6×2.4mm — chip + flash +
crystal + **PCB trace antenna** + shield can, pre-certified, solders flat as one part; the `-1U`
variant swaps the trace antenna for U.FL); and the **XIAO ESP32C3 dev board** (a module plus USB-C,
LDO, charge IC, buttons, castellated pads — and it uses an **external U.FL antenna**, same as the S3).
Same silicon in all three. The MINI-1 is not an upgrade or a different family — it is the form that
can sit directly on a custom board. Cost of moving off the XIAO: you take on its USB-C, ESD, LDO,
charger and boot/reset circuitry (~15 passives + 3 ICs of reference design).

**USB-C:** keep it. Mid-mounted (connector dropped into a routed slot so its centerline sits at the
board centerline) it stands **1.6mm above the PCB — below the 2.4mm MINI-1 module, so it costs zero
height.** The pogo-pad/dock alternative buys ~55mm² of area, still needs the same charger IC, loses
one-cable flashing, and adds a dock to design. Rejected on those grounds.

**Antenna is a non-issue for this design (user, 2026-09-12):** data is stored on-device and BLE-synced
to the phone on reconnect, so range/connection quality is not a priority.

Any "upload somewhere for an ML model" backend must be Pioneer Supabase/Azure.

**Application — proxy blood-alcohol concentration (BAC) with ML (user-committed goal, 2026-09-12):**
following Kaczor et al., *"Detecting Ethanol Intoxication and Impairment Using Wearable Biosensors"*
(HICSS 2026) — a wrist HR + skin-temp + EDA + accelerometry combo with an XGBoost model (~0.80
accuracy). Three of four channels map to candidate parts (PPG=HR, contact temp, BMI160=accel); the
missing channel is **EDA/GSR**.

> **Jargon (user asked 2026-09-14):** **EDA** here = **electrodermal activity**, a.k.a. GSR/galvanic
> skin response — skin conductance between two skin electrodes, which rises with sweat-gland activity.
> *Not* to be confused with "EDA" meaning Electronic Design Automation (KiCad). **LCSC** = the
> component distributor that **JLCPCB** (PCB fab) pulls parts from when it assembles a board — it
> matters only on the fab track, because the fab can only place parts LCSC stocks.

EDA is **analog, not I2C** — read as a voltage on an ADC pin via oversampled `analogRead()`, gated on
BMI160 motion ≈ 0. **Open V1 decision (assistant recommends YES, user not yet decided):** whether to
design EDA into the carrier PCB — it needs two skin electrodes + a small front end (op-amp, 2
resistors, cap, 1 ADC pin, 2 gold skin pads); adding it after a fab run is a full board respin, and
EDA is often the strongest single BAC predictor. **Fab constraint if EDA is included (2026-09-15):**
the skin electrodes are **ENIG-plated pads on the board itself, not a purchased part** — the board
must be ordered with an **ENIG (gold) finish; the default HASL (tin/lead) corrodes against sweat.**
Candidate front-end op-amp filed in `parts/mcp6002/` (MCP6002T-I/SN; alts TLV9002 / OPA2333, LCSC# TBD)
— its existence does NOT change the status: EDA-in-V1 is still an OPEN, undecided call.

**V1 sensor scope locked down (user, 2026-09-15):** "**We won't be doing microphone or ECG.**" Also
**ruled out for V1** (assistant analysis, user did not object): transdermal-alcohol (TAC) sensor,
barometer, bioimpedance. Working recommendation is **EDA + SHT40, then stop** — adding more channels
worsens overfitting risk (self-labeled data + ~30 features on XGBoost will memorize sessions). MLX/
non-contact IR is NOT needed — contact TMP117 replaces it.

**Ground-truth labels require a fuel-cell breathalyzer (user aware, 2026-09-15):** "I'm aware of the
breathalyzer part." No BAC model trains without labels — a **fuel-cell** (not semiconductor) unit
(~$50–150) is the highest-value near-term purchase. Not a board component; an external labeling tool.

**Battery cannot capture a full drinking session — physical (height) limit, not firmware (2026-09-15):**
real sessions run 4–6+ h vs the ~3–4 h the 250 mAh cell gives; the cell (which also pins the 11mm
height budget) is the binding constraint on session-length data capture, so this is a form-factor
tradeoff, not something a firmware heat-cut fixes.

**Free ML channels at zero BOM cost (2026-09-15):** the MAX30101 PPG alone can also yield HRV
(parasympathetic suppression), **perfusion index** (AC/DC — peripheral vasodilation, one of the
cleaner alcohol signals), SpO₂, and PPG waveform morphology; the LSM6DS3TR-C gyro adds sway/tremor.
These come from parts already on the candidate list — no extra sensors, so they don't add overfitting
surface the way new hardware does.

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

### Environments (`platformio.ini`, one folder per env under `archive/v1/src/<env>/main.cpp`)

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
| `max30102_hr_ble` | HR → BLE stream, no flash buffer (data lost if unsubscribed) | — (use `archive/v1/scripts/ble_hr_stream.py`) |
| `max30102_hr_ble_log` | HR → **store-and-forward**: logs to LittleFS AND streams BLE; back-fills the offline gap on reconnect | — (use `archive/v1/scripts/ble_hr_stream.py`; `d`/`e`/`i` over USB) |
| `max30102_raw_ir` | Raw IR waveform → BLE (~100 Hz, batched) for HR-algorithm dev | — (use `archive/v1/scripts/raw_ir_capture.py`) |
| `battery_blink` | Onboard-LED blink, no serial dep — battery test | — |
| `led_test` | External 5mm LED on GPIO4 (D3 pad) blink, 500ms | — |

**Filter gotcha:** the shared default filter `csv_capture` only matches HR/temp line format, so
`combined_hr_motion` writes an *empty* `run_*.csv` (header only). For motion charting use
`bmi160_motion_log`; `combined_hr_motion` is for watching both sensors live, not logging. Same
trap for `max30102_hr_ble` if you open the monitor on it: it inherits the `csv_capture` default but
prints the comma format `t_ms,avg_bpm,last_bpm,beats,ir,finger  ble=advertising`, which the filter
ignores → empty `run_*.csv`. Its ONLY data path is BLE (no flash logging) — capture via
`archive/v1/scripts/ble_hr_stream.py`; serial is watch-only.

## Repo Layout

- `archive/v1/src/archive/led_test/main.cpp` — external-LED blink on **GPIO4** (the `D3` pad). Chanzon 5mm yellow,
  20mA / Vf 2.0–2.2V, wired **without a series resistor** (user's call), so the sketch limits the pad to
  `GPIO_DRIVE_CAP_1` (~10mA) via `gpio_set_drive_capability()` — a bare 3.3V pad into a 2.1V Vf part
  would pull ~40mA, at/over the ESP32-S3 per-pad limit. LED runs dim by design. Blinks rather than
  holding steady HIGH so a lit LED proves firmware is running, not a floating pin. Supersedes a stray
  root-level `LEDtest.c++` (deleted — PlatformIO only builds `<src_dir>/<env>/`, and `.c++` is not a compiled
  extension). **CONFIRMED lit and blinking on hardware 2026-09-13** at `GPIO_DRIVE_CAP_1` (~10mA);
  the first attempt used `CAP_0` (~5mA) and was too dim to see. Sketch also blinks the onboard LED
  in anti-phase + prints over serial, so a dark external LED isolates wiring from firmware.
- `archive/v1/src/<env>/main.cpp` — firmware, one folder per PlatformIO env (see table). Split from a single
  a single `src/main.cpp` on 2026-07-12 via `build_src_filter`; shared settings live under `[env]`.
  **Layout drift (2026-07-29): only `max30102_hr_ble_log` and `max30102_raw_ir` remain live at
  the top of `src_dir`; the other 11 env folders sit under `archive/v1/src/archive/`.** Their `platformio.ini`
  `build_src_filter` paths were NOT updated, so those envs' filters now match nothing and a bare
  `pio run` (all envs) fails — the two live envs still build. Update the filter to `+<archive/<env>/>`
  or move a folder back before building an archived env. Also note `[env:max30102_heartrate]` has a
  stray typo — `build_src_filter =u+<...>` (the `u` is invalid).
- `platformio.ini` — build/upload/monitor config; **source of truth for the serial port**. Sets
  `src_dir = archive/v1/src` (firmware archived 2026-09-15 but still builds — see `archive/v1/README.md`).
- `monitor/filter_*.py` — serial-monitor capture filters: `filter_csv_capture.py`,
  `filter_motion_csv.py`, `filter_flash_dump.py`. Wired per-env via `monitor_filters`.
- `archive/v1/scripts/ble_hr_stream.py` — Mac-side BLE client (`pip install bleak`); streams `Wearable-HR`
  to terminal and saves `data/ble_hr_*.csv`. Runs a **reconnect loop**: on a dropped link (out of
  range, board reset) it re-scans/reconnects on its own and appends to one CSV across reconnects, so
  the device's buffered data back-fills automatically on return (bleak's `BleakClient` has no built-in
  reconnect — this is added client-side). Syntax-checked only, NOT yet hardware-verified.
- `archive/v1/scripts/raw_ir_capture.py` — Mac client for the `max30102_raw_ir` firmware; subscribes to
  `Wearable-IR`, expands each batched notify into per-sample rows, saves `data/raw_ir_*.csv`
  (`recv_ts,t_ms,ir`). Auto-reconnects. **Purpose:** record the true wrist PPG waveform to design a
  band-pass + autocorrelation/FFT HR estimator (SparkFun `checkForBeat` is unreliable on wrist PPG —
  see HR beat detection note).
- `archive/v1/scripts/plot_raw_ir.py` — plots a raw-IR capture (raw waveform, AC pulse, HR-band FFT) with numpy+
  matplotlib; prints the FFT peak BPM and saves a `.png` next to the CSV.
- `notebooks/` — plotters: `plot_combined_run.ipynb`, `plot_motion_run.ipynb`, `plot_ble_hr.ipynb`.
- `data/` — **live** capture target for new runs (gitignored; scripts and monitor filters write
  here). Empty apart from `.gitkeep` — the 17 historical breakout-era CSVs moved to
  `archive/v1/data/` on 2026-09-15.
- `parts/` — **candidate-component research for the fab-track BOM** (added 2026-09-14). One folder per
  part, named by manufacturer part number in lowercase-kebab; each holds `README.md`, `datasheet.pdf`,
  and `images/`. Copy `parts/_template/` to start one. **READMEs are now schematic-ready (2026-09-15):**
  beyond specs/availability/LCSC#, each part README carries a **complete pin table with net
  assignments**, a **required-externals table with values**, and layout notes — all extracted from the
  datasheet with page refs; `parts/README.md` adds the system glue (the **three-rail power tree**, the
  **I2C address map**, and a consolidated support-part list). Schematic-critical gotchas the breakouts
  hid, now filed in the part READMEs: MAX30101 **4.7µF on VLED+ is mandatory** (200mA LED pulses) + its
  6 N.C. pins still solder mechanically + PGND≠GND; LSM6DS3TR-C **CS(12) high or it boots SPI, SDx(2)/
  SCx(3) must be tied**; TMP117 **ADD0 must not float** + thermal-pad placement *is* the measurement;
  ESP32-C3-MINI-1 **GPIO8 needs an external 10kΩ pull-up or it won't boot**, and **native USB on IO18/19
  means no UART bridge and no auto-reset transistors** (a real parts saving); SHT40 must vent to outside
  air + be thermally isolated. Nothing in it is a decision — decisions live here.
  `parts/_reference/` is NOT per-part datasheets — it holds three cross-cutting ESP32-C3 design docs
  (hardware design guidelines, DevKitM-1 reference schematic, C3 chip datasheet) to design the carrier
  schematic against.
- `enclosure/` — **v2 placeholder, intentionally empty of geometry.** Blocked on the fab PCB: the
  enclosure can't be dimensioned until the board outline is fixed. See `enclosure/README.md`. The
  v1 box moved to `archive/v1/enclosure/`.
- `ios/` — iOS companion app (BLE client for the wearable), scaffolded 2026-09-15. See `ios/README.md`.
  **Stack (user-chosen):** SwiftUI + CoreBluetooth, iOS 17, iPhone-only, bundle `com.pioneer.wearable`,
  generated via **XcodeGen `project.yml`** (the tracked source of truth — the binary `.xcodeproj` is
  gitignored/regenerated, NOT committed). **V1 scope is "Live HR readout only"** — no persistence,
  export, or labeling yet. **BLE contract the app targets:** it **scans the standard Heart Rate
  service `0x180D` and filters by advertised name** (not by the 128-bit telemetry UUID) — the firmware's
  advertising packet (name + 16-bit + 128-bit UUID ≈ 38 B) overflows the 31 B BLE payload, so the
  128-bit UUID is dropped over the air; HR arrives as the standard 2-byte `0x2A37` packet
  (`pkt[0]`=flags 0x00, `pkt[1]`=bpm). Raw-IR firmware uses Nordic UART-style
  `6E400001…/6E400003…` as `Wearable-IR`, 10 IR samples/notify.
  **CANNOT be built on this Mac (confirmed 2026-09-15):** the machine has **Command Line Tools only —
  no `Xcode.app`, no iOS SDK (`iphoneos` unlocatable), and `xcodegen` is not installed**, so the
  project can't be generated or compiled here; sources were only proxy-typechecked against the macOS
  SDK. **CoreBluetooth also does not run in the iOS Simulator** — real BLE needs a physical iPhone +
  signing identity. Building the app requires a Mac with full Xcode.
- `archive/v1/` — **the frozen breakout prototype** (archived 2026-09-15; `.claude/docs/` and
  `enclosure/archive/` were consolidated here). Not authoritative — this file wins on conflict.
  See `archive/v1/README.md` for a per-file "still useful?" table.
  - `archive/v1/docs/` — `archive/v1/docs/hardware_debug_log.md` (bring-up narrative: thermal fault, battery
    saga, MLX death, HR bring-up), `wiring.md` (breakout I2C tables + scanner troubleshooting),
    `development_setup.md` (PlatformIO/upload recovery), `wearable_hardware.md` (breakout specs,
    superseded by `parts/`), `project_plan.md` (original 6-phase roadmap, obsolete),
    `component_images/` (reference photos).
  - `archive/v1/enclosure/` — first-pass two-part printed box (`.3mf` + renders), never fitted.
  - `archive/v1/data/` — the 17 breakout-era captures (BLE HR, motion, combined, flash dumps),
    2026-07-12 → 2026-07-23. **Still contains zero raw-IR captures** — the wrist PPG diagnostic
    has never been run.

Wi-Fi is out of scope; BLE (snap-on U.FL antenna — see Board note) is used for HR streaming.

## Board

- **Board:** Seeed Studio XIAO ESP32S3 — PlatformIO ID `seeed_xiao_esp32s3`, Arduino framework.
  ESP32-S3 (QFN56) rev v0.2, 8MB PSRAM, USB-Serial/JTAG (no drivers). CONFIRMED enumerating
  2026-09-13 on `/dev/cu.usbmodem1101` (`303A:1001`).
  **Serial numbers are deliberately NOT tracked here (user, 2026-09-15).** Two XIAO S3 units have
  been through this project and the docs disagreed about which `SER=` belonged to which, so the IDs
  were removed rather than left misleading. Consequence to keep in mind: **it is not established
  whether the board currently in use is the 2026-07 thermal-fault unit or its replacement**, so treat
  the debug-log heat history as *possibly* applying. If that ever matters, read the serial off the
  live board (`pio device list`) and re-establish it from scratch — do not trust any historical
  mapping. This is low-stakes going forward: the prototype board is superseded by the fab PCB.
- **Possible board switch → XIAO ESP32-C3 (under consideration, 2026-07-24):** the current S3 is
  likely damaged (board thermal fault — see debug log), so a replacement is coming. Considering the
  **XIAO ESP32-C3** instead of another S3: single-core RISC-V @160 MHz, 4 MB flash, no PSRAM — all
  fine for this workload — and **lower power/heat + longer battery runtime**, which matters for a
  wearable. Nearly drop-in: same wiring pads, `Wire.begin()` defaults, BLE/LittleFS/SparkFun libs all
  port; only the PlatformIO board id changes to `seeed_xiao_esp32c3` + recompile. **Does NOT fix the
  antenna** — the C3 uses the same external U.FL antenna as the S3. A true zero-change drop-in is
  another S3. No C3 ordered yet; no `seeed_xiao_esp32c3` env added yet.
  **Replacement-board option (discussed 2026-07-24, not committed):** the **XIAO ESP32-C3** is a
  near drop-in for the retire-this-board plan — single-core RISC-V 160 MHz, 4MB flash, no PSRAM, but
  runs **cooler / longer on battery** and everything this project uses (I2C via `Wire` defaults, ESP32
  BLE stack, LittleFS, SparkFun MAX3010x) ports with only a one-line PlatformIO board-id change
  (`seeed_xiao_esp32c3`) + recompile. It does **NOT** fix the antenna — the C3 uses the same external
  U.FL. Only a board with an onboard PCB-trace antenna (e.g. a C3 "SuperMini") eliminates the U.FL.
- **Port:** `/dev/cu.usbmodem101` — the name flips on each replug. If upload/monitor fails with
  "No such file or directory," run `pio device list`, match the `303A:1001` entry, and update
  `upload_port`/`monitor_port` in `platformio.ini`.
- **Pin positions** (USB-C at top): left side top→bottom `D0, D1, D2, D3, D4/SDA, D5/SCL, TX`;
  right side `5V, GND, 3V3, D10, D9, D8, D7`. I2C: SDA=GPIO5, SCL=GPIO6 (`Wire.begin()` defaults).
- **Pad label ≠ GPIO number — the left side is offset by +1** (GPIO0 is the BOOT strapping pin and is
  not broken out, so Seeed's `Dn` numbering starts at GPIO1). `D0`=1, `D1`=2, `D2`=3, **`D3`=4**,
  `D4`=5 (SDA), `D5`=6 (SCL); then `D6/TX`=43, `D7/RX`=44, `D8`=7, `D9`=8, `D10`=9. The Arduino core
  defines the `Dn` constants, so prefer `digitalWrite(D3, ...)` over the raw GPIO number to avoid
  wiring to the wrong pad.
- **BLE antenna is a detachable external U.FL antenna (NOT onboard) — the XIAO ESP32S3 has no usable
  onboard antenna, so this piece IS the antenna.** It's the flat black flex-PCB in
  `archive/v1/docs/component_images/xiao_esp32s3/with_antenna_connected.png` (connects via a thin coax + U.FL snap).
  **KNOWN ROOT CAUSE (confirmed 2026-07-22): the antenna has NEVER been installed** (user finds it too
  large for a wristband) → BLE runs on just the bare U.FL stub, giving only ~1–2 ft of unstable range.
  This is the cause of ALL the chronic drops this session (every ~40–90 s, drops at 5 ft, and
  "died/never reconnected" = the device drifted out of the tiny bubble and the Mac can no longer hear
  its advertising; the device is fine and still advertising). **TX-power and supervision-timeout
  tuning only treat symptoms — they cannot replace the missing radiator** (the +9 dBm P9 boost tried
  earlier was wasted current/heat for zero range gain; reverted to P3 2026-07-24). For any reliable BLE work,
  plug the antenna in (it's flexible — tape/fold it). Form-factor conflict is open: options are a
  smaller U.FL chip antenna, routing the flat antenna along the band, or a board with a PCB antenna.

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
Full saga in `archive/v1/docs/hardware_debug_log.md`.
**Suspected battery-power fault (2026-07-23) — battery cleared, cause reassigned (2026-07-24):** a BLE
capture died after only ~20 min, and afterward the MAX30102 red LED was dark on battery (out of the
enclosure). On USB the board is fully healthy — boot log shows `Sensor ready`, live IR ~27k, buffered
flash intact. Follow-up: `battery_blink` was flashed and **CONFIRMED the board powers and boots on
battery** (LED kept blinking), so the cell and BAT/JST joint are sound — the earlier battery-side
suspicion did NOT hold. The ~20 min "death" is now attributed to the **Mac's Bluetooth stack wedging
after laptop sleep** (bleak/CoreBluetooth stuck on endless "Not in range"), a client-side capture
dropout, not a battery or firmware fault. If a capture stalls, first wake/reset Bluetooth on the Mac
before suspecting hardware.

**Verifying the battery — the serial monitor CANNOT do it** (serial rides USB; unplugging USB
always kills the monitor regardless of battery state). Use USB-independent signals:
- **Charge LED** (BAT joints conduct): battery + USB-C plugged → small charge LED near USB lights.
- **Discharge** (cell powers the board): flash `battery_blink`, unplug USB → LED keeps blinking
  = on battery ✅; goes dark = flat cell or open BAT joint.
- **Rapid heating with battery + USB = reverse polarity or a short (SAFETY, LiPo fire risk).**
  STOP, unplug both, let cool, inspect the cell. It is NOT an open-joint symptom.
- **Steady, noticeable (not burning) module warmth on battery is expected under the always-on
  firmware** (`max30102_hr_ble_log`: 240 MHz + BLE radio never sleeps → the same root cause as the
  ~3–4 h runtime). Distinguish from the fault above: benign = only the XIAO module is warm, the cell
  stays cool, warmth stabilizes, and USB-only is equally warm; fault = the LiPo **cell** itself is
  warm/swelling or the temperature keeps climbing → unplug. Fix if wasteful: light-sleep between
  samples, lower BLE TX power, `setCpuFrequencyMhz` 80–160 — all cut heat and extend runtime together.
- **Enclosure overheat resolved (2026-07-24): the heat is board-side, NOT the battery.** While
  charging over USB **sealed in the enclosure**, the XIAO got too-hot-to-touch after ~30 min; it
  cooled the moment it was removed. Cell-vs-module check (with the NEW cell): the **XIAO module was
  hot, the cell stayed cool** → not a LiPo-fire fault. Cumulative causes: always-on 240 MHz + BLE +
  the **+9 dBm (P9) TX boost** (a mistake — see antenna note) + a **ventless enclosure trapping all
  the heat** (and possibly compressing a bare solder joint into a short). Working-tree fix (queued,
  NOT yet flashed): **CPU 240→160 MHz** and **TX P9→P3** in `archive/v1/src/max30102_hr_ble_log/main.cpp` CONFIG
  block — cuts idle current/heat and extends runtime. **Do NOT charge sealed in the enclosure or
  unattended**; charge bare on a non-flammable surface. Bare-charge test is the fork: merely warm =
  it was the enclosure (needs **ventilation slots + insulation over the bare MAX30102 joints** before
  sealed reuse); still too-hot bare = board-level fault (short, or charge IC damaged by the earlier
  reverse-polarity episode → use a standalone LiPo charger).
  **Session-end escalation (2026-07-24):** overheat recurred within only **a few minutes** of USB
  charging (new cell, cell cool, module too-hot-to-touch), so the working conclusion now leans
  **board-level hardware fault** — firmware heat-cuts (160 MHz/P3) reduce compute+radio draw but
  **cannot** fix a short or a damaged charge IC. Recommendation: **retire this XIAO**, charge the
  good cell on a standalone LiPo charger, and bring up a **fresh board with the U.FL antenna
  installed**. Not a clean bare-charge test yet, so the fork above is not formally closed — but do
  not burn time re-diagnosing runtime/heat on this board.
- **The OLD LiPo cell is likely damaged (deep-discharged to death) — retired.** Its ~45 min runtime
  (vs the expected ~3–4 h) is an invalid measurement from a collapsed-capacity cell, not the firmware's
  real draw; the NEW cell charges cool. Re-measure runtime fresh on the new cell after flashing the
  160 MHz/P3 build.

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
summary line/sec. **HR is only validated at the FINGERTIP** — a first on-wrist attempt (2026-07-24)
gave garbage (BPM bouncing 0↔250, `beats`≈0), but it ran on the un-reflashed bad-`0x1F` firmware so it
is inconclusive, not proof the algorithm fails on wrist. Wrist PPG is weaker/noisier than fingertip;
if fingertip-tuned `checkForBeat` doesn't transfer once `0x0A` is reflashed, the proposed path is a
raw-IR capture → DC-removal + 0.7–3.5 Hz band-pass + autocorrelation/FFT pipeline (replacing beat
counting). Not built. This matters because the target form factor is a wristband.

**BLE HR (`max30102_hr_ble`):** broadcasts as `Wearable-HR` — standard Heart Rate service (0x180D) for
generic apps + a custom telemetry notify with CSV `t_ms,avg_bpm,last_bpm,beats,ir,finger`. Untethered
workflow: flash over USB (battery out), unplug USB, power from battery, run `archive/v1/scripts/ble_hr_stream.py`.

**HR flash logger (`max30102_hr_log`):** 1 Hz CSV `t_ms,avg_bpm,last_bpm,beats,ir,finger` appended to
LittleFS (`/hr_log.csv`, capped 512 KB). Serial commands: `d`=dump (`---FLASH_DUMP_BEGIN/END---`),
`e`=erase, `i`=size.

**HR store-and-forward (`max30102_hr_ble_log`):** merges the flash logger and BLE stream. One sample per
`SAMPLE_INTERVAL_MS` (now **3 s**, was 1 Hz — beat detection still samples IR every `loop()`; only the
append+notify+serial line is throttled) is appended to `/hr_log.csv`; **all telemetry flows through a
persisted byte cursor** (`/hr_sent.off`)
— when a BLE client connects it back-fills from the cursor to EOF, then streams live, so an offline gap
(Mac asleep, out of range) is buffered and delivered on reconnect. No app-layer acks: the cursor advances
as each line is notified, so a clean reconnect resumes exactly, and only the single in-flight line can drop
on an abrupt disconnect. Once fully drained past 64 KB the flash is **compacted** (rewritten to header only)
to reclaim space, so continuous wear won't hit the 512 KB cap unless offline for hours. Same `d`/`e`/`i`
USB commands. The Mac client (`ble_hr_stream.py`) skips the header line that leads a back-fill burst.
**Buffer is sized to the hardware:** at ~30 B/line and one line / 3 s the 512 KB cap holds ~14 h offline
(~4.5–5 h at the old 1 Hz), but the 250 mAh cell (no sleep: ~50–70 mA draw → ~3–4 h) dies first —
**battery is the binding constraint, not flash.** No point enlarging the buffer until the battery is extended (light-sleep during no-finger, or a
bigger cell); a binary log format (~8 B/sample) would only matter after that.
**Status: the 3 s-cadence build is FLASHED and boots on-device (2026-07-22, 968 KB / 29% flash)** and is
the board's active firmware (replaces `max30102_hr_ble`). The `beats` column now counts beats over each
3 s window (was 1 s) — the CSV header is generic so nothing downstream breaks, just reinterpret that field;
`t_ms` still resets to 0 on each reboot, so erase (`e`) old 1 Hz-spaced data before a clean capture.
Store-and-forward reconnect/resume ran LIVE on hardware (2026-07-22 walk-away test): the client logged
repeated `Disconnected — will re-scan and reconnect` → `Connected. Streaming (back-fill first…)` with
`t_ms` continuing near-continuously across each drop (e.g. …544751 → reconnect → 550803), so the
firmware buffers across a drop and the client resumes without a gap. NOT yet byte-verified line-for-line
against buffer contents — resume was continuous but the burst wasn't counted against what was logged
offline. A fast ~10 lines/sec burst on connect with `t_ms` stepping ~3000/line is the expected back-fill
draining, not a bug.
**BLE link is unstable even in-range (2026-07-22):** drops recur every ~40–90 s at 5+ ft. Leading
suspicion is the **detachable U.FL antenna not fully seated** — check that before trusting any TX-power
tuning. (Uncommitted `archive/v1/src/max30102_hr_ble_log/` edits add a CONFIG block, TX power (now `P3` — was
`P9`, reverted 2026-07-24 after the antenna diagnosis + overheat, see Board/battery notes), CPU clock
`CPU_MHZ=160` (was 240, for heat/runtime), and a 6 s
supervision timeout `CONN_TIMEOUT=600` to fight the drops, plus `RED_PULSE_AMPLITUDE` 0x0A→0x1F for
stronger finger signal, plus a **30 s time-window BPM average** (`BPM_WINDOW_MS=30000`) that replaces the
4-beat ring: `avg_bpm` now averages every beat in the last 30 s (`60000×(beats−1)÷span`), needs ≥2 beats
(reads 0 until then), takes ~30 s to reflect a real rate change, and clears on finger-lift — steadier for
resting HR, not for fast changes. These are now **FLASHED and boot-confirmed on-device (2026-07-23)** —
they are the board's active firmware, replacing the plain 3 s build. Boot capture over USB showed the
MAX30102 initializing fine (`Sensor ready`, live IR ~27k) and buffered data intact in flash
(`log=65390 sent=61538 buffered=3874`).)
**Halved-BPM diagnosis (2026-07-22):** the 3 s cadence does NOT affect the BPM math (beat intervals are
still timed every `loop()`). Low/halved readings were **missed beats** from noisy finger contact (IR
swinging wildly line-to-line + `finger` flipping 1/0) and reconnect stalls — not a cadence bug. Clean,
still, light fingertip contact is the fix.
**Client wall-clock timestamps (2026-07-22):** `ble_hr_stream.py` now prepends a `recv_ts` receive-time
column/print to each line (Mac-side, no flash needed). `recv_ts` is accurate for live data but is *drain*
time, not sample time, during a back-fill burst — the device's `t_ms` remains the true relative clock.
**Clock-anchor / true sample time (2026-07-23, UNCOMMITTED + NOT YET FLASHED):** the current working-tree
edits to `archive/v1/src/max30102_hr_ble_log/main.cpp` (+`anchorSent`) and `ble_hr_stream.py` add a second column,
`reading_ts`, giving the *actual sample time* even for back-filled rows. Mechanism: the firmware sends its
current uptime as `#now,<millis()>` as the **first** telemetry notify of every connection (reset in
`onDisconnect`); the client pairs that with its wall clock into a boot anchor and maps each line's `t_ms`
back to a real timestamp. Rows from a **prior** boot (device rebooted mid-buffer — `t_ms` > current uptime,
since `t_ms` resets on reboot) are unknowable, so `reading_ts` is left **blank** rather than guessed.
Compiled only — the board wouldn't enumerate at session end, so this was NOT flashed; the active firmware is
still the 2026-07-23 CONFIG/P9/30 s-window build above, which does not emit `#now`. `reading_ts` stays blank
until this is flashed.
**`RED_PULSE_AMPLITUDE` 0x1F REVERTED → 0x0A (2026-07-23, working tree, NOT YET FLASHED):** the earlier
0x0A→0x1F bump was the WRONG call — it pushed baseline IR to ~130k+, which flattens the AC pulse ripple
`checkForBeat` needs, so the `beats` column sat at ~0, `last_bpm` fired only every tens of seconds (below
the 20 BPM floor → rejected), and `avg_bpm` never populated. 0x0A historically gives ~118k IR + reliable
74–82 BPM. Source is now back at 0x0A (built green) but the board wasn't enumerating at session end, so the
**active on-board firmware still runs the bad 0x1F** — reflash to fix. Live proof of the fault: IR pinned
~125–144k, `beats`≈0, `avg_bpm`=0 the whole capture. Lighter/stiller fingertip contact (IR ~100–120k) is
the other half of the fix.

## Known Toolchain Issues

- **Do NOT use `adafruit/Adafruit MLX90614 Library`** — it pulls in Adafruit BusIO, which fails to
  compile under this toolchain (`fatal error: SPI.h: No such file or directory`) even though MLX90614
  is I2C-only. Read the MLX directly via `Wire` instead. `robtillaart/MLX90614` is not a valid registry
  name either. Only `sparkfun/SparkFun MAX3010x` is declared in `lib_deps`.
- `toolchain-riscv32-esp` is a PlatformIO dep not needed for ESP32-S3 (Xtensa); a stub at
  `~/.platformio/packages/toolchain-riscv32-esp/` prevents download loops.
- **Reading `parts/` datasheets needs poppler — now installed (2026-09-15).** The machine originally
  had no poppler, so `Read` on a PDF and `pdftotext`/`pdftoppm` all failed; `brew install poppler` was
  run and PDFs are now readable (`/opt/homebrew/bin/pdftotext`). **RESOLVED 2026-09-15: all six part folders now hold a
  valid English `datasheet.pdf`** (verified as real PDFs, 1.0–2.1 MB each) — the earlier ST
  (LSM6DS3TR-C) and ADI (MAX30101) 404s have been fixed. `parts/esp32-c3-mini-1/` also keeps the
  superseded Chinese v1.7 datasheet, suffixed `_SUPERSEDED`.
- **Two PlatformIO Cores on this machine — keep their versions matched (2026-09-13).** The project
  `.venv` had Core 6.1.19 while `~/.platformio/penv` (the VSCode PIO extension) had 6.2.0, which
  shares `~/.platformio/packages/`. 6.1.19 demanded `tool-scons-4.40801.0` but only 6.2.0's
  `scons-local-4.8.1` was on disk, so every `pio run` sat in an **infinite mirror-retry loop**
  (`SSL: TLSV1_ALERT_ACCESS_DENIED` from `usc1.contabostorage.com`) — presenting as a silent 10-minute
  hang right after `Processing <env>`, not as an error. Fixed by `pip install -U platformio` inside
  the venv (now both 6.2.0). Do NOT delete either core: the venv one is the documented workflow, the
  penv one backs the IDE extension.
- **Do not run `pio run` in a background shell piped to `tail`** — the pipe buffers, so the mirror-loop
  output above is invisible until exit, and a second concurrent `pio run` on the same env crashes with
  `FileNotFoundError: .pio/build/<env>/.sconsign313.tmp` (two processes fighting over the build dir).
- PlatformIO mirrors occasionally fail SSL (`[SSL] record layer failure`) — it retries other mirrors,
  wait it out. `framework-arduinoespressif32` is ~3GB installed (need ≥5GB free before first build).
- **Two PlatformIO installs on this machine (2026-09-13): builds warn `Obsolete PIO Core v6.1.19 is
  used (previous was 6.2.0)`.** Plausible cause of multi-minute (~10 min) builds and a
  `.sconsign313.tmp` crash seen this session. Prefer running build/upload in the foreground so it
  isn't silently blocked; reconcile the duplicate core if builds keep hanging.
