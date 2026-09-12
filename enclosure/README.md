# Hardware — Enclosure

First-pass **3D-printed enclosure** for the XIAO ESP32S3 wearable. A simple two-part box
that holds the board, MAX30102, and LiPo cell, with corner lugs for a strap.

| File | What it is |
|---|---|
| `enclosure_top.3mf` | Lid (snaps/seats onto the bottom shell; `>><<` motif on top) |
| `enclosure_bottom.3mf` | Bottom shell — holds the electronics; internal posts seat the board |
| `images/enclosure_assembled.png` | Rendered assembled view (lid on) |
| `images/enclosure_interior.png` | Rendered bottom-shell interior (mounting posts, cutouts) |

## Design

- **Form factor:** simple rectangular box, rounded edges — not yet a watch/wristband profile.
- **Two parts:** top lid + bottom shell, printed separately (`.3mf`).
- **Strap:** four corner lugs with through-holes for a band/strap.
- **USB-C access:** oblong slot in one end wall keeps the port reachable for charging and
  reflashing without opening the box (per the design constraint in `CLAUDE.md`).
- **Interior:** upright posts / tabs to locate the module; a raised rectangular pad and side
  slots for board/battery seating.

## Status

Design exists as `.3mf`; **not yet confirmed printed/fitted** against the assembled electronics.
Open questions: skin-side sensor window for the MAX30102, final internal fit of board + 402030
cell, and lid retention method. Material target is TPU (flexible) per the roadmap.

Slicing/printing is done off-repo (Bambu A1 Mini). These `.3mf` files are the source of
truth for the geometry.
