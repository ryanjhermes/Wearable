# V2 fab PCB — authoritative parts and power plan

**Status:** approved to begin schematic capture, updated 2026-09-16. This is the authoritative source
for v2 part selection, required support circuitry, and unresolved hardware choices. It is **not**
approval to freeze the schematic, route, or order boards; the release gates below still apply.
Component folders hold the datasheet evidence. After a schematic exists, its generated BOM becomes
authoritative for reference designators and quantities; this file remains authoritative for part
rationale and approval status.

Read [`V2_HARDWARE_AUDIT.md`](V2_HARDWARE_AUDIT.md) for the feasibility, power-margin, storage,
mechanical, assembly, and bring-up risks that remain after part selection.

The goal is the smallest design likely to work on the first spin. Required decoupling, boot straps,
USB protection, battery protection, and charger load sharing are not treated as optional component
savings.

## Decisions already locked

- One double-sided fab PCB; no stacked development board.
- ESP32-C3-MINI-1 module family, native USB, and a standard horizontal USB-C receptacle. The stocked
  N4 is the capture baseline; N4X is Espressif's recommended, footprint-compatible order-time choice.
- MAX30101, TMP117, LSM6DS3TR-C, and SHT40 sensors on one I2C bus.
- No EDA/GSR, microphone, ECG, screen, status LED, RTC, USB-UART bridge, or user buttons in v2.
- Hardware USB/battery load sharing using one P-channel MOSFET, one Schottky diode, and one gate
  resistor. Firmware-only charge management is rejected.
- 100 mA nominal charge current from a TP4054 and 10 kOhm 1% program resistor.
- Green PPG is mandatory. The TPS61099 4.7 V boost block is therefore populated in v2.
- The 250 mAh battery is permanently attached: direct-wire BAT+/BAT- solder pads plus strain relief,
  with no PCB connector.
- Charging is supervised prototype use only, off the wrist and never unattended.
- No mechanical power switch. Firmware uses deep sleep; a protected battery supplies last-resort
  over-discharge protection.

## Remaining user inputs before schematic freeze

Only the battery evidence below is still open. Retention, the module order code, and the
debug-LED question were all closed on 2026-09-16 (see the JLCPCB verification section).

### Battery evidence

The user owns several 250 mAh cells with pigtails. Before schematic freeze, obtain a purchase link
or clear photos of both faces, label, wire colors, connector, and any small protection PCB under the
wrapper. Confirm polarity, dimensions including the protection-board bulge, built-in protection, and
that the cell permits at least 100 mA charging (0.4 C). Do not assume connector polarity from wire
color alone; small LiPo pigtails are not universally wired the same way.

### Offline data-retention requirement — RESOLVED 2026-09-16

**Decision (user): no external storage in v2. Log per-second summaries to internal flash only.**
A 32-byte summary each second is about 691 kB over six hours and fits the N4's 4 MB alongside
firmware. Full-session raw PPG/motion capture is therefore only possible while the phone is
connected and streaming. External QSPI flash and a microSD socket were both considered and
rejected: the former costs four GPIO on an already-constrained C3, the latter breaks the
32 x 24 mm envelope. Adding raw-session capture later is a board revision.

## Power tree

```text
USB-C VBUS -----------------------------------------------------> TP4054 VCC
     |
     +-- SS14 Schottky --> VSYS --> ME6211 3.3 V --> 3V3 loads
                              |                     |
                              |                     +--> XC6206 1.8 V --> MAX30101 VDD
                              |
                              +--> TPS61099 4.7 V --> MAX30101 VLED+
                                   EN <-- GPIO10 / PPG_PWR_EN
                                         + 100 kOhm to GND

TP4054 BAT --> BAT+ --> protected 1-cell LiPo
                 |
                 +-- AO3401A drain
                     AO3401A source --> VSYS
                     AO3401A gate --> VBUS and 100 kOhm --> GND
```

