# V2 support-circuit decisions

Read this with [`../V2_BOM.md`](../V2_BOM.md). The design priority is first-spin reliability with as
few parts as practical, not the absolute minimum component count.

## Hardware load sharing is required

Connecting the system directly to the TP4054 BAT node would make charger current equal battery
current plus system current. A running system can keep measured current above the C/10 termination
threshold, preventing clean termination and lengthening charging.

The approved solution follows Microchip AN1149's discrete topology:

- AO3401A P-MOSFET: drain BAT+, source VSYS, gate VBUS plus 100 kOhm to ground.
- SS14: anode VBUS, cathode VSYS.
- TP4054 BAT connects only to the cell/MOSFET drain node.

When USB is present, USB powers VSYS and the cell charges independently. When USB is absent, the
MOSFET connects the cell to VSYS with low loss. This also lets the device run and flash over USB.

The earlier firmware-deep-sleep-on-VBUS proposal is rejected. It did not isolate the charger from
all possible system load, made charging correctness dependent on firmware, and prevented normal
use/debugging while attached.

Primary reference: <https://ww1.microchip.com/downloads/en/appnotes/01149c.pdf>.

## Two LDO rails are intentional

- ME6211C33M5G-N makes 3.3 V for the MCU and ordinary sensors. Its low dropout preserves more of the
  LiPo range than a 1117-class regulator, but regulation still ends around 3.42 V. A buck-boost was
  rejected to save parts and switching-layout risk; firmware must sleep early.
- XC6206P182MR makes 1.8 V only for MAX30101 VDD. The optical sensor's VDD absolute maximum is
  2.2 V, so this rail cannot be removed.

## Green PPG creates a real third regulated rail

MAX30101 has different LED supply requirements: 3.1-5.0 V for red/IR and 4.5-5.5 V for green. The
previous claim that direct LiPo power covered green was incorrect. A 3.0-4.2 V cell cannot guarantee
green operation.

Green is mandatory for v2, so use TPS61099DRVR with a 2.2 uH inductor, three 10 uF capacitors, and a
1 MOhm/270 kOhm divider for about 4.704 V. That target sits in the overlap between the red/IR and
green supply ranges. Drive EN from GPIO10 (`PPG_PWR_EN`) and fit a 100 kOhm pulldown so MAX30101 VDD
rises before VLED+ as recommended. It is a small, low-quiescent-current converter whose datasheet
explicitly lists optical heart-rate LED bias and wearable use. All eight parts are
populated; a red/IR-only future revision could omit the entire block.

Primary reference: <https://www.ti.com/lit/ds/symlink/tps61099.pdf>.

## TP4054 is prototype-grade here

The TP4054 is compact and needs only a 10 kOhm program resistor for 100 mA nominal charge current.
It does not provide a cell thermistor input or safety timer. It is acceptable only under the current
requirement of a protected cell and supervised, off-wrist research-prototype charging. A product intended for
unattended or on-body charging needs a charger/safety architecture review, not a drop-in substitution.

## Component savings deliberately taken

- No LED, button, USB-UART bridge, auto-reset transistor pair, RTC, I2C level shifter, or power switch.
- MAX30101 and TMP117 are polled, avoiding interrupt pull-ups.
- The permanently soldered battery avoids a connector and allows omission of the
  TP4054 BAT capacitor under the datasheet's battery-present condition.
- One shared I2C pull-up pair serves all four sensors.
- Test pads and DNP footprints are used where they add recovery options without populated BOM cost.

## USB-C remains the bring-up and charging interface

Use a standard horizontal SMD receptacle, not mid-mount. The 3.2 mm connector fits within the
top-side height already set by the 2.4 mm module plus 4.0 mm battery. Fit one 5.1 kOhm pull-down on
each CC pin; without both resistors, a USB-C source is not required to supply VBUS.
