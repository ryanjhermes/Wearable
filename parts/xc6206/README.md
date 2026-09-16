# XC6206P182MR — 1.8 V LDO for MAX30101 VDD

| Field | Value |
|---|---|
| Order code | XC6206P182MR |
| LCSC | **C21659** (Torex) |
| Package | SOT-23-3 |
| Output | 1.8 V; 80 mA minimum rated output for the 1.8 V variant; project load is approximately 20 mA maximum |
| Quiescent current | about 1 uA typical |
| Datasheet | `datasheet.pdf` (17-page Torex document, re-encoded as a clean standard PDF on 2026-09-15) |
| Official source | <https://product.torexsemi.com/en/series/xc6206> · direct PDF: <https://product.torexsemi.com/system/files/series/xc6206.pdf> |

Feed VIN from 3V3. Use 1 uF ceramic capacitors from VIN to GND and VOUT to GND, placed close to the
part. This rail is mandatory because MAX30101 VDD has a 2.2 V absolute maximum.

## Verified SOT-23 pinout

| Pin | Name | Connect to |
|---:|---|---|
| 1 | VSS | GND |
| 2 | VOUT | 1V8 |
| 3 | VIN | 3V3 |

**Do not use the former project note that said pin 2 was VIN and pin 3 was VOUT.** The current
manufacturer datasheet's SOT-23 assignment table confirms the mapping above.
