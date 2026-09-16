# TP4054 — single-cell LiPo charger

| Field | Value |
|---|---|
| Order code | TP4054-42-SOT25R |
| LCSC | **C32574** |
| Package | SOT-23-5 |
| Input | 4-9 V from USB VBUS |
| Programmed current | 100 mA nominal with 10 kOhm 1% |
| Datasheet | `datasheet.pdf` |

## Correct pinout

| Pin | Name | Connect to |
|---:|---|---|
| 1 | CHRG | Leave open in v2; no status LED |
| 2 | GND | GND |
| 3 | BAT | BAT+ cell node and AO3401A drain |
| 4 | VCC | USB VBUS; bypass locally |
| 5 | PROG | 10 kOhm 1% to GND |

There is **no TEMP pin** on this part. Earlier project notes that labeled pin 1 TEMP and shifted the
remaining pins were wrong and would have produced a nonfunctional/unsafe footprint.

For charge current at or below 150 mA, the datasheet gives `RPROG = 1000 / IBAT`. Therefore 10 kOhm
sets 0.1 A. Do not substitute 5% tolerance.

Use the hardware load-sharing circuit in [`../V2_BOM.md`](../V2_BOM.md); the system must not attach
directly to BAT. Place at least 1 uF at VCC; v2 uses 4.7 uF for margin. A BAT capacitor is omitted only
if the battery is permanently connected. This charger has no cell-temperature input or safety timer,
so its approved use is a protected cell in a supervised, off-wrist prototype, not unattended/on-body
charging.
