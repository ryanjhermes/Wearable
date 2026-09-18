# V2 enclosure

Two-piece printable enclosure built parametrically around the populated-PCB STEP and the selected
EEMB `LP502030-PCM` battery envelope. See [`../parts/V2_BOM.md`](../parts/V2_BOM.md) for
battery/release evidence and [`../pcb/README.md`](../pcb/README.md) for authoritative board status.

## Generate

```bash
source .venv/bin/activate          # CadQuery 2.8.0
python enclosure/generate_enclosure.py
```

The script writes STEP, STL, SVG previews and the machine-readable review report under
`generated/mechanical_review/`. It exits non-zero if any mechanical check fails.

## Structural rebuild — 2026-09-18

The 2026-09-17/18 geometry was structurally broken. Three defects were found and fixed:

| Defect | Was | Now |
|---|---|---|
| Snap tabs joined to the lid by a sliver | tab spanned z -2.05..+0.25, lid wall started at +0.15 → **0.10 mm of weld, 0.18 mm³** carrying a 2.2 mm cantilever | fingers cut from a continuous lap skirt, rooted over their full 6.0 x 0.70 mm section → **2.10 mm³** |
| PCB not retained | plain 25 x 47 x 1.85 mm pocket, no ledge or hold-down; 0.50 mm lateral slop, 1.05 mm vertical travel | 1.25 mm perimeter ledge (1.00 mm bearing) + full-length lid hold-down blocks; 0.25 mm slop, 0.05 mm vertical |
| Parting line through the board | at z +0.15, i.e. 0.195 mm *below* the board's top face — the tray rim could not capture the board | parting plane is the board's top face, z +0.345 |

The board datum was re-measured from `wearable_v2_pcb.step` rather than assumed: board faces at
-0.085 / +0.995, top-side bodies from +0.995, lowest bottom-side body at -0.905, all shifted by
`BOARD_Z_SHIFT = -0.65`.

## Current geometry

**Closed exterior 27.7 x 49.7 x 12.75 mm.** 1.6 mm wall, 0.25 mm of slop per side around the
24 x 46 mm board, 3.0 mm outer corner radius.

- `generated/mechanical_review/enclosure_bottom.step` / `.stl` — skin-side tray. PCB support ledge,
  MAX30101 and TMP117 windows, the outer half of the lap joint, four blind snap catches.
- `generated/mechanical_review/enclosure_top.step` / `.stl` — lid. Continuous 0.70 mm lap skirt with
  four snap fingers, PCB hold-down blocks, battery shelves and end stop, USB-C mouth, SHT40 vent.

Each file is one watertight solid (verified: 1 connected component, 0 non-manifold edges).

| Interface | Value |
|---|---|
| Lap joint | 2.445 mm deep, 0.70 mm skirt, 0.10 mm clearance per face |
| Snap latches | 4 fingers, 6.0 x 0.70 mm, 0.20 mm hook projection and engagement, peak bending strain **3.51 %** |
| PCB support | 1.25 mm ledge, 1.00 mm bearing on the board edge |
| PCB hold-down | 2.30 mm overlap west, 1.00 mm east, 0.05 mm nominal gap above the board |
| Battery | 20.5 x 32 x 5.3 mm on shelves at z 3.65; 0.55 mm bearing west, 0.70 mm east |
| Battery to antenna keepout | 2.1 mm, backed by a 0.60 mm end stop so the cell cannot drift over the trace antenna |
| Battery to roof | 0.35 mm |
| USB-C mouth | 10.0 x 4.0 mm, 0.53 mm side and 0.80 mm top clearance, **single piece** — the parting plane sits at the connector's seating plane |
| MAX30101 | 5.4 x 7.7 mm hard window + separate opaque compliant gasket, 0.25 mm clearance per side |
| TMP117 | 4.2 x 4.2 mm relief + separate 3 x 3 x 1.345 mm soft insulating pad, zero nominal interference |
| SHT40 | 3 x 2 mm roof vent offset 1.4 mm toward the case end, 1.2 mm clear of the battery |
| Tray floor | 1.20 mm, 0.72 mm under the lap-joint groove |

Height rose 0.35 mm against the old 12.4 mm figure. That buys the lap-joint depth and the floor under
its groove; the old 12.4 mm number described a case that could not hold the board.

All 24 checks pass and all 12 collision volumes are 0.0000 mm³. The authoritative pass/fail fields are
in `generated/mechanical_review/mechanical_review.json`. KiCad could not load local 3D models for J1,
U7 or U10, so the assembly uses conservative body-envelope surrogates documented in that report.

## Printing

PETG or nylon. **Not PLA** — it will fatigue or snap at the snap fingers when the lid is opened
repeatedly. Print the lid roof-down. Printer shrinkage may require tuning the 0.10 mm lap clearance or
the 0.20 mm hook projection; print one test pair before committing.

## Remaining physical checks

- Print and fit-test with the real PCB, the selected cell, the optical gasket and the thermal pad.
  CAD clearance is not a tolerance validation.
- The battery end stop **bridges 13.2 mm** over the ESP32-C3-MINI-1 when the lid prints roof-down.
  Verify that bridge on the first print.
- The USB-C mouth is sized to the receptacle envelope, not to a specific cable overmold. Check a real
  cable reaches the receptacle.
- Select the actual compliant optical gasket and TMP117 thermal-pad materials and verify contact
  pressure on hardware.
- Snap strain is the closed-form cantilever estimate `eps = 1.5*t*delta/L^2`, not FEA.
- ~~Manufacturer permission to charge this cell at 100 mA remains open.~~ **CLOSED 2026-09-18.**
  EEMB's own LP502030 specification states a 250 mA maximum charge current; the planned 100 mA is
  0.4 C. **The battery is final and is not to be re-sourced** — see `../parts/V2_BOM.md`.
