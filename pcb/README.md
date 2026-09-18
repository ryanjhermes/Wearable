# pcb — Wearable V2 schematic

KiCad project for the custom ESP32-C3 fab PCB. Open `wearable_v2.kicad_pro` in KiCad 10.

**This is the single living status document for the PCB. There are no dated handoff files.**
Read `## Current state`, `## Verified log` and `## Next actions` below; read the rest only if the
task needs it. `parts/V2_BOM.md` owns part rationale and approval status;
`bom_from_schematic.csv` owns reference designators and quantities.

**Update discipline:** documentation follows saved artifact changes; it does not predict them.
After changing and saving an artifact, run the required verification and immediately update this
file with the observed result and truthful next action. Never defer that update to the end of a
session.

## SETTLED — do not re-verify, do not re-open

Everything in this section is closed. A fresh agent must **not** re-run these checks, re-search these
parts, or re-litigate these decisions. Re-open an item only if the user asks, or if a design object it
depends on actually changes — and say which object changed before you do.

**Design checks — all pass, all current as of 2026-09-18.** The last design change was R10
270k -> 249k on 2026-09-18; ERC, DRC, schematic parity and `analyze_pcb.py` were all re-run after it
and returned results identical to the accepted 2026-09-17 baseline.

| Check | Accepted result | Do not re-run unless |
|---|---|---|
| `sch erc` | 2 violations = the 2 known `pin_to_pin` warnings | the schematic changes |
| `pcb drc` | 5 violations = the known-acceptable set, 0 unconnected | the board changes |
| `pcb drc --schematic-parity` | 0 parity issues, 0 unconnected | either design file changes |
| `analyze_pcb.py` | 51 findings: 2 error / 18 warning / 31 info, all reviewed and accepted | the board changes |
| Visual route + 3D review | Accepted for the first prototype | the board changes |
| CAD mechanical review | PASS for fabrication-file preparation | the board outline or battery envelope changes |
| Fabrication artifact validation | 15/15 PASS | the BOM, board or exports change |

**KiCad F8 (Update PCB from Schematic): do not run it.** The netlist has not changed since parity
last returned 0. KiCad 10.0.5 reintroduces a stale U4 pad net in this project when F8 runs. The
2026-09-18 R10 change was applied by patching the value/MPN/LCSC property fields in both files
directly, precisely to avoid this.

**Battery — CLOSED, final, by user decision 2026-09-18.** The EEMB `LP502030-PCM` already in the
user's possession is the cell for v2. EEMB's own LP502030 specification states a 250 mA maximum
charge current, so the planned 100 mA (0.4 C) is inside rating. **Do not search for alternative
cells, do not price-compare, do not re-open the envelope or wire-count questions.** Alternatives
investigated on 2026-09-17/18 are recorded in the log below for history only.

**JLCPCB — the decisions below are made. Do not re-derive, re-search or re-price them.**

| Settled | Value |
|---|---|
| Service | Standard PCBA |
| Layers / thickness | 4 layers, 1.0 mm |
| Panelization | Panel by JLCPCB, 5 mm process rails |
| Fiducials | Factory-added on the panel. **Do not add local board fiducials** unless JLCPCB actually rejects this workflow |
| Assembly sides | Top and bottom (45 top / 6 bottom) |
| Excluded from placement | BT1 and TP1-TP12 |
| R10 assembly class | `C11425` is Extended. So was the outgoing `C25770`. **No Basic 0402 1% part exists at either value** — checked 2026-09-18, does not need rechecking |
| Substitutions | Not acceptable for regulators, MOSFETs or connectors |
| Gerber/drill ZIP | Current and correct. R10's value lives only on F.Fab, which is not in the gerber set, so the 2026-09-18 change did not alter it |

**What genuinely still requires the live JLCPCB cart — once, not repeatedly.** These are not
desk-checkable and no amount of re-reading this repo will close them. They are the *only* JLCPCB work
left: confirm 4-layer/1.0 mm availability; run the cart's DFM; confirm the factory rails, fiducials
and tooling holes serve both assembly sides; read current stock, lifecycle, assembly class and price;
and eyeball the BOM/CPL overlay, especially J1, U1, U6, U7, U8, U10 and R10. Record the result once,
in the log below, and then treat it as settled too.

**Nothing here is fabrication approval.** Layout complete, checks clean, and artifacts validated are
all separate from reviewed, and all separate from ordered. No order is authorized.

## Current state — 2026-09-18

**The design is complete, internally consistent and fully verified on desk. It has never been built,
measured or ordered.**

*Schematic.* Captured, ERC-clean (2 understood warnings), frozen. One user-approved change since the
2026-09-16 freeze: R10 270k -> 249k on 2026-09-18, a value/MPN/LCSC change only — the netlist is
untouched.

*Layout.* 662 segments, 53 vias, 4 layers. Both inner GND zones filled and saved; In1.Cu carries no
traces and In2.Cu only the approved four 3V3 and two VSYS segments. Project-aware DRC without
refilling gives the 5 known-acceptable warnings, 0 unconnected items and 0 footprint errors; parity
gives 0 issues. `analyze_pcb.py` gives 51 reviewed and accepted findings. Route reviewed visually and
in 3D and accepted for the first prototype.

*Enclosure.* First-prototype geometry exists around the populated PCB STEP and the EEMB LP502030-PCM
32 x 20.5 x 5.3 mm envelope. CAD review passes with zero modeled hard collisions, 2.1 mm
battery-to-antenna clearance, a cleared USB opening, separate MAX30101 optical-gasket and TMP117
soft-thermal-pad volumes, and an unobstructed SHT40 vent. It exports as separate one-solid top and
bottom print files with four concealed long-wall snap latches; closed exterior 28 x 50 x 12.4 mm.

*Power.* Desk power/thermal analysis and an ngspice simulation of the 4V7 boost are complete and give
a conditional pass. The worst-case 4V7 low corner is 4.770 V against the MAX30101's 4.5 V green
minimum, and a green LED pulse moves the rail only 4 mV, so boost dynamics are not a risk. **Two
firmware constraints carry into bring-up: cap BLE TX at 0 dBm, and hold `PPG_PWR_EN` low until 1V8 is
up.** The 3.45 V deep-sleep threshold is provisional pending a measured cell-sag figure.

