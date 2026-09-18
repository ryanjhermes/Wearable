# v1 — breakout prototype (ARCHIVED 2026-09-15)

Everything here describes the **XIAO ESP32S3 + Amazon breakout modules** build: the desk/wrist
prototype that proved the signal chain. It is frozen. The project has moved to a **custom
fab-assembled PCB** (`parts/` for the BOM, `CLAUDE.md` for decisions).

**Nothing in this folder is authoritative. `CLAUDE.md` wins on every conflict.**

## Why it was archived, not deleted

The breakout prototype is still the only *working* hardware, and the next useful experiment —
the wrist PPG raw-IR capture that validates wavelength and algorithm assumptions — runs on it.
`docs/wiring.md` is the wiring reference for that rig. Archived ≠ useless; archived = not the
current design.

## Contents

| Path | What it is | Still useful? |
|---|---|---|
| `V1_REFERENCE.md` | v1 firmware, XIAO board, breakout I2C and PlatformIO detail, moved out of `CLAUDE.md` 2026-09-17 | **Yes** — the reference for any v1 firmware work |
| `docs/hardware_debug_log.md` | Bring-up narrative: board thermal fault, reverse-polarity battery saga, MLX90614 death, HR bring-up | **Yes** — the *root causes and diagnostic heuristics* transfer to any board |
| `docs/wiring.md` | Breakout I2C wiring tables + scanner troubleshooting | Yes, while the prototype rig exists |
| `docs/development_setup.md` | PlatformIO setup, boot/reset upload recovery | Partly — recovery steps transfer; the `platformio.ini` and board sections are S3-specific |
| `docs/wearable_hardware.md` | Breakout component specs (MAX30102, MLX90614, BMI160, XIAO) | Superseded by `parts/` for the new board |
| `docs/project_plan.md` | Original 6-phase roadmap | **No** — describes a different project (OLED, buttons, vibration motor, all since cut) |
| `docs/component_images/` | Reference photos of the breakouts, XIAO and LiPo | Yes for the prototype; `mlx90614_gy906/` is a dead part |
| `enclosure/` | First-pass two-part printed box (`.3mf` + renders) | Reference geometry only — never printed or fitted |
| `src/` | All 13 firmware envs (2 live + 11 already-retired under `src/archive/`) | **Yes — still builds.** `platformio.ini` sets `src_dir = archive/v1/src` |
| `scripts/` | `ble_hr_stream.py`, `raw_ir_capture.py`, `plot_raw_ir.py` — Mac-side BLE clients | **Yes** — `raw_ir_capture.py` is half the unrun wrist-PPG diagnostic |
| `data/` | 17 captures from the breakout rig, 2026-07-12 → 2026-07-23: BLE HR streams, motion logs, combined runs, flash dumps | Yes as baseline reference signal — but see note below |

## About `archive/v1/data/`

These were previously gitignored (`data/*.csv`, root-anchored), so moving them here makes them
**trackable for the first time** — 328 KB across 17 files. That is deliberate: archiving is for
preservation, and left ignored they would exist only on one Mac. To keep them out of git instead,
add `archive/v1/data/` to `.gitignore`.

`data/` at the repo root stays live — scripts and monitor filters write new captures there.

**There are still zero raw-IR captures in this set.** The wrist PPG diagnostic for wavelength and
wrist-algorithm validation has never been run; MAX30101 selection is already locked.

## What was carried forward

`CLAUDE.md` was slimmed to a pointer file on 2026-09-17 to stop it costing ~18k tokens on every
message. The v1 technical detail it used to carry now lives in **`V1_REFERENCE.md`, in this folder**
— nothing was lost:

- I²C diagnostic heuristics → `V1_REFERENCE.md` § Hardware & I2C
- Battery verification procedure and the LiPo safety signatures → § Hardware & I2C
- Boot/reset upload recovery → § Board, "Upload/monitor procedure"
- Toolchain traps (Adafruit BusIO, dual PlatformIO cores) → § Known Toolchain Issues
- PlatformIO envs, monitor filters and firmware architecture → § Toolchain, § Firmware Architecture

Two v2-facing items stayed live: the BOOT/RESET test-pad requirement and the LiPo safety
signatures are repeated in `CLAUDE.md` under "Hard rules" and "Locked constraints". V2 design
rationale moved to `docs/DESIGN_HISTORY.md`.

## Known stale references inside this folder

Left as-is rather than rewritten — these are historical documents.

- `docs/project_plan.md` points at a `hardware/` folder that no longer exists (it became
  `enclosure/`, and its v1 contents are now `archive/v1/enclosure/`).
- Board serial numbers were removed from `docs/hardware_debug_log.md` on 2026-09-15 because two
  docs recorded contradictory mappings. Which physical XIAO is in use is **unestablished** —
  assume the thermal-fault history may apply to it.


## Firmware is archived but NOT dead

`platformio.ini` stays at the repo root (PlatformIO requires it) and was repointed with
`src_dir = archive/v1/src`, so every env still builds and uploads exactly as before. Verified with
a complete 13-environment `pio run` on 2026-09-16.

This matters for one specific reason: **`src/max30102_raw_ir/` + `scripts/raw_ir_capture.py` +
`scripts/plot_raw_ir.py` are the wrist-PPG diagnostic that has never been run.** MAX30101 is now
selected because it preserves green, red, and IR in one package, so this test no longer gates the
part choice; it remains the next experiment for wavelength and wrist-algorithm validation.

`monitor/` stayed at the repo root: PlatformIO resolves `monitor_filters` relative to the project
root, so moving it would break `csv_capture`, `motion_csv` and `flash_dump`.
