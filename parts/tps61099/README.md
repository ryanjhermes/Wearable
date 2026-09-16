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
| 4 | EN | VSYS for always enabled, lowest-parts-count design |
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
| 1 | 270 kOhm, 1% | 0402WGF2703TCE / C25770 | FB to GND |

The output is about 4.704 V. This target stays inside both MAX30101 VLED ranges: 3.1-5.0 V for
red/IR and 4.5-5.5 V for green, including the TPS61099 feedback-reference tolerance. Account for
ceramic-capacitor DC bias; two nominal 10 uF output parts provide margin. Keep the
input-capacitor/inductor/SW loop compact and the feedback trace away from SW.
