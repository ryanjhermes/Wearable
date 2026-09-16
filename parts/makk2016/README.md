# MAKK2016T2R2M — 2.2 µH power inductor (TPS61099 boost)

| Field | Value | Source |
|---|---|---|
| Order code | MAKK2016T2R2M | |
| LCSC | **C92923** — JLCPCB Extended, 2,712 in stock, $0.076 @1 | checked 2026-09-16 |
| Manufacturer | Taiyo Yuden | |
| Inductance | **2.2 µH ±20%** | manufacturer, 2026-09-16 |
| Isat | **1.5 A** (ΔL = 30%) | manufacturer |
| Irms / Itemp | **1.5 A** (ΔT = 40 °C) | manufacturer |
| DCR max | **0.16 Ω** | manufacturer |
| Body | **2.0 ±0.1 × 1.6 ±0.1 × 1.0 max mm** (2016 metric / 0806) | manufacturer |
| Type | Shielded wire-wound metal-core chip power inductor | |
| Role | VSYS → SW energy-storage inductor for the TPS61099 4.7 V green-LED boost | |
| Datasheet PDF | **not on file** — see below | |

## Lifecycle: this part number has been renamed

Taiyo Yuden's product database returns a rename notice for `MAKK2016T2R2M`. The current
part numbers are **`LSANB2016KKT2R2M`** (general equipment / medical / mobile) and
**`LLANB2016KKT2R2M`** (medical). Same 2016 body, same 2.2 µH, same ratings.

This does not block the v2 spin: LCSC stocks C92923 under the old code and JLCPCB can place it.
But treat the old number as legacy, and if a future order finds C92923 gone, the successors above
are the direct replacement rather than a re-selection exercise.

## Current margin — adequate

The TPS61099's switch current limit is **0.8 A minimum**, so the peak inductor current the
converter can ever command is bounded well below the 1.5 A Isat rating. The boost's actual working
current is far lower again: roughly 300 mA input while the MAX30101 pulses its LEDs. Conduction
loss at that current is about 0.3² × 0.16 = **14 mW**, negligible.

Current rating is therefore **not** a risk on this part. See
[`../tps61099/README.md`](../tps61099/README.md) and the audit's open question about boost rail
margin, which is about the converter's regulation, not this inductor.

## Remaining gap: no land-pattern drawing

The electrical and mechanical figures above are manufacturer-confirmed. What is still missing is
the **recommended land pattern** — Taiyo Yuden supplies it as a DXF download that could not be
retrieved automatically, and LCSC's PDF endpoint serves an HTML bot page rather than the file.

The PDF should be fetched by hand from the LCSC product page and saved here as `datasheet.pdf`.
`check_parts.py` will keep reporting this folder as a gap until it is.

## Footprint

`pcb:L_MAKK2016T_2.0x1.6mm`, imported from LCSC C92923 on 2026-09-16.

Two 1.2 × 1.8 mm pads on a 2.0 mm centre pitch. Geometry is plausible for a 2016-metric part and
the pads comfortably cover a 2.0 × 1.6 mm body, but it is **the only footprint in this project not
checked against a manufacturer drawing**, because of the gap above. Verify before ordering.

One real defect was found and fixed on import: the EasyEDA courtyard was 2.00 × 1.60 mm, i.e. the
body size, which is **smaller than the pads** (they reach ±1.60 × ±0.90 mm). A courtyard inside the
pads lets KiCad place another component on top of them without a DRC error. Rebuilt at
±1.85 × ±1.15 mm.

## Layout note

The VIN capacitor → inductor → SW loop is the boost's hot loop and must be kept extremely short.
See [`../tps61099/README.md`](../tps61099/README.md) and [`../V2_BOM.md`](../V2_BOM.md).
