# CLAUDE.md

@AGENTS.md

`AGENTS.md` is the workflow contract: context discipline, the verified-log rule, and when to
delegate. Follow it. This file is deliberately short so it costs little to load every session —
**keep it under ~200 lines.** Detail belongs in the authority documents below, not here.

## What this is

An experimental wearable moving from an archived Seeed XIAO ESP32S3 breakout prototype to a custom
**ESP32-C3 fab PCB**. It reads body/environment signals over one I2C bus. Long-term goal: proxy
blood-alcohol concentration from HR/HRV + skin temp + accelerometry (Kaczor et al., HICSS 2026),
labeled with an external fuel-cell breathalyzer. **Not a medical device.**

**Layout is complete and verified as of 2026-09-18.** Current work is the three pre-order gates — the
JLCPCB cart pass, the enclosure print/fit test, and bench validation of the rails on a built board.
None can be closed from the keyboard. Firmware is treated as done; v1 is frozen in `archive/v1/`.

**Before doing anything, read `## SETTLED — do not re-verify, do not re-open` at the top of
`pcb/README.md`.** It lists the checks, decisions and JLCPCB settings that are closed. Re-running them
wastes the usage window and has repeatedly been this project's failure mode.

## Authority map — read only what the task needs

| Document | Owns | Read when |
|---|---|---|
| `AGENTS.md` | Agent workflow, delegation, context discipline | Always (auto-loaded) |
| `pcb/README.md` | **Current PCB + schematic state, verified log, next work** | Any PCB/schematic task |
| `parts/V2_BOM.md` | Part rationale, power tree, approval/release gates | Sourcing, BOM, release questions |
| `pcb/bom_from_schematic.csv` | Reference designators and quantities | When refdes/qty matter |
| `docs/DESIGN_HISTORY.md` | *Why* past decisions were made | Only to avoid re-opening a settled question |
| `archive/v1/V1_REFERENCE.md` | v1 firmware, XIAO board, breakout I2C, PlatformIO | Only for v1 firmware work |
| `parts/<part>/README.md` | Per-part pinout, required externals, layout notes | That specific part |

Nothing outside this table is authoritative. If two documents disagree, the one that owns the topic
wins; if that is ambiguous, ask rather than guess.

## Hard rules

- **The user has no electrical-engineering experience.** Layout guidance must be click-level: exact
  menu path, exact field, exact value. Do not assume KiCad fluency.
- **The KiCad schematic is frozen for layout.** Raise a suspected circuit change; never edit
  `pcb/wearable_v2.kicad_sch` silently during layout work.
- **Do not rerun KiCad F8** (Update PCB from Schematic) unless the schematic genuinely changed.
  KiCad 10.0.5 reintroduces a stale U4 pad net in this project. If it is rerun, parity DRC must
  return to zero before layout continues.
- **Never patch `pcb/wearable_v2.kicad_pcb` while KiCad PCB Editor is open.** Use Ctrl+S in KiCad,
  never File > Save As (it divorced the board from the project once already).
- **Clean checks are not fabrication approval.** Layout complete ≠ reviewed ≠ ordered. Release
  gates in `parts/V2_BOM.md` are separate and explicit.
- **"ERC: 0 errors" is not connectivity-verified** — the section-G PWR_FLAGs mask unconnected-pin
  warnings. Three silent first-spin killers were found this way; check nets, not just ERC.
- Any cloud/ML backend must use Pioneer's official Supabase, Azure, or GitHub accounts.
- LiPo safety: never charge sealed in the enclosure or unattended. Rapid heating with battery +
  USB means reverse polarity or a short — unplug immediately.

## Locked constraints (do not re-litigate)

Rationale for each is in `docs/DESIGN_HISTORY.md`.

- **One double-sided PCB, not a board stack.** Sensors on the skin side, MCU + LiPo on top.
- **Board is 24 x 46 mm, 1.0 mm thick, 4 layers.** Battery sits *on top of* the board.
- **No status LEDs, no screen, no buttons.** BOOT (GPIO9) + RESET are exposed as test pads — that
  is the only recovery path into a sealed board.
