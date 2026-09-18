# TPS61099 — mandatory 4.7 V boost for MAX30101 green LED

| Field | Value |
|---|---|
| Order code | TPS61099DRVR, adjustable version |
| LCSC | **C2842395**; recheck stock at order time |
| Manufacturer | Texas Instruments |
| Package | DRV WSON-6, 2 x 2 mm, exposed pad |
| Capability | Up to 300 mA for 3.3 V to 5 V conversion; 0.8 A minimum switch limit |
| Datasheet | `datasheet.pdf` |

**Status: approved and populated in v2.** Green PPG is mandatory, and MAX30101 specifies 4.5-5.5 V
for green, above a one-cell LiPo over its entire charge range.

## Pinout

| Pin | Name | Connect to |
|---:|---|---|
| 1 | GND | GND |
| 2 | VOUT | 4V7_PPG and output capacitors |
| 3 | FB | center of 1 MOhm / 270 kOhm divider |
| 4 | EN | ESP32 GPIO10 `PPG_PWR_EN`; 100 kOhm pulldown to GND |
| 5 | SW | 2.2 uH inductor output |
| 6 | VIN | VSYS and input capacitor |
| 7 / exposed pad | GND | solder to ground |

## Required externals

| Qty | Value | Part / LCSC | Connection |
|---:|---|---|---|
| 1 | 2.2 uH, 1.5 A saturation | MAKK2016T2R2M / C92923 | VSYS to SW |
| 1 | 10 uF, 10 V X5R | CL10A106KP8NNNC / C19702 | VIN to GND |
| 2 | 10 uF, 10 V X5R | CL10A106KP8NNNC / C19702 | VOUT to GND |
| 1 | 1 MOhm, 1% | 0402WGF1004TCE / C26083 | VOUT to FB |
| 1 | 249 kOhm, 1% | 0402WGF2493TCE / C11425 | FB to GND (was 270k/C25770 until 2026-09-18; see `../V2_BOM.md`) |
| 1 | 100 kOhm, 1% | 0402WGF1003TCE / C25741 | EN to GND; off during reset |

The output is about 4.704 V. This target stays inside both MAX30101 VLED ranges: 3.1-5.0 V for
red/IR and 4.5-5.5 V for green, including the TPS61099 feedback-reference tolerance. Account for
ceramic-capacitor DC bias; two nominal 10 uF output parts provide margin. Keep the
input-capacitor/inductor/SW loop compact and the feedback trace away from SW.

MAX30101 recommends VDD before VLED+ at power-up. Firmware must keep `PPG_PWR_EN` low through reset,
wait until the 1.8 V rail is established, and only then drive it high. The external pulldown makes the
safe state independent of GPIO reset behavior. TPS61099 provides true output disconnection while
disabled; never replace this connection with EN tied directly to VSYS.

Taiyo Yuden renamed MAKK2016T2R2M to **LSANB2016KKT2R2M**, its mass-production preferred successor.
Both are 2.2 uH, 0806/2016, 1.5 A rated/saturation-current class, and 0.16 Ohm maximum DCR. Keep C92923
for the current capture baseline, but recheck the old number at order time and use the successor only
after confirming its exact assembly identifier and footprint.
