# TP4054 — single-cell LiPo charger

| Field | Value |
|---|---|
| Order code | TP4054-42-SOT25R |
| LCSC | **C32574** (TOPPOWER). Alternates: C382138 (TPOWER), C5381776 (JSMSEMI) |
| Package | **SOT-23-5** |
| Input | 4–9 V (from USB-C VBUS) |
| Charge current | Programmable, 450 mA max — **we use ~100 mA** |
| Datasheet | `datasheet.pdf` (14pp) |

Chosen over the TP4056 (C16581): that is ESOP-8 with a thermal pad and 1 A class — oversized and
larger for a 250 mAh cell.

## Charge current — the one calculation that matters

From the datasheet: **I_BAT = 1000 V / R_PROG**

| R_PROG | Charge current | C-rate on the 250 mAh cell |
|---|---|---|
| **10 kΩ** | **100 mA** | **0.4 C — use this** |
| 8 kΩ | 125 mA | 0.5 C |
| 2 kΩ | 500 mA | 2 C — **never** |

**Use 10 kΩ.** It is a standard E24 value, gives a gentle 0.4 C, and charges the cell in ~3 h.
The datasheet specifies a **1% resistor** — do not substitute a 5% part.

Getting this wrong is a LiPo safety issue, not a performance one. This board has already had one
reverse-polarity episode and one suspected charge-IC fault (`archive/v1/docs/hardware_debug_log.md`).

## Schematic

| Pin | Name | Connect to |
|---|---|---|
| 1 | TEMP | Battery thermistor. **Tie to GND if unused** — do not float |
| 2 | PROG | 10 kΩ 1% → GND |
| 3 | GND | `GND` |
| 4 | VCC | USB-C `VBUS` |
| 5 | BAT | `VBAT` (cell +) |

Externals: 10 µF on VCC→GND, 10 µF on BAT→GND, 10 kΩ 1% on PROG→GND.

No CHRG status LED — LEDs are cut from this design. Charge state is not externally visible; the
battery sense divider on an ADC pin is the only indication.