The AO3401A is intentionally reversed relative to the usual high-side-switch orientation: drain to
BAT+, source to VSYS. With USB absent, its body diode starts VSYS and the low gate turns the MOSFET
fully on. With USB present, the SS14 powers VSYS and VBUS raises the gate, isolating the battery from
the system load. The charger therefore measures battery current rather than battery-plus-system
current and can terminate correctly. This follows Microchip AN1149's minimal load-sharing topology.

The ME6211 is an LDO, not a buck-boost regulator. It holds 3.3 V only while VSYS is roughly 3.42 V or
higher. This deliberate simplification leaves some cell capacity unused. Firmware should enter deep
sleep around 3.45 V battery voltage, with calibrated threshold and hysteresis, rather than attempt to
operate the MCU below its guaranteed supply range.

The MAX30101 recommends VDD before VLED+ at power-up. GPIO10 therefore controls TPS61099 EN as
`PPG_PWR_EN`; a 100 kOhm pulldown keeps the boost disabled during reset. Firmware must hold the net
low through boot and enable it only after 1V8 is established. TPS61099 true shutdown disconnects its
output, so this also removes the LED rail's idle load. Do not tie EN directly to VSYS.

## Mandatory populated parts — base design

**JLCPCB assembly availability VERIFIED 2026-09-16** against JLCPCB's own SMT parts API (not LCSC):
all 25 BOM line items are in the assembly library, all `source: shop` (JLCPCB-stocked, not consign),
all with non-zero stock. 13 Extended types, 12 Basic. See the verification section at the end of this
file for the recorded stock and library class. Distributor state still changes; recheck in the cart
at order time.

| Qty | Function | Approved part | LCSC | Package | Critical note |
|---:|---|---|---|---|---|
| 1 | MCU/radio | ESP32-C3-MINI-1-N4 | C2838502 | module, 13.2 x 16.6 mm | Observe antenna keepout; battery cannot overlap antenna |
| 1 | PPG | MAX30101EFD+T | C2859066 | OLGA-14 | VDD is 1.8 V; green VLED needs guaranteed 4.5-5.5 V |
| 1 | skin temperature | TMP117AIDRVR | C699536 | WSON-6 | ADD0 to ground. **TI says do NOT solder the thermal pad on a rigid PCB** — the +/-0.1 C accuracy spec assumes it unsoldered; soldering trades accuracy for response time. See the footprint audit in `../pcb/README.md` |
| 1 | IMU | LSM6DS3TR-C | C967633 | LGA-14 | CS high; SA0, SDx, and SCx must not float |
| 1 | ambient temperature/humidity | SHT40-AD1B-R3 | C2848306 | DFN-4 | Vent to ambient air; keep away from heat sources |
| 1 | 3.3 V LDO | ME6211C33M5G-N | C82942 | SOT-23-5 | CE to VIN; do not substitute active-low ME6211H |
| 1 | 1.8 V LDO | XC6206P182MR | C21659 | SOT-23-3 | **Pin 1 GND, pin 2 VOUT, pin 3 VIN** |
| 1 | LiPo charger | TP4054-42-SOT25R | C32574 | SOT-23-5 | Pin 1 CHRG, 2 GND, 3 BAT, 4 VCC, 5 PROG |
| 1 | USB ESD array | USBLC6-2SC6 | C7519 | SOT-23-6 | Place next to connector, before series resistors |
| 1 | USB-C receptacle | TYPE-C-31-M-12 | C165948 | horizontal SMD, 16-pin | Use the exact library footprint and mechanical pegs |
| 1 | battery/USB load-share MOSFET | AO3401A | C15127 | SOT-23 | Pin 1 gate, 2 source, 3 drain; source goes to VSYS |
| 1 | USB-to-system diode | SS14 | C2480 | SMA | Anode VBUS, cathode VSYS; stripe/cathode toward VSYS |

The core PCB before the green supply block has **12 non-passives + 14 resistors + 17 capacitors = 43
populated components**. Green is mandatory, so the complete planned v2 count is **51**, not counting
the battery or bare test pads. This count is a planning check, not a substitute for a BOM generated
from the schematic.

