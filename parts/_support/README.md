# Support circuitry — candidate BOM (v2 fab board)

> **Why each part was chosen, and the open charge-path decision: [`DECISIONS.md`](DECISIONS.md).**

The parts the XIAO and the breakouts were silently providing. **EDA is cut from v2**, so this is the
complete support list.

**Verification status is marked per row. Nothing here is confirmed Basic/in-stock.** JLCPCB's part
pages render library type and stock via JavaScript and did not extract reliably on 2026-09-15 — the
LCSC numbers below are real and the parts exist, but *confirm Basic-vs-Extended and stock in your own
JLCPCB cart before ordering*. Extended parts carry a per-part setup fee; that changes cost, not
feasibility.

## ICs and connector

| Block | Candidate | LCSC | Package | Status |
|---|---|---|---|---|
| 3.3 V LDO | ME6211C33M5G-N | **C82942** | SOT-23-5 | → `../me6211/`. 500 mA, **120 mV dropout**. **CE pin must be tied high** or the board is silently dead |
| 1.8 V LDO | XC6206P182MR | **C21659** (Torex) / **C347373** (UMW) | SOT-23-3 | 80 mA, 1 µA Iq; load is only 20 mA. Feed from **+3V3**. ⚠️ **Pinout is 1=VSS, 2=VIN, 3=VOUT** — ground on pin 1, not the layout you expect. Verify before routing |
| LiPo charger | TP4054-42-SOT25R | **C32574** | SOT-23-5 | → `../tp4054/` (datasheet held). **R_PROG = 10 kΩ 1% → 100 mA (0.4 C)**. Chosen over TP4056 (C16581), which is ESOP-8 with a thermal pad and 1 A class |
| USB-C receptacle | TYPE-C-31-M-12 | **C165948** | 16-pin horizontal SMD | **Standard, not mid-mount** — see height note below |
| USB ESD | USBLC6-2SC6 | **C7519** | SOT-23-6 | Confirmed **Extended** |

## Passives

All 0402 unless noted. Values come from each part folder's "required externals" table.

| Qty | Part | Net | Purpose |
|---|---|---|---|
| 2 | 5.1 kΩ | CC1→GND, CC2→GND | **Mandatory.** Tells the USB-C *source* this is a sink. Without them: no power at all |
| 2 | 4.7 kΩ | SDA→3V3, SCL→3V3 | Whole-bus I²C pull-ups. The breakouts each had their own |
| 1 | 10 kΩ | EN→3V3 | EN must not float |
| 1 | 1 µF | EN→GND | Power-on reset delay |
| 1 | 10 kΩ | IO8→3V3 | **Strapping pin — module will not boot reliably without it** |
| 1 | **10 kΩ, 1%** | PROG→GND | Sets TP4054 charge current: I = 1000/R → **100 mA (0.4 C)**. Datasheet requires 1% |
| 2 | 1 MΩ / 1 MΩ | VBAT→ADC→GND | Battery sense divider. High value to minimise idle drain |
| 1 | 10 µF | 3V3→GND | Module bulk — C3 draws ~350 mA TX peaks |
| ~10 | 0.1 µF / 1 µF / 4.7 µF | per part | Decoupling. **The 4.7 µF on MAX30101 VLED+ is not optional** |

## Height — mid-mount is NOT needed

The top side already stacks **MINI-1 (2.4 mm) + LiPo (4.0 mm) = 6.4 mm**. A standard horizontal SMD
USB-C is ~3.2 mm, which fits *inside* that envelope. It costs floorplan area at one edge, not height.

Mid-mount receptacles need a routed board cutout and were never sourced. Dropped — they solved a
problem this board does not have.

## Why USB-C stays even though it is "not essential"

Removing the connector does not remove the charger — it relocates it. A sealed wristband charged
externally needs either exposed contacts (corrode against sweat, short against keys) or a dock, which
is a second thing to design and fab. And you lose single-cable flashing on the board you will reflash
many times during bring-up. Keeping USB-C is the *lower*-effort path, not the higher one.

## Not needed

| | Why |
|---|---|
| USB-UART bridge (CH340/CP2102) | ESP32-C3 has **native USB** on IO18/IO19 |
| DTR/RTS auto-reset transistors | Same reason |
| RTC chip | The `#now` BLE clock anchor + phone time cover timestamps |
| Level shifters | MAX30101 I/O tolerates 6 V despite its 1.8 V VDD |
| Boost converter | VBAT 3.0–4.2 V already sits inside MAX30101 VLED+ 3.1–5.0 V |

## Folder convention

A support part gets its own folder **only when getting it wrong is silent or dangerous** — otherwise
it stays a row in this table. Two qualify so far:

| Folder | Why it earned one |
|---|---|
| `../tp4054/` | The PROG resistor sets charge current into a LiPo. Wrong value is a safety issue |
| `../me6211/` | The CE pin must be tied high; floating = no output, no symptom. **Datasheet still needs manual download** |

Everything else here is copy-the-reference-circuit: 2-terminal passives, a 6-pin ESD array, a
connector. A folder per 5.1 kΩ resistor would be noise.

## Open

- **BOOT (IO9) + RESET (EN) test pads.** Free, but must be drawn. With no LEDs, no buttons and a
  sealed enclosure they are the only recovery path.
- Confirm Basic/Extended + stock for every row above in a live JLCPCB cart.
- No power switch is currently planned — the device runs whenever the battery is connected.
