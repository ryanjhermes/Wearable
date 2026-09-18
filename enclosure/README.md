# V2 enclosure

The first-prototype CAD enclosure was generated on 2026-09-17 around the completed populated-PCB
STEP and the selected protected EEMB `LP502030-PCM` battery envelope. See
[`../parts/V2_BOM.md`](../parts/V2_BOM.md) for battery/release evidence and
[`../pcb/README.md`](../pcb/README.md) for authoritative board status.

## Generate

`generate_enclosure.py` requires CadQuery 2.8 or newer and writes STEP, STL, SVG/PNG previews and
the machine-readable review report under `generated/mechanical_review/`.

## Two-piece snap-fit revision — 2026-09-18

The printable enclosure is now exactly two separate rigid bodies:

- `generated/mechanical_review/enclosure_top.step` and `.stl` — lid, battery cradle, USB opening,
  SHT40 vent and four integral snap tabs.
- `generated/mechanical_review/enclosure_bottom.step` and `.stl` — skin-side tray, four matching
  recessed catches, MAX30101 opening and TMP117 relief.

Each file contains **one printable solid**. Four 4.0 x 0.45 x 2.3 mm cantilever tabs are recessed
inside the long-side walls, outside the PCB envelope. Their 0.20 mm hooks engage concealed catches
in the bottom tray. The slots give 0.125 mm clearance on each tab face, intended as a first PETG or
nylon FDM trial. Print one test pair before committing to the final material: printer shrinkage may
require increasing the clearance or reducing the hook projection. PLA is more likely to fatigue or
break when the lid is removed repeatedly.

The closed exterior remains **28 x 50 x 12.4 mm**. CAD confirms zero top/bottom hard overlap, zero
snap-tab/PCB intersection and all previously accepted battery, antenna, USB and sensor clearances.

## Accepted CAD fit review — 2026-09-17

- Outer enclosure: **28 x 50 x 12.4 mm**; internal PCB cavity clears the square 24 x 46 mm board
  outline by 0.5 mm per side.
- Selected battery envelope: **20.5 x 32 x 5.3 mm**. It remains **2.1 mm** from the ESP32 antenna
  keepout, has 2.25 mm side clearance per side and 0.35 mm roof clearance.
- The PCM/two-wire end faces BT1 at the USB end. A dedicated wire keepout reaches the solder pads
  and stays 33.6 mm from the antenna keepout.
- USB-C opening: 10.0 x 4.6 mm around the 8.94 x 3.2 mm receptacle envelope, leaving 0.53 mm per
  side and 0.70 mm vertically.
- MAX30101: 5.4 x 7.7 mm hard-shell opening plus a separate opaque compliant gasket. The gasket
  clears the 3.3 x 5.6 mm package by 0.25 mm per side for light isolation without hard contact.
- TMP117: 4.2 x 4.2 mm hard-shell relief and a separate 3 x 3 x 1 mm soft, electrically insulating
  thermal-pad volume. Nominal CAD interference is zero so the rigid shell does not stress the IC.
- SHT40: a 3 x 2 mm exterior vent is offset 1.4 mm toward the enclosure end. The vent has a direct
  air path and is not covered by the battery or exposed to the skin side.
- Solid intersections are **0.0 mm^3** for hard shell vs populated PCB, shell vs battery, cradle vs
  populated PCB, battery vs populated PCB, the reserved wire path vs populated PCB, assembled top
  vs bottom and snap tabs vs populated PCB.

The authoritative measurements and pass/fail fields are in
`generated/mechanical_review/mechanical_review.json`. KiCad could not load local 3D models for J1,
U7 or U10, so the assembly uses conservative body-envelope surrogates documented in that report.

## Remaining physical/release checks

- Print and test-fit the enclosure with the real PCB and selected battery before ordering a final
  enclosure revision. CAD clearance is not a physical tolerance validation.
- Select the actual compliant optical gasket and TMP117 thermal-pad materials and verify contact
  pressure on hardware.
- ~~Manufacturer permission to charge this cell at 100 mA remains open.~~ **CLOSED 2026-09-18.**
  EEMB's own LP502030 specification states a 250 mA maximum charge current; the planned 100 mA is
  0.4 C. **The battery is final and is not to be re-sourced** — see `../parts/V2_BOM.md`.
