# ESP32-C3-MINI-1-N4 — MCU module

| Field | Value |
|---|---|
| Order code | ESP32-C3-MINI-1-N4 (4 MB flash) |
| LCSC | **C2838502** |
| Manufacturer | Espressif |
| Size | **13.2 × 16.6 × 2.4 mm** |
| Supply | 3.0–3.6 V |
| Antenna | **Onboard PCB trace** (the `-1U` variant is U.FL instead) |
| Datasheet | `datasheet.pdf` — **English v2.2, May 2026** |

## Datasheet versions

`datasheet_zh_v1.7_SUPERSEDED.pdf` is the Chinese v1.7 (Sept 2024) copy JLCPCB serves. It is **five
revisions behind**. Use `datasheet.pdf` (v2.2) as authoritative; the old one is kept only for provenance.

## Why a module, not the XIAO

A XIAO on a carrier board is two stacked PCBs, which breaks the one-double-sided-board constraint and
adds ~3.5 mm. Same C3 silicon, same toolchain, same libraries — only the PlatformIO board id changes.

**Cost of the move:** you now own the USB-C, ESD, LDO, charger and boot/reset circuitry the XIAO
provided. See `../_reference/` for Espressif's reference schematic and design guidelines.

## Layout

The PCB trace antenna needs a keepout — clear copper beneath and around it, and **no battery over it**
(a LiPo pouch is metal and will detune it). Rules are in
`../_reference/esp32-c3_hardware_design_guidelines_en.pdf`.

## Schematic — pin definitions (53 pins, from datasheet Table 3-1)

Only the pins this design uses. Everything else is `NC` (pins 4, 7, 9, 10, 15, 17, 24, 25, 28, 29, 32–35).

| Pin | Name | Connect to |
|---|---|---|
| 1, 2, 11, 14, 36–53 | GND | `GND` — **all of them**, including the thermal/shield pads |
| 3 | 3V3 | `+3V3` |
| 8 | EN | **Must not float.** 10 kΩ to `+3V3` + 1 µF to `GND` (RC delay so the rail settles before boot) |
| 22 | IO8 | **Strapping pin** — 10 kΩ pull-up to `+3V3` |
| 23 | IO9 | **Strapping pin = BOOT** — 10 kΩ pull-up to `+3V3`; expose test pad for pulling low |
| 26 | IO18 | `USB_D−` through 22 Ohm series resistor |
| 27 | IO19 | `USB_D+` through 22 Ohm series resistor |
| 5 | IO2 | **Strapping pin** — 10 kΩ pull-up to `+3V3`; do not use for peripherals |
| 6 | IO3 | `BAT_SENSE` from 1 MOhm / 1 MOhm divider; 100 nF to GND |
| 20 | IO6 | Free — proposed `SDA` |
| 21 | IO7 | Free — proposed `SCL` |
| 30, 31 | RXD0 / TXD0 | UART0. Optional debug header; not needed (native USB) |

> Net assignments marked **proposed** are this project's choice, not datasheet requirements. The C3's
> GPIO matrix puts I²C on any pin — `Wire.begin(sda, scl)` sets it in firmware.

### Strapping pins — the boot-failure trap

GPIO2, GPIO8, GPIO9 are sampled at reset (datasheet §4). GPIO2 and GPIO8 default floating; GPIO9 has
an internal weak pull-up. SPI boot requires GPIO9 high; GPIO8 may have either value. Joint USB/UART
download mode requires GPIO2 and GPIO8 high while GPIO9 is low. Fit 10 kΩ pull-ups on all three so
normal boot and the test-pad recovery path are deterministic. Espressif specifically recommends the
GPIO2 pull-up for glitch immunity. Keep peripherals off these nets. Strapping values are held 3 ms
after EN goes high (Table 4-2).

### Recovery pads — mandatory given no LEDs and no buttons

Expose **IO9 (BOOT)** and **EN (RESET)** as test pads. With no status LED, no buttons and a sealed
enclosure, these two pads are the only way back into a board running bad firmware. The
"hold BOOT, tap RESET" recovery recurs throughout `archive/v1/docs/hardware_debug_log.md`.
They cost nothing.

## Schematic — required externals

| Component | Value | Net | Why |
|---|---|---|---|
| C_bulk | 10 µF | 3V3 → GND | Module draws ~350 mA peaks on TX |
| C_bypass | 0.1 µF | 3V3 → GND | Close to pin 3 |
| R_EN | 10 kΩ | EN → 3V3 | EN must not float |
| C_EN | 1 µF | EN → GND | Power-on reset delay |
| R_IO8 | 10 kΩ | IO8 → 3V3 | Strapping |
| R_IO2 | 10 kΩ | IO2 → 3V3 | Strapping; avoids download-mode glitches |
| R_IO9 | 10 kΩ | IO9 → 3V3 | Normal boot; test pad can pull low for recovery |
| R_USB_DM | 22 Ω | IO18 → USB D− | USB impedance/source damping; close to module |
| R_USB_DP | 22 Ω | IO19 → USB D+ | USB impedance/source damping; close to module |

Copy the known-good arrangement from `../_reference/esp32-c3-devkitm-1_reference_schematic.pdf`.
**Native USB (IO18/IO19) means no USB-UART bridge and no DTR/RTS auto-reset transistors** — a real
parts saving versus most ESP32 designs.

Battery sensing uses GPIO3 (ADC1_CH3), a 1 MΩ / 1 MΩ divider, and 100 nF from the ADC node to ground.
Do not use GPIO2 for it.

## Layout

PCB trace antenna keepout, from `../_reference/esp32-c3_hardware_design_guidelines_en.pdf`:

- No copper on any layer under the antenna; keep the board edge clear.
- **No LiPo over the antenna end** — the pouch is metal and will detune it. Battery goes over the
  opposite end. This is the constraint that fixes the board's floorplan.
