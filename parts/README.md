# Parts — BOM research for the miniaturized board

One folder per part. **`CLAUDE.md` holds decisions; this folder holds evidence.**

## Conventions

| Rule | Why |
|---|---|
| Folder = **lowercase generic chip name** (`max30101`, not `MAX30101EFD+T`) | Stable across packaging suffixes; no `+` or spaces to break globs and shell paths |
| Datasheet is always **`datasheet.pdf`** | Any agent can find it by pattern without listing the directory |
| Each folder has a **`README.md` with the specs extracted** | Answers the common questions without opening a 114-page PDF |
| **Record the LCSC number (`Cxxxxxx`)** + Basic/Extended + stock + date checked | Decides whether the part is buildable at all |
| Superseded docs keep a `_SUPERSEDED` suffix | Never silently mix two revisions |

Requires `poppler` (`brew install poppler`) for PDFs to be machine-readable. Already installed.

## Sensors + MCU — selected

| Folder | Part | LCSC | Supply | I²C addr | Package |
|---|---|---|---|---|---|
| `max30101/` | MAX30101EFD+T | C2859066 | **1.8 V VDD + 3.1–5.0 V VLED** | 0x57 | 5.6 × 3.3 × 1.55 |
| `tmp117/` | TMP117AIDRVR | C699536 | 1.7–5.5 V | 0x48 | 2.0 × 2.0 × 0.75 |
| `lsm6ds3tr-c/` | LSM6DS3TR-C | C967633 | 1.71–3.6 V | 0x6A/0x6B | 2.5 × 3.0 × 0.83 |
| `sht40/` | SHT40-AD1B-R3 | C2848306 | 1.08–3.6 V | 0x44 | DFN-4 1.5 × 1.5 × 0.5 |
| `esp32-c3-mini-1/` | ESP32-C3-MINI-1-N4 | C2838502 | 3.0–3.6 V | — | 13.2 × 16.6 × 2.4 |

No address conflicts. **Only the MAX30101 needs a non-3.3 V rail.**

`mcp6002/` also exists on disk (EDA front end) but is **CUT FROM V2** — deferred to v3.

## Power tree

Three rails, driven by the MAX30101's 1.8 V VDD requirement:

```
LiPo 3.0–4.2 V ──┬── VBAT ──────────────► MAX30101 VLED+ (3.1–5.0 V, 200 mA peak)
                 │
                 ├── 3.3 V LDO ── +3V3 ──► ESP32-C3-MINI-1, TMP117, SHT40,
                 │                          LSM6DS3TR-C, I²C pull-ups, MCP6002
                 │
                 └── 1.8 V LDO ── +1V8 ──► MAX30101 VDD  (abs max 2.2 V)
```

`VBAT` feeds VLED+ directly — no boost needed, since 3.0–4.2 V sits inside the 3.1–5.0 V window.
The 1.8 V LDO can be fed from `+3V3` (tiny load: 20 mA max).

**Do not cross these rails.** 3.3 V on MAX30101 VDD destroys the part.

## I²C bus — one shared bus, four devices

| Device | Address | Address set by |
|---|---|---|
| SHT40 | 0x44 | fixed (`AD1B` variant) |
| TMP117 | 0x48 | ADD0 → GND |
| MAX30101 | 0x57 | fixed |
| LSM6DS3TR-C | 0x6A | SDO/SA0 → GND |

**The bus needs exactly one pair of pull-ups: 2 × 4.7 kΩ to `+3V3` on SDA and SCL.** Every prototype
breakout carried its own; the bare chips do not. MAX30101 I/O tolerates 6 V despite its 1.8 V VDD,
so no level shifting is required.

### Pins that must not float

A bare chip does not strap itself. These break the board silently if left unconnected:

| Part | Pin | Tie to |
|---|---|---|
| LSM6DS3TR-C | CS (12) | `+3V3` — else it comes up in SPI mode |
| LSM6DS3TR-C | SDx (2), SCx (3) | `+3V3` or `GND` |
| LSM6DS3TR-C | SDO/SA0 (1) | `GND` |
| TMP117 | ADD0 (4) | `GND` |
| ESP32-C3-MINI-1 | EN (8) | 10 kΩ → `+3V3` + 1 µF → `GND` |
| ESP32-C3-MINI-1 | IO8 (22) | 10 kΩ → `+3V3` |

## Support circuitry — NOT YET SELECTED

Blocks still needing LCSC part numbers before a schematic can be built:

| Block | Parts | Notes |
|---|---|---|
| 3.3 V LDO | 1 IC + 2 caps | Must have low dropout — the LiPo falls to ~3.0 V at empty. `ME6211C33M5G-N` (LCSC C82942, SOT-23-5, 500 mA, 120 mV @ 100 mA) is a candidate, **not verified as Basic/in-stock** |
| 1.8 V LDO | 1 IC + 2 caps | Load is only ~20 mA, so an 80 mA part is ample. `XC6206P182MR` class. Feed from `+3V3` |
| LiPo charger | 1 IC + program resistor + caps | MCP73831 / TP4054 class. Program resistor sets charge current — size it to ≤0.5 C of the 250 mAh cell |
| USB-C | Receptacle + **2 × 5.1 kΩ CC resistors** + ESD array | The CC resistors are mandatory: without them a USB-C source delivers no power at all. `USBLC6-2SC6` (LCSC C7519, **Extended**) for ESD. **Mid-mount part not yet identified** — the common right-angle parts are not mid-mount |
| ~~EDA front end~~ | ~~Op-amp + R/C network~~ | **CUT FROM V2 (user, 2026-09-15)** — deferred to v3. `mcp6002/` kept as research, not on the BOM |
| Passives | ~8 decoupling caps, 2 × 4.7 kΩ I²C pull-ups, EN RC, IO8 pull-up | Per-part values are in each folder's "required externals" table |

Rough count: **~25–30 support parts.** Most are JLCPCB Basic with no setup fee, but each is a chance
to get something wrong. No RTC needed — the `#now` BLE clock anchor plus phone time covers timestamps.

**Open before a schematic can be drawn:**
1. ~~EDA in or out?~~ **RESOLVED 2026-09-15 — out for v2.**
2. ~~Mid-mount USB-C.~~ **RESOLVED 2026-09-15 — mid-mount not needed.** The top side already stacks
   MINI-1 (2.4 mm) + LiPo (4.0 mm) = 6.4 mm, so a standard 3.2 mm horizontal SMD receptacle fits
   inside that envelope and adds zero total height. Mid-mount was solving a problem this board
   does not have.
3. **Wrist PPG wavelength** — gates MAX30101 vs MAX30102, the largest BOM line. Still open.

## Support circuitry

`_support/` — the LDOs, charger, USB-C and passives the XIAO and breakouts were providing.
`_support/DECISIONS.md` records why each was chosen and what is still open.

## Ruled out

| Part | Why |
|---|---|
| BMI160 | **Consign-only, stock 0** at JLCPCB (Bosch EOL) → LSM6DS3TR-C |
| MAX30205 | Pre-order only, stock 0, ~10 day lead → TMP117 |
| MAX30102 | Identical package/address/library to MAX30101 but no green LED |
| MLX90614 | Non-contact IR (wrong measurement), 4.1 mm tall, unit suspected dead |

## Reference docs

`_reference/` — Espressif hardware design guidelines, DevKitM-1 reference schematic, chip datasheet.
