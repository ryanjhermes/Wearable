# V2 hardware feasibility audit

Reviewed 2026-09-16 against `V2_BOM.md`, all selected component READMEs and local datasheets,
the project requirements in `CLAUDE.md`, and current manufacturer references linked below.

**Verdict: feasible sensor-platform architecture; proceed to schematic development, not fabrication.**
The selected sensor functions, MCU interfaces, and power architecture can form a working board.
No schematic, routed PCB, verified footprint set, or completed mechanical model exists in this
checkout. Consequently this is a component/architecture review, not electrical or manufacturing
sign-off. It cannot establish first-spin yield, wrist signal quality, runtime, or BAC prediction.

Schematic capture is approved because the circuit blocks, interfaces, and mandatory support parts are
defined. Freeze/order approval remains gated by the battery and retention decisions, exact module order
code, symbol/footprint audit, ERC, power-budget review, and the physical floorplan.

The most consequential unresolved requirements are offline raw-data duration and physical fit.
The audit does not change the approved sensor scope or substitute parts. Existing working-tree
changes were preserved. The observations below qualify several stronger claims in existing notes.

## Findings that affect schematic or layout release

### 1. Offline raw-data storage can exceed the entire module flash

The selected N4 module has 4 MB shared by firmware, configuration and logging; an OTA partition
would consume additional space. There is no external storage in the BOM.

Illustrative, uncompressed binary acquisition budget (not a prescribed sampling configuration):

| Stream | Assumption | Bytes/s |
|---|---|---:|
| PPG | Three wavelengths, 100 samples/s, 3 bytes per wavelength | 900 |
| Motion | Six axes, 50 samples/s, 2 bytes per axis | 600 |
| Total before timestamps, temperature and file overhead | | 1,500 |

That is 5.4 MB/hour or 32.4 MB for six hours. Even the entire 4 MiB would hold only 46.6 minutes,
and the actual log partition substantially less. One wavelength plus the same motion stream is
still 19.44 MB over six hours. Conversely, a deliberately small 32-byte summary each second is
only 691,200 bytes over six hours.

**Close before schematic freeze:** decide whether V2 saves summaries, streams raw data to a
nearby phone, or records raw sessions independently. For the latter, provision adequately sized
external storage and its GPIO/power/footprint budget. Compression needs measured evidence;
it must not be assumed to close this gap. An 8 MB module alone does not solve the example above.

### 2. The 3.3 V power-margin claim is too strong

The ME6211C33 table gives **typical**, not worst-case, dropout of 120 mV at 100 mA and 260 mV
at 200 mA. Its 500 mA figure is specified at VIN = VOUT + 1 V; this is not proof of 500 mA
capability at a nearly discharged cell voltage. The SOT23 dissipation listing is 300 mW.
See [local ME6211 datasheet](me6211/datasheet.pdf), pp. 5 and 8–9.

Thus the existing 3.42 V regulation boundary and 3.45 V sleep threshold are starting estimates,
not validated limits. Losing exactly 3.3 V regulation is also different from falling below the
module's 3.0 V operating minimum.

Example thermal check: 4.7 V VSYS to 3.3 V at 200 mA continuous dissipates 280 mW in the LDO,
already near that package listing before temperature derating. Short bursts need separate
transient analysis; this example is not a prediction of actual BLE-only average consumption.

**Close:** budget boot, BLE TX, flash writes, sensor loads and USB operation. Check regulator
thermal limits, load steps, cell/wire/MOSFET drops and effective decoupling. Scope 3V3 at the
module during worst-case simultaneous activity, at low battery and during cable insertion/removal.
Change the LDO or its support circuitry if margin is inadequate. A buck-boost is not automatically
required, but the existing LDO choice is not yet proven.

### 3. Green supply is plausible, but nominal voltage is not a complete validation

The TPS61099 is appropriate in principle. Its 1 MOhm/270 kOhm divider gives 4.704 V nominal.
Using 1% resistor endpoints and the PWM reference limits gives about **4.538–4.874 V** before
feedback leakage and transient effects. The lower endpoint leaves only 38 mV above 4.5 V.
Light-load PFM uses a different typical reference (1.03 V), without the same published min/max
bound; a PWM-only calculation does not guarantee the rail in all operating states.

