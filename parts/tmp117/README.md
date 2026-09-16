# TMP117 — contact skin temperature

| Field | Value |
|---|---|
| Order code | TMP117AIDRVR |
| LCSC | **C699536** |
| Manufacturer | Texas Instruments |
| Package | **WSON-6 (DRV), 2.0 × 2.0 × 0.75 mm** |
| Supply | **1.7–5.5 V** (single rail, runs directly off 3.3 V) |
| Interface | I²C, address **0x48** (strappable 0x48–0x4B) |
| Accuracy | ±0.1 °C |
| Datasheet | `datasheet.pdf` (50pp, English) |

## Layout note

Measures its own die temperature, so it needs thermal coupling to skin (via stitch to an exposed
pad) and thermal isolation from the ESP32 side. Treated as **optional insurance, not a requirement** —
the self-heating hypothesis was never validated. See `CLAUDE.md`.

Replaces the MLX90614, which was non-contact IR (wrong measurement), 4.1 mm tall, and is suspected dead.

## Schematic — pinout (WSON-6 / DRV, from datasheet Table 5-1)

| Pin | Name | Type | Connect to |
|---|---|---|---|
| 1 | SCL | I | `SCL` |
| 2 | GND | — | `GND` |
| 3 | ALERT | O | Open-drain. Leave unconnected for polled reads, or pull up + route to a GPIO |
| 4 | ADD0 | I | **Address select — must NOT float.** Tie to `GND` for 0x48 |
| 5 | SDA | I/O | `SDA` |
| 6 | V+ | P | `+3V3` |
| — | Thermal pad | — | Solder to a `GND` copper pour — this is the thermal path to the die |

Address strapping (ADD0): `GND` → **0x48** · `V+` → 0x49 · `SDA` → 0x4A · `SCL` → 0x4B.
Use **0x48**; no conflict with SHT40 (0x44), MAX30101 (0x57), LSM6DS3TR-C (0x6A/0x6B).

## Schematic — required externals

| Component | Value | Net | Why |
|---|---|---|---|
| C_V+ | 0.1 µF | V+ → GND | Supply bypass, close to pin 6 |
| R_ALERT | 10 kΩ | ALERT → 3V3 | Only if ALERT is used (open-drain) |

No other support parts. ~3.5 µA active — negligible against the 250 mAh budget.

## Layout — this part's placement IS its calibration

It reports **its own die temperature**, so the thermal path defines the measurement:

- Thermal pad down to a copper pour that reaches a **skin-facing exposed pad**; vias stitch pad → pour.
- Keep it away from the ESP32-C3-MINI-1 and both LDOs — they are the heat sources on this board.
- A slot or copper relief between it and the MCU section is **optional cheap insurance, not a
  requirement** — the self-heating hypothesis was inferred from the MLX90614 behaviour and never
  measured. See `CLAUDE.md`.