*Battery.* **Closed and final.** EEMB LP502030-PCM already in hand; its 250 mA maximum charge rating
covers the planned 100 mA. Not to be re-sourced.

*Fabrication package.* `pcb/fabrication/jlcpcb_standard_pcba/` — gerbers, separate PTH/NPTH drills,
the authoritative 25-line/51-part BOM, 45-part top CPL, 6-part bottom CPL, PCB STEP and assembly
review artifacts. Regenerated after the R10 change; `artifact_validation.json` is 15/15 PASS.

*What is left.* Three things, all of which need hardware or the live cart, none of which can be
closed by further desk work: **the JLCPCB cart pass, printing and fit-testing the enclosure, and
bench-validating the rails on the first article.** See the SETTLED section above for what must not be
re-checked, and `## Verification NOT done` for the full list of what genuinely remains.

**Not bench-validated. Not peer-reviewed by a second person. Not approved for fabrication. No order
is authorized.**

## Verified log — append-only

Rows are chronological and **never edited or deleted**, so superseded rows remain visible. Two rows
below are superseded and must not be acted on: the `enclosure` row marked **BLOCKED** (superseded the
same day by the passing CAD mechanical review) and the `battery` row reporting a three-conductor
30 x 20 x 4 mm cell (superseded by the confirmed EEMB `LP502030-PCM` evidence, then closed entirely on
2026-09-18). Where a row conflicts with the SETTLED section or Current state above, those win.

Append one row per accepted check. Never edit or delete a row except to remove obsolete workflow
metadata such as revision fingerprints. A superseded result remains as historical evidence.

