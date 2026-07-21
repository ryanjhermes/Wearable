# Hardware Debug Log

Historical bring-up / debugging narrative moved out of CLAUDE.md. Not authoritative for
current state — CLAUDE.md wins on any conflict. Kept because the *root causes* and
*diagnostic heuristics* here are reusable if the same faults recur.

## Board swap (2026-07-19)

The user replaced the original XIAO (old serial `SER=E0:72:A1:FC:4F:CC`) with a fresh
XIAO ESP32S3. No re-provisioning needed — same PlatformIO config, native USB-Serial/JTAG
(no drivers), board-agnostic firmware. A brand-new board may not enter upload mode on the
first try; if it hangs at `Connecting...`, force the bootloader (hold BOOT, tap RESET,
release BOOT, re-upload). Bring-up CONFIRMED: new board enumerated on `/dev/cu.usbmodem101`
(serial `SER=E0:72:A1:FC:4F:80`), accepted uploads, ran firmware over USB. No forced-bootloader
step was needed.

## Battery wiring saga (2026-07-19 → 2026-07-20)

**Outcome (authoritative version in CLAUDE.md):** board-side **black → silkscreen `+` (BAT+)**,
board-side **red → silkscreen `−` (GND)**. Looks backwards on the wires alone, but the JST
housing is mirrored so after the connector the battery's red lands on BAT+. CONFIRMED working.

Root-cause chain, in order of discovery:
1. `battery_blink` LED went dark instantly on USB unplug → first blamed on a flat cell (a flat
   cell and an open BAT joint look identical, and USB was connected only ~10s = ~zero charge).
2. No charge LED with USB plugged → shifted lead from "flat cell" toward "current not reaching
   the cell" (open/cold BAT joint or mis-seated JST).
3. **Board heated up quickly** with battery + USB → SAFETY signature of REVERSED POLARITY or a
   solder bridge, not an open joint. With a LiPo this is a fire/venting hazard. Guidance: STOP,
   unplug both, let cool, inspect cell.
4. **Root cause = mirrored JST housing**, visually confirmed: the battery's BLACK lands on the
   pigtail's RED wire and vice-versa. The keyed connector only plugs one way, and that way is
   mirrored — so matching red-to-red across the connector reverses polarity.
5. Fix: wick pads clean (no bridge), dry-fit to trace which pigtail wire carries the battery's
   RED *through the connector*, solder THAT wire to silkscreen `+` (ignore pigtail wire colors).
   Solder battery UNPLUGGED. Re-solder CONFIRMED: `battery_blink` kept blinking on battery,
   board stayed cool, USB enumeration still works (charge IC survived the reverse-polarity episode).

**Reusable lessons:**
- The user has NO multimeter — polarity source of truth is XIAO underside silkscreen `+`/`−`
  (cross-check `pinout_back.png`) traced *through* the mated connector, never the pigtail's paint.
- Serial monitor CANNOT verify the battery (serial rides USB; unplugging USB always kills the
  monitor regardless of battery state). Use USB-independent signals: charge LED (joints conduct)
  and `battery_blink` unplug test (cell powers the board).
- Rapid heating = reverse polarity or short, NOT an open joint. Open joint = no power, no heat.
- If reverse-powered for a while and a clean correct re-solder still won't charge → charge IC
  may be dead, not bad soldering.

## MLX90614 detection saga (2026-07-01 → 2026-07-14)

**Outcome:** MLX90614 is **suspected dead.** Last confirmed a working stable `0x5A` with
temperature reads on 2026-07-13, then stopped ACKing the same session and never recovered.
Last direct-wire test 2026-07-14 returned `Error -1` (no ACK). Temperature deprioritized.

Timeline: soldered headers 2026-07-01 → detection at 0x5A CONFIRMED 2026-07-13 (stable every
scan, wired alone) → temperature reads CONFIRMED (ambient ~25–30°C, object tracked target,
100°C+ near the hot iron) → died the same session. Isolation test: MLX wired ALONE, direct
jumpers, on the exact D4/D5 pins that had just returned a rock-solid `0x57` from the MAX,
scanned clean `(none)` every scan. Localizes fault to the MLX (XIAO I2C proven good) and, being
clean `(none)` not random shifting addresses, rules out a floating-bus/ground fault — MLX is
either unpowered (broken VIN/GND joint) or dead.

**Two candidate kill causes:** (a) reverse polarity (VIN↔GND swap fries it; SDA↔SCL swap is
harmless); (b) thermal overheating — held near the hot soldering iron (object temps 45–134°C)
shortly before death (matches commit `f1d529f` "overheated? fried out?").

**Dead-or-not test (needs a multimeter the user lacks, so unrun):** VIN→GND at the MLX should
read ~3.3V (no 3.3V = power-joint fault, reflow; 3.3V present but still `(none)` = dead chip).
Touch test: a reverse-powered/shorted chip runs warm within seconds; a healthy one stays cool.

## Shared-bus progress (2026-07-13)

`i2c_scanner` on the shared bus returned a stable `0x57` every scan with the MAX wired (bus
healthy, not a power/ground fault). MLX dropped off (0x5A absent) after breadboard components
shifted, and re-seating did not restore it → led to the suspected-dead conclusion above.

**MAX30102 + BMI160 simultaneous read CONFIRMED live (2026-07-13)** via `combined_hr_motion`:
"we are getting data!" BMI160 enumerates at `0x69` (SDO/SA0 high on this HiLetgo GY-BMI160 unit)
alongside MAX at `0x57`. Rest values healthy — lying flat `A[g]≈0.0,-0.1,1.0` (gravity on Z),
gyro near 0, both respond live to tilt/rotation. First confirmed simultaneous multi-sensor read
on the shared I2C bus.

## Heart-rate bring-up (2026-07-12 → 2026-07-13)

PPG signal path confirmed first (fingertip → IR climbs ~500 baseline to ~118,000). Two bugs
fixed along the way: (1) phantom first beat — `lastBeat` initialized to 0 produced a frozen
bogus `BPM=4.6`; fix skips the first beat until `lastBeat != 0`. (2) "pressing too hard" —
a flat high steady DC (~119–122k, no ripple) defeats beat detection, which needs the small AC
pulse ripple riding on the DC. Real beats then appeared; the planned custom AC-detector rewrite
was considered but NOT applied — SparkFun `checkForBeat` kept as-is. Serial output throttled to
one summary line/sec. Fully CONFIRMED end-to-end: ~60s hold locked `Avg BPM` at a stable 74–82.

## Pre-solder contact history

Both sensor breakouts started as bare holes / breadboard pressure-fit and were intermittent
(`Error -1`, dropped ACKs on movement). Soldering headers was the fix, as predicted — MLX
2026-07-01, MAX 2026-07-12. `I2C_SPEED_FAST` (400kHz) was too aggressive for breadboard wiring
and contributed to read errors; `I2C_SPEED_STANDARD` (100kHz) is reliable. The pre-solder
full-bus scanner (2026-07-01) found nothing at any address — a power/ground contact issue, not
firmware.
