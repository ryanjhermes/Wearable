Enclosure work begins after the v2 fab-PCB outline and component placement are fixed. See
[`../parts/V2_BOM.md`](../parts/V2_BOM.md) for the authoritative capture-approved hardware plan.

The enclosure is currently blocked by:

- The exact protected 402030-class battery, including wire exit, protection-board bulge, and true
  dimensions.
- Exact placement of the permanently soldered cell wires, pads, and strain relief.
- Final placement of the mandatory TPS61099 green-PPG boost block.
- The ESP32-C3 antenna keepout: no battery or metal may overlap the module antenna end.
- Sensor interfaces: MAX30101 and TMP117 face skin; SHT40 needs a separate ambient-air vent.

Do not create final geometry from nominal component dimensions alone. Use the completed PCB STEP
model plus measured battery dimensions.