## Mandatory passives — base design

| Qty | Value / rating | Approved part | LCSC | Uses |
|---:|---|---|---|---|
| 8 | 100 nF, 16 V, X7R, 0402 | Samsung CL05B104KO5NNNC | C1525 | ESP bypass; MAX VDD/VLED; TMP117; two LSM rails; SHT40; battery ADC |
| 6 | 1 uF, 25 V, X5R, 0402 | Samsung CL05A105KA5NQNC | C52923 | ESP EN; MAX VDD bulk; ME6211 input/output; XC6206 input/output |
| 2 | 4.7 uF, 16 V, X5R, 0603 | Samsung CL10A475KO8NNNC | C19666 | TP4054 VCC and MAX30101 local VLED bulk |
| 1 | 10 uF, 10 V, X5R, 0603 | Samsung CL10A106KP8NNNC | C19702 | ESP 3.3 V bulk |
| 2 | 22 Ohm, 1%, 0402 | UNI-ROYAL 0402WGF220JTCE | C25092 | USB D- and D+ series resistors |
| 2 | 4.7 kOhm, 1%, 0402 | UNI-ROYAL 0402WGF4701TCE | C25900 | One shared I2C pull-up pair |
| 2 | 5.1 kOhm, 1%, 0402 | UNI-ROYAL 0402WGF5101TCE | C25905 | USB-C CC1 and CC2 to ground |
| 5 | 10 kOhm, 1%, 0402 | UNI-ROYAL 0402WGF1002TCE | C25744 | EN, GPIO2/8/9 pull-ups, and TP4054 PROG |
| 1 | 100 kOhm, 1%, 0402 | UNI-ROYAL 0402WGF1003TCE | C25741 | AO3401A gate to ground |
| 2 | 1 MOhm, 1%, 0402 | UNI-ROYAL 0402WGF1004TCE | C26083 | BAT-to-ADC divider |

Use GPIO3/ADC1_CH3 for battery sense. The center of the 1 MOhm/1 MOhm divider
goes to the ADC and gets the listed 100 nF capacitor to ground. This halves battery voltage and draws
about 2.1 uA at full charge.

No TP4054 BAT capacitor is populated because the cell is permanently connected. Its VCC pin still
gets 4.7 uF close to the IC. Changing to a removable battery requires revisiting this detail from the
charger datasheet.

## Mandatory 4.7 V green-LED block

MAX30101 specifies VLED+ at 3.1-5.0 V for red/IR but **4.5-5.5 V for green**. A one-cell LiPo ranges
from about 3.0 to 4.2 V and therefore cannot guarantee green operation. Selecting a three-color
sensor does not remove this electrical requirement.

Approved 4.7 V boost:

| Qty | Function/value | Approved part | LCSC | Package |
|---:|---|---|---|---|
| 1 | adjustable boost converter | TPS61099DRVR | C2842395 | WSON-6, 2 x 2 mm |
| 1 | 2.2 uH inductor, 1.5 A saturation | Taiyo Yuden MAKK2016T2R2M | C92923 | 2.0 x 1.6 mm |
| 1 | 1 MOhm, 1%, 0402, VOUT-to-FB | UNI-ROYAL 0402WGF1004TCE | C26083 | 0402 |
| 1 | 270 kOhm, 1%, 0402, FB-to-GND | UNI-ROYAL 0402WGF2703TCE | C25770 | 0402 |
| 1 | 100 kOhm, 1%, 0402, EN-to-GND | UNI-ROYAL 0402WGF1003TCE | C25741 | 0402 |
| 3 | 10 uF, 10 V, X5R, 0603 | Samsung CL10A106KP8NNNC | C19702 | one input, two output |

