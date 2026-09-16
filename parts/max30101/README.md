# MAX30101 — PPG / heart rate

| Field | Value |
|---|---|
| Order code | MAX30101EFD+T (tape & reel) |
| LCSC | **C2859066** |
| JLCPCB | In stock 319, **Extended**, ~$8.34 @ qty 1 (checked 2026-09-14) |
| Manufacturer | Analog Devices / Maxim |
| Package | OLGA-14, **5.6 × 3.3 × 1.55 mm** |
| Interface | I²C, address **0x57** |
| Datasheet | `datasheet.pdf` (32pp, English) |

## Power — READ THIS BEFORE WIRING

Verified from datasheet Absolute Maximum Ratings + Electrical Characteristics:

| Rail | Operating | Absolute max |
|---|---|---|
| **VDD** | **1.7–2.0 V (1.8 V typ)** | **+2.2 V** |
| **VLED+** | 3.1–5.0 V | +6.0 V |
| All other pins (incl. SDA/SCL) | — | +6.0 V |

- **3.3 V on VDD destroys this part.** It needs its own 1.8 V LDO.
- VLED+ is a separate rail and can run **straight off the LiPo** (3.0–4.2 V sits inside 3.1–5.0 V),
  so no boost converter is needed.
- SDA/SCL tolerate +6.0 V, so a **3.3 V I²C bus needs no level shifting** despite the 1.8 V VDD.

The MH-ET LIVE breakout hid all of this behind an onboard regulator.

## Why this part

Green LED (plus red + IR). Red/IR alone is a fingertip/SpO₂ combination; wrist PPG in commercial
devices uses green. Identical package, address and library to the MAX30102 — see `../README.md`.

## Open

- Wrist PPG performance is **unproven in this project** — the raw-IR capture diagnostic has never
  been run. See `CLAUDE.md`.

## Schematic — pinout (OLGA-14, from datasheet p.9)

| Pin | Name | Connect to |
|---|---|---|
| 1, 5, 6, 7, 8, 14 | N.C. | **Solder to PCB pads anyway** — datasheet calls for it for mechanical stability. Do not net them. |
| 2 | SCL | `SCL` |
| 3 | SDA | `SDA` |
| 4 | PGND | `GND` — LED-driver power ground. **Star-connect to GND at one point**, do not merge with pin 12 arbitrarily |
| 9, 10 | VLED+ | `VBAT` — both pins, tied together |
| 11 | VDD | `+1V8` |
| 12 | GND | `GND` — analog ground |
| 13 | INT | Active-low, **open-drain → needs a pull-up**. Datasheet Figure shows 1 kΩ. Optional: tie to a GPIO for interrupt-driven reads, or leave unconnected + poll |

## Schematic — required externals

From the Typical Application Circuit (datasheet p.24):

| Component | Value | Net | Why |
|---|---|---|---|
| C_VDD | 0.1 µF | VDD → GND | Analog supply bypass, place closest to pin 11 |
| C_VDD_bulk | 1 µF | VDD → GND | Datasheet shows 0.1 µF + a bulk cap on the 1.8 V rail |
| C_VLED | 4.7 µF | VLED+ → PGND | **Mandatory.** LED pulses draw up to 200 mA in bursts; without this the rail collapses and the PPG signal is garbage |
| C_VLED_hf | 0.1 µF | VLED+ → PGND | High-frequency bypass |
| R_INT | 1 kΩ | INT → 3V3 | Only if INT is used |

Rail budget from the same figure: **VDD +1.8 V @ 20 mA**, **VLED+ up to 200 mA peak**.

## Layout

- The 4.7 µF VLED cap and the LED return path are the critical loop — keep it tight and low-impedance.
  This is the single most common cause of bad PPG on a custom board.
- Skin-facing side. No air gap to skin.
- If wrist PPG is weak, the fallback is an **opaque ring printed into the enclosure** between the LEDs
  and the photodiode — an enclosure change, not a board change, so this stays reversible.

## Blocking risk

**Wrist PPG at this wavelength has never been measured in this project.** The green-LED case for
MAX30101 over MAX30102 is commercial-practice inference only. The diagnostic
(`archive/v1/src/max30102_raw_ir/` + `archive/v1/scripts/raw_ir_capture.py`) exists and has never
been run. ~$8/unit and the largest single BOM line — settle it before ordering.
