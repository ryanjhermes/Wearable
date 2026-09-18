# pcb — Wearable V2 schematic

KiCad project for the custom ESP32-C3 fab PCB. Open `wearable_v2.kicad_pro` in KiCad 10.

**This is the single living status document for the PCB. There are no dated handoff files.**
Read `## Current state`, `## Verified log` and `## Next actions` below; read the rest only if the
task needs it. `parts/V2_BOM.md` owns part rationale and approval status;
`bom_from_schematic.csv` owns reference designators and quantities.

## Current state — 2026-09-17

**Schematic captured, ERC-clean and frozen for layout. Layout is partially routed: 9 unconnected
items remain, no copper pours yet. Not independently bench-validated, not ready to order.**

| Artifact | SHA-256 (first 12) |
|---|---|
| `wearable_v2.kicad_sch` | `40f095722e05` |
| `wearable_v2.kicad_pcb` | `0264043f9463` |

```bash
shasum -a 256 pcb/wearable_v2.kicad_sch pcb/wearable_v2.kicad_pcb
```

**Hash gating (see `AGENTS.md` section 2): if these hashes still match, every check in the verified
log below stands. Do not rerun it.** A changed hash invalidates that artifact's logged checks.

## Verified log — append-only

Append one row per accepted check. Never edit or delete a row; a superseded result is simply an
older hash.

| Date | Artifact | Check | Result |
|---|---|---|---|
| 2026-09-16 | sch `40f0957` | `kicad-cli sch erc` | 0 errors, 2 understood U9 strap warnings |
| 2026-09-16 | sch `40f0957` | Hand netlist review, net by net | 3 silent opens found and fixed; no others |
| 2026-09-16 | sch `40f0957` | BOM reconcile vs `parts/V2_BOM.md` | 25 lines / 51 populated, every qty matches |
| 2026-09-16 | sch `40f0957` | IC pinouts vs local datasheets | 12/12 pin maps, **0 errors** |
| 2026-09-16 | sch `40f0957` | Footprint courtyards | all 16 enclose their own pads |
| 2026-09-16 | sch `40f0957` | JLCPCB assembly library, 25 lines | all present, `source: shop`, non-zero stock. **Stock drifts — recheck only at cart time** |
| 2026-09-17 | sch `40f0957` | Independent electrical review against the exported netlist | **no new topology defect**; load share, USB-C, CC, ESD, straps, NCs all correct |
| 2026-09-17 | pcb `0264043` | `pcb drc --schematic-parity` | **0 parity issues, 0 footprint errors** |
| 2026-09-17 | pcb `0264043` | `pcb drc` clearance / edge | 0 errors |
| 2026-09-17 | pcb `0264043` | Unconnected items | **9 remaining** (listed under `## Routing`) |
| 2026-09-17 | pcb `0264043` | Courtyard overlap, all 64 footprints | 0 overlaps, all inside the outline |
| 2026-09-17 | pcb `0264043` | Cell body vs `ANTENNA_KEEPOUT_U1` | **passes with 2.1 mm clearance** |
| 2026-09-17 | pcb `0264043` | Silkscreen warnings | 2 remain, both J1 footprint outline at the intentional connector-mouth overhang |
| 2026-09-17 | pcb `0264043` | Net-island analysis of the 9 open items (union-find over segments/vias/pads) | Confirms exactly 9. **VSYS is split into two islands**: `D1.1`+`Q1.2` vs everything downstream (`U4.1`, `U4.3`, `C3.1`, `C7.1`, `L1.1`, `TP5.1`). `/SW_PPG` has **zero** copper. All four U10 pads have zero copper |

Known-acceptable warnings that must be **preserved**, not "fixed": the 2 J1 silk-to-edge warnings,
and 3 footprint-library mismatches (U1 project override; U6/U8 deliberate pad-7 overrides).

## Next actions — in order

1. **Finish the 9 remaining connections** listed under `## Routing`, as three jobs in this order:
   **(a) the VSYS trunk** — item 6 is not a local link, it is the whole system rail: `D1.1`/`Q1.2`
   currently feed nothing, so U4 and U6 have no source. Route the widest, least-constrained copper
   first, before signals box it in. **(b) the U6/L1 boost block** — items 7, 8, 9.
   **(c) U10 (SHT40)** — items 1, 2, 4, 5 are all four of U10's pads; U10 is entirely unrouted.
   Item 3 (`C10.2` GND) is a single local stitch and can go last.
