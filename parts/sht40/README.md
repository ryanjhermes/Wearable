# SHT40 — ambient temperature + humidity

| Field | Value |
|---|---|
| Order code | SHT40-AD1B-R3 (`-R2`/`-R3` differ only in reel quantity) |
| Manufacturer | Sensirion |
| Supply | **1.08–3.6 V** (single rail, runs directly off 3.3 V) |
| Interface | I²C, address **0x44** (the `AD1B` variant; `BD1B` would be 0x45) |
| Datasheet | `datasheet.pdf` (16pp, English) |

## Why this part

**Not for more data — to stop the other data from lying.** A bar is hot and crowded, which raises
skin temperature and sweat with zero alcohol involved. Without an ambient reference the model can
learn "warm room" instead of "intoxicated". Same confound applies to EDA.

Must be exposed to outside air, NOT sealed against skin — this is the one sensor that belongs on the
top side / vented, not the skin side.

## Sourcing

| Field | Value |
|---|---|
| LCSC | **C2848306** |
| Package | DFN-4, **1.5 × 1.5 × 0.5 mm** |

## Schematic — pinout (from datasheet §5.4)

| Pin | Name | Connect to |
|---|---|---|
| 1 | SDA | `SDA` |
| 2 | SCL | `SCL` |
| 3 | VDD | `+3V3` |
| 4 | VSS | `GND` |

The center pad is **not** internally connected. Sensirion recommends leaving it unsoldered and
avoiding copper beneath it so heat is not conducted into the sensing element.

## Schematic — required externals

| Component | Value | Net | Why |
|---|---|---|---|
| C_VDD | 0.1 µF | VDD → GND | Decoupling, place close to pin 3 |

Address is fixed at **0x44** for the `AD1B` variant — not strappable. Uses the shared bus pull-ups.

## Layout — the placement rules are unusually strict

Sensirion's own guidance, and the reason this part can silently produce garbage:

- **Must see outside air.** Needs a vent or opening in the enclosure. Sealed against skin it measures
  the inside of the enclosure, which defeats the entire purpose.
- **Thermally isolate from the PCB.** Self-heat from the board biases both temperature *and* the
  relative-humidity calculation that depends on it. Slot or cut-away around it, minimal copper
  connection, keep it far from the LDOs and MCU.
- Do not solder the center pad or place copper beneath it.
- Top side, opposite the skin-facing optics.
- Humidity sensors drift with solder flux outgassing and IPA. Handle per Sensirion's reflow/cleaning
  notes and expect a settling period after assembly.
