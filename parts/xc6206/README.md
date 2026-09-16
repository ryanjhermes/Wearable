# XC6206P182MR — 1.8 V LDO (MAX30101 VDD only)

| Field | Value |
|---|---|
| Order code | XC6206P182MR |
| LCSC | **C21659** (Torex) · **C347373** (UMW) · C5252894 (MSKSEMI) |
| Package | SOT-23-3 |
| Output | 1.8 V, 80 mA |
| Iq | 1 µA |
| Datasheet | **NEEDED** — see below |

Feed from **+3V3**, not VBAT. Load is only ~20 mA (MAX30101 VDD), so 80 mA is ample.

## Pin trap

Reported pinout: **1 = VSS, 2 = VIN, 3 = VOUT** — ground on pin 1, which is not the arrangement
most SOT-23-3 parts use. **Verify against the datasheet before routing.**

## Externals

1 µF on VIN→GND, 1 µF on VOUT→GND.

## Why this rail exists at all

MAX30101 VDD absolute max is **+2.2 V**. 3.3 V destroys it. The breakout you own hid this behind
an onboard regulator. See `../max30101/README.md`.