2. Remove or properly connect the dangling `/PPG_PWR_EN` via at `(72.965, 115.1131)`.
3. Run project-aware DRC after every small group. Require 0 unconnected, 0 clearance errors,
   0 parity issues, preserving the known-acceptable warnings above.
4. Review the autoroute visually — shorten and clean USB D+/D-, U6/L1 SW/FB, MAX30101 VLED/PGND,
   decoupling paths, and any circuitous power route. **Autorouter completion is not layout quality.**
5. Silkscreen pass (cosmetic, owed before fab outputs).
6. Pour planes only after track cleanup. Preserve the antenna keepout and the SHT40 no-via/no-pour
   area. In1.Cu should be a continuous GND plane; **decide and document In2.Cu deliberately** rather
   than pouring GND on all four layers by reflex.
7. Rerun ERC, full DRC, parity, `kicad-happy` PCB analysis, and a 3D/mechanical review.
8. Only then: gerbers, drills, BOM, top+bottom CPL, and cart verification. Those are release-gated
   separately in `parts/V2_BOM.md`.

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
| `bom_from_schematic.csv` | BOM generated from the schematic — 25 lines, 51 populated parts, with `Qty`/`MPN`/`LCSC` |
| `.kicad-happy.json` | Config for the `kicad-happy` analysis skills: supplier, design intent, rail voltages, suppressions |
| `datasheets/` | MPN-named symlinks into `parts/*/datasheet.pdf`, so the analyzers can verify pinouts |

### The bootstrap generators have been removed

`build.py` and its helpers (`schgen.py`, `libtool.py`, `sexp.py`, `mksym.py`, `gen_lib.py`) wrote
the first `.kicad_sch` and were deleted once it had been hand-edited. Re-running any of them
regenerates the schematic from scratch and discards every placement, wire and fix — and one of
their defects (never emitting `(junction ...)` items) had already cost a silent open on the 3.3 V
rail. They remain in git history at commit `2c00110` if the provenance of the first draft is ever
needed. **The `.kicad_sch` is the only source of truth.**

### Part properties

Every BOM symbol carries both an `MPN` and an `LCSC` property. `MPN` was added 2026-09-16 — the
sourcing gate and the JLCPCB BOM/CPL export both key on it, and without it the analyzers refuse
to call any electrical finding "verified".

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
- **A third silent open was found and fixed on 2026-09-16: U4 pin 1 (VIN) was on no net**, so the
  board had no 3.3 V rail at all. The wire T'd into the middle of the VSYS wire, and KiCad does
  not connect a mid-wire T without an explicit `(junction ...)` item — of which the generated
  schematic had **zero**. Two junctions were added. Every wire endpoint and symbol pin in the
  schematic was then swept for the same failure mode; **U4 VIN was the only instance.** Verified
  against `kicad-cli`'s own exported netlist, not a third-party parser: `VSYS` now carries
  `U4.1` and `U4.3`, and `unconnected-(U4-V_{IN}-Pad1)` is gone.

## Verification NOT done — do not treat this as reviewed

1. **No independent electrical review.** One pass by one author is not the peer check the BOM
   requires before fabrication.
2. **No power-budget or thermal check.** Audit findings 2 and 3 (ME6211 dropout margin, TPS61099
   rail margin) are untouched by capture and remain open.
3. **Routing is incomplete and unreviewed.** 585 tracks and 41 vias exist from an accepted
   autoroute; 9 connections remain and no zone is poured. See `## Routing`.

## Footprint audit — done 2026-09-16 (release gate #5)

Method: resolve all 16 distinct footprints to their `.kicad_mod`, extract real pad geometry, and
compare **pad-number → function** against the manufacturer datasheet pin table, and pad geometry
against the vendor land pattern where the datasheet contains one.

### Pin maps — 12 of 12 verified, zero errors

Every IC, connector and discrete was checked pad-by-pad against its datasheet pin table (not the
package name). **No pinout error was found.**

