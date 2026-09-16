# Parts evidence and v2 BOM

Start with **[`V2_BOM.md`](V2_BOM.md)**. It is the authoritative pre-schematic list of approved
parts, exact passives, power architecture, approval status, and unresolved evidence.
Then read **[`V2_HARDWARE_AUDIT.md`](V2_HARDWARE_AUDIT.md)** for the remaining system-level risks
and validation gates.

Each component folder contains a human-readable summary and its local `datasheet.pdf`. The folders
are evidence, not an independent BOM: quantities and population choices belong in `V2_BOM.md` until
the schematic exists, then in the schematic-generated BOM.

## Selected v2 devices

| Function | Part | LCSC | Evidence |
|---|---|---|---|
| MCU | ESP32-C3-MINI-1-N4 | C2838502 | [`esp32-c3-mini-1/`](esp32-c3-mini-1/) |
| PPG | MAX30101EFD+T | C2859066 | [`max30101/`](max30101/) |
| Skin temperature | TMP117AIDRVR | C699536 | [`tmp117/`](tmp117/) |
| IMU | LSM6DS3TR-C | C967633 | [`lsm6ds3tr-c/`](lsm6ds3tr-c/) |
| Ambient temperature/humidity | SHT40-AD1B-R3 | C2848306 | [`sht40/`](sht40/) |
| 3.3 V LDO | ME6211C33M5G-N | C82942 | [`me6211/`](me6211/) |
| 1.8 V LDO | XC6206P182MR | C21659 | [`xc6206/`](xc6206/) |
| LiPo charger | TP4054-42-SOT25R | C32574 | [`tp4054/`](tp4054/) |
| Load-share MOSFET | AO3401A | C15127 | [`ao3401a/`](ao3401a/) |
| Load-share diode | SS14 | C2480 | [`ss14/`](ss14/) |
| USB ESD | USBLC6-2SC6 | C7519 | [`usblc6/`](usblc6/) |
| USB-C | TYPE-C-31-M-12 | C165948 | [`usb-c-16p/`](usb-c-16p/) |
| Mandatory green-LED boost | TPS61099DRVR | C2842395 | [`tps61099/`](tps61099/) |

`mcp6002/` is retained only as archived v3 EDA/GSR research and is not part of v2.

## Repository convention

- Folder names are lowercase generic part names.
- The current source PDF is always `datasheet.pdf`; superseded copies are labeled explicitly.
- Never infer approval merely because a folder exists.
- Recheck LCSC stock, lifecycle, price, and JLCPCB assembly class immediately before ordering.
