# USB-C receptacle, 16-pin (USB 2.0)

| Field | Value |
|---|---|
| Candidate | TYPE-C-31-M-12 |
| LCSC | **C165948** (Korean Hroparts Elec) |
| Type | **Standard horizontal SMD — NOT mid-mount** |
| Height | ~3.2 mm above board |
| Datasheet | **NEEDED** — the mechanical/footprint drawing is the part that matters |

## Mid-mount is not needed

The top side already stacks MINI-1 (2.4 mm) + LiPo (4.0 mm) = 6.4 mm. A 3.2 mm horizontal
receptacle fits inside that envelope, so it costs floorplan area at one edge, not total height.
Mid-mount needs a routed board cutout and was never sourced — dropped.

## Mandatory

**2 × 5.1 kΩ, one from CC1→GND and one from CC2→GND.** These tell the USB-C *source* that this is a
sink. Without them a USB-C charger delivers nothing. Most common USB-C design mistake.

Only VBUS, GND, CC1, CC2, D+ and D− are used. D+/D− go to the ESP32-C3's native USB (IO19/IO18)
via the ESD array — no USB-UART bridge needed.

## What to check in the datasheet

Footprint land pattern, mounting-peg holes, and whether the shield tabs need a GND connection.
