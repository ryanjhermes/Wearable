# AO3401A — P-channel load-sharing MOSFET

| Field | Value |
|---|---|
| Order code | AO3401A |
| LCSC | **C15127**; recheck stock at order time |
| Manufacturer | Alpha & Omega Semiconductor |
| Package | SOT-23 |
| Rating | -30 V; RDS(on) max 85 mOhm at VGS = -2.5 V |
| Datasheet | `datasheet.pdf` |

Used in the three-part USB/battery load-sharing circuit derived from Microchip AN1149.

## Pinout and connection

| Pin | Name | Connect to |
|---:|---|---|
| 1 | Gate | USB VBUS and 100 kOhm to GND |
| 2 | Source | VSYS |
| 3 | Drain | BAT+ / TP4054 BAT |

This reverse orientation is intentional. With USB absent, the body diode starts VSYS and the gate
pulldown turns the MOSFET on. With USB present, VBUS drives the gate high while the SS14 supplies
VSYS, so the MOSFET isolates the cell from system load. Verify the symbol's pad numbers and body-diode
direction before routing.

