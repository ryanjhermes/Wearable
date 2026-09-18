# V2 design history — moved out of `CLAUDE.md` on 2026-09-17

Background and rationale only. **Not authoritative.** Where this disagrees with `CLAUDE.md`,
`pcb/README.md`, or `parts/V2_BOM.md`, those win.

Read this only when you need to know *why* a decision was made, or to avoid re-opening a settled
question. Do not read it to establish current state.

---

## Project

Experimental wearable transitioning from an archived Seeed Studio XIAO ESP32S3 prototype to a
custom ESP32-C3 fab PCB. It collects body/environment signals via I2C sensors. Not a medical device;
readings are experimental.

> **Current v2 hardware authority:** [`parts/V2_BOM.md`](parts/V2_BOM.md). It supersedes older
> candidate-BOM and power-path notes elsewhere in this file. Component folders contain evidence;
> once a schematic exists, its generated BOM owns reference designators and quantities.

**V2 schematic status (2026-09-16): schematic CAPTURED, ERC-clean, and frozen for layout purposes;
release/order still not approved.**
A KiCad project now exists at [`pcb/`](pcb/) (`wearable_v2.kicad_sch`, opens in KiCad 10.0.5
installed here). **ERC: 0 errors, 2 understood warnings; the generated BOM reconciles exactly to the
planned 51 populated parts** and to `parts/V2_BOM.md`. Five symbols with no stock equivalent were
hand-authored (ESP32-C3-MINI-1, MAX30101, TPS61099, TP4054, USBLC6-2SC6), pinouts checked against the
`parts/` datasheets. **Two real defects caught and fixed during capture** (both silent first-spin
killers): LSM6DS3TR-C ground ties were routed across the SDA/SCL stubs (would short the whole I2C bus
to GND), and `BAT+` was two unconnected nets with the AO3401A gate on its own net not VBUS (cell never
reaches the charger; load-share MOSFET stuck on). Screenshot-iterate workflow works: send a KiCad crop
and the `.kicad_sch` gets patched. **The one-shot bootstrap generators, including `pcb/build.py`,
were removed after capture; `.kicad_sch` is the sole source of truth. Do not restore or rerun them.**
TPS61099 EN is `PPG_PWR_EN` on GPIO10 with a 100 kOhm pulldown so MAX30101 VDD rises before VLED+.

