# V2 PCB Layout — Handoff (2026-09-16)

Read `../CLAUDE.md` first for project context. This file covers only the PCB layout task
and supersedes CLAUDE.md where they disagree about PCB state.

## Who you are helping

The user has **no electrical engineering experience**. Give click-level instructions
(menu path, exact field, exact value). Do not assume KiCad fluency. Do not read the
`parts/*/datasheet.pdf` files unless genuinely necessary — they are large and burn context.
The user has asked to be conservative with tool calls.

## Where things stand

- Schematic `wearable_v2.kicad_sch` is captured, ERC-clean, 51 populated parts. **Do NOT
  re-run `build.py`** — it regenerates from scratch and erases hand-fixes.
- KiCad 10.0.5. The schematic is still in KiCad 8 file format; KiCad 10 converts it on
  first save. `pcb/` is committed to git, so there is a rollback.
- **F8 (Update PCB from Schematic) has already been run.** 64 footprints landed
  (51 BOM parts + 12 test points + 1 battery-pad footprint).
- Board Setup is mostly configured (see below). **Nothing is placed or routed yet.**

### File-location incident (verify this was fixed)

The user did File > Save As and produced a divorced standalone project at
`pcb/symbols/wearable_v2.pcbeditor.kicad_pcb`. The board must live at
`pcb/wearable_v2.kicad_pcb` — KiCad pairs board to schematic **by filename**. The fix was
to move/rename it and delete the stray `.kicad_pro`/`.kicad_prl`/`.history` in `symbols/`.
**Confirm `pcb/wearable_v2.kicad_pcb` exists and `pcb/symbols/` contains only
`wearable_v2.kicad_sym` before doing anything else.** Tell the user to use Ctrl+S only.

## BLOCKING DEFECT — fix before any placement

**U4 (ME6211C33M5G-N, 3.3 V LDO) pin 1 VIN is connected to nothing.** Confirmed from the
generated netlist: pad 1 is on `unconnected-(U4-V_{IN}-Pad1)`. Pin 3 (CE) is correctly on
VSYS; pin 5 (VOUT) is correctly on 3V3. As drawn there is no 3.3 V rail, therefore no ESP32,
no sensors, and no 1.8 V rail (which is fed from 3V3).

ERC missed it — section G of the schematic carries PWR_FLAGs added to silence exactly this
warning class. **Fix in the schematic** (wire U4 pin 1 to VSYS), re-run ERC, re-run F8.

Given one defect of this class slipped through, it is worth sweeping the netlist for any
other power/enable pin sitting on an `unconnected-` net before layout. The check that found
this: extract each IC footprint's pad->net map from the `.kicad_pcb` and look for power pins
on `unconnected-` nets. Known-benign unconnected pins: U1 NC/IO0/IO1/IO4/IO5/RXD0/TXD0,
U3 CHRG (status LED declined), U4 NC, U7 NC/INT, U8 ALERT, U9 INT1/INT2/NC, J1 SBU1/SBU2.

## Exact net names (verified from the generated netlist)

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

## Board Setup — applied

4 copper layers. Impedance controlled OFF (so the dielectric values are documentation only;
JLCPCB uses its own stackup — do not spend time on them).

| Constraint | Value |
|---|---|
| Min clearance | 0.15 mm |
| Min track width | 0.15 mm |
| Min via diameter / drill | 0.6 / 0.3 mm |
| Copper to hole clearance | 0.25 mm |

Netclass `Power` exists at 0.4 mm track width. **Verify these 8 assignment patterns are
present and each previews a match:** `GND`, `VBUS`, `VSYS`, `BAT+`, `3V3`, `1V8`, `4V7`,
`/SW_PPG`. Leave `/FB_PPG` in Default deliberately.

## Board Setup — still to change

| Where | Change | Why |
|---|---|---|
| Constraints | Min connection width 0 -> **0.15 mm** | 0 disables the check for hairline zone-to-pad necks |
| Constraints | Copper to edge 0.5 -> **0.3 mm** | recovers usable width on a tight board |
| Constraints | Min annular width 0.1 -> **0.13 mm** | match fab capability |
| Constraints | Hole to hole 0.25 -> **0.5 mm** | conservative; costs nothing here |
| Constraints | Min text height 0.8 -> **1.0 mm**, thickness 0.08 -> **0.15 mm** | below the fab's printable silkscreen minimum |
| Board Editor Layers | In1.Cu and In2.Cu type "signal" -> **power**; optionally rename to GND / PWR | they are the planes |
| Net Classes | Set explicit vias: Default **0.6/0.3**, Power **0.8/0.4** | both are currently blank |
| Physical Stackup | **Board thickness decision: 1.6 mm (current) vs 1.0 mm** | the height stack assumes 1.0 mm PCB; 1.6 spends 0.6 mm of an ~11 mm budget. User has not decided. Confirm 1.0 mm 4-layer availability in the JLCPCB cart. |