| Date | Artifact | Check | Result |
|---|---|---|---|
| 2026-09-16 | schematic | `kicad-cli sch erc` | 0 errors, 2 understood U9 strap warnings |
| 2026-09-16 | schematic | Hand netlist review, net by net | 3 silent opens found and fixed; no others |
| 2026-09-16 | schematic | BOM reconcile vs `parts/V2_BOM.md` | 25 lines / 51 populated, every qty matches |
| 2026-09-16 | schematic | IC pinouts vs local datasheets | 12/12 pin maps, **0 errors** |
| 2026-09-16 | schematic | Footprint courtyards | all 16 enclose their own pads |
| 2026-09-16 | schematic | JLCPCB assembly library, 25 lines | all present, `source: shop`, non-zero stock. **Stock drifts — recheck only at cart time** |
| 2026-09-17 | schematic | Independent electrical review against the exported netlist | **no new topology defect**; load share, USB-C, CC, ESD, straps, NCs all correct |
| 2026-09-17 | PCB | `pcb drc --schematic-parity` | **0 parity issues, 0 footprint errors** |
| 2026-09-17 | PCB | `pcb drc` clearance / edge | 0 errors |
| 2026-09-17 | PCB | Unconnected items | **9 remaining** (listed under `## Routing`) |
| 2026-09-17 | PCB | Courtyard overlap, all 64 footprints | 0 overlaps, all inside the outline |
| 2026-09-17 | PCB | Cell body vs `ANTENNA_KEEPOUT_U1` | **passes with 2.1 mm clearance** |
| 2026-09-17 | PCB | Silkscreen warnings | 2 remain, both J1 footprint outline at the intentional connector-mouth overhang |
| 2026-09-17 | PCB | Net-island analysis of the 9 open items (union-find over segments/vias/pads) | Confirms exactly 9. **VSYS is split into two islands**: `D1.1`+`Q1.2` vs everything downstream (`U4.1`, `U4.3`, `C3.1`, `C7.1`, `L1.1`, `TP5.1`). `/SW_PPG` has **zero** copper. All four U10 pads have zero copper |
| 2026-09-17 | PCB | `/SW_PPG` routed by direct file edit, U6.5 -> L1.2, F.Cu 0.4 mm | `pcb drc`: **8 unconnected (was 9), 6 violations identical to the known-acceptable set** |
| 2026-09-17 | PCB | Rule-area audit | **Three rule areas exist, not two.** An unnamed F.Cu `tracks not_allowed` area covers U10 (see `## Rule areas`) |
| 2026-09-17 | PCB | Item 7 `VSYS` -> U6.6 routed: F.Cu stub, via `(79.1375, 120.9)`, B.Cu to the VSYS diagonal | `pcb drc`: no new violation |
| 2026-09-17 | PCB | Item 4 `GND` U10.4 -> trunk at `(72.25, 142.1983)`, 0.25 mm through the notch then 0.4 mm | `pcb drc`: no new violation |
| 2026-09-17 | PCB | Full `pcb drc` after the above | **6 unconnected (from 9), 6 violations identical to the known-acceptable set** |
| 2026-09-17 | PCB | Item 3 `C10.2` GND attempted and **reverted** | Shorts `/BAT_SENSE`; C10 is walled in on F.Cu by R7 + the `/BAT_SENSE` diagonal and on B.Cu by the 3V3 run at y 114.4336. **Defer to the In1.Cu GND plane** |
| 2026-09-17 | PCB | Grid maze-route feasibility sweep of the 5 open items, F.Cu/B.Cu only (0.05 mm grid, exact clearance raster, all three rule areas enforced) | Items 9, 1, 2 routable. **Item 6 VSYS has no direct corridor** — best F/B path is 46.7 mm around the west board edge. **Item 5 `/SCL` has no path at all** |
| 2026-09-17 | PCB | Same sweep with `In2.Cu` allowed as a routing layer | Item 6 drops 46.7 mm -> **15.96 mm, 2 vias**; item 2 drops 20.8 mm -> 12.5 mm. **Item 5 is unaffected** — its blocker is via placement, not layer count |
| 2026-09-17 | PCB | Cause analysis of the item 5 `/SCL` blockage | U10.2 is boxed by the `BT1.1` pad + the F.Cu 3V3 feed at x 68.9307 (west), U10.1's pad (north), C20 + GND (south), the F.Cu notch keepout (east). `SHT40_U10_NO_COPPER` forbids a via anywhere it could reach. **Only opens if the 3V3 -> C20.1 feed is ripped up and rerouted** |
| 2026-09-17 | PCB | Item 1 `3V3` -> U10.3, and the logged "unresolved" C20 question | **Resolved: no B.Cu detour and no moving C20 needed.** 1.59 mm, 0 vias, all F.Cu: east through U10.3's notch, south around the keepout, west to C20.1 |
| 2026-09-17 | PCB | **Item 6 `VSYS` trunk routed on In2.Cu** — F.Cu out of `D1.1`, via `(64.4, 137.3)`, In2.Cu diagonal to `(71.4, 130.3)` then east to `(76.9, 130.3)`, via up to `U4.3`. 15.96 mm, 0.4 mm | `pcb drc`: 5 unconnected (from 6), no new violation |
| 2026-09-17 | PCB | **Item 9 `/PPG_PWR_EN` routed**, U6.4 -> via `(78.7, 123.05)` -> B.Cu -> the dangling via at `(72.965, 115.1131)`. 16.8 mm, 0.2 mm | `pcb drc`: 4 unconnected. **Also cleared the `via_dangling` warning** — that via is now a real connection, closing next-action 2 |
| 2026-09-17 | PCB | 3V3 feed to C20.1 **ripped up** (2 F.Cu segments at x 68.9307) per the 2026-09-17 user decision, and re-fed C20.1 from the existing via `(68.9307, 138.638)` down In2.Cu at x 69.4. 5.20 mm, 1 via (was 15.58 mm / 3 vias on F/B) | Opens the 0.62 mm western channel that item 5 needs |
| 2026-09-17 | PCB | **Items 5 `/SCL`, 2 `/SDA`, 1 `3V3` routed to U10** — all three escape laterally through their own 0.3 mm notch at exactly the pad centreline, then leave the corner. `/SCL` 22.9 mm / 3 vias, `/SDA` 24.5 mm / 3 vias, `3V3` 2.1 mm / 0 vias | `pcb drc`: **1 unconnected** — item 3 only |
| 2026-09-17 | PCB | Escape-geometry cleanup: 3 `connection_width` necks (0.040 / 0.115 / 0.128 mm) and 1 `hole_clearance` violation against BT1's NPTH at `(67.4, 139.6)` | All 4 fixed. Root cause: a track that only *touches* a pad or via edge is tangent, not connected |
| 2026-09-17 | PCB | `pcb drc` full, in-project | **5 violations = exactly the known-acceptable set, 1 unconnected (item 3, deferred to the pour), 0 footprint errors** |
| 2026-09-17 | PCB | `pcb drc --schematic-parity` | **0 parity issues, 0 footprint errors** |
| 2026-09-17 | PCB | In2.Cu trace inventory | Exactly 2 nets: `VSYS` trunk (2 segments, 0.4 mm) and the `3V3` C20 feed (4 segments, 0.3 mm, ~3.9 mm long). **In1.Cu is still completely empty** |
| 2026-09-17 | PCB | Project-aware `pcb drc` after interactive U10 move + plane-pour attempt | **REGRESSION: 24 violations and 75 unconnected items.** Includes 2 zones forbidden by `SHT40_U10_NO_COPPER`, 11 clearance, 4 hole-clearance and 1 connection-width issue; 6 are the previously known silk/library warnings. The GND zones do not yet provide a valid connectivity result |
| 2026-09-17 | PCB | `pcb drc --schematic-parity` | **0 schematic parity issues**; the temporary stale U4 VIN net seen in KiCad history is not present in this saved state |
| 2026-09-17 | PCB | Exact recovery after the interactive regression | **RESTORED byte-for-byte from the agent scratch artifact** with PCB Editor closed: 661 segments, 52 vias, 3 rule areas and no copper-pour zones. Existing applicable checks stood and were not redundantly rerun |
| 2026-09-17 | project settings | Restore text/graphic defaults after accidental 0.1 mm horizontal-size edits | `wearable_v2.kicad_pro` matches the committed defaults again: Fab/Other 1.0 x 1.0 mm, 0.15 mm stroke; Silk 1.0 x 1.0 mm, 0.10 mm stroke |
| 2026-09-17 | PCB | Project-aware `pcb drc` after KiCad re-save of the recovered route | **5 violations = exactly the known-acceptable set, 1 unconnected (`C10.2` GND, deferred to the pour), 0 footprint errors** |
| 2026-09-17 | PCB | `pcb drc --schematic-parity` | **0 schematic parity issues, 0 footprint errors** |
| 2026-09-17 | PCB | C10 ground-plane feasibility correction + In1/In2 GND-zone definitions | Added a 0.2 mm `C10.2` stub to a GND through-via at `(64.78, 113.20)`. This corrects the earlier assumption that an inner plane could directly contact a top-side SMD pad; it cannot do so without a via |
| 2026-09-17 | PCB | Project-aware `pcb drc --refill-zones` and parity check (in-memory refill; fills not saved) | **5 violations = exactly the known-acceptable set, 0 unconnected items, 0 footprint errors, 0 schematic parity issues** |
| 2026-09-17 | PCB | Visual route review from F.Cu/B.Cu/In2.Cu plots and top/bottom 3D renders | Accepted for the first prototype. Long SHT40 SDA/SCL and PPG enable runs are low-speed/static; boost SW is 3.41 mm and FB is 3.98 mm; MAX30101 bypass parts are adjacent on B.Cu. USB is the weakest-looking route, but end-to-end D+/D- lengths are approximately 67.1/69.6 mm and the MCU-side resistor stubs are 2.59/2.91 mm. Preserve as a known first-spin signal-integrity risk rather than churn DRC-clean copper cosmetically |
| 2026-09-17 | PCB | Saved zone-fill presence check after the user pressed `B` and saved | 2 filled polygons present: one for `GND_PLANE_In1`, one for `GND_PLANE_In2`; final no-refill DRC waits until PCB Editor is closed |
| 2026-09-17 | PCB | Final project-aware `pcb drc` against the saved fills, without refilling | **5 violations = exactly the known-acceptable set, 0 unconnected items, 0 footprint errors** |
| 2026-09-17 | PCB | Final `pcb drc --schematic-parity` against the saved fills | **0 schematic parity issues, 0 footprint errors** |
| 2026-09-17 | PCB | Saved inner-layer inventory | 2 filled polygons; In1.Cu has 0 trace segments; In2.Cu has exactly 6 segments: 4 on 3V3 and 2 on VSYS |
| 2026-09-17 | PCB | Final `kicad-happy` `analyze_pcb.py` review | Analyzer completed successfully: 662 segments, 53 vias, 4 copper layers, 0 unrouted nets. Reviewed all 51 raw findings (2 error / 18 warning / 31 info). U10-inside-keepout is the intentional sensor copper keepout; U1 pad-49 thermal-via repeats are one module-land heuristic repeated eight times; narrow low-current signals, 0402 thermal-asymmetry notices, 11/61 test-net coverage, 3 GND stitching vias, J1/U1 edge placement and C7-C11 edge-clearance warnings are accepted first-prototype risks. Existing U1/U6/U8 footprint overrides and J1 silk-edge warnings remain intentional. |
| 2026-09-17 | PCB assembly | JLCPCB fiducial workflow decision | Use **Standard PCBA with Panel by JLCPCB / 5 mm edge rails** and factory-added panel fiducials/tooling holes; do not consume this 24 x 46 mm board with local fiducials. Confirm the generated rails/fiducials on both assembly sides during cart DFM review. |
| 2026-09-17 | enclosure | Final mechanical-review gate | **BLOCKED, not accepted:** `enclosure/` has no enclosure model or opening geometry, and the exact protected battery dimensions/wire exit are unresolved. USB-C opening alignment, MAX30101/TMP117 skin-opening contact and SHT40 vent clearance cannot be confirmed. The nominal 30 x 20 mm cell-to-antenna clearance remains the previously accepted 2.1 mm PCB-layout result, not an enclosure/battery fit check. No fabrication outputs generated. |
| 2026-09-17 | battery | Selected-cell identity and reported envelope | User selected the already-owned protected 402030, 3.7 V, 250 mAh three-conductor cell and reported a 30 x 20 x 4 mm maximum envelope. No substitute sourcing or circuit redesign. Mechanical integration remains blocked pending bulge/envelope confirmation, wire-exit evidence, polarity, third-conductor identification and 100 mA charge permission. |
| 2026-09-17 | battery | Selected-cell product evidence | User supplied the exact listing and label photo for EEMB `LP502030-PCM` (ASIN `B08VRZTHDL`): protected 3.7 V, 250 mAh, 32 x 20.5 x 5.3 mm, 5 g. The pictured selected pack has two wires exiting beside the PCM, not three; its label explicitly marks red positive and black negative. This supersedes the earlier reported envelope and three-wire concern. The listing does not establish a charge-current rating, so 100 mA permission remains open. |
| 2026-09-17 | enclosure + populated PCB STEP | Parametric CAD mechanical review | **PASS for fabrication-file preparation; physical fit still open.** Generated 28 x 50 x 12.4 mm enclosure around the populated PCB STEP and selected battery envelope. CAD reports 0.0 mm^3 hard-shell/PCB, shell/battery, cradle/PCB, battery/PCB and wire-path/PCB intersections; battery-to-antenna 2.1 mm, battery-to-roof 0.35 mm, USB side/vertical opening clearance 0.53/0.70 mm. MAX30101 uses a cleared opaque-gasket volume, TMP117 a zero-interference soft thermal-pad volume, and SHT40 a direct exterior vent. Evidence: `enclosure/generated/mechanical_review/mechanical_review.json`, STEP/STL assembly parts and isometric previews. J1/U7/U10 use documented conservative envelope surrogates because their local KiCad 3D models were unavailable. |
| 2026-09-17 | fabrication package | Gerber/drill/BOM/CPL/STEP export and local artifact validation | **PASS locally; cart gates remain open.** `pcb/fabrication/jlcpcb_standard_pcba/` contains upload ZIPs, 4 copper layers, paste/mask/silkscreen, separate PTH/NPTH drill files, assembly PDFs/renders and PCB STEP. Outline centerline is exactly 24 x 46 mm. Gerber viewer top/bottom review shows aligned copper, mask, drill and outline. BOM is 25 lines/51 parts; CPL is the identical 51 references split 45 top/6 bottom. BT1 and TP1–TP12 are excluded. J1/U1/U6/U10 top 0 degrees and U7/U8 bottom 180 degrees match KiCad. Evidence: `artifact_validation.json`. Four-layer/1.0 mm live availability, factory 5 mm rails/fiducials/tooling for both sides, DFM, current sourcing and price must still be confirmed in the JLCPCB cart. |
| 2026-09-17 | power tree | Desk power/thermal margin analysis — gate 3 (analysis only, no bench) | **CONDITIONAL PASS with two firmware constraints and one open corner. No design file changed.** 3V3 budget from datasheet peaks: 17 mA sensing, 90 mA BLE RX, 174 mA BLE TX at 0 dBm, 344 mA BLE TX at 20 dBm (ESP32-C3-MINI-1 p22 + 4 mA for the XC6206 branch, SHT40, TMP117 and two 4.7 k I2C pull-ups). ME6211 dropout linear-extrapolated from its only two published typical points (120 mV/100 mA, 260 mV/200 mA, me6211/datasheet.pdf p8): ~224 mV at 174 mA and ~462 mV at 344 mA. At a 3.45 V cell with 0.085 Ohm Q1 max plus an **assumed** 0.25 Ohm cell+PCM ESR, 3V3 holds 3.17 V at 0 dBm TX but falls to 2.87 V at 20 dBm TX — below the module's 3.0 V VDD33 minimum (esp32-c3-mini-1/datasheet.pdf p21). USB-powered LDO dissipation is 226 mW at 0 dBm and 447 mW at 20 dBm against a 300 mW SOT-23 rating (me6211/datasheet.pdf p5). 4V7 rail: PWM divider worst-case corner is 4.538 V, and 50 nA max FB leakage across R9 = 1 MOhm can subtract a further 50 mV, giving **4.488 V — under the 4.5 V green VLED+ minimum** (tps61099/datasheet.pdf p5; max30101/datasheet.pdf p2). Light-load PFM sits at ~4.845 V, safely under the 5.6 V OVP minimum. 4V7 COUT is C8+C9+C15+C16 = 24.8 uF nominal, ~13.9 uF at a pessimistic 50% DC-bias derate, still inside TI's 10-100 uF recommendation. Hysteretic charge packet is 0.135 uC, so PFM ripple is ~8.5 mV and a 51 mA green pulse needs ~156 switch pulses (~152 us) within its 411 us window; capacitor-only sag is ~10 mV at 3 us and ~32 mV at 10 us of loop delay. L1 peak is ~247 mA against 1.5 A saturation and a 0.8 A minimum switch limit. TP4054 at 100 mA dissipates ~130 mW. Evidence: local datasheets as cited. **Not measured. TPS61099 publishes no switching-frequency, ripple, start-up or numeric transient spec, ME6211 publishes no theta-JA, no TJ(max) and no dropout maximum, MAKK2016 has no local datasheet, and the cell+PCM ESR is assumed, not sourced.** |
| 2026-09-17 | power tree | Boost topology confirmation from the saved PCB netlist | TPS61099 input is on `VSYS` (L1 pad 1, U6 pad 6), not `3V3`, so green-LED energy does not pass through the ME6211. MAX30101 VLED+ pads 9/10 are on `4V7`, VDD pad 11 on `1V8`. The 1V8 branch is XC6206 from `3V3` feeding MAX30101 VDD and the LSM6DS3TR-C, ~2 mA worst case. |
| 2026-09-18 | 4V7 rail | ngspice behavioral simulation of the TPS61099 boost — gate 3 dynamic half | **Dynamic behaviour PASSES with wide margin; the DC tolerance stack is the only failure mode, and it confirms the R10 finding.** Netlist `pcb/analysis/tps61099_4v7_boost.cir`, ngspice 47, no design file changed. Model is behavioral, not TI silicon: hysteretic peak-current control with the datasheet's 350 mA fixed inductor ripple, 300/350 mOhm Rds(on), 1.03 V PFM reference, MAKK2016 2.2 uH/0.16 Ohm, the real C7/C3/C8/C9/C15/C16 network DC-bias derated, 2 nH of bulk-to-sensor trace, and the MAX30101 51 mA / 411 us / 100 sps green pulse. Light-load PFM sits at 4.830-4.869 V, agreeing with the 4.845 V hand calculation. **The LED pulse pulls the rail down only 4 mV** (to 4.826 V) — the converter tracks it easily, so the idle-to-pulse transient is not a risk. Peak inductor current 363-366 mA against 1.5 A saturation and the 0.8 A minimum switch limit. VIN 3.5 / 3.7 / 4.2 V changes the rail by under 2 mV; no down-mode entry (threshold is VIN > 4.78 V). Raising assumed FB-node capacitance from 5 pF to 20 pF costs only 15 mV of ripple, which retires the concern that the 1 MOhm divider impedance would slow the loop dangerously. Worst-case corner with VREF at its 0.98 V PWM minimum, 1% resistor endpoints and 50 nA of FB leakage injected: **4.470 V with R10 = 270k (30 mV under the 4.5 V green minimum) and 4.770 V with R10 = 249k (270 mV above it)**, within 20 mV of the hand calculation. **Model-dependent caveats: the 5 mV burst-comparator hysteresis is assumed, not published; TI publishes no min/max for the PFM reference, no switching-frequency, ripple or start-up spec; start-up, temperature and MAX30101 pin-level waveforms were not simulated. This is a desk model, not a measurement.** |
| 2026-09-18 | battery | EEMB LP502030 charge-current evidence found — gate 1 substantially closed | EEMB's own LP502030 cell specification (ZJQM-RD-SPC-H2305, 2022-10-25, linked from eemb.com/product-130, accessed 2026-09-18) states **maximum charge current 250 mA, 1.0C5A (CC&CV)**. The planned TP4054 charge current of 100 mA is 0.4 C, inside that rating. **This supersedes the earlier conclusion that no charge rating existed for the selected cell.** Residual gap: that document is the bare-cell revision and gives dimensions as <=31 x 20.5 x 5.3 mm with no PCM section, so it does not itself document the -PCM pack's protection-circuit current limits or finished pack length. Backup candidate if a distributor-sourced cell with pack-level documentation is preferred: Cellevia ACCU-LP502030/CL, 250 mAh, 30 +/-0.4 x 20 +/-0.4 x 5.0 +/-0.2 mm pack, two 26AWG wires, standard charge 125 mA / rapid charge 250 mA, sold by TME; its price, stock and US availability are unverified. Jauch LP502030JH+PCM was rejected on envelope: DigiKey states 32.0 x 21.0 x 5.4 mm, over both the 20.5 mm width and 5.3 mm thickness limits. |
| 2026-09-18 | enclosure | Separate top/bottom snap-fit revision | **PASS in CAD; physical snap test open.** Rebuilt the enclosure as two separate one-solid printable parts while retaining the 28 x 50 x 12.4 mm closed exterior. The lid has four 4.0 x 0.45 x 2.3 mm wall-mounted cantilever tabs with 0.20 mm hooks; the tray has matching concealed catches with 0.125 mm clearance per tab face. Fixed the earlier disconnected battery rails by bridging them into the lid. Regenerated STEP/STL/assembly/review artifacts. CAD reports 0.0 mm^3 assembled top/bottom overlap and 0.0 mm^3 snap-tab/PCB intersection; all prior mechanical checks still pass. First print should use PETG or nylon and validate/tune latch clearance before release. |
| 2026-09-18 | battery | **Battery selection CLOSED by user decision — final, not to be reopened** | The EEMB `LP502030-PCM` already in the user's possession is the battery for v2. Charge-current permission is satisfied by EEMB's own LP502030 specification (250 mA maximum, 1.0C5A CC&CV), against which the TP4054's 100 mA is 0.4 C. Alternative cells investigated on 2026-09-17/18 are recorded above for history only; **do not source a substitute and do not reopen this question.** Residual documentation gap, explicitly accepted by the user: the EEMB document is the bare-cell revision and does not specify the -PCM pack's protection trip current or finished pack length. |
| 2026-09-18 | schematic + PCB | **R10 270k -> 249k — user-approved schematic change, implemented and verified** | R10 value, MPN (`0402WGF2703TCE` -> `0402WGF2493TCE`) and LCSC code (`C25770` -> `C11425`) changed in both `wearable_v2.kicad_sch` and the R10 footprint properties in `wearable_v2.kicad_pcb`. Diff against a pre-change backup is **exactly 3 lines in each file**; no copper, net, footprint or position changed. **KiCad F8 was deliberately NOT rerun** — the netlist is unchanged, so the documented KiCad 10.0.5 stale-U4-pad hazard was avoided by patching the two files' property fields directly. KiCad PCB Editor was confirmed closed and no `.lck` files were present. Verification after the change: **ERC 2 violations = the 2 known `pin_to_pin` warnings; `pcb drc` 5 violations = exactly the known-acceptable set (2 J1 silk-edge, 3 library overrides for U1/U6/U8) with 0 unconnected items; `pcb drc --schematic-parity` 0 parity issues, 0 unconnected; `analyze_pcb.py` 51 findings / 2 error / 18 warning / 31 info — byte-identical severity split to the accepted 2026-09-17 run.** Zero regressions. Nominal 4V7 rail moves from 4.704 V to 5.016 V; worst-case low corner from 4.470 V to 4.770 V. |
| 2026-09-18 | fabrication package | Regenerated after the R10 change and revalidated | `pcb/bom_from_schematic.csv` R10 row updated; top/bottom raw position files and both assembly PDFs re-exported from the changed board; `build_and_validate.py` rerun. `artifact_validation.json` = **PASS on all 15 checks** (24 x 46 mm outline, 4 copper layers, 1.0 mm, 25 BOM lines / 51 parts, 45 top / 6 bottom CPL, BT1 and TP1-TP12 excluded, critical orientations match). **The gerber/drill ZIP is unchanged and did not need regenerating** — R10's value lives only on F.Fab, which is not part of the exported gerber set. `wearable_v2_pcba_bom_cpl.zip` was found stale after the rebuild and was regenerated; the zipped BOM now reads `249k,R10,...,C11425`. No stale `270k`/`C25770`/`2703TCE` string remains anywhere under `pcb/fabrication/`. |
| 2026-09-18 | documentation sync | Stale `270k` / `C25770` references cleared across the repo, and re-verified | Updated: the schematic's on-sheet annotation text (now `VOUT = 1.0 V x (1M + 249k) / 249k = 5.016 V nominal.`), `parts/tps61099/README.md` required-externals table, the passive inventory line in this file, and the JLCPCB parts table in `parts/V2_BOM.md`. **JLCPCB assembly class confirmed unchanged: C11425 (249k) and C25770 (270k) are both Extended — no Basic 0402 1% part exists at either value**, so the R10 change adds no assembly-class burden. C11425 stock 44,965 at approximately $0.0005/ea (jlcsearch, accessed 2026-09-18); treat stock, lifecycle and price as cart-verified only. Re-verified after the annotation edit: **ERC 2 violations (the known pair), `pcb drc` 5 violations with 0 unconnected, parity 0 issues.** `docs/DESIGN_HISTORY.md` deliberately still records C25770 — it is the historical rationale document and is not authoritative. |
| 2026-09-18 | documentation | Full documentation-consistency pass and checkpoint | Added the `## SETTLED — do not re-verify, do not re-open` section at the top of this file, recording the closed design checks, the closed battery decision and the settled JLCPCB settings, so a fresh agent does not re-run or re-search them. Rewrote `## Current state` (it had become a lumpy accretion of edits), replaced `## Next actions` with three live hardware/cart items plus a compressed completed-work table, and rewrote `## Verification NOT done`, whose three entries were all stale — the electrical review, power-budget work and routing they listed as outstanding are done. Noted in the log preamble which two rows are superseded, since the log is append-only and both still read as live blockers. Synced `CLAUDE.md` (layout is complete; open questions rewritten; cell recorded as final), `parts/V2_BOM.md` (status section, gate 4, JLCPCB parts table), `parts/V2_HARDWARE_AUDIT.md` (finding 3 marked resolved), `enclosure/README.md` (charge-current item closed) and the fabrication package README. **No design file was touched in this pass, so ERC, DRC, parity and the analyzer were deliberately not re-run** — their 2026-09-18 results stand. |