The divider gives approximately 4.704 V: `VOUT = 1 V x (1 MOhm + 270 kOhm) / 270 kOhm`. This sits
inside the red/IR and green VLED ranges under the published PWM feedback-reference limits, but rail
margin still requires bench validation. Connect EN to GPIO10 (`PPG_PWR_EN`) and fit the listed
100 kOhm pulldown. Pinout is 1 GND, 2 VOUT, 3 FB, 4 EN, 5 SW, 6 VIN, exposed pad GND. Keep the VIN
capacitor/inductor/SW loop and VOUT capacitors extremely short.
The MAX30101 still needs its local 4.7 uF + 100 nF VLED capacitors.

The MAX30101 datasheet guarantees its 4.5-5.5 V green-LED supply range only at 25 C. The 4.704 V rail
meets that published condition, but green performance over actual skin/ambient temperature must be
validated on hardware; it is not a datasheet guarantee across the sensor's full temperature range.

This block adds **8 populated components**, taking the planned PCB total from 43 to **51**. It is not
DNP or optional in v2. Removing it would be a later red/IR-only design change.

## Required schematic connections and test pads

- Expose test pads for GND, 3V3, **1V8**, **4V7 (VLED+)**, BAT+, VSYS, EN/RESET, GPIO9/BOOT,
  USB D-/D+, SDA, and SCL. The 1V8 and 4V7 pads were added 2026-09-16 when the debug LED was
  declined: they are the two hardest rails to verify and the two most likely to be wrong on a first
  spin, and with no LED the only bring-up diagnostics are native-USB serial, these pads, and BLE.
- Pull GPIO2, GPIO8, and GPIO9 up with 10 kOhm. Do not hang sensors on strapping pins.
- Use GPIO10 for `PPG_PWR_EN`; add the 100 kOhm EN pulldown and do not place it on a strapping pin.
- Route GPIO9 and EN to accessible recovery pads. To force download mode: GPIO9 low while EN resets.
- Put 22 Ohm resistors in series with D-/D+ close to the ESP32 module. Reserve optional DNP shunt-cap
  footprints only if routing space allows; do not populate without signal-integrity evidence.
- Tie USB-C shield tabs to ground with the exact connector's mechanical pads.
- Leave MAX30101 INT and TMP117 ALERT unconnected and poll them; this avoids two pull-ups. Route
  LSM6DS3TR-C INT1 directly to a GPIO if wake-on-motion is needed.
- Use solder pads and mechanical strain relief for the recommended two-wire battery connection.
- Specify the MAX30101 no-connect pads exactly as its datasheet requires for mechanical mounting.

## Parts intentionally not included

| Part/block | Reason |
|---|---|
| MCP6002 / EDA front end | Explicitly deferred to v3; its folder is archival research only |
| MAX30101 INT pull-up | FIFO can be polled, saving a resistor and GPIO |
| TMP117 ALERT pull-up | Temperature can be polled |
| USB-UART bridge and auto-reset transistors | ESP32-C3 has native USB |
| RTC | Phone/BLE time anchor covers timestamps |
| I2C level shifter | MAX30101 SDA/SCL tolerate the 3.3 V bus |
| LEDs and buttons | Explicitly cut. Re-confirmed 2026-09-16: a DNP 0402 LED footprint was offered and **declined** by the user. Bring-up visibility comes from native-USB serial (the C3 enumerates whenever the chip runs, no UART bridge), the rail test pads including the new 1V8/4V7, and BLE data reaching the iOS app. Note what BLE data does **not** validate: 4V7 rail margin, TMP117 skin accuracy, SHT40 venting, or charge termination |
| External QSPI flash / microSD | Declined 2026-09-16 with the summaries-only retention decision |
| Power switch | Omitted for space and sealing; use deep sleep |
| 3.3 V buck-boost | Avoids several parts; accepted tradeoff is reduced usable battery capacity |
| Battery connector | Omitted; the protected cell wires are permanently soldered to marked pads with strain relief |

## Schematic and layout status — 2026-09-16

