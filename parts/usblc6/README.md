# USBLC6-2SC6 — USB ESD protection

| Field | Value |
|---|---|
| Order code | USBLC6-2SC6 |
| LCSC | **C7519** |
| JLCPCB | **Extended** (confirmed 2026-09-15) |
| Package | SOT-23-6 |
| Datasheet | `datasheet.pdf` (STMicroelectronics, 14 pages) |

Two-channel ESD/TVS array on the USB D+/D− pair. Place it immediately behind the USB-C receptacle,
before the two 22 Ohm series resistors and the ESP32-C3's IO18/IO19.

| Pin | Connect to |
|---:|---|
| 1 and 6 | D− pass-through, connector side and MCU side |
| 3 and 4 | D+ pass-through, connector side and MCU side |
| 2 | GND with a short, low-inductance return |
| 5 | USB VBUS |

Copy the routing topology from the datasheet/reference schematic, but verify the chosen D+/D− pairing
in the symbol. Keep connector-to-array traces short and avoid stubs.