Known-acceptable warnings that must be **preserved**, not "fixed": the 2 J1 silk-to-edge warnings,
and 3 footprint-library mismatches (U1 project override; U6/U8 deliberate pad-7 overrides).

## Next actions — in order

**Nothing on this list can be closed from the keyboard.** All three remaining items need the live
JLCPCB cart, a 3D printer or a built board. If you are a fresh agent and you find yourself re-running
DRC or re-searching parts, stop and read the SETTLED section at the top of this file.

1. **JLCPCB cart pass — the only remaining JLCPCB work.** Upload
   `pcb/fabrication/jlcpcb_standard_pcba/wearable_v2_gerbers_drills.zip`,
   `assembly/jlcpcb_bom.csv`, `assembly/jlcpcb_top_cpl.csv` and `assembly/jlcpcb_bottom_cpl.csv`.
   Settings are already decided (Standard PCBA, 4 layers, 1.0 mm, Panel by JLCPCB, 5 mm rails — see
   SETTLED). Confirm in the cart: 4-layer/1.0 mm availability, the DFM result, that factory rails,
   fiducials and tooling holes serve **both** assembly sides, current stock/lifecycle/assembly
   class/price, and the BOM-CPL overlay for J1, U1, U6, U7, U8, U10 and R10. Reject similar
   substitutions for regulators, MOSFETs and connectors. Record the outcome once in the verified log.