**PCB layout STARTED (2026-09-16) — [`pcb/README.md`](pcb/README.md) is the authority for the PCB
and supersedes this file on PCB state** (net names, Board Setup, stackup/side convention, floorplan
order, and the tooling commands all live in its `# Layout` section). The board contains 64 footprints
(51 BOM + 12 test points + 1 battery-pad). Board Setup is partly configured; **nothing is intentionally
positioned or routed, and no outline exists.** Both items that were open at the previous session's end are now
CLOSED:
- **The third silent first-spin killer (U4 VIN unconnected) is FIXED and verified (2026-09-16).**
  Root cause was not a missing wire: the U4-pin-1 wire *ended mid-span* of the vertical VSYS wire, and
  **KiCad does not connect a mid-wire T without an explicit `(junction ...)` item — the generated
  schematic contained ZERO junctions.** Two junctions were added. Verified with `kicad-cli` (installed
  at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`, 10.0.5): `unconnected-(U4-V_{IN}-Pad1)`
  is gone, net `VSYS` now carries `U4.1` and `U4.3`, and ERC reports **0 errors / 2 warnings** (the two
  benign LSM6DS3TR-C strap ties). **Every wire endpoint and symbol pin was then swept for the same
  failure mode — U4 VIN was the only instance**, and no other power or enable pin sits on an
  `unconnected-` net. Note the general lesson: "ERC: 0 errors" is NOT connectivity-verified, because
  the section-G PWR_FLAGs mask exactly this warning class. **Resolved 2026-09-16:** repeated F8 runs
  failed to transfer U4 pin 1, so its PCB pad assignment was corrected directly to `VSYS`.
  KiCad 10.0.5's authoritative `pcb drc --schematic-parity` now reports **0 schematic parity issues
  and 0 footprint errors**. Do not rerun F8 unless the frozen schematic changes; if it does, require
  the parity DRC to return to zero before layout continues.
- **The board file now lives at `pcb/wearable_v2.kicad_pcb`** (KiCad pairs board↔schematic by
  filename) and the divorced standalone board from the File>Save As incident is gone. The leftover
  `pcb/symbols/wearable_v2.pcbeditor.kicad_pro` was also removed. Use Ctrl+S, never Save As.

**Design-review tooling — the `kicad-happy` plugin (added 2026-09-16).** Cloned at `kicad-happy/`
(gitignored, nested git repo) and symlinked into `.claude/skills/` as 11 skills: `kicad`, `bom`,
`datasheets`, `emc`, `spice`, `jlcpcb`, `pcbway`, `lcsc`, `digikey`, `mouser`, `element14`. All
symlinks resolve. Use `python3 kicad-happy/skills/kicad/scripts/analyze_schematic.py` /
`analyze_pcb.py` instead of writing ad-hoc parsers — it independently caught the U4 defect.
`pcb/.kicad-happy.json` configures it (LCSC primary, 0402 passives, `MPN`-then-`LCSC` field priority,
rail voltage overrides, and documented suppressions for three known false positives: VM-001 on
SDA/SCL because the MAX30101's I2C pins are +6.0 V tolerant, and PU-001 on U7/U8/U9 because those
interrupt pins are deliberately polled or unused). `pcb/datasheets/` holds MPN-named symlinks into
`parts/*/datasheet.pdf` (13 of 25 BOM lines covered; the gaps are the Samsung caps, UNI-ROYAL
resistors and the MAKK2016 inductor). **Every BOM symbol now also carries an `MPN` property**
alongside the `LCSC` one — 51/51 coverage, which clears the analyzers' sourcing gate and is what the
JLCPCB BOM/CPL export keys on. KiCad's own CLI is the authority when the two disagree.

**The user has NO electrical-engineering experience** — layout guidance must be click-level (menu path,
exact field, exact value); do not assume KiCad fluency, and be conservative with tool calls / large
datasheet reads.

Two release gates are now RESOLVED: **offline-retention = summaries-only** (user decision), and the
**module order code is forced to N4 (`C2838502`)** because N4X shows 0 stock at JLCPCB (see JLCPCB
verification below). The **diagnostic LED was declined by the user**; 1V8 and 4V7 test pads replace it.
**All three missing footprints are now created and assigned (2026-09-16); every one of the 51 symbols
resolves to a footprint and ERC dropped from 5 warnings to 2** (both the benign LSM6DS3TR-C strap
warnings). They live in `pcb/pcb.pretty/`: `ESP32-C3-MINI-1.kicad_mod` and
`L_MAKK2016T_2.0x1.6mm.kicad_mod` were **imported from LCSC via `easyeda2kicad`** (installed in the
project venv), NOT hand-authored; `BatteryPads_2x.kicad_mod` was hand-authored (two pads + 2 NPTH
strain-relief holes). Two fixes applied post-import: the ESP32 import carried **no antenna keepout** —
a labelled dashed rectangle now marks the 5.4 mm bare-antenna strip (of the module's 16.6 mm length only
11.2 mm carries pads); and the inductor's **courtyard was smaller than its own pads** (EasyEDA bug) and
was rebuilt to ±1.85 × ±1.15 mm. STEP models for the module and inductor were also copied into
`pcb/pcb.3dshapes/`. **Footprint audit COMPLETE 2026-09-16 (release gate #5): all 12 IC/connector/discrete pin maps
verified pad-by-pad against the manufacturer datasheets with ZERO errors**, and all 16 footprints
have courtyards enclosing their pads. Two land patterns stay unverifiable because the vendor
doesn't publish them in the datasheet — **MAX30101** (Maxim land-pattern 90-0602, external; the
$8.34 part) and **MAKK2016** (no datasheet at all). One open decision it surfaced: **TI says do NOT
solder the TMP117 thermal pad on a rigid PCB** (the ±0.1 °C accuracy spec assumes it unsoldered),
but the shared WSON-6 footprint pastes it — accuracy vs response time, needs a call before layout.
Two layout rules also came out of it: **no copper under the SHT40 except its pin pads**, and the
**MAX30101 VLED+ bypass returns to PGND**. Full findings are in `pcb/README.md`. The inductor's
**electrical ratings ARE now
manufacturer-confirmed (Taiyo Yuden, 2026-09-16): 2.2 µH ±20%, Isat/Irms 1.5 A, DCR 0.16 Ω max,
2.0×1.6×1.0 mm — current margin is comfortable, since the TPS61099's 0.8 A minimum switch limit bounds
peak inductor current well under Isat.** What is still missing is only the recommended land-pattern
drawing (LCSC's PDF endpoint serves a bot page), so `parts/makk2016/` holds a README but no
`datasheet.pdf` — the project's only `check_parts.py` gap. (Taiyo Yuden renamed this part to
LSANB2016KKT2R2M/LLANB2016KKT2R2M; LCSC still stocks the old C92923, so v2 is unaffected — the
successors are the drop-in replacement if C92923 disappears.) Also still open: exact protected-battery evidence,
independent electrical review, power-budget/thermal check, and the PCB layout itself.

**JLCPCB single-supplier/assembler CONFIRMED (2026-09-16), queried against JLCPCB's own SMT assembly
API (not LCSC):** all 25 BOM line items are in JLCPCB's assembly library, every one `source: shop`
(JLCPCB holds the stock — no consignment) with non-zero stock. **13 Extended part types + 12 Basic**
→ ~$3/unique-Extended-type loading fee ≈ $39 one-time (the dominant NRE on a small run; confirm in
cart). The board's **single supply risk is the MAX30101 (`C2859066`): ~304 stock, ~10× below every
other line, $8.34** — fine for a 5-board spin, not for a months-later reorder. `C25770` (270k 0402 1%)
is the only Extended *passive* (no Basic equivalent; keep it). The two-sided form factor forces a
second SMT setup (quote both sides); the **battery is hand-soldered by you, not in the JLCPCB shipment.**

**Status:** Phase 3 (sensor reads) is **COMPLETE**. MAX30102 heart rate and BMI160 motion both
read live and are CONFIRMED simultaneously on the shared I2C bus. BLE HR streaming works
untethered on battery. Battery power CONFIRMED working. Open work: enclosure — a first
**simple two-part box** design exists as `.3mf` in `archive/v1/enclosure/` (see its `README.md`);
`enclosure/` now holds only the v2 placeholder, blocked on the fab PCB outline. Target
form factor is wristband/watch in 3D-printed TPU; the assembled electronics measure ~57×24×11mm.
Not yet confirmed printed/fitted against the assembled electronics.

**Direction change — miniaturization is the binding blocker (user, 2026-09-12):** firmware is
treated as done/clean-slate; the hardest open problem is **physical size/comfort** — the current
~57×24×11mm packing is too bulky (a volume audit found ~60% of it is air + jumper wire; the LiPo and
XIAO, not the sensors, dominate). Working direction: a **custom carrier PCB**, skin-facing optical
side, **externally assembled/fabbed**; target ≈Whoop-class (~32×24×11mm). **Form-factor constraint
(user, 2026-09-12):** **ONE double-sided PCB, NOT a board stack**, and **cannot be significantly
taller** — sensors on the skin side, MCU + LiPo on the top side; height budget ~11mm, pinned by the
LiPo. **The `pcb/` folder was DELETED 2026-09-14** at the user's request — it was an abandoned rough
start (schematic + PCB empty, one stale breakout footprint) and is not a basis for anything. It is
recoverable from commit `ebf99dc` if ever needed. The new board starts from scratch.

**Physical constraints (user, 2026-09-14):**
- **No status LEDs and no screen** — both cut to save space. Caveat worth remembering: the
  `battery_blink` and `led_test` envs exist precisely because an LED is the only diagnostic that works
  when USB won't enumerate (a recurring failure in `archive/v1/docs/hardware_debug_log.md`). Losing that costs
  bring-up visibility; a single DNP-able 0402 LED footprint would keep the option for ~1mm².
- **Recovery path — expose BOOT (GPIO9) + RESET as test pads (assistant recommendation, 2026-09-15).**
  No LEDs + no buttons + a sealed enclosure means a firmware failure could leave NO way in. The
  ESP32-C3 needs BOOT (GPIO9) pulled low to enter download mode (the "hold BOOT, tap RESET" fix that
  recurs throughout `archive/v1/docs/hardware_debug_log.md`). Two exposed pads cost ~0 and preserve the escape hatch.
- **Battery sits on TOP of the double-sided board** (over the top-side components), not beside it —
  confirmed as the plan. Stack: sensors 1.55 + PCB 1.0 + MINI-1 2.4 + LiPo 4.0 + walls ≈ **10.5mm**.
  Beside-mounting is thinner (~8mm) but makes the footprint far too long for a wrist.
- **Antenna keepout vs battery:** if an ESP32-C3-MINI-1 is used, the LiPo's metal pouch must NOT sit
  over the module's PCB trace antenna — it detunes/blocks it. Battery goes over the opposite end;
  the antenna end needs clear copper and no metal above it.
- **Component-area audit from the captured schematic (2026-09-16):** summing every footprint's KiCad
  courtyard, all 51 populated parts = **550 mm²** total → **~23×23 mm per side** two-sided at realistic
  packing. The ESP32-C3-MINI-1 alone is 219 mm² (**40%**), USB-C 100 mm² (18%), all 37 passives only
  78 mm² (14%). **The 402030 battery (30×20 = 600 mm², on top) is larger than all the electronics
  combined** — so shrinking the circuit barely shrinks the board; the **cell (and its runtime) is the
  binding size constraint**, and deleting every passive would save just 14%. This makes the ~32×24 mm
  target tight: whether the battery and the module antenna can coexist inside 32×24 has **never been
  checked** — that verification needs a floorplan (the 3 missing footprints imported, big items placed,
  no routing; ~a day, not started). The three size levers are smaller battery (biggest win, costs
  runtime), drop USB-C (100 mm² + 4 parts, already rejected), or bare ESP32-C3 chip (~120 mm², high
  first-spin risk). **User relaxed the size target (2026-09-16): a 30×20 mm (3×2 cm, i.e. the 402030)
  cell "is totally fine" because "most consumer wearable sizes are dominated by the battery anyway"** —
  so the smaller-battery lever is CLOSED and the ~32×24 mm Whoop-class goal is no longer a hard target;
  plan for a battery-dominated footprint sized around the 30×20 cell rather than shrinking under it.
- **Optical isolation deprioritized (user's call).** Not being designed as a PCB-level feature. The
  cheap fallback if wrist PPG is weak: an opaque ring printed into the enclosure between LED and
  photodiode, and no air gap to skin — costs nothing at the PCB level, so this stays reversible.
- **Thermal-isolation slot is an UNVALIDATED hypothesis, not a finding.** The claim that board
  self-heat corrupted the MLX90614 readings was inference from `archive/v1/docs/hardware_debug_log.md`, never
  measured. Treat as optional cheap insurance at layout time, not a requirement.

### V2 fab-board part selection

The fab track and core devices are selected. Exact part numbers, passives, power architecture, and
the remaining battery verification are maintained in `parts/V2_BOM.md`. Green PPG, permanent battery
attachment, and supervised off-wrist charging are locked. The table below
includes historical evaluation context and must not override that file.

1. **Fab track is selected.** Bare LGA/OLGA parts will be machine assembled; the old breakout track
   remains only in `archive/v1/`.
2. **Wrist PPG wavelength is still unvalidated.** The green-LED argument for MAX30101 rests on commercial
   practice (Apple/Fitbit/Whoop use green on the wrist), NOT on any measurement from this project.
   The one on-wrist attempt (2026-07-24) ran on known-bad firmware and is inconclusive. **The
   diagnostic to settle it already exists and has NEVER been run** — `archive/v1/src/max30102_raw_ir/` +
   `archive/v1/scripts/raw_ir_capture.py` + `archive/v1/scripts/plot_raw_ir.py` were built 2026-07-23 and `data/` contains
   **zero** raw-IR captures. Run that on the wrist before spending money on either sensor.

| Function | Currently owned | Candidate | Why considered | Status |
|---|---|---|---|---|
| PPG / HR | MAX30102 (MH-ET LIVE breakout, ~20.5×15.5mm) | MAX30101 | Adds a **green** LED (red/IR is a fingertip/SpO₂ combo); wrist PPG in commercial devices is green | **MAX30101 CHOSEN for the fab board (user, 2026-09-15):** *"Let's go with the MAX30101 then, since a previous analysis said green is better for this use case."* This settles the sensor pick for the carrier PCB. **Caveat: the wrist-PPG wavelength test above STILL has not been run** — the choice rests on commercial practice, not a measurement. Because MAX30101 includes red, IR, and green, the test is now post-arrival validation rather than an ordering gate. **Fab track sourcing CONFIRMED (2026-09-14):** `MAX30101EFD+T` = LCSC **C2859066**, in stock ~319, Extended, ~$8.34@qty1 — the biggest BOM sourcing risk, now resolved |
| Temp | MLX90614 GY-906 (suspected dead, tall TO-39 can) | TMP117AIDRVR | Contact temperature, low power, and <1 mm height | **SELECTED** — LCSC **C699536**, WSON-6 2.0×2.0×0.75 mm; evidence in `parts/tmp117/` |
| IMU | BMI160 (GY-BMI160 breakout) | Keep BMI160 | Only needs to subtract activity from HR; existing driver works | **BMI160 confirmed DEAD on fab track (2026-09-14):** LCSC **C94021** is **consign-only, 0 stock** (the Bosch-EOL outcome) — not machine-placeable by JLCPCB. So on the fab track the accel is **LSM6DS3TR-C** (near-identical footprint; port ≈ axis-remap + register-address changes, ~a day of firmware). Keeping BMI160 only remains viable on the prototype/breakout track. User declined an upgrade to LIS2DH12 (2026-09-14) unless it's a large improvement. **LSM6DS3TR-C now sourced & filed (2026-09-15):** LCSC **C967633**, datasheet in `parts/lsm6ds3tr-c/`. It is **6-axis — the gyro is free**; use it for sway/tremor/gait-instability BAC features, not only activity-subtraction |
| MCU | XIAO ESP32S3 (dev board) | ESP32-C3-MINI-1 module | A dev board on a carrier = two stacked PCBs, violating the one-board constraint | **SELECTED FAMILY** — N4/LCSC **C2838502** is the stocked capture baseline; Espressif marks it NRND and recommends footprint-compatible N4X for new orders. Lock one exact order code before release; evidence in `parts/esp32-c3-mini-1/` |
| Battery | LiPo 402030 (30×20×4, 250mAh) | unchanged for now | Pins the height budget | Owned |
| EDA/GSR | none | analog front end | 4th Kaczor channel; see Application section | **CUT FROM V2 (user, 2026-09-15)** — "no EDA, maybe for v3... we'll need to get v2 working in the first place." Complexity reduction to maximise first-spin success. Costs the strongest single BAC predictor; revisit in v3. `parts/mcp6002/` kept as research, NOT on the BOM |
| Ambient temp+humidity | none | SHT40-AD1B-R3 | De-confounds skin temperature; must be vented to ambient air | **SELECTED** — LCSC **C2848306**; evidence in `parts/sht40/` |

**Fab-track I2C bus has no address collisions (2026-09-15):** the four selected sensors sit at
distinct addresses — SHT40 `0x44`, TMP117 `0x48` (strappable 0x48–0x4B), MAX30101 `0x57`,
LSM6DS3TR-C `0x6A/0x6B` — so they share one bus cleanly. Note this differs from the prototype
breakouts' map in **Hardware & I2C**: the fab accel is `0x6A/0x6B`, not the GY-BMI160's `0x69`.

**Sizes are chip-vs-breakout, not chip-vs-chip — do not conflate them.** The bare MAX30101 and bare
MAX30102 are the **same size** (5.6×3.3×1.55mm OLGA-14, same `0x57` address, same SparkFun MAX3010x
library). An earlier revision of this file claimed MAX30101 was "smaller" — **that is false.** Any
size win comes from going breakout→bare chip, which is available with either sensor. Amazon sells
breakouts only; bare chips come from LCSC/Mouser and are placed by the fab.

**Bare-chip power trap — MAX30101/MAX30102 VDD is 1.8V, NOT 3.3V (from JLCPCB listing, 2026-09-14).**
The breakout you own hides this behind an onboard regulator (why it accepts 3.3V today). On a bare-chip
board you must supply **1.8V yourself** (a second LDO) **plus a separate higher VLED rail** — the power
design goes from one rail to **three**. The I2C pins are spec'd to tolerate a 3.3V bus even with 1.8V
VDD, so the shared bus is fine. **All three now datasheet-verified (2026-09-15, filed in
`parts/max30101/`):** VDD 1.7–2.0V (abs max **+2.2V** — 3.3V destroys it); SDA/SCL abs max +6.0V so the
3.3V bus needs **no level shifting**. VLED+ is **3.1–5.0 V for red/IR but 4.5–5.5 V for green**.
A single LiPo cannot guarantee green; `parts/V2_BOM.md` defines the mandatory 4.704 V TPS61099 boost.
Without that block the board would be red/IR-only. This breakout→bare-chip
"the breakout was doing work you didn't know about" trap must be re-checked for every part picked.
**Concrete instance already known: I2C pull-ups.** The prototype breakouts each carry their own
SDA/SCL pull-ups; the bare chips do NOT, so the carrier board must add **one pair of ~4.7k pull-ups**
for the whole bus.

**"You have sensors, not a BOM" (assistant, 2026-09-15).** Part *selection* is settled pending the
EDA call, but a schematic needs **~25–30 more support parts** the XIAO + breakouts were silently
providing: 3.3V LDO + the 1.8V LDO above + LiPo charger (MCP73831/TP4054) + program resistor + bulk/
decoupling caps (~8); mid-mount USB-C + 2× 5.1k CC resistors (mandatory or it won't draw power) + ESD
array (~4); EN pull-up + RC + BOOT/RESET access + decoupling (~6); the 2 I2C pull-ups above; EDA front
end if included (~5). Most are Basic (no setup fee), but each is a chance to get something wrong. No
RTC chip needed — the `#now` BLE clock-anchor + phone time already cover timestamps.
**Support-part BOM now drafted & filed — `parts/_support/README.md` (2026-09-15).** A full candidate
list (≈31 support parts, 5 ICs/connectors) with LCSC numbers, values, and net assignments: **3.3V LDO
ME6211C33M5G-N (C82942)** — the 120mV dropout is the point, a generic AMS1117's ~1.1V would waste the
bottom of the cell; **1.8V LDO XC6206P182MR (C21659)** for the MAX30101, fed from 3V3 not the battery
(load ~20mA); **charger TP4054 (C32574)**, SOT-23-5, chosen over TP4056 (C16581, ESOP-8/1A-class,
oversized for a 250mAh cell) — size the program resistor to ≤0.5C (~125mA); **USB-C TYPE-C-31-M-12
(C165948)**; **ESD USBLC6-2SC6 (C7519)**. **Two parts the earlier list missed, both would break a first
spin:** a **10kΩ pull-up on GPIO8** (strapping pin, defaults floating — module won't boot reliably
without it, same category as the EN resistor) and a **battery-sense divider (2× 1MΩ)** for
battery-percentage (the XIAO had one). **Caveat:** JLCPCB Basic-vs-Extended and stock render via JS and
did NOT extract reliably — LCSC numbers are real and the parts exist, but confirm Basic/Extended in a
JLCPCB cart before ordering (affects setup-fee cost, not feasibility). USBLC6 and MAX30101 are both
**Extended**, so "mostly Basic" was optimistic.

**Support parts now filed & sourcing-gated (2026-09-15).** The five support ICs/connectors each have a
folder + datasheet: `parts/me6211/`, `parts/xc6206/`, `parts/tp4054/`, `parts/usb-c-16p/`,
`parts/usblc6/`. Datasheet-verified pinouts/values (the class of detail that kills a first spin):
- **ME6211C33M5G-N — CE (pin 3) MUST be tied high; floating = no output, no other symptom** (board
  looks dead). Pinout `1=VIN, 2=VSS, 3=CE, 4=NC, 5=VOUT` (p.4). **Do NOT substitute the ME6211*H*** —
  C and H series differ in enable *polarity*, same package/voltage.
- **XC6206P182MR — verified SOT-23 pinout `1=VSS, 2=VOUT, 3=VIN`.** The older reversed note was wrong.
- **TP4054 — I_charge = 1000/R_PROG, so R_PROG = 10kΩ 1% → 100mA (0.4C)** — gentle on the 250mAh cell,
  ~3h charge (supersedes the earlier "≤0.5C/~125mA" estimate).

**Charge-path load sharing is resolved (2026-09-15).** V2 uses the Microchip AN1149-style discrete
topology: AO3401A P-MOSF + SS14 Schottky + 100 kOhm gate pulldown. USB powers VSYS while attached and
the TP4054 sees only battery current, so termination does not depend on firmware. Exact orientation
and rationale are in `parts/V2_BOM.md` and `parts/_support/DECISIONS.md`.

**Remaining pre-freeze evidence (updated 2026-09-16):** identify the user's exact 250 mAh cell and verify
its protection board, polarity, physical dimensions, and >=100 mA charge rating. Green PPG is
mandatory, the cell is permanently soldered, and charging is supervised/off-wrist. All passives have
exact MPNs and LCSC numbers. **No KiCad symbols/footprints exist yet** — `parts/` holds evidence only;
every imported symbol and footprint must be checked against the manufacturer datasheet. Proposed
fixed signals are SDA=GPIO6, SCL=GPIO7, and battery ADC=GPIO3. GPIO2/8/9 remain dedicated boot straps
with 10 kOhm pull-ups. GPIO10 is assigned to `PPG_PWR_EN` with a 100 kOhm pulldown; firmware enables
the boost only after the MAX30101 1.8 V logic rail is established.

**No BOM generator was built, deliberately (assistant, 2026-09-15).** Quantities/refdes live in the
schematic, not in `parts/`, so a `parts/`-reading script could only ever emit a parts *list* and would
become a second source of truth that disagrees with KiCad's netlist BOM. Sequencing is **schematic →
KiCad BOM (authoritative, with quantities) → cross-check against `parts/V2_BOM.md`** for
LCSC#/sourcing. `parts/check_parts.py` is only an evidence-integrity gate: it checks part folders for
LCSC codes, missing/corrupt/duplicated PDFs, unresolved merge markers, and broken relative links.
Its “No gaps” result is not schematic, connectivity, quantity, stock, or safety validation.

**Wavelength test no longer gates ordering — MAX30101 is a SUPERSET of the MAX30102 (2026-09-15):** it
carries red (660nm), IR (880nm) *and* green (527nm) in the same package/`0x57`/library, so buying it
doesn't commit to green — all three wavelengths are testable in firmware once the board arrives. This
converts the undiagnosed wrist-PPG wavelength question from a **blocking pre-order risk into a
post-arrival firmware experiment** (~$5 + Extended status is the whole cost of keeping the option open).

**Mid-mount USB-C is UNNECESSARY — resolved (2026-09-15), reversing the note below.** A standard
**~3.2mm horizontal SMD receptacle** fits *inside* the top-side height envelope already set by MINI-1
(2.4mm) + LiPo (4.0mm) = 6.4mm, so it costs floorplan area at one board edge, not height. Mid-mount was
solving a height problem this board doesn't have; the unsourced mid-mount part is dropped. **USB-C kept**
(user called it "not essential," assistant argued to keep it): dropping the connector relocates the
charger rather than removing it — external charging needs corrodible exposed contacts or a second
dock to design, and loses single-cable flashing on a board reflashed constantly during bring-up. It's
4 parts; keeping it is the lower-effort path to "works first try."

**MCU — "ESP32-C3" names three different things:** the bare **chip** (QFN 5×5mm, needs crystal/
antenna/flash support circuitry); the **ESP32-C3-MINI-1 module** (13.2×16.6×2.4mm — chip + flash +
crystal + **PCB trace antenna** + shield can, pre-certified, solders flat as one part; the `-1U`
variant swaps the trace antenna for U.FL); and the **XIAO ESP32C3 dev board** (a module plus USB-C,
LDO, charge IC, buttons, castellated pads — and it uses an **external U.FL antenna**, same as the S3).
Same silicon in all three. The MINI-1 is not an upgrade or a different family — it is the form that
can sit directly on a custom board. Cost of moving off the XIAO: you take on its USB-C, ESD, LDO,
charger and boot/reset circuitry (~15 passives + 3 ICs of reference design).

**USB-C:** keep it — decision confirmed. **A standard horizontal SMD receptacle is used, NOT mid-mount**
(see the mid-mount-is-unnecessary resolution above): at ~3.2mm it fits inside the top-side envelope, so
it costs area at a board edge, not height. The pogo-pad/dock alternative buys ~55mm² of area, still needs
the same charger IC, loses one-cable flashing, and adds a dock to design. Rejected on those grounds.

**Antenna is a non-issue for this design (user, 2026-09-12):** data is stored on-device and BLE-synced
to the phone on reconnect, so range/connection quality is not a priority.

Any "upload somewhere for an ML model" backend must be Pioneer Supabase/Azure.

**Application — proxy blood-alcohol concentration (BAC) with ML (user-committed goal, 2026-09-12):**
following Kaczor et al., *"Detecting Ethanol Intoxication and Impairment Using Wearable Biosensors"*
(HICSS 2026) — a wrist HR + skin-temp + EDA + accelerometry combo with an XGBoost model (~0.80
accuracy). Three of four channels map to candidate parts (PPG=HR, contact temp, BMI160=accel); the
missing channel is **EDA/GSR**.

> **Jargon (user asked 2026-09-14):** **EDA** here = **electrodermal activity**, a.k.a. GSR/galvanic
> skin response — skin conductance between two skin electrodes, which rises with sweat-gland activity.
> *Not* to be confused with "EDA" meaning Electronic Design Automation (KiCad). **LCSC** = the
> component distributor that **JLCPCB** (PCB fab) pulls parts from when it assembles a board — it

**V2 BOM DECISION — EDA IS OUT (user, 2026-09-15).** Deferred to v3. The reasoning was explicitly
about scope control, not merit: get a simpler board working first. Accept that the v2 dataset will
have 3 of Kaczor's 4 channels (HR/HRV, skin temp, accelerometry) and no electrodermal channel, and
that adding it later is a full respin. `parts/mcp6002/` stays as filed research.

EDA is analog rather than I2C, but **it is not part of v2**. GPIO3 is reassigned to battery sensing.
The MCP6002/electrode notes remain in `parts/mcp6002/` only as archived v3 research. Adding EDA later
will require a board revision and, for skin electrodes, an appropriate corrosion-resistant finish.

**V1 sensor scope locked down (user, 2026-09-15):** "**We won't be doing microphone or ECG.**" Also
**ruled out for V1** (assistant analysis, user did not object): transdermal-alcohol (TAC) sensor,
barometer, bioimpedance. Working v2 scope is **SHT40, then stop** — adding more channels
worsens overfitting risk (self-labeled data + ~30 features on XGBoost will memorize sessions). MLX/
non-contact IR is NOT needed — contact TMP117 replaces it.

**Ground-truth labels require a fuel-cell breathalyzer (user aware, 2026-09-15):** "I'm aware of the
breathalyzer part." No BAC model trains without labels — a **fuel-cell** (not semiconductor) unit
(~$50–150) is the highest-value near-term purchase. Not a board component; an external labeling tool.

**Battery cannot capture a full drinking session — physical (height) limit, not firmware (2026-09-15):**
real sessions run 4–6+ h vs the ~3–4 h the 250 mAh cell gives; the cell (which also pins the 11mm
height budget) is the binding constraint on session-length data capture, so this is a form-factor
tradeoff, not something a firmware heat-cut fixes.

**Free ML channels at zero BOM cost (2026-09-15):** the MAX30101 PPG alone can also yield HRV
(parasympathetic suppression), **perfusion index** (AC/DC — peripheral vasodilation, one of the
cleaner alcohol signals), SpO₂, and PPG waveform morphology; the LSM6DS3TR-C gyro adds sway/tremor.
These come from parts already on the candidate list — no extra sensors, so they don't add overfitting
surface the way new hardware does.

