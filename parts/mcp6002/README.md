# MCP6002 — archived v3 EDA/GSR research

> **Not in the v2 BOM.** EDA/GSR was explicitly deferred to v3. This folder is retained only so the
> research is not lost; no schematic agent should place this part on v2.

| Field | Value |
|---|---|
| Order code | **MCP6002T-I/SN** (`-I` = industrial temp grade, `/SN` = SOIC-8 narrow) |
| LCSC | **C116706** (MCP6002-I/SN, SOIC-8). JLCPCB also lists `MCP6002-E/SN` = C636235. Checked 2026-09-15 — **Basic/Extended not confirmed** |
| Manufacturer | Microchip |
| Channels | Dual (one for EDA, one spare) |
| Package | **SOIC-8, 1.75 mm tall** — MSOP-8 (1.1 mm) is not stocked at JLCPCB. Mount **top side**, where the 2.4 mm module sets the height, so this costs nothing |
| Datasheet | `datasheet.pdf` |

> **Folder-naming note:** the order code contains a `/`, which the filesystem reads as a directory
> separator. Never put an order code in a folder name. Folder = generic lowercase chip name
> (`mcp6002`); the full order code lives in this table. Same rule as every other part here.

## Role

Converts skin conductance into a voltage the ESP32's ADC can read. Electrodes are **ENIG-plated pads
on the PCB itself**, not a purchased part — specify ENIG finish when ordering the board, or the
tin/lead HASL finish will corrode against sweat.

## Alternatives if stock is a problem

`TLV9002` (TI, equivalent) · `OPA2333` (precision/chopper, better noise, pricier)

## Schematic — pinout (SOIC-8 / MSOP-8, from datasheet §3)

| Pin | Name | Note |
|---|---|---|
| 1 | VOUTA | Op-amp A output |
| 2 | VINA− | A inverting input |
| 3 | VINA+ | A non-inverting input |
| 4 | VSS | `GND` |
| 5 | VINB+ | B non-inverting input |
| 6 | VINB− | B inverting input |
| 7 | VOUTB | Op-amp B output |
| 8 | VDD | `+3V3` |

Rail-to-rail in and out, single supply — no negative rail needed.

## Schematic — required externals

| Component | Value | Net | Why |
|---|---|---|---|
| C_VDD | 0.1 µF | VDD → GND | Decoupling |
| R_sense | ~100 kΩ | electrode divider | Sets the measurable skin-conductance range; pick against expected 1–20 µS |
| R_fb, C_fb | TBD | feedback | Gain + low-pass; EDA is sub-1 Hz so filter hard |

**Values are not specified yet** — they depend on the electrode geometry and the conductance range
you target. This is the one block on the board that still needs a designed circuit, not just a
part choice.

## Interface

Output → one ESP32-C3 **ADC1** pin, read with oversampled `analogRead()`, gated on accelerometer
motion ≈ 0. ADC1 channels are GPIO0–GPIO4; **GPIO2 is a strapping pin — do not use it.**
GPIO3 (ADC1_CH3) was the clean candidate during this research, but v2 now reserves it for battery
sensing. A future v3 that restores EDA must assign and review a different ADC pin or redesign that
allocation.

## Status

Cut from v2 by user decision on 2026-09-15. Reconsider only in a separately scoped v3 design.
