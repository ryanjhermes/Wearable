# Support-circuitry decisions — why each part, and how confident

Written for a future agent drawing the schematic. **Read this before substituting anything.**

The governing objective: **a v2 board that works on the first fab run.** That biases every choice
below toward *widely-used parts with well-tested reference circuits*, not toward optimal parts.
A boring part with ten thousand hobbyist boards behind it is lower-risk than a better part nobody
has debugged.

## How these were selected — and the limits of that

| What I did | What I did NOT do |
|---|---|
| Derived hard requirements from the sensor datasheets (rails, dropout, currents) | A systematic parametric search across all LCSC LDOs/chargers |
| Picked parts that are ubiquitous in the LCSC/JLCPCB ecosystem, so reference circuits and footprints exist | Compare efficiency, noise, or thermal performance between candidates |
| Verified pinouts against datasheets where a mistake would be silent (ME6211, TP4054) | Verify Basic-vs-Extended or live stock — JLCPCB renders these in JavaScript and they did not extract |
| Chose smaller/simpler packages over higher-spec ones | Optimise for cost or for battery life |

**Consequence: treat every row as "sound and conventional", not "provably optimal".** The one thing
that must still be checked by a human is Basic/Extended + stock, in a live JLCPCB cart.

## Per-part rationale

### 3.3 V LDO — ME6211C33M5G-N (C82942)

The requirement is **dropout**, not current. A LiPo falls 4.2 → 3.0 V; an LDO cannot boost, so the
regulator stops regulating once Vin < 3.3 V + dropout. At 120 mV this part holds regulation down to
~3.42 V. A generic AMS1117 (1.1 V dropout) would need 4.4 V in and **would never regulate on a
single LiPo at all** — a classic beginner failure.

500 mA is oversized for a ~70 mA load; that is deliberate headroom for the C3's ~350 mA TX peaks.

⚠️ Do not substitute the **ME6211H** — the C and H series differ in enable polarity.

### 1.8 V LDO — XC6206P182MR (C21659)

Exists solely because **MAX30101 VDD absolute max is 2.2 V** (datasheet-verified). Not a
preference — 3.3 V destroys the sensor.

80 mA against a 20 mA load, and 1 µA quiescent current, which matters on a 250 mAh cell. Fed from
**+3V3** rather than VBAT: less dropout stress, and the input is already filtered.

### LiPo charger — TP4054 (C32574)

Chosen over the far more common **TP4056 (C16581)** on size and current class: TP4056 is ESOP-8 with
a thermal pad and targets 1 A, which is 4 C on a 250 mAh cell. TP4054 is SOT-23-5 and sets current
with one resistor.

**R_PROG = 10 kΩ 1% → 100 mA (0.4 C).** Datasheet equation `I = 1000/R_PROG`, verified.

### USB-C — TYPE-C-31-M-12 (C165948) + 2 × 5.1 kΩ + USBLC6-2SC6 (C7519)

Standard horizontal SMD, **not mid-mount**. Mid-mount needs a routed board cutout and was never
sourced; it also solves a problem this board does not have, since the top side already stacks
MINI-1 (2.4 mm) + LiPo (4.0 mm) = 6.4 mm and a 3.2 mm receptacle fits inside that envelope.

The 5.1 kΩ CC resistors are not optional — without them a USB-C source supplies no power.

## DECISION REQUIRED — charge path

**Problem.** The 3.3 V LDO input is `VBAT`, and there is no power switch, so with USB connected the
charger refills the cell *while the system draws 50–70 mA from the same node*. Two consequences:

1. **Termination never fires.** TP4054 terminates at ~1/10 of programmed current = 10 mA. System
   draw keeps the node above that indefinitely, so the charger sits in CV holding 4.2 V forever.
2. **Charging is very slow.** 100 mA charge − 60 mA load ≈ 40 mA into the cell → 6+ hours for
   250 mAh.

Given this project's history of thermal faults and one suspected charge-IC failure
(`archive/v1/docs/hardware_debug_log.md`), a charger that never stops is a poor fit.

### Options

| | Approach | Parts | Risk |
|---|---|---|---|
| **A** | Do nothing | 0 | Slow charge, no termination, cell held at float. **Rejected** |
| **B (recommended)** | **VBUS-sense divider → GPIO; firmware deep-sleeps while charging** | **2 resistors** | Deep sleep is ~5 µA, far below the 10 mA threshold, so termination works normally. Failure mode is *soft* — if firmware misbehaves you get option A back, recoverable by reflash, **not a respin** |
| C | Discrete P-FET load-share | ~4 | Correct in hardware, but a discrete power-path arrangement is easy to get subtly backwards |
| D | Integrated power-path charger — **BQ24074RGTR, LCSC C54313**, ~$1.19, in stock | 1 IC + ~5 | Most correct. But VQFN-16 with a thermal pad, three programming resistors (ISET/ILIM/TS), and a mis-wired QFN **is** a respin |

### Recommendation: B

Two resistors, and it is the only option whose failure mode is recoverable in firmware rather than
in copper. It also gives the device something it wants anyway — knowledge of whether it is plugged
in. **D (BQ24074, C54313) is the documented upgrade path** if a future revision wants power-path
guaranteed in hardware.

Note this couples to an open item: there is **no power switch**, so the device draws current
whenever the battery is connected. Deep-sleep-on-charge does not fix standby drain in a drawer.