| Ref | Part | Datasheet pin table | Verdict |
|---|---|---|---|
| U2 | USBLC6-2SC6 | 1 I/O1, 2 GND, 3 I/O2, 4 I/O2, 5 VBUS, 6 I/O1 | ✅ hand-authored symbol matches; DM through 1→6, DP through 3→4 |
| U3 | TP4054 | 1 CHRG, 2 GND, 3 BAT, 4 VCC, 5 PROG | ✅ |
| U4 | ME6211C33M5G-N | 1 VIN, 2 VSS, 3 CE, 4 NC, 5 VOUT | ✅ CE tied to VSYS |
| U5 | XC6206P182MR | 1 VSS, 2 VOUT, 3 VIN | ✅ |
| U6 | TPS61099DRVR | 1 GND, 2 VOUT, 3 FB, 4 EN, 5 SW, 6 VIN, 7 PowerPAD→GND | ✅ incl. PowerPAD on GND as required |
| U7 | MAX30101EFD+T | 1 NC, 2 SCL, 3 SDA, 4 PGND, 5–8 NC, 9/10 VLED+, 11 VDD, 12 GND, 13 INT, 14 NC | ✅ |
| U8 | TMP117AIDRVR | 1 SCL, 2 GND, 3 ALERT, 4 ADD0, 5 V+, 6 SDA | ✅ ADD0→GND = 0x48 |
| U9 | LSM6DS3TR-C | 1 SDO/SA0, 2 SDx, 3 SCx, 4 INT1, 5 VDDIO, 6/7 GND, 8 VDD, 9 INT2, 10/11 NC, 12 CS, 13 SCL, 14 SDA | ✅ SA0→GND = **0x6A**; CS→3V3 = I2C mode |
| U10 | SHT40-AD1B-R3 | 1 SDA, 2 SCL, 3 VDD, 4 VSS | ✅ |
| Q1 | AO3401A | 1 G, 2 S, 3 D | ✅ G→VBUS, S→VSYS, D→BAT+ |
| D1 | SS14 | — | ✅ symbol pin 1 = K, `D_SMA` pad 1 is the cathode end (F.Fab bar + silk band both on the pad-1 side); K→VSYS, A→VBUS |
| L1 | MAKK2016T2R2M | non-polar | ✅ |

Two datasheet details worth re-reading before layout: LSM6DS3TR-C pins 10/11 are
*"leave electrically unconnected **and soldered to PCB**"* (the footprint has pads, so this is
satisfied), and both its VDD and VDDIO want their own 100 nF — which the BOM already fits.

### Geometry — courtyards

All 16 footprints have a courtyard that fully encloses their own pads. (This was the bug found in
the MAKK2016 import; nothing else has it.)

### Land patterns

| Footprint | Vendor land pattern | Verdict |
|---|---|---|
| `Sensirion_DFN-4_…_SHT4x_NoCentralPad` | Datasheet Figure 10 | ✅ pad size 0.5 × 0.3 mm and 0.8 mm Y pitch match exactly; X placement agrees to ~0.05 mm. **`NoCentralPad` is the correct variant** |
| `WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` (U6, U8) | TI DRV0006B example | ⚠️ 0.65 mm pitch and the 1.0 × 1.6 mm EP match. Pads differ: TI 0.45 × 0.30 at ±0.75 mm, KiCad 0.375 × 0.40 at ±0.887 mm. KiCad's is IPC-7351-derived with a toe fillet; TI's is heel-weighted. Both fully cover the terminal — acceptable, but it is **not** TI's pattern |
| `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` | **Not in the datasheet** (ST points to st.com/mems) | ⚠️ consistent with the package outline: 3.00 × 2.50 mm body, 0.5 mm pitch, 4/3/4/3 pad arrangement, pads 0.625 × 0.350 vs 0.475 × 0.25 terminals (normal fillet). Pin 1 top-left in top view, matching ST's pin-1 indicator. **Not vendor-land-pattern-verified** |
| `Maxim_OLGA-14_3.3x5.6mm_P0.8mm` | **Not in the datasheet.** It cites "Land Pattern Number 90-0602" at maximintegrated.com | ❌ **still unverified, and this is the $8.34 part.** Pad pitch 0.8 mm and the 7-down-left / 7-up-right arrangement match the pin diagram, but no dimensioned land pattern was available to check pad size or position against |
| `pcb:L_MAKK2016T_2.0x1.6mm` | **No datasheet on file at all** | ❌ still unverified |
| SOT-23 / -23-5 / -23-6, 0402, 0603, D_SMA, TestPoint | KiCad standard IPC-7351 | ✅ correct pad counts and standard numbering; treated as trusted stock geometry, not individually vendor-checked |

