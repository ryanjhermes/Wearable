# SS14 — USB-to-system Schottky diode

| Field | Value |
|---|---|
| Order code | SS14 |
| LCSC | **C2480**; recheck stock at order time |
| Package | SMA / DO-214AC |
| Rating | 1 A, 40 V; forward drop up to about 0.55 V at 1 A |
| Datasheet | `datasheet.pdf` (SS12-SS1200 family) |

Part of the USB/battery load-sharing circuit. Connect **anode to USB VBUS** and **cathode/stripe to
VSYS**. The diode must carry the entire system load while USB is attached. Its drop also makes VSYS
lower than the AO3401A gate voltage, ensuring the battery MOSFET is off.

