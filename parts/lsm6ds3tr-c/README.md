# LSM6DS3TR-C — 6-axis accelerometer + gyroscope

| Field | Value |
|---|---|
| LCSC | **C967633** |
| Manufacturer | STMicroelectronics |
| Package | **LGA-14L, 2.5 × 3.0 × 0.83 mm** |
| Supply | **1.71–3.6 V** (single rail, runs directly off 3.3 V) |
| Interface | I²C, address **0x6A / 0x6B** (SA0) |
| Datasheet | `datasheet.pdf` (114pp, English) |

## Why this part

Replaces the **BMI160**, which is Bosch EOL and **consign-only with zero stock at JLCPCB** — i.e.
JLCPCB will not source it at all.

**It is 6-axis: the gyroscope is free.** Use it — sway, tremor and gait instability are established
impairment markers, and it costs no extra board area or BOM.

## Firmware

The existing BMI160 driver (direct `Wire` register reads) does not port unchanged: different register
map and a possible axis remap. Estimated ~1 day.

## Schematic — pinout (LGA-14, from datasheet §3 Figure 1 / Table 2)

| Pin | Name | Connect to (I²C, "Mode 1") |
|---|---|---|
| 1 | SDO/SA0 | **Address LSb.** `GND` → 0x6A, `VDDIO` → 0x6B. Must not float — tie to `GND` |
| 2 | SDx | **Tie to `VDDIO` or `GND`** — datasheet requires it, not a leave-floating pin |
| 3 | SCx | **Tie to `VDDIO` or `GND`** — same |
| 4 | INT1 | Programmable interrupt. Route to a GPIO if you want data-ready/wake; else leave unconnected |
| 5 | VDDIO | `+3V3` — I/O rail, must match the I²C bus level |
| 6, 7 | GND | `GND` |
| 8 | VDD | `+3V3` |
| 9 | INT2 | Programmable interrupt 2 / DEN. Optional |
| 10, 11 | NC | Leave unconnected |
| 12 | CS | **I²C/SPI select — tie HIGH to `VDDIO`** for I²C. Floating or low puts the part in SPI mode and the bus read fails |
| 13 | SCL | `SCL` |
| 14 | SDA | `SDA` |

**Three pins here will silently break the design if left floating: CS (pin 12), SDx (2), SCx (3).**
The GY-BMI160 breakout handled the equivalent strapping for you.

## Schematic — required externals

| Component | Value | Net | Why |
|---|---|---|---|
| C_VDD | 100 nF | VDD → GND | Per ST's Figure 15 application circuit |
| C_VDDIO | 100 nF | VDDIO → GND | Per the same figure |

> The capacitor value glyphs do not extract cleanly from this PDF (the figure is vector text).
> 100 nF is ST's standard recommendation and matches the figure's `nF` unit — **confirm against
> Figure 15 on datasheet p.45 before finalizing.**

## Layout

- Orientation matters: record the package's X/Y/Z axes relative to the wrist so the firmware axis
  remap is known at bring-up rather than guessed.
- Mount on rigid board area; avoid flex or near a mounting screw that could pre-stress the package.