### The one decision this audit surfaced — U8 TMP117 thermal pad

`WSON-6-1EP…` gives pad 7 copper **and solder paste**. **[CORRECTED 2026-09-17 — it does not;
the stock footprint has no paste aperture on pad 7. See "U8 TMP117 thermal pad" in the Layout
section, which also records the U6 PowerPAD defect this uncovered.]** The TMP117 symbol has only 6 pins, so
pad 7 carries **no net** — it will be reflowed and left floating.

TI explicitly permits that (*"If the thermal pad is soldered, it must be left floating or
grounded"*), so this is **not an error**. But it is an undocumented choice with a real cost:

- Layout Guidelines: *"To achieve a high precision temperature reading for a rigid PCB, **do not
  solder down the thermal pad**."*
- *"The package thermal pad is not connected to the device ground and should be left unsoldered
  for best measurement accuracy."*
- The headline ±0.1 °C accuracy row in the E-characteristics table is specified **"Thermal Pad
  unsoldered (DRV Package)"**.
- Against that: soldering it *lowers* thermal resistance to the board and *shortens* response
  time; the cost is mechanical stress on the package, which is a measurement-error source unless
  the system is calibrated.

So it is accuracy vs. response time, and it needs a call before layout. If the answer is "do not
solder", the fix is a project copy of the footprint for U8 with pad 7's `F.Paste` removed.
**Note this contradicts the claim in `../parts/V2_BOM.md` that "thermal-pad placement *is* the
measurement" — TI's guidance is the opposite.**

Also note U6 and U8 currently **share one footprint while having opposite exposed-pad
requirements** (the TPS61099 PowerPAD *must* be soldered to GND; the TMP117 pad should not be tied
to device ground). Today that resolves correctly by accident, because only U6's symbol has a pin 7.

### Layout rules this audit extracted

- **SHT40 (U10): "There shall be no copper under the sensor other than at the pin pads."**
  The GND pour needs a keepout under U10 on every layer it would otherwise flood.
- **MAX30101 (U7): the VLED+ bypass capacitor returns to PGND, not GND** (datasheet pin
  description). PGND and GND are one net here, so this is a layout instruction: join them at a
  single point near the part rather than letting LED pulse current share the analog return.


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

---

# Layout

**State 2026-09-17: Board Setup complete, outline drawn, all 64 footprints placed, and a partial
two-layer route accepted (585 tracks, 41 vias, 9 connections still open, no zones).** All 64 footprints
(51 BOM + 12 test points + 1 battery pad) sit at intentional positions; 6 of them are on B.Cu.
Verified with `kicad-cli`: **0 DRC errors, 0 schematic-parity issues**, 174 unconnected pads
(nothing routed yet, expected) and 134 silkscreen warnings (reference text over pads — a
cosmetic pass owed before fab). ERC is unchanged at 0 errors / 2 understood warnings; the
schematic was not touched.

## Schematic/PCB parity — verified, do not rerun F8 casually

U4 pin 1 (VIN) is now `VSYS` in both schematic and PCB. KiCad's own parity DRC reports
**0 schematic parity issues and 0 footprint errors** after the PCB pad assignment was corrected on
2026-09-16. This is stronger evidence than the old string-count gate.

Do **not** rerun **Tools > Update PCB from Schematic (F8)** unless the frozen schematic genuinely
changes: KiCad 10.0.5 repeatedly reintroduced the stale U4 pad net in this project. If F8 is ever
required, immediately rerun the parity command below and require 0 parity issues before layout
continues.

## Design-review tooling (the `kicad-happy` skill)

`.claude/skills/` symlinks the `kicad-happy` plugin cloned at the repo root (gitignored, nested
git repo). Use it rather than writing ad-hoc parsers — it is what caught the U4 defect
independently.

```bash
# from the repo root; ~2 s, no network, no KiCad needed
python3 kicad-happy/skills/kicad/scripts/analyze_schematic.py pcb/wearable_v2.kicad_sch --analysis-dir pcb/analysis/
python3 kicad-happy/skills/kicad/scripts/analyze_pcb.py       pcb/wearable_v2.kicad_pcb --analysis-dir pcb/analysis/
```

KiCad's own CLI is installed and is the authority when the two disagree:

```bash
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K sch erc --severity-error --severity-warning -o /tmp/erc.rpt pcb/wearable_v2.kicad_sch
$K pcb drc --severity-error --severity-warning -o /tmp/drc.rpt pcb/wearable_v2.kicad_pcb
$K pcb drc --schematic-parity --severity-error --severity-warning -o /tmp/parity.rpt pcb/wearable_v2.kicad_pcb
```

`.kicad-happy.json` configures it: LCSC primary, 0402 passives, `MPN`-then-`LCSC` field priority,
rail voltage overrides, and **written-down suppressions for three known false positives**
(VM-001 on SDA/SCL — the MAX30101's I2C pins are +6.0 V tolerant; PU-001 on U7/U8/U9 — those
interrupt pins are deliberately polled or unused). Read the `reason` field before re-raising any
of them. The schematic analyzer prints suppressed findings anyway by design; suppression takes
effect in the EMC/cross-analysis/report stages.

`datasheets/` holds MPN-named symlinks into `../parts/*/datasheet.pdf` so the analyzers can do
pin-level verification. 13 of 25 lines are covered — the gaps are the Samsung caps and UNI-ROYAL
resistors, which have no datasheet on file, plus the MAKK2016 inductor.

### Exact net names (verified from the generated netlist)

Power-symbol nets are bare; label nets carry a leading `/`.

| Net | Meaning |
|---|---|
| `VBUS` | USB 5 V input |
| `BAT+` | LiPo cell positive |
| `VSYS` | system rail after load-share MOSFET |
| `3V3` | main logic rail (NOT `+3V3`) |
| `1V8` | MAX30101 VDD (NOT `+1V8`) |
| `4V7` | 4.704 V green-LED boost output (NOT `+4V7`) |
| `GND` | |
| `/SW_PPG` | boost switch node, TPS61099 <-> L1 |
| `/FB_PPG` | boost feedback tap — keep THIN and away from `/SW_PPG` |
| `/SDA` `/SCL` | shared I2C bus |
| `/EN` `/PROG` `/BAT_SENSE` `/PPG_PWR_EN` | |
| `/IO2_STRAP` `/IO8_STRAP` `/IO9_BOOT` | boot straps, 10k pull-ups |
| `/IO18_USB_DM` `/IO19_USB_DP` `/USB_DM` `/USB_DP` `/USB_DM_CON` `/USB_DP_CON` | native USB |
| `/CC1` `/CC2` | USB-C, 5.1k each |

### Board Setup — COMPLETE 2026-09-17

4 copper layers (F.Cu / In1.Cu / In2.Cu / B.Cu), board thickness **1.0 mm** (user decision
2026-09-17 — the enclosure height stack assumed it; **confirm 1.0 mm 4-layer availability in the
JLCPCB cart before ordering**). Impedance control OFF, so the dielectric values are documentation
only — JLCPCB uses its own stackup; do not spend time on them. The 1.0 mm total is made up by
shrinking the core from 1.24 mm to 0.64 mm; copper and mask thicknesses are unchanged.

Every value below was applied and read back from the project files:

| Constraint | Value | Note |
|---|---|---|
| Min clearance | 0.15 mm | was 0.0, which disabled the check |
| Min track width | 0.15 mm | |
| Min connection width | 0.15 mm | was 0.0 |
| Min text height | 1.0 mm | was 0.1 mm |
| Min via diameter / through-hole | 0.5 / 0.3 mm | unchanged |
| Copper to edge / hole to hole / annular | 0.3 / 0.5 / 0.13 mm | unchanged |
| Netclass `Default` | track 0.2, **via 0.6 / 0.3** | |
| Netclass `Power` | track 0.4, **via 0.8 / 0.4** | |
| In1.Cu / In2.Cu layer type | **power** | was `signal` |

`Power` netclass patterns verified against the real netlist — all eight match an existing net:
`GND`, `VBUS`, `VSYS`, `BAT+`, `3V3`, `1V8`, `4V7`, `/SW_PPG`. `/FB_PPG` is deliberately left in
`Default` (thin, high-impedance feedback tap).

**Never place a uVia.** JLCPCB does not do blind/buried vias on a standard order and DRC will not
warn you. Switch the PCB editor to **mm** (Ctrl+U) — every part is metric.

### U8 TMP117 thermal pad — DECIDED: unsoldered (user, 2026-09-17)

TI's layout guideline for best accuracy. Implemented as a **board-level pad override on U8 only**,
not a new footprint, so the schematic's footprint assignment is untouched and parity stays at zero:
U8 pad 7 now carries **B.Cu only** (no mask opening, no paste), so nothing can wet it.

**Defect found while doing this, and fixed.** The audit section above states this footprint "gives
pad 7 copper **and solder paste**". That is wrong: the stock KiCad 10 footprint
`Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm` defines pad 7 as `(layers "F.Cu" "F.Mask")` —
**no paste aperture at all**. U8 was therefore already going to arrive unsoldered; the real victim
was **U6 TPS61099, whose PowerPAD *must* be soldered to GND** and would have been left dry by the
stencil. U6 pad 7 now has `F.Cu F.Mask F.Paste` with a **-10 % paste margin ratio** (reduced
aperture, standard practice for an exposed pad). Both edits show up as `lib_footprint_mismatch`
warnings against the stock library — that is the intended record of a deliberate local override.
A third such warning, on U1, is pre-existing and unrelated.

### Stackup and side convention (do not change mid-layout)

| Layer | Side | Contents |
|---|---|---|
| F.Cu | top, away from wrist | ESP32-C3-MINI-1 (U1), USB-C (J1), charger, regulators, boost, battery pads (BT1), SHT40 (U10) |
| — | board thickness | **1.0 mm** (decided 2026-09-17) |
| In1.Cu | — | solid GND plane |
| In2.Cu | — | power |
| B.Cu | **skin side** | MAX30101 (U7), TMP117 (U8) |

Flip a part to the other side with **F**. Move with **M**, rotate with **R**.

### Build order

#### Steps 0-2 — DONE 2026-09-17

Board Setup, outline and floorplan are complete; both user decisions that gated them are answered
(1.0 mm board, U8 thermal pad unsoldered). What was actually built is recorded below, and it
supersedes the plan that used to sit here.

#### Outline — 24 x 46 mm, not 24 x 42 mm

Edge.Cuts rectangle **(60, 100) to (84, 146)**, i.e. **24 mm wide x 46 mm long**, drawn 2026-09-17.

The planned 24 x 42 mm **cannot physically work**, and this is the substantive finding of the
floorplan. Three things must occupy three non-overlapping bands along the long axis, because none
of them may sit under the cell:

| Band | Depth | Why it cannot overlap the cell |
|---|---|---|
| U1 antenna strip | 5.4 mm | a LiPo pouch over a PCB trace antenna detunes it |
| Cell footprint | 30.0 mm | the cell itself |
| J1 USB-C body | 7.3 mm | **3.2 mm tall vs the module's 2.4 mm** — the cell would rest on the connector |

5.4 + 30 + 7.3 + edge margins = **~46 mm**. The user chose the long/narrow option (24 mm across the
wrist, a normal strap width) over a 32 x 36 mm watch-like board on 2026-09-17. Growing the board is
free until order; shrinking later is a drag, so this is deliberately not tight.

#### THE CHECK THAT HAD NEVER BEEN DONE — now done, and it PASSES

**Does the 30 x 20 mm cell clear the antenna keepout?** Yes, by **2.1 mm**.

- U1 is at (72.0, 111.5), rotation 0, antenna end pointing at the board's y=100 edge.
- Its antenna strip therefore spans **y 100.5 to 105.9**, full module width.
- The cell body rectangle on `User.Drawings` spans **(62, 108) to (82, 138)**.
- 108.0 - 105.9 = **2.1 mm of clearance**, and the cell is 2 mm inside each long edge.

The cell does sit over the rest of U1 (the module body runs to y 117.6) — that is the intended
stack: the pouch rests on the 2.4 mm module. Only the antenna end is kept clear.

#### Keepouts — real Rule Areas, not artwork

Two `Place > Rule Area` zones now exist. The dashed rectangle inside the U1 footprint is only a
marking and enforces nothing; these do.

| Rule area | Extent | Layers | Disallows |
|---|---|---|---|
| `ANTENNA_KEEPOUT_U1` | (59.5, 99.5) - (84.5, 105.9), i.e. past both board edges | F.Cu, In1.Cu, In2.Cu, B.Cu | tracks, vias, pads, zone fills |
| `SHT40_U10_NO_COPPER` | (69.3, 140.2) - (71.7, 142.2) | F.Cu, In1.Cu, In2.Cu, B.Cu | vias, zone fills |

`ANTENNA_KEEPOUT_U1` deliberately does **not** disallow footprints: U1's own body reaches into it,
and switching that flag on makes U1 itself a DRC error. The SHT40 area implements the datasheet's
"no copper under the sensor other than at the pin pads" — it blocks the pour and vias but allows
tracks, because a track that cannot reach U10's pads cannot connect it. **Route U10's four nets in
from outside the area and stop at the pads.**

#### Floorplan as placed — 64 footprints, 0 courtyard overlaps

Verified numerically: no two courtyards on the same side intersect, and everything is inside the
outline. J1's courtyard overhangs the bottom edge by 0.5 mm, which is the connector mouth and is
intended.

| Zone | Contents |
|---|---|
| y 100.5-117.6, centre | **U1** ESP32-C3-MINI-1, antenna at the y=100 edge |
| x ~63.8 column, left of U1 | 3V3 decoupling C12/C4, EN pull-up R12 + C10, strap R13, battery divider R7/R8 + C2 |
| x ~81 column, right of U1 | USB series R3/R4 at module pins 26/27, TP9/TP10 |
| y 118-120, under U1 | R11 (PPG_PWR_EN pulldown), I2C pull-ups R16/R17, strap R14/R15, TP8/TP11/TP12 |
| left, y 121-137 | U9 IMU + C18/C19, then U3 charger, R5 PROG, Q1, D1, R6 |
| right column x 78 | U6 boost, L1, U4 3V3 LDO, U5 1V8 LDO, stacked top to bottom |
| right column x 82 | that chain's bulk/decoupling caps C8, C9, C16, C7, C11, C5, C3, C6 + TP4 |
| bottom, y 133-137 | U2 ESD array, C1 VBUS bulk, CC resistors R1/R2 |
| bottom edge | **BT1** battery pads (left, rotated 180 so the strain-relief holes face the cell), **U10 SHT40 + C20** (centre, at the USB opening), **J1 USB-C** (right, mouth flush with the y=146 edge) |
| **B.Cu, skin side** | **U7 MAX30101** at (70, 128) — board centre — with C15 (4.7 uF VLED+), C13/C14 (1V8); **U8 TMP117** at (64.5, 133.5) with C17 |

Two placement decisions worth keeping:

- **U10 SHT40 sits between BT1 and J1 at the bottom edge, not beside the regulators.** It must read
  *ambient* air, and everywhere else on the top side is under the cell pouch, which has no airflow.
  The enclosure's USB-C opening doubles as its vent.
- **D1 (SS14, SMA) is ~2.4 mm tall — the same as the module** — so the cell rests level on both. No
  other part under the cell exceeds 1.2 mm.

#### Silkscreen — cleaned 2026-09-17

All 64 footprint reference fields were hidden. That was the entire cleanup: versus the pre-cleanup
board, only 64 `(hide yes)` lines were added. It removed all 73 silk-over-copper and 61
silk-over-silk warnings. The 2 that remain are J1's outline at the intentional connector-mouth
overhang — **do not move J1 to eliminate them.**

## Routing

**Accepted 2026-09-17: a partial two-layer route — 585 track segments, 41 through vias, on
F.Cu/B.Cu. 9 connections remain open. No copper pours exist.** The two zones the board API reports
are the antenna and SHT40 rule areas, not copper zones.

### How the route was produced

Freerouting 2.4.1 was used **only as a route generator**, from a KiCad 10 DSN export, imported back
through `File > Import > Specctra Session`. No router output was accepted without KiCad DRC. The
DSN clearance was corrected from the exporter's 0.15 mm to the active netclass clearance of
**0.20 mm** before routing. Inner layers stayed DSN type `power`.

Attempts already tried and rejected — **do not repeat these**:

| Attempt | Outcome |
|---|---|
| Freerouting 2.2.4 @ 0.15 mm | 10 opens, many KiCad clearance failures |
| Freerouting 2.2.4 @ 0.20 mm | 24 KiCad opens |
| Freerouting 2.4.1 continuing from the partial route | regressed to 16 opens |
| Scripted closure of five items | tracks did not persist in the saved board — **assume they do not exist** |

The accepted run is Freerouting 2.4.1 from the **unrouted** board at 0.20 mm.

### The 9 remaining connections

From the accepted KiCad DRC report at pcb `0264043`:

| # | Net | From | To | Note |
|---|---|---|---|---|
| 1 | `3V3` | U10.3 `(71.2, 141.6)` | 3V3 branch near `(70.02, 143.2)` | |
| 2 | `/SDA` | B.Cu branch near `(63.6125, 132.85)` | U10.1 `(69.8, 140.8)` on F.Cu | |
| 3 | `GND` | C10.2 `(64.28, 113.2)` | GND branch near `(64.31, 115.8)` | route around the intervening R7 `/BAT_SENSE` pad |
| 4 | `GND` | branch near `(73.16, 142.1983)` | U10.4 `(71.2, 140.8)` | |
| 5 | `/SCL` | U8.1 / B.Cu `(65.3875, 132.85)` | U10.2 / F.Cu `(69.8, 141.6)` | |
| 6 | `VSYS` | `D1.1` `(63.0, 136.0)` / `Q1.2` `(64.062, 133.35)` island | downstream island (`TP5.1` `(72.8, 127.0)`, `U4.1` `(76.862, 127.65)`, `L1.1`, `C3.1`, `C7.1`) | **system power trunk, ~11 mm, Power class 0.4 mm — route this first, not last** |
| 7 | `VSYS` | U6.6 `(78.8875, 121.15)` | routed VSYS network / L1.1 side | |
| 8 | `/SW_PPG` | U6.5 `(78.8875, 121.8)` | L1.2 `(79.0, 124.6)` | **critical — keep very short and compact, away from `/FB_PPG`** |
| 9 | `/PPG_PWR_EN` | U6.4 `(78.8875, 122.45)` | its routed branch | the dangling via at `(72.965, 115.1131)` belongs to this net |

**SHT40 constraint:** the `SHT40_U10_NO_COPPER` rule area forbids vias and pours but deliberately
permits tracks to reach U10's four pads. Put SDA/SCL transition vias **outside** x 69.3..71.7,
y 140.2..142.2.

### Then: pour, verify, export

Pour only after track cleanup. Place > Filled Zone, net GND; In1.Cu as a continuous GND plane, with
In2.Cu decided deliberately. Then Inspect > Design Rules Checker (zero errors), the CLI DRC with
`--schematic-parity`, View > 3D Viewer, and finally File > Fabrication Outputs > Gerbers + Drill,
the position/CPL file for **both sides**, and the BOM.

## Electrical review — accepted 2026-09-17

A read-only review against the exported KiCad netlist and the local datasheets found **no new
circuit-topology defect** and made no repository edits. Verified: load sharing wired as intended
(VBUS to D1.A/Q1.G/U3.VCC; BAT+ to U3.BAT/Q1.D/battery; VSYS joining D1.K/Q1.S/U4 VIN+CE/U6 VIN);
USB-C duplicated pins, CC resistors, USBLC6 paths, 22R series resistors and shield/GND; U4/U5/U6
support parts, boot straps, EN RC, GPIO10 boost-enable pulldown, I2C straps and addresses, explicit
NCs, U6 PowerPAD grounding/paste, and U8's unsoldered thermal pad.

**No schematic change is justified by that review.** What remains are validation gates, not
topology questions, and none of them should cause schematic churn without new evidence:

- ME6211 dropout, transient and thermal margin under ESP32 boot / BLE / flash loads.
- TPS61099 4V7 margin and ripple during MAX30101 green-LED pulses.
- Exact protected-battery identity, polarity, dimensions, and permission to charge at 100 mA.
- Load-share source transitions and charge termination with the system active.
- Start I2C bring-up at 100 kHz until actual rise time is measured.
- Firmware must hold `PPG_PWR_EN` low through boot and raise it only after 1V8 is valid.

## Verification commands

Run KiCad CLI **outside the sandbox** if it aborts with exit 134 — inside, it cannot reach all
runtime/cache resources.

```bash
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
$K sch erc --severity-error --severity-warning -o /tmp/erc.rpt    pcb/wearable_v2.kicad_sch
$K pcb drc --severity-error --severity-warning -o /tmp/drc.rpt    pcb/wearable_v2.kicad_pcb
$K pcb drc --schematic-parity --severity-error --severity-warning -o /tmp/parity.rpt pcb/wearable_v2.kicad_pcb
python3 kicad-happy/skills/kicad/scripts/analyze_pcb.py pcb/wearable_v2.kicad_pcb --analysis-dir pcb/analysis/
```

Close KiCad before patching the board file. Remove a stale `.lck` only when the GUI is confirmed
closed.
