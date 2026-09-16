# V2 fab PCB — authoritative parts and power plan

**Status:** pre-schematic review, updated 2026-09-16. This is the authoritative source for v2 part
selection, required support circuitry, and unresolved hardware choices. Component folders hold the
datasheet evidence. After a schematic exists, its generated BOM becomes authoritative for reference
designators and quantities; this file remains authoritative for part rationale and approval status.

Read [`V2_HARDWARE_AUDIT.md`](V2_HARDWARE_AUDIT.md) for the feasibility, power-margin, storage,
mechanical, assembly, and bring-up risks that remain after part selection.

The goal is the smallest design likely to work on the first spin. Required decoupling, boot straps,
USB protection, battery protection, and charger load sharing are not treated as optional component
savings.

## Decisions already locked

- One double-sided fab PCB; no stacked development board.
- ESP32-C3-MINI-1-N4 module, native USB, and a standard horizontal USB-C receptacle.
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

### Battery evidence

The user owns several 250 mAh cells with pigtails. Before schematic sign-off, obtain a purchase link
or clear photos of both faces, label, wire colors, connector, and any small protection PCB under the
wrapper. Confirm polarity, dimensions including the protection-board bulge, built-in protection, and
that the cell permits at least 100 mA charging (0.4 C). Do not assume connector polarity from wire
color alone; small LiPo pigtails are not universally wired the same way.

### Offline data-retention requirement

Decide what must survive when the phone is absent: per-second summaries, a limited raw-data window,
or a full raw session. The N4 module has 4 MB shared by firmware and logs. The audit's illustrative
three-wavelength PPG plus six-axis motion stream is about 5.4 MB/hour before timestamps and file
overhead, so multi-hour raw logging cannot fit in internal flash. Full-session raw capture requires
external storage or a different acquisition workflow; summaries can fit without changing hardware.

## Power tree

```text
USB-C VBUS -----------------------------------------------------> TP4054 VCC
     |
     +-- SS14 Schottky --> VSYS --> ME6211 3.3 V --> 3V3 loads
                              |                     |
                              |                     +--> XC6206 1.8 V --> MAX30101 VDD
                              |
                              +--> TPS61099 4.7 V --> MAX30101 VLED+

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

## Mandatory populated parts — base design

Order-time availability and JLCPCB Basic/Extended status must be rechecked. Distributor state can
change; the identifiers below were reviewed on 2026-09-15.

| Qty | Function | Approved part | LCSC | Package | Critical note |
|---:|---|---|---|---|---|
| 1 | MCU/radio | ESP32-C3-MINI-1-N4 | C2838502 | module, 13.2 x 16.6 mm | Observe antenna keepout; battery cannot overlap antenna |
| 1 | PPG | MAX30101EFD+T | C2859066 | OLGA-14 | VDD is 1.8 V; green VLED needs guaranteed 4.5-5.5 V |
| 1 | skin temperature | TMP117AIDRVR | C699536 | WSON-6 | ADD0 to ground; thermal placement determines measurement quality |
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
populated components**. Green is mandatory, so the complete planned v2 count is **50**, not counting
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
| 3 | 10 uF, 10 V, X5R, 0603 | Samsung CL10A106KP8NNNC | C19702 | one input, two output |

The divider gives approximately 4.704 V: `VOUT = 1 V x (1 MOhm + 270 kOhm) / 270 kOhm`. This sits
inside the red/IR and green VLED ranges even with the converter's feedback-reference tolerance. Connect EN
to VSYS for the lowest-parts-count implementation. Pinout is 1 GND, 2 VOUT, 3 FB, 4 EN, 5 SW,
6 VIN, exposed pad GND. Keep the VIN capacitor/inductor/SW loop and VOUT capacitors extremely short.
The MAX30101 still needs its local 4.7 uF + 100 nF VLED capacitors.

The MAX30101 datasheet guarantees its 4.5-5.5 V green-LED supply range only at 25 C. The 4.704 V rail
meets that published condition, but green performance over actual skin/ambient temperature must be
validated on hardware; it is not a datasheet guarantee across the sensor's full temperature range.

This block adds **7 populated components**, taking the planned PCB total from 43 to **50**. It is not
DNP or optional in v2. Removing it would be a later red/IR-only design change.

## Required connections that add no BOM lines

- Expose test pads for GND, 3V3, BAT+, VSYS, EN/RESET, GPIO9/BOOT, USB D-/D+, SDA, and SCL.
- Pull GPIO2, GPIO8, and GPIO9 up with 10 kOhm. Do not hang sensors on strapping pins.
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
| LEDs and buttons | Explicitly cut; recovery uses test pads |
| Power switch | Omitted for space and sealing; use deep sleep |
| 3.3 V buck-boost | Avoids several parts; accepted tradeoff is reduced usable battery capacity |
| Battery connector | Omitted; the protected cell wires are permanently soldered to marked pads with strain relief |

## Before schematic approval or ordering

1. Verify the exact battery evidence listed above; green, permanent attachment, and supervised
   charging are already locked.
2. Lock the offline data-retention requirement. If full raw sessions must survive without a phone,
   add storage before the schematic is frozen.
3. Re-evaluate the NRND ESP32-C3-MINI-1-N4 ordering code against the recommended N4X/H4X successors;
   do not accept a silent module substitution.
4. Draw and peer-check the load-share orientation, every regulator pinout, USB-C pin duplication,
   and every no-connect/thermal pad against the local PDFs.
5. Import the exact LCSC symbol/footprint for every IC and connector, then compare pad numbers to the
   manufacturer datasheet. Never trust a symbol merely because its part number matches.
6. Run ERC, generate the BOM from the schematic, and reconcile every line and quantity against this
   document. The expected populated count is 50.
7. Confirm current stock, assembly class, lifecycle, and price in the JLCPCB cart. Use exact order
   codes; do not allow “similar” substitutions for regulators, MOSFETs, or connectors.
8. Have another electrical review before PCB layout, then review antenna, optical, thermal, USB, and
   switching-regulator placement before fabrication.

## Primary design references

- Microchip, *AN1149: Designing a Li-Ion Battery Charger and Load Sharing System With Microchip's
  Stand-Alone Li-Ion Battery Charge Management Controller*: the
  discrete P-MOSF/Schottky load-sharing principle used here is in the load-sharing discussion.
  <https://ww1.microchip.com/downloads/en/appnotes/01149c.pdf>
- Texas Instruments, *TPS61099 datasheet*: output capability, optical-heart-rate application,
  external values, and layout. <https://www.ti.com/lit/ds/symlink/tps61099.pdf>
- Espressif, ESP32-C3 hardware design guidelines: local copy in
  [`_reference/esp32-c3_hardware_design_guidelines_en.pdf`](_reference/esp32-c3_hardware_design_guidelines_en.pdf).