The schematic at [`../pcb/`](../pcb/) (KiCad 10.0.5) is frozen for layout purposes. It is ERC-clean
with 0 errors and 2 understood warnings, and its generated BOM reconciles exactly to the 51
populated components planned here, per-value quantities included. KiCad schematic-parity DRC reports
0 parity issues and 0 footprint errors. Layout has started with 64 footprints loaded, but nothing is
intentionally positioned or routed and no board outline exists. Independent electrical review and
power-budget/thermal review remain open; the design is not ready to order.

Two real defects were caught during capture and are worth recording because both would have killed
a first spin silently: the IMU ground ties shorted the I2C bus to ground, and `BAT+` existed as two
unconnected nets so the cell never reached the charger while the load-share gate floated off VBUS.

**Footprint audit COMPLETE 2026-09-16 — release gate #5 is closed for pin maps, partially open for
land patterns.** All 12 IC/connector/discrete pin maps were verified pad-by-pad against the
manufacturer datasheets with **zero errors**, and all 16 footprints have courtyards that enclose
their pads. Two land patterns remain unverifiable because the vendor does not publish them in the
datasheet: **MAX30101** (Maxim land pattern 90-0602, external) and **MAKK2016** (no datasheet at
all). One decision was surfaced and is open: whether to solder the TMP117 thermal pad. Full
findings, including two layout rules extracted from the datasheets, are in `../pcb/README.md`.

**Footprints complete 2026-09-16.** The three parts with no stock-library footprint were resolved:
the ESP32-C3-MINI-1 and MAKK2016T2R2M were imported from LCSC with `easyeda2kicad`, and the battery
solder pads were hand-authored. Every schematic symbol now resolves to a footprint and ERC reports
0 errors with 2 understood warnings. The module footprint was checked pad by pad against Espressif
Figure 11-1 and its 5.4 mm antenna keepout is now marked in the footprint itself. The inductor
footprint carried a courtyard smaller than its own pads, which was rebuilt.

**One evidence gap remains:** MAKK2016T2R2M has no dimensioned manufacturer land-pattern drawing on
file. Its electrical ratings were confirmed, but its imported land pattern remains unverified.
`check_parts.py` reports the missing manufacturer PDF as the project's only evidence gap.

## Layout approval versus release approval

The schematic is captured and frozen for layout purposes. The component classes, primary order
codes, pinouts, rail topology, I2C addresses, USB connections, boot straps, and mandatory support
parts are sufficiently defined to floorplan and route the board. Raise any suspected schematic
change instead of editing it during layout.

The design is **not ready to order** until the remaining items below are closed. Provisional layout
may continue, but independent electrical review is still required before fabrication.

## Before ordering or release

1. Verify the exact battery evidence listed above; green, permanent attachment, and supervised
   charging are already locked.
2. ~~Lock the offline data-retention requirement.~~ **CLOSED 2026-09-16: per-second summaries use
   internal flash; full raw sessions require a connected phone.**
3. ~~Lock the exact module order code.~~ **CLOSED 2026-09-16: ESP32-C3-MINI-1-N4 (C2838502).**
   Espressif recommends N4X, but JLCPCB lists N4X (C9900263492) at **0 stock** while N4 shows 16,000
   in stock. N4 is therefore the only machine-placeable option at this assembler. It is NRND, not
   discontinued, and remains valid for a prototype spin. If a future spin needs N4X, the land pattern
   is identical but assembly sourcing must be rechecked and chip revision v1.1 SDK support confirmed.
4. **Pinout/datasheet audit complete; independent electrical peer review remains open.** Recheck the
   load-share topology and power-budget assumptions before fabrication.
5. **Footprint pin-map audit complete.** MAX30101 and MAKK2016 vendor land-pattern evidence remains
   unavailable; treat those footprints as documented residual risks.
6. **ERC and BOM reconciliation complete:** 0 errors, 2 understood warnings, 51 populated parts.
7. Confirm current stock, assembly class, lifecycle, and price in the JLCPCB cart. Use exact order
   codes; do not allow “similar” substitutions for regulators, MOSFETs, or connectors.
8. Have another electrical review and review antenna, optical, thermal, USB, and switching-regulator
   placement before fabrication.

## Primary design references

