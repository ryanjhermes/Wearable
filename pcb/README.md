# pcb — Wearable V2 schematic

KiCad project for the custom ESP32-C3 fab PCB. Open `wearable_v2.kicad_pro` in KiCad 10.

**Status: schematic captured and all footprints assigned, 2026-09-16. ERC-clean (0 errors,
2 understood warnings). NOT frozen, NOT reviewed, NOT laid out, NOT ready to order.** `parts/V2_BOM.md` remains authoritative for
part rationale and approval status; this schematic's generated BOM is now authoritative for
reference designators and quantities.

This is not the abandoned `pcb/` folder deleted on 2026-09-14. That one is unrelated and was
never a basis for anything. This project starts from scratch.

## What is here

| File | Role |
|---|---|
| `wearable_v2.kicad_sch` | **The schematic. Authoritative from the moment you open it.** |
| `wearable_v2.kicad_pro` | Project file |
| `symbols/wearable_v2.kicad_sym` | Project symbols: the five parts with no stock-library equivalent |
| `pcb.pretty/` | Project footprints — **all three now present and verified** |
| `pcb.3dshapes/` | STEP models for the module and inductor (needed later for enclosure fit) |
| `bom_from_schematic.csv` | BOM generated from the schematic (51 populated parts) |
| `build.py`, `schgen.py`, `libtool.py`, `sexp.py`, `mksym.py`, `gen_lib.py` | Bootstrap generator |

### The generator is a bootstrap, not a source of truth

`build.py` wrote the first `.kicad_sch`. **Do not re-run it over an edited schematic** — it
overwrites the file and would discard your placement, wiring and any parts you added. It is kept
only so the provenance of the first draft is auditable. After the first edit in KiCad, the
`.kicad_sch` is the only source of truth and all changes are made in KiCad or by patching that
file directly.

## Sheet layout

One A2 root sheet, seven dashed blocks. Inter-block nets use labels and power symbols rather than
long drawn wires, so blocks can be moved without re-routing.

| Block | Contents |
|---|---|
| A | USB-C receptacle, CC pulldowns, USBLC6 ESD array |
| B | TP4054 charger, AO3401A + SS14 load sharing, battery pads, battery-sense divider |
| C | ME6211 3.3 V and XC6206 1.8 V linear regulators |
| D | TPS61099 4.7 V boost for the green LED rail |
| E | ESP32-C3-MINI-1, EN reset RC, strapping pull-ups, USB series resistors, I2C pull-ups |
| F | MAX30101, TMP117, LSM6DS3TR-C, SHT40 on one I2C bus |
| G | Twelve bring-up test pads |

## Verification done

- **ERC: 0 errors, 2 warnings** (both understood, listed below). Was 5 warnings before
  the footprints landed on 2026-09-16.
- **Netlist reviewed by hand, net by net.** Two real defects were found and fixed during capture:
  - The LSM6DS3TR-C ground ties were routed across the SDA/SCL stubs, **shorting the whole I2C
    bus to ground**. Ties now route away from the bus pins.
  - `BAT+` existed as two separate nets (a power symbol and a local label), so **the cell was not
    connected to the charger**, and the AO3401A gate sat on its own net instead of VBUS, which
    would have left the load-share MOSFET permanently on. Both are now single nets.
- **BOM reconciles exactly against `parts/V2_BOM.md`: 51 populated components**, and every
  per-value quantity matches (100 nF x8, 1 uF x6, 4.7 uF x2, 10 uF x4, 22R x2, 4.7k x2, 5.1k x2,
  10k x5, 100k x2, 1M x3, 270k x1, 14 non-passives).
- **Pinouts checked against the local datasheets in `parts/`** for every IC.

## Verification NOT done — do not treat this as reviewed

1. **Footprint audit is only 2 of 51 done.** The ESP32-C3-MINI-1 was checked pad by pad against
   Espressif Figure 11-1, and `BatteryPads_2x` is hand-authored so its geometry is known. **The
   other 48 stock-library footprints were matched by package name only**, and the MAKK2016
   inductor has no manufacturer drawing at all. BOM gate 5 requires checking every one before
   layout. Package-name matching is not that check: `SOT-23-5` and `SOT-23-6` parts in particular
   share silhouettes while differing in pad count and pin order.