2. **Print and fit-test the enclosure** with the real PCB, the EEMB cell, the optical gasket and the
   TMP117 thermal pad. CAD clearance is not tolerance validation. Geometry and evidence are under
   `enclosure/generated/mechanical_review/`.
3. **Bench-validate the rails on the first article.** 3V3 under simultaneous BLE TX, flash write and
   PPG pulses at low battery and across cable insertion; 4V7 start-up, ripple and temperature
   behaviour measured at the MAX30101 VLED+ pins; ME6211 case temperature on USB; and LP502030-PCM
   terminal sag at 200 mA and 400 mA to replace the assumed 0.25 Ohm cell+PCM resistance and fix the
   provisional 3.45 V deep-sleep threshold.

**Carry into firmware bring-up** (the desk analysis depends on both): cap BLE TX power at 0 dBm, and
hold `PPG_PWR_EN` low until the 1V8 rail is established.

**Do not place an order or claim fabrication approval without explicit user authorization.**

### Completed — for the trail only, do not redo

| Done | What |
|---|---|
| 2026-09-17 | Recovered the exact PCB after the interactive regression; restored project text/graphic defaults |
| 2026-09-17 | Closed the 9 remaining connections, including the `C10.2` GND via to In1.Cu; removed the dangling `/PPG_PWR_EN` via |
| 2026-09-17 | Visual route review — accepted for the first prototype, with the long `/SDA`, `/SCL`, `/PPG_PWR_EN` runs and the USB D+/D- route preserved as known first-spin risks |
| 2026-09-17 | Silkscreen pass; references hidden, only the 2 intentional J1 connector-mouth edge warnings left |
| 2026-09-17 | Saved and verified both inner GND pours |
| 2026-09-17 | Final `kicad-happy` PCB analysis reviewed and accepted; JLCPCB panel/fiducial workflow decided |
| 2026-09-17 | Enclosure CAD mechanical review — PASS for fabrication-file preparation |
| 2026-09-17 | Generated and locally validated gerbers, drills, BOM, top+bottom CPL and PCB STEP |
| 2026-09-17/18 | Desk power/thermal margin analysis — conditional pass; produced the 0 dBm TX cap and the R10 finding |
| 2026-09-18 | ngspice simulation of the 4V7 boost — dynamics are not a risk; confirmed the DC corner |
| 2026-09-18 | **R10 270k -> 249k** implemented, verified (ERC/DRC/parity/analyzer all unchanged) and re-exported |
| 2026-09-18 | **Battery closed, final** — EEMB LP502030-PCM, 250 mA max charge rating covers the planned 100 mA |
| 2026-09-18 | Repo-wide documentation sync; stale `270k`/`C25770` references cleared |

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
rail. They remain in git history if the provenance of the first draft is ever needed. **The
`.kicad_sch` is the only source of truth.**

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
  10k x5, 100k x2, 1M x3, 249k x1, 14 non-passives).