Verify idle-to-LED-pulse response, ripple, start-up, temperature and USB-powered operation.
The converter has down mode and pass-through behavior; do not model it as an ideal fixed source.
Check actual DC-bias capacitance of the selected ceramics and inductor saturation/current margin.
Accept the rail only after bounding the relevant waveform at the sensor pins. This is an open
margin issue, not proof that the converter must be replaced.

The original always-on boost connection also violated the MAX30101's recommended power-up order
(VDD before VLED+). The capture baseline now drives TPS61099 EN from GPIO10 with a 100 kOhm pulldown.
This keeps VLED disconnected during reset and lets firmware enable it only after 1V8 is established.
Verify that sequence and the VLED rise waveform during bring-up.

**RESOLVED 2026-09-18:** R10 changed 270 kOhm -> 249 kOhm (user-approved), moving the nominal rail to
5.016 V and the worst-case low corner from 4.470 V to 4.770 V. Dynamic behaviour was simulated in
ngspice and is not a risk: a 51 mA green pulse moves the rail 4 mV. See `V2_BOM.md` and the verified
log in `../pcb/README.md`. Bench validation of ripple, start-up and temperature is still required.

Source: [TI TPS61099 datasheet](https://www.ti.com/lit/ds/symlink/tps61099.pdf), §§6.5, 7.3, 8.2.

### 4. TMP117 assembly treatment must be a deliberate design choice

`tmp117/README.md` now reflects TI's recommendation to leave the thermal pad unsoldered for best
accuracy on a rigid PCB. Soldering is allowed, floating or grounded, but can introduce stress-related
error and requires a deliberate thermal/calibration decision. It is not a mandatory ground terminal.

The part measures its die temperature. A skin measurement needs a defined skin-to-sensor thermal
path, and separation from MCU/regulator/battery heating. Slots are one possible implementation;
the underlying thermal problem does not depend on proving the old MLX90614 failure hypothesis.
A 0.75 mm TMP117 and 1.55 mm optical package also do not automatically contact the same skin plane.

**Close:** choose pad/paste treatment, skin interface and thermal geometry together; compare readings
against a reference while MCU and radio activity change. Do not interpret chip accuracy as finished
wearable skin-temperature accuracy.

Source: [TI TMP117 datasheet](https://www.ti.com/lit/ds/symlink/tmp117.pdf), §§9–10.

### 5. Exact MCU ordering code is NRND

Espressif's current v2.2 module datasheet lists **ESP32-C3-MINI-1-N4 as NRND** and recommends
N4X/H4X variants. NRND does not mean an N4 cannot work or is unavailable. However, a new board
should evaluate the recommended successor, its exact assembly sourcing, and the SDK requirements
for chip revision v1.1 before locking the order code. Do not silently substitute an ExpressLink
preprogrammed variant or assume the existing PlatformIO setup supports every revision.

Source: [Espressif module datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-c3-mini-1_datasheet_en.pdf), Table 1-1 and notes.

### 6. The target enclosure size is not yet demonstrated

A nominal 30 × 20 mm battery nearly fills a 32 × 24 mm envelope before walls, wire exit and
protection-board bulge. The module antenna also needs clearance from battery metal. Espressif
recommends placing the antenna outside the baseboard where possible and substantial clearance
inside the enclosure. Reduced clearance is an RF compromise requiring testing.

The proposed height sum is only a rough stack. Include PCB/component tolerances, battery
insulation and mechanical support, swelling allowance, optical contact geometry, and enclosure
walls. The pouch should not be pressed against sharp joints/components. USB plug access and
recovery-pad access need physical space too.

**Close:** make a component floorplan and 3D stack before detailed routing. If the battery,
antenna and sensors cannot coexist, change the outline or battery choice before ordering.
One board populated on both sides can still use four copper layers; that does not violate the
one-board requirement. Layer count should follow routing and return-path needs.

Source: [Espressif layout guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/pcb-layout-design.html), module placement and USB sections.

### 7. Battery identity and runtime remain open

Verify the exact cell's protection, charge voltage, charge/discharge ratings, polarity and measured
dimensions. The 100 mA charger setting needs the cell's permission, not just a capacity calculation.
The TP4054 has no cell thermistor input or safety timer; the existing supervised, off-wrist
prototype-use restriction remains applicable. Protection circuitry is not a charger-temperature sensor.

The existing claim that 250 mAh necessarily means 3–4 hours is unsupported for V2. Ideal battery-side
average-current limits are 62.5 mA for four hours and 41.7 mA for six hours; usable capacity and
reserve reduce them. Build the budget from sensor settings, MCU sleep, BLE, flash activity and
conversion losses, then measure. Firmware duty cycling can materially affect runtime.

No switch plus permanently powered rails also requires an explicit sleep/wake/recovery plan.
Deep sleep is not a physical disconnect. Route an appropriate IMU interrupt if motion wake is
required; ensure there is a way to recover after a low-battery sleep state when USB is inserted.

## Parts and interface reconciliation

| Selected block | Audit disposition |
|---|---|
| ESP32-C3-MINI-1 | Adequate class of MCU for these sensor streams and BLE. Native USB and proposed GPIO6/7 I2C assignment are workable. See lifecycle/storage/power findings. |
| MAX30101 | Appropriate experimental three-wavelength PPG source. Needs 1.8 V VDD and the separate LED supply. Shared 3.3 V I2C is compatible with input thresholds and pin tolerance; absolute maximum alone would not establish compatibility. |
| TMP117 | Electrically compatible at 3.3 V; ADD0 grounded gives 0x48. Correct thermal-pad instructions before footprint release. |
| LSM6DS3TR-C | Compatible at 3.3 V, 0x6A with SA0 grounded. CS high, SDx/SCx tied. Both 100 nF capacitors confirmed in §7.1 text; NC pads remain electrically open but solder mechanically. Gyro adds power/data even though it adds no BOM part. |
| SHT40-AD1B-R3 | Compatible at 3.3 V, fixed 0x44. Needs a vent and isolation from device heat and skin humidity. Its location determines whether it measures ambient conditions or the wrist microclimate. |
| ME6211C33M5G-N | Correct active-high enable/pin mapping in current notes; performance margin still needs closure above. |
| XC6206P182MR | Correct 1=GND, 2=VOUT, 3=VIN mapping; suitable in principle for the 1.8 V sensor rail from 3V3. |
| TP4054 | Current notes have the correct CHRG/GND/BAT/VCC/PROG mapping and nominal 100 mA programming. Battery and thermal qualification remain open. |
| AO3401A + SS14 | Drain-to-battery/source-to-VSYS MOSFET orientation and VBUS-to-VSYS diode implement the intended load share. Check transition behavior and low-USB/high-cell corners; correct topology alone does not prove all margins. |
| TPS61099 + inductor/divider/caps | Correct general topology and DRV pin mapping. GPIO10 control plus an EN pulldown now enforces the recommended MAX30101 start-up order. Resolve the rail-margin finding before treating it as guaranteed. Taiyo Yuden renamed the selected inductor; recheck its successor at order time. |
| TYPE-C-31-M-12 | Appropriate USB 2.0 connector concept; exact footprint, duplicated data/power pins, pegs and mating access need verification. |
| USBLC6-2SC6 | Suitable protection class; route at connector, pin 5 to VBUS, short ground return, correct paired I/O pins. |
| Listed resistors/capacitors | The planned 51-part arithmetic reconciles after adding the boost EN pulldown. Values are a design starting point, not proof of completeness. Check effective capacitance, stability, voltage/temperature ratings and layout; generated schematic BOM must own final counts. |

The four sensor addresses (0x44, 0x48, 0x57, 0x6A) do not collide. One pull-up pair is appropriate;
4.7 kOhm must still satisfy measured bus rise time at the selected speed. At 400 kHz a 300 ns
rise-time budget corresponds to roughly 75 pF with that resistance. Start bring-up at 100 kHz.
Boot pull-ups, EN RC and exposed BOOT/RESET pads are sensible. Add accessible 1V8 and VLED test
pads to the existing list, and UART RX/TX pads as an inexpensive alternate diagnostic path.

Supporting sources: [ST LSM6DS3TR-C datasheet](https://www.st.com/resource/en/datasheet/lsm6ds3tr-c.pdf),
[MAX30101 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX30101.pdf),
[Microchip AN1149](https://ww1.microchip.com/downloads/en/appnotes/01149c.pdf),
and each selected part's local `datasheet.pdf`.

## Sensor performance and assembly are part of the hardware

MAX30101 register reads do not establish usable wrist HR or pulse-interval data. Preserve room
for an opaque enclosure barrier and consistent skin pressure; verify ambient-light rejection and
motion performance. This can remain an enclosure feature, as already chosen, but its physical
space must be reserved. Red/IR availability does not guarantee reliable wrist SpO2, and PPG-derived
pulse variability is not automatically interchangeable with ECG HRV.

The SHT40 needs an outward-facing air path, separated from the skin-side cavity. Venting alone
does not remove thermal bias. Assess sweat ingress and material outgassing in the actual enclosure.
The absence of a V1 thermal measurement does not validate the V2 thermal arrangement.

MAX30101's package is not liquid/dust sealed; its manufacturer prohibits liquid cleaning, baking
and coating the sensor. SHT40 also needs its manufacturer's handling procedure. Supply explicit
assembly instructions and obtain confirmation that double-sided processing, cleaning and sensor
handling are compatible. A normal generic wash/coating instruction is inappropriate.

Sources: [MAX30101 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/MAX30101.pdf), Applications Information;
[ADI configurations and enclosure guide](https://www.analog.com/media/en/technical-documentation/user-guides/max3010x-ev-kits-recommended-configurations-and-operating-profiles.pdf), p.32;
[Sensirion design guide](https://sensirion.com/media/documents/FC5BED84/662A065D/Sensirion_Temperature_Sensors_Design_Guide_V1.pdf).

## What “ship it back and plug it in” requires

A parts list is not a manufacturing package. Release needs a reviewed schematic, audited symbols
and footprints, routed board with stackup, ERC/DRC disposition, Gerbers/drills, generated BOM,
placement files, assembly drawings and handling instructions. Check exact stock and assembly
eligibility in the actual order; those were not verified in this audit. Do not impose a 51-part
ceiling if validation reveals necessary support parts.

Agree separately who supplies/attaches the protected battery, adds strain relief, programs firmware,
assembles the enclosure and tests the unit. A PCB assembly order does not itself define those tasks.
JLCPCB offers programming/basic verification for Standard PCBA after reviewing customer-supplied
files and interface instructions; support for this exact board must be agreed.
Source: [JLCPCB programming service](https://jlcpcb.com/help/article/pcba-programming-service).

Define a minimum acceptance procedure before release:

1. Inspect for shorts and polarity; use a current-limited supply for initial power-up. Verify 3V3,
   1V8 and VLED before sustained operation and before attaching the cell.
2. Flash/recover through USB, test both cable orientations, and verify boot/reset access.
3. Identify and configure all four sensors; exercise FIFO reads and simultaneous acquisition.
4. Scope power rails during LED pulses, BLE traffic and flash writes, including low battery.
5. Verify USB/battery transitions, charge current and termination with the system running,
   sleep current, and recovery after low-battery operation.
6. Validate BLE with the real battery and enclosure installed, plus offline log retention and sync.
7. Verify optical and thermal measurements on the wrist; run the required session duration and
   inspect for data gaps. These checks cannot be replaced by factory solder-joint inspection.

Start with a small engineering batch and retain budget for a possible revision. After those checks,
confidence in repeat assemblies can be much higher. No numerical first-spin probability is justified
from the present evidence.

This hardware can support collecting PPG, skin temperature, motion and local environmental data
for the V2 experiment. It cannot establish that those channels predict BAC accurately; that requires
the project's labeled validation data. EDA remains intentionally excluded.