2. **No independent electrical review.** One pass by one author is not the peer check the BOM
   requires before layout.
3. **No power-budget or thermal check.** Audit findings 2 and 3 (ME6211 dropout margin, TPS61099
   rail margin) are untouched by capture and remain open.
4. **No layout, no floorplan, no antenna keepout check.**

## Open items before this can be frozen

### ~~Three footprints must be created or imported~~ — DONE 2026-09-16

All three now exist in `pcb.pretty/` and the schematic resolves every footprint. ERC footprint
warnings went from 3 to 0.

| Footprint | Source | Verified against |
|---|---|---|
| `ESP32-C3-MINI-1` | LCSC C2838502 via `easyeda2kicad` | **Espressif datasheet v2.2 Figure 11-1** (official land pattern) |
| `L_MAKK2016T_2.0x1.6mm` | LCSC C92923 via `easyeda2kicad` | **Nothing — no manufacturer drawing on file.** See `parts/makk2016/README.md` |
| `BatteryPads_2x` | Hand-authored | N/A — a custom pad pair, not a catalogue part |

Importing from LCSC rather than hand-drawing was deliberate: it also carries the JLCPCB assembly
rotation, which a hand-drawn footprint does not.

#### ESP32-C3-MINI-1 — checked pad by pad

Every dimension in the import matches Espressif Figure 11-1: 48 perimeter pads of 0.4 mm on 0.8 mm
pitch, spanning 11.9 x 9.9 mm; four 0.7 mm corner pads; a 3 x 3 grid of 1.45 mm thermal pads with
the top-left one chamfered as the pin-1 marker; body outline 13.2 x 16.6 mm. Pin 1 sits at
(-5.9, -4.0), upper-left, matching Figure 3-1.

**Added during import:** the module's 16.6 mm length includes a **5.4 mm antenna area at the
negative-Y end that carries no pads**, and the raw import did not mark it. It is now drawn as a
dashed `User.Drawings` rectangle spanning Y -11.0 to -5.6 labelled "ANTENNA KEEPOUT". This is the
constraint that decides the floorplan: no copper underneath, and **no battery above it**.

#### MAKK2016 inductor — one real defect found and fixed

The EasyEDA courtyard was 2.00 x 1.60 mm, the *body* size, while the pads reach ±1.60 x ±0.90 mm.
A courtyard smaller than the pads lets KiCad place another component directly on top of them with
no DRC error. Rebuilt at ±1.85 x ±1.15 mm, confirmed to enclose the pads.

This is the footprint to distrust. It is the only one with no manufacturer drawing behind it,
because the part had no evidence folder at all until 2026-09-16.

#### BatteryPads_2x — hand-authored

Two 2.0 x 1.4 mm solder pads on a 4.0 mm pitch for the cell's flying leads, plus two 1.1 mm
non-plated holes to thread the wires through before soldering, which is the strain relief the BOM
asks for. Marked `exclude_from_bom` and `exclude_from_pos_files` so JLCPCB neither charges for it
nor tries to place anything there. Pad 1 = BAT+, pad 2 = BAT-.

### Everything in `parts/V2_BOM.md` under "Before schematic freeze or ordering"

Still open, unchanged by this capture: exact battery evidence, symbol/footprint audit, power-budget
review, independent electrical review, and confirming stock and assembly class in a JLCPCB cart.

## The two remaining ERC warnings

| Warning | Why it is expected |
|---|---|
| 2x LSM6DS3TR-C pins 1 and 2 bidirectional tied to a power-output net | SDO/SA0 and SDx are deliberately strapped to ground per the datasheet (0x6A, I2C mode). The symbol declares them bidirectional; the design is correct |

## Net naming

Power symbols: `GND`, `3V3`, `1V8`, `4V7`, `VSYS`, `VBUS`, `BAT+`. Everything else is a local
label. Fixed GPIO assignments carry their function in the name (`IO9_BOOT`, `IO18_USB_DM`,
`IO2_STRAP`) so a mis-wire is visible in the netlist rather than hidden behind a bare `IO` number.
