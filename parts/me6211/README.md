# ME6211C33M5G-N — 3.3 V LDO

| Field | Value |
|---|---|
| Order code | ME6211C33M5G-N |
| LCSC | **C82942** — 243k stock at LCSC (checked 2026-09-15). **Basic/Extended unconfirmed** |
| Manufacturer | MICRONE (Nanjing Micro One) |
| Package | **SOT-23-5** |
| Output | 3.3 V fixed, 500 mA |
| Dropout | **120 mV @ 100 mA** |
| Datasheet | `datasheet.pdf` (20pp) |

## Why low dropout is the whole point

A LiPo falls 4.2 V → 3.0 V as it drains. An LDO cannot boost: once the input drops below
3.3 V + dropout, the output follows the input down. With 120 mV dropout this part regulates until
the cell reaches ~3.42 V; a generic AMS1117 (1.1 V dropout) would stop regulating at 4.4 V — i.e.
never regulate at all on a single LiPo. **Do not substitute a generic 1117.**

## Pinout — VERIFIED against datasheet p.4 (2026-09-15)

SOT-23-5: **1 = VIN, 2 = VSS, 3 = CE, 4 = NC, 5 = VOUT.**
(The earlier web-sourced figure was correct; the warning is withdrawn.)

**Tie CE to VIN.** A floating CE gives no output, and the board looks completely dead with no other
symptom.

⚠️ **Do not substitute the ME6211H.** Per the Selection Guide (p.2) the `C` and `H` series differ in
enable polarity — `H` is the active-low variant. Same package, same voltage, opposite behaviour.

## Externals

1 µF on VIN→GND, 1 µF on VOUT→GND (ceramic, close to the pins).