- **Pinouts checked against the local datasheets in `parts/`** for every IC.
- **A third silent open was found and fixed on 2026-09-16: U4 pin 1 (VIN) was on no net**, so the
  board had no 3.3 V rail at all. The wire T'd into the middle of the VSYS wire, and KiCad does
  not connect a mid-wire T without an explicit `(junction ...)` item — of which the generated
  schematic had **zero**. Two junctions were added. Every wire endpoint and symbol pin in the
  schematic was then swept for the same failure mode; **U4 VIN was the only instance.** Verified
  against `kicad-cli`'s own exported netlist, not a third-party parser: `VSYS` now carries
  `U4.1` and `U4.3`, and `unconnected-(U4-V_{IN}-Pad1)` is gone.

## Verification NOT done — do not treat this as reviewed

**Rewritten 2026-09-18.** The three items that used to sit here are resolved; see the SETTLED section
at the top of this file. For the record: the electrical topology review was accepted 2026-09-17;
power-budget, ME6211 dropout/thermal and TPS61099 rail margin were analysed on desk 2026-09-17/18 and
the boost was simulated in ngspice; routing is complete, poured, DRC-clean and visually accepted.

What remains genuinely unverified is **everything that needs physical hardware or the live cart.** Do
not attempt to close these by reading or re-analysing this repo:

