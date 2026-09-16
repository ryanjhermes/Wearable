# V2 support circuitry

The complete support-part list has moved to the authoritative
[`../V2_BOM.md`](../V2_BOM.md). Read [`DECISIONS.md`](DECISIONS.md) for the power-path rationale and
tradeoffs.

The key blocks are:

- AO3401A + SS14 + 100 kOhm hardware USB/battery load sharing.
- TP4054 at 100 mA for a protected one-cell LiPo.
- ME6211 3.3 V LDO and XC6206 1.8 V LDO.
- Mandatory TPS61099 4.7 V boost for green PPG, GPIO10-controlled with an EN pulldown.
- USB-C CC resistors, USB ESD, 22 Ohm data resistors, ESP32 boot straps, I2C pull-ups, battery ADC,
  and all local decoupling.

This folder is explanatory only. Do not maintain a second parts table here.
