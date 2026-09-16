# MAKK2016T2R2M — 2.2 µH power inductor (TPS61099 boost)

| Field | Value |
|---|---|
| Order code | MAKK2016T2R2M |
| LCSC | **C92923** — JLCPCB Extended, 2,712 in stock, $0.076 @1 (checked 2026-09-16) |
| Manufacturer | Taiyo Yuden |
| Package | 2.0 × 1.6 × 1.0 mm (2016 metric / 0806 imperial) |
| Value | 2.2 µH, 1.5 A saturation |
| Role | VSYS → SW energy-storage inductor for the TPS61099 4.7 V green-LED boost |
| Datasheet | **MISSING — see below** |

## Open gap: no datasheet on file

This folder was created on 2026-09-16 because the part was on the BOM and in the schematic with
**no evidence folder at all** — it was the only BOM line without one. The gap is now visible rather
than silent, but it is not closed.

What still needs a manufacturer document:
- Saturation and RMS current ratings at the boost's actual operating point. TI's TPS61099 datasheet
  asks for headroom above the switch current limit; "1.5 A saturation" is a distributor figure, not
  a verified curve.
- DCR, which sets conduction loss and therefore boost efficiency.
- The land-pattern drawing, to confirm the footprint below.

## Footprint

`pcb_v2:L_MAKK2016T_2.0x1.6mm`, imported from LCSC C92923 on 2026-09-16.

Two 1.2 × 1.8 mm pads on a 2.0 mm centre pitch. Geometry is plausible for a 2016-metric part but is
**the one footprint in this project not checked against a manufacturer drawing**, because of the gap
above. Verify before ordering.

One real defect was found and fixed on import: the EasyEDA courtyard was 2.00 × 1.60 mm, i.e. the
body size, which is **smaller than the pads** (they reach ±1.60 × ±0.90 mm). A courtyard inside the
pads lets KiCad place another component on top of them without a DRC error. Rebuilt at
±1.85 × ±1.15 mm.

## Layout note

The VIN capacitor → inductor → SW loop is the boost's hot loop and must be kept extremely short.
See [`../tps61099/README.md`](../tps61099/README.md) and [`../V2_BOM.md`](../V2_BOM.md).