1. **No bench measurement of anything.** Every power-rail number in this repo is a desk calculation
   or a behavioral simulation. Still needed on the first article: 3V3 under simultaneous BLE TX,
   flash write and PPG pulses at low battery and across cable insertion; 4V7 start-up, ripple and
   behaviour over temperature measured at the MAX30101 VLED+ pins; ME6211 case temperature on USB;
   and LP502030-PCM terminal sag at 200 mA and 400 mA, which replaces the assumed 0.25 Ohm cell+PCM
   resistance and confirms or moves the provisional 3.45 V deep-sleep threshold.
2. **No physical fit test.** The enclosure passes in CAD only. Print it and fit it with the real PCB,
   cell, optical gasket and TMP117 thermal pad before treating any tolerance as production-ready.
3. **No live JLCPCB cart pass.** Listed in the SETTLED section; it is the only remaining JLCPCB work.
4. **No peer electrical review by a second person.** The topology review was one author's pass.
5. **Wrist-PPG wavelength has never been measured.** This is a post-arrival firmware experiment
   (`archive/v1/src/max30102_raw_ir/`), not an ordering gate.

**Two firmware constraints must be carried into bring-up** or the analysis above does not hold: cap
BLE TX power at 0 dBm, and hold `PPG_PWR_EN` low until the 1V8 rail is established.

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

**State 2026-09-17: Board Setup, outline, all 64 footprints, routing and zone definitions are
complete.** The board has 662 segments, 53 vias and two saved inner-layer GND fills; 6 footprints
are on B.Cu. The pre-save DRC with refill gave the 5 known-acceptable warnings, 0 unconnected items
and 0 parity issues. The remaining immediate action is to close PCB Editor and repeat the checks
without refill. ERC remains at 0 errors / 2 understood warnings; the schematic was not touched.

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
| In2.Cu | — | GND pour + 2 routed traces — see `## Inner layers` |
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

**Accepted 2026-09-17: the route is complete; item 3 closes through the In1.Cu plane after refill.** It began as a partial two-layer
Freerouting result (585 segments, 41 vias, F.Cu/B.Cu, 9 open). The 9 were then closed by hand and
by a purpose-built maze router; two of them needed In2.Cu. The board now also contains two GND-zone
definitions plus the three rule areas; both calculated inner-layer fills are saved.

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

**The 9 opens were closed without re-running Freerouting** — by direct edits to the board file,
with each candidate first checked against a 0.05 mm clearance raster and then against KiCad's own
DRC. If you close copper interactively instead, use KiCad PCB Editor,
**Route > Interactive Router Settings > Mode: Walk around**, with the toolbar track-width dropdown
on **"Use netclass width"**. Walk around cannot produce a clearance violation, so the router itself
is the first line of defence; `Allow DRC violations` is greyed out in that mode and is not a setting
to change. Press `/` while routing to flip corner posture if a corner comes out diagonal.