- **The cell is final: EEMB `LP502030-PCM`, 250 mAh, 32 x 20.5 x 5.3 mm, already owned.** It
  dominates the footprint and that is accepted; the Whoop-class ~32 x 24 mm target is no longer a
  hard goal. Battery selection is closed and is not to be reopened or re-sourced.
- **A LiPo pouch must never sit over the ESP32-C3-MINI-1 trace antenna.** Enforced by a Rule Area.
- **Sensor scope is final for v2:** MAX30101 (PPG), LSM6DS3TR-C (6-axis), TMP117 (skin temp),
  SHT40 (ambient). **No EDA/GSR, no microphone, no ECG** — EDA is deferred to v3.
- **USB-C is kept** (standard horizontal SMD, not mid-mount). **Green PPG is mandatory**, which is
  why the TPS61099 4.7 V boost exists. The cell is permanently soldered; charging is supervised
  and off-wrist.
- Bare chips do not include what breakouts hid: the board supplies its own I2C pull-ups, and the
  MAX30101 needs **1.8 V VDD** (3.3 V destroys it) plus a separate VLED+ rail.

## Toolchain

```bash
# KiCad 10.0.5 CLI — the authority when tools disagree
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli

# PlatformIO (v1 firmware only) — venv, never pip install system-wide
source .venv/bin/activate && pio run -e <env>    # always name an env with -e
```

Verification commands for the PCB live in `pcb/README.md`. Design-review analyzers are the
`kicad-happy` skills (`kicad`, `bom`, `datasheets`, `emc`, `jlcpcb`, `lcsc`, ...) — use
`kicad-happy/skills/kicad/scripts/analyze_*.py` rather than writing ad-hoc parsers. PDFs are
readable (`poppler` installed).

## Repo layout

| Path | Contents |
|---|---|
| `pcb/` | **The live KiCad project.** Schematic frozen, layout in progress. Authority: its `README.md` |
| `parts/` | Per-part evidence folders (`README.md` + `datasheet.pdf`). Authority: `V2_BOM.md` |
| `docs/` | `DESIGN_HISTORY.md` — non-authoritative rationale |
| `enclosure/` | v2 placeholder; blocked on the final board outline |
| `ios/` | SwiftUI BLE companion app. **Cannot be built on this Mac** (Command Line Tools only, no Xcode) |
| `archive/v1/` | Frozen breakout prototype: firmware, data, docs, enclosure. Not authoritative |
| `data/` | Live capture target (gitignored). Still contains **zero** raw-IR wrist captures |
| `kicad-happy/` | Analysis plugin, gitignored nested repo, symlinked into `.claude/skills/` |

## Known open questions

These are unresolved and must not be silently decided:

- **Bench validation of the rails.** Every power number in this repo is a desk calculation or a
  behavioral simulation. ME6211 dropout/thermal and TPS61099 4V7 ripple and transient response were
  analysed on desk and in ngspice on 2026-09-17/18 and pass, but nothing has been measured.
- **Peer electrical review by a second person.** The topology review was one author's pass.
- **Physical enclosure fit.** CAD passes; nothing has been printed.
- **1.0 mm 4-layer availability, DFM and current sourcing** must be confirmed in the JLCPCB cart
  before ordering. This is a one-time cart pass, not a recurring check.
- Wrist-PPG wavelength has **never been measured**. The diagnostic exists
  (`archive/v1/src/max30102_raw_ir/`) and has never been run. It is a post-arrival firmware
  experiment, not an ordering gate.

**Closed 2026-09-18 — do not re-open:** the battery (EEMB LP502030-PCM already in hand, 250 mA max
charge rating covers the planned 100 mA; **do not source a substitute**) and the 4V7 green-rail
margin (R10 changed 270k -> 249k with user approval, implemented and re-verified).