**Never place a uVia.** JLCPCB does not do blind/buried vias on a standard order. DRC will
not warn you. Also: switch the PCB editor to **mm** (Ctrl+U) — every part is metric.

## Stackup and side convention (do not change mid-layout)

| Layer | Side | Contents |
|---|---|---|
| F.Cu | top, away from wrist | ESP32-C3-MINI-1 (U1), USB-C (J1), charger, regulators, boost, battery pads (BAT1), SHT40 (U10) |
| In1.Cu | — | solid GND plane |
| In2.Cu | — | power |
| B.Cu | **skin side** | MAX30101 (U7), TMP117 (U8) |

Flip a part to the other side with **F**. Move with **M**, rotate with **R**.

## Next steps

### Step 3 — provisional outline
Edge.Cuts rectangle, start **24 x 42 mm** (deliberately oversized — JLCPCB charges the same
for anything under 100 x 100 mm, so extra area is free until order; shrinking later is a drag,
growing after routing is a rework). Fillets (2 mm corners) at the very end.

### Step 4 — floorplan, in this order
1. **U1 ESP32-C3-MINI-1** lengthwise, antenna end pointing away from the battery. 40% of total
   component area (219 mm2 of 550 mm2).
2. **Antenna keepout, immediately after U1.** The imported footprint carries only a dashed
   *marking* of the 5.4 mm antenna strip — it enforces nothing. Add a real
   Place > Rule Area (Keepout) over that strip, **all four copper layers**, keep out
   tracks/vias/pours/footprints, extended to the board edge.
3. **BAT1 battery pads** at the opposite end. Separately draw the **30 x 20 mm cell body**
   as a rectangle on **User.Drawings** — the cell sits on top of the board, and its metal
   pouch must NOT overlap the antenna keepout.
4. **J1 USB-C** flush to a board edge. Standard ~3.2 mm horizontal SMD part — fits inside the
   top-side height envelope, costs edge area not height.
5. **U7 MAX30101** — flip to B.Cu, centred where it sits flattest on the wrist.
   `C15` (4.7 uF on 4V7) immediately adjacent — mandatory for the 200 mA LED pulses.
6. **U8 TMP117** — flip to B.Cu. Its thermal pad IS the measurement: keep it away from
   U3/U4/U5/U6 (regulators) and away from U1.
7. **U10 SHT40** — opposite requirement: must read AMBIENT air. Top side, near a board edge,
   as far from the regulators and ESP32 as possible. Enclosure needs a vent over it.
8. **U6 TPS61099 + L1** tight together, short fat `/SW_PPG` — that loop radiates.
9. **U9 LSM6DS3TR-C, U2, U3, U4, U5, Q1, D1**, then all 37 passives.
   Each decoupling cap hard against its chip's power pin (the shortest ratline tells you which).
10. **TP1-TP12** reachable with a probe. BOOT (GPIO9) + RESET are the only recovery path —
    no LEDs, no buttons on this board.

Then shrink Edge.Cuts to fit, add fillets, keep all parts >= 1 mm inside the edge.

### THE CHECK THAT HAS NEVER BEEN DONE
Once U1, BAT1 and the cell-body rectangle are placed: **does the 30 x 20 mm cell clear the
antenna keepout entirely?** Never verified. A LiPo pouch over the trace antenna detunes it.
If it does not clear, lengthen the board — free right now, a full re-layout later.

### Step 5 — route, then pour
Route on F.Cu/B.Cu; via down to the GND plane rather than hand-routing returns.
Zones last: Place > Filled Zone, net GND, on all four layers, then `B` to fill.

### Step 6 — verify and export
Inspect > Design Rules Checker (zero errors), View > 3D Viewer, then
File > Fabrication Outputs > Gerbers + Drill, plus the position/CPL file for **both sides**
and the BOM.

## Open before ordering (not blocking layout)

1. **Footprint audit — release gate #5, still OPEN.** Only the ESP32 module is datasheet-
   verified pad-by-pad. MAX30101 uses generic `OptoDevice:Maxim_OLGA-14` and the accel uses
   generic `Package_LGA:LGA-14`; both are package-name matches only. DRC cannot catch a wrong
   pinout. The MAKK2016 inductor has no datasheet on file at all.
2. `pcb/bom_from_schematic.csv` is **stale** — it still says `pcb_v2:` from before the folder
   rename. The schematic is correct (`pcb:`). Regenerate from KiCad, do not trust that file.
3. Battery evidence: exact 250 mAh cell, protection board, polarity, dimensions, >=100 mA
   charge rating.
4. Independent electrical review; power-budget / thermal check.
5. Two-sided assembly forces a second SMT setup at JLCPCB — quote both sides.
   The battery is hand-soldered by the user, not in the JLCPCB shipment.