- Microchip, *AN1149: Designing a Li-Ion Battery Charger and Load Sharing System With Microchip's
  Stand-Alone Li-Ion Battery Charge Management Controller*: the
  discrete P-MOSF/Schottky load-sharing principle used here is in the load-sharing discussion.
  <https://ww1.microchip.com/downloads/en/appnotes/01149c.pdf>
- Texas Instruments, *TPS61099 datasheet*: output capability, optical-heart-rate application,
  external values, and layout. <https://www.ti.com/lit/ds/symlink/tps61099.pdf>
- Espressif, ESP32-C3 hardware design guidelines: local copy in
  [`_reference/esp32-c3_hardware_design_guidelines_en.pdf`](_reference/esp32-c3_hardware_design_guidelines_en.pdf).

## JLCPCB assembly availability — verified 2026-09-16

Queried JLCPCB's SMT assembly parts API directly. Every line is `source: shop`, meaning JLCPCB holds
the stock for assembly rather than requiring consignment. **All 25 line items are assemblable in one
JLCPCB fab + assembly order.**

| LCSC | Part | Library | Stock | $/1 |
|---|---|---|---:|---:|
| C2838502 | ESP32-C3-MINI-1-N4 | Extended | 16,000 | 3.84 |
| C2859066 | MAX30101EFD+T | Extended | 304 | 8.34 |
| C699536 | TMP117AIDRVR | Extended | 8,441 | 1.01 |
| C967633 | LSM6DS3TR-C | Extended | 25,216 | 1.52 |
| C2848306 | SHT40-AD1B-R3 | Extended | 10,878 | 1.75 |
| C82942 | ME6211C33M5G-N | Extended | 245,159 | 0.06 |
| C21659 | XC6206P182MR | Extended | 40,037 | 0.16 |
| C32574 | TP4054-42-SOT25R | Extended | 30,267 | 0.13 |
| C7519 | USBLC6-2SC6 | Extended | 32,785 | 0.17 |
| C165948 | TYPE-C-31-M-12 | Extended | 222,702 | 0.19 |
| C2842395 | TPS61099DRVR | Extended | 3,984 | 1.27 |
| C92923 | MAKK2016T2R2M 2.2 uH | Extended | 2,712 | 0.08 |
| C25770 | 270 kOhm 0402 1% | Extended | 139,988 | 0.004 |
| C15127 | AO3401A | Basic | 469,801 | 0.09 |
| C2480 | SS14 | Basic | 1,096,775 | 0.02 |
| C1525 / C52923 / C19666 / C19702 | 100 nF / 1 uF / 4.7 uF / 10 uF | Basic | 3.3M-30.7M | <=0.03 |
| C25092 / C25900 / C25905 / C25744 / C25741 / C26083 | 22R / 4.7k / 5.1k / 10k / 100k / 1M | Basic | 2.6M-27.4M | <=0.003 |

Risks this surfaces, none of them blocking:

- **MAX30101 stock is 304**, roughly ten times lower than anything else on the board and by far the
  most expensive line. It is the one part where a delayed order could force a redesign. Nothing else
  is close to supply-constrained.
- **13 Extended part types.** JLCPCB bills a per-unique-Extended-type loading fee, historically
  about $3 each with some waived. That is roughly $39 and is the dominant non-recurring cost on a
  small prototype run. Confirm the actual figure in the cart.
- **C25770 is the only Extended passive.** No Basic 0402 1% 270 kOhm exists in the JLCPCB library, so
  restructuring the TPS61099 feedback divider to Basic-only values is not available without changing
  the target voltage. Keep it.
- **Two-sided SMT assembly is required** by the form factor (optical skin-side, MCU top-side). JLCPCB
  supports it but it is a second assembly setup with its own cost and process risk, and it constrains
  what may sit opposite tall or heavy parts. Quote both sides explicitly.
- **The battery is not part of the shipment.** Permanent-attach solder pads mean the cell is
  hand-soldered on arrival; JLCPCB ships a finished but unpowered board.