### The 9 connections — all closed after zone refill

Numbering is from the first accepted KiCad DRC report. **Current status:**

| # | Net | Closed by | Result |
|---|---|---|---|
| 1 | `3V3` | U10.3 east through its notch at y 141.6, south around the keepout, west to C20.1 | 2.13 mm, 0 vias, all F.Cu. **Resolved the old C20 question** — no B.Cu detour, C20 not moved |
| 2 | `/SDA` | U10.1 west through its notch at y 140.8, north, then B.Cu down the west side to U7.3 | 24.52 mm, 3 vias. Works, but **flagged for the cleanup pass** |
| 3 | `GND` | `C10.2` -> 0.2 mm F.Cu stub -> via `(64.78, 113.20)` -> In1.Cu GND plane | Closes after zone refill. Routing down to the old surface trunk shorts `/BAT_SENSE`; see the log |
| 4 | `GND` | U10.4 east through its notch, 0.25 mm then 0.4 mm to the trunk | done 2026-09-17 |
| 5 | `/SCL` | U10.2 west through its notch at y 141.6, north past BT1, then B.Cu down the west side | 22.85 mm, 3 vias. **Only possible after the 3V3 C20 feed was ripped up** |
| 6 | `VSYS` | `D1.1` -> via `(64.4, 137.3)` -> **In2.Cu** diagonal -> via `(76.9, 130.3)` -> `U4.3` | 15.96 mm, 2 vias, 0.4 mm. The F/B-only alternative was 46.7 mm around the west board edge |
| 7 | `VSYS` | U6.6 F.Cu stub, via `(79.1375, 120.9)`, B.Cu to the VSYS diagonal | done 2026-09-17 |
| 8 | `/SW_PPG` | U6.5 -> L1.2 direct, F.Cu 0.4 mm | done 2026-09-17 |
| 9 | `/PPG_PWR_EN` | U6.4 -> via `(78.7, 123.05)` -> B.Cu -> the formerly dangling via at `(72.965, 115.1131)` | 16.84 mm, 1 via |

### Two rules the U10 escapes proved the hard way

1. **A track that only touches a pad or via edge is tangent, not connected.** Four separate defects
   came from this — one `unconnected_items`, one `via_dangling` and three `connection_width` necks
   as thin as 0.040 mm. Every escape must end **at the pad or via centre**, not at its edge.
2. **Each U10 pad escapes only along its own centreline**, because the F.Cu notch is 0.3 mm and the
   track plus clearance consumes nearly all of it. `/SDA` leaves at exactly y 140.8, `/SCL` at
   exactly y 141.6, `3V3` at exactly y 141.6 eastward. A 45-degree escape does not fit.

### Inner layers — decided 2026-09-17 (user)

**In1.Cu is a solid, unbroken GND plane and carries no traces. Its zone definition now exists; keep
it trace-free.** In2.Cu is a GND pour that carries a deliberately short list of routed traces, which
cut local voids in that pour; In1.Cu stays continuous so both F.Cu and B.Cu always have an
unbroken reference somewhere in the stack.

The complete In2.Cu trace list — **do not add to it without recording the reason here:**

| Net | Segments | Width | Extent |
|---|---|---|---|
| `VSYS` | `(64.4, 137.3)` -> `(71.4, 130.3)` -> `(76.9, 130.3)` | 0.4 mm | the system power trunk, 15.4 mm |
| `3V3` | `(69.4, 142.9)` -> `(69.4, 139.45)` -> `(68.9307, 138.638)` | 0.3 mm | C20 decoupling feed, ~3.9 mm |

The alternative considered and rejected for `VSYS` was both inner layers solid GND, which forces
the trunk into a 46.7 mm / 37-segment detour down the west board edge and across y 108.5 under the
cell. Rejected on IR drop and loop area. A split power plane on In2.Cu was also rejected, because
`/SDA`, `/SCL` and the USB pair all run on B.Cu and would then reference plane splits.


### Rule areas — there are THREE, not two

| Name | Layer | Forbids | Extent |
|---|---|---|---|
| `SHT40_U10_NO_COPPER` | all Cu | vias, copper pour (**tracks allowed**) | x 69.3..71.7, y 140.2..142.2 |
| *(unnamed)* uuid `870c7573` — **it belongs to the U10 footprint**, not the board | **F.Cu only** | **tracks**, vias, pour | x 69.75..71.25, y 140.45..141.95, with four 0.3 mm notches cut around U10's pads |
| `ANTENNA_KEEPOUT_U1` | all Cu | tracks, vias, pads, pour | x 59.5..84.5, y 99.5..105.9 |

**Consequence for U10, found the hard way on 2026-09-17:** the unnamed area means each U10 pad may
only escape **sideways through its own 0.3 mm notch** — U10.1/U10.2 west, U10.3/U10.4 east. An
escape track must be **<= 0.3 mm wide** (0.25 mm recommended) until it clears x 71.25 / x 69.75.
Netclass 0.4 mm on 3V3 and GND is rejected with `items_not_allowed`. Transition vias also stay
outside x 69.3..71.7, y 140.2..142.2. **As built:** `/SDA` and `/SCL` escape at 0.2 mm, `3V3` and
`GND` at 0.25 mm, each exactly on its pad centreline — see `## Two rules the U10 escapes proved
the hard way`.

**~~Unresolved~~ RESOLVED 2026-09-17:** U10.3 (3V3) escapes east through its notch, turns south
*outside* the keepout (y > 141.95) and runs west to C20.1 entirely on F.Cu — 1.59 mm, no vias, and
it clears the GND track `(71.9817, 142.1983) -> (70.98, 143.2)` because it stays north of it. No
B.Cu detour and no moving C20. Geometry is in the verified log.

### Then: verify the saved fills and export

The two GND-zone definitions and their fills are saved. **In1.Cu is a continuous GND plane and must
stay trace-free. In2.Cu pours around the two traces listed under `## Inner layers`.** The In1 fill
connects the dedicated `C10.2` GND via; verify that with no-refill DRC after PCB Editor is closed.
Then
Inspect > Design Rules Checker (zero errors), the CLI DRC with `--schematic-parity`,
View > 3D Viewer, and finally File > Fabrication Outputs > Gerbers + Drill,
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
