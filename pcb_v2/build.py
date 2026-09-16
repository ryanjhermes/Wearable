#!/usr/bin/env python3
"""Bootstrap generator for the Wearable V2 schematic.

Emits pcb_v2/wearable_v2.kicad_sch from parts/V2_BOM.md. Run once; after the
schematic is opened and edited in KiCad the .kicad_sch is authoritative and
this script must not be re-run over it.
"""
import os
import schgen
from schgen import Sch

ROOT = "/Users/ryanhermes/Desktop/BIZTECH/Wearable/pcb_v2"
schgen._load_local(os.path.join(ROOT, "symbols", "wearable_v2.kicad_sym"))

sch = Sch("A2")
sch.root = "7e1c0000-0000-4000-8000-00000000c3v2"

RAIL = {"GND": "power:GND", "3V3": "power:+3V3", "1V8": "power:+1V8",
        "VBUS": "power:VBUS", "VSYS": "wearable_v2:VSYS",
        "4V7": "wearable_v2:+4V7", "BAT+": "wearable_v2:BAT+"}
_pwr = [0]


def rail(name, x, y, rot=0):
    _pwr[0] += 1
    sch.place(RAIL[name], x, y, ref=f"#PWR{_pwr[0]:03d}", value=name,
              rot=rot, fields_hidden=("Reference", "Value"), in_bom=False,
              snap=False)


def pin(ref, num):
    return sch.pins[ref][num]


def route(ref, num, segs):
    """segs: list of (dx, dy) applied in order. Returns the final point."""
    x, y = pin(ref, num)
    for dx, dy in segs:
        nx, ny = round(x + dx, 4), round(y + dy, 4)
        sch.wire(x, y, nx, ny)
        x, y = nx, ny
    return x, y


def to_rail(ref, num, name, segs):
    x, y = route(ref, num, segs)
    rail(name, x, y)


def to_label(ref, num, name, segs, rot=0):
    x, y = route(ref, num, segs)
    sch.label(name, x, y, rot)


def nc(ref, num, segs=((2.54, 0),)):
    x, y = route(ref, num, segs)
    sch.nc(x, y)


# ---- passive helpers -------------------------------------------------------
def R(ref, val, x, y, lcsc):
    return sch.place("Device:R", x, y, ref=ref, value=val,
                     footprint="Resistor_SMD:R_0402_1005Metric",
                     extra_props=(("LCSC", lcsc),))


def C(ref, val, x, y, lcsc, fp="Capacitor_SMD:C_0402_1005Metric"):
    return sch.place("Device:C", x, y, ref=ref, value=val, footprint=fp,
                     extra_props=(("LCSC", lcsc),))


C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
LC = {"100n": "C1525", "1u": "C52923", "4u7": "C19666", "10u": "C19702",
      "22R": "C25092", "4k7": "C25900", "5k1": "C25905", "10k": "C25744",
      "100k": "C25741", "1M": "C26083", "270k": "C25770"}


def decap(ref, val, x, y, top, lcsc, fp=C0402):
    """Vertical cap: pin1 up to `top` rail, pin2 down to GND."""
    C(ref, val, x, y, lcsc, fp)
    to_rail(ref, "1", top, [(0, -2.54)])
    to_rail(ref, "2", "GND", [(0, 2.54)])


def pulldown(ref, val, x, y, lcsc, label_top):
    R(ref, val, x, y, lcsc)
    to_label(ref, "1", label_top, [(0, -2.54)])
    to_rail(ref, "2", "GND", [(0, 2.54)])


def pullup(ref, val, x, y, lcsc, label_bot, top="3V3"):
    R(ref, val, x, y, lcsc)
    to_rail(ref, "1", top, [(0, -2.54)])
    to_label(ref, "2", label_bot, [(0, 2.54)])


def title(t, x, y):
    sch.text(t, x, y, size=3.0, bold=True)


# ============================================================================
# BLOCK A — USB-C input, CC resistors, ESD
# ============================================================================
sch.box(15, 20, 155, 125)
title("A  USB-C input + ESD", 18, 26)

sch.place("Connector:USB_C_Receptacle_USB2.0_16P", 45, 62, ref="J1",
          value="TYPE-C-31-M-12", footprint="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
          extra_props=(("LCSC", "C165948"),))
to_rail("J1", "A4", "VBUS", [(7.62, 0), (0, -5.08)])
to_rail("J1", "A1", "GND", [(0, 5.08)])
to_rail("J1", "SH", "GND", [(0, 5.08)])
to_label("J1", "A6", "USB_DP_CON", [(5.08, 0)])
to_label("J1", "B6", "USB_DP_CON", [(5.08, 0)])
to_label("J1", "A7", "USB_DM_CON", [(7.62, 0)])
to_label("J1", "B7", "USB_DM_CON", [(7.62, 0)])
nc("J1", "A8", [(5.08, 0)])
nc("J1", "B8", [(5.08, 0)])
to_label("J1", "A5", "CC1", [(5.08, 0)])
to_label("J1", "B5", "CC2", [(5.08, 0)])

pulldown("R1", "5.1k", 90, 40, LC["5k1"], "CC1")
pulldown("R2", "5.1k", 104, 40, LC["5k1"], "CC2")

sch.place("wearable_v2:USBLC6-2SC6", 120, 85, ref="U2", value="USBLC6-2SC6",
          footprint="Package_TO_SOT_SMD:SOT-23-6",
          extra_props=(("LCSC", "C7519"),))
to_label("U2", "1", "USB_DM_CON", [(-5.08, 0)], rot=180)
to_label("U2", "3", "USB_DP_CON", [(-5.08, 0)], rot=180)
to_label("U2", "6", "USB_DM", [(5.08, 0)])
to_label("U2", "4", "USB_DP", [(5.08, 0)])
to_rail("U2", "5", "VBUS", [(0, -5.08)])
to_rail("U2", "2", "GND", [(0, 5.08)])

# ============================================================================
# BLOCK B — Charger, load sharing, battery, battery sense
# ============================================================================
sch.box(163, 20, 308, 125)
title("B  Charger + USB/battery load share  (Microchip AN1149)", 166, 26)

sch.place("wearable_v2:TP4054", 200, 55, ref="U3", value="TP4054-42-SOT25R",
          footprint="Package_TO_SOT_SMD:SOT-23-5",
          extra_props=(("LCSC", "C32574"),))
to_rail("U3", "4", "VBUS", [(-5.08, 0), (0, -10.16)])
to_rail("U3", "2", "GND", [(0, 5.08)])
to_rail("U3", "3", "BAT+", [(5.08, 0), (0, -5.08)])
to_label("U3", "5", "PROG", [(-7.62, 0)], rot=180)
nc("U3", "1", [(5.08, 0)])

decap("C1", "4.7uF", 175, 48, "VBUS", LC["4u7"], C0603)
pulldown("R5", "10k", 178, 78, LC["10k"], "PROG")

# SS14: USB -> VSYS.  Symbol pin 1 = K (left), pin 2 = A (right).
sch.place("Diode:SS14", 240, 40, ref="D1", value="SS14",
          footprint="Diode_SMD:D_SMA", rot=180,
          extra_props=(("LCSC", "C2480"),))
to_rail("D1", "2", "VBUS", [(-5.08, 0), (0, -5.08)])
to_rail("D1", "1", "VSYS", [(5.08, 0), (0, -5.08)])

# AO3401A load-share P-FET: G=VBUS, S=VSYS, D=BAT+
sch.place("Transistor_FET:AO3401A", 245, 75, ref="Q1", value="AO3401A",
          footprint="Package_TO_SOT_SMD:SOT-23",
          extra_props=(("LCSC", "C15127"),))
to_rail("Q1", "1", "VBUS", [(-5.08, 0), (0, -7.62)])
to_rail("Q1", "2", "VSYS", [(0, 5.08)])
to_rail("Q1", "3", "BAT+", [(0, -5.08)])

R("R6", "100k", 222, 90, LC["100k"])
to_rail("R6", "1", "VBUS", [(0, -2.54)])
to_rail("R6", "2", "GND", [(0, 2.54)])
sch.text("Gate to VBUS, 100k to GND: USB present turns Q1 OFF so the charger sees", 166, 114, 1.6)
sch.text("only cell current and terminates. Body diode starts VSYS on battery.", 166, 118, 1.6)

# Battery: permanent solder pads, not populated by the assembler
sch.place("Device:Battery_Cell", 285, 55, ref="BT1", value="LiPo 402030 250mAh",
          footprint="pcb_v2:BatteryPads_2x", in_bom=False,
          extra_props=(("Note", "Hand-soldered pads; NOT assembled by JLCPCB"),))
to_rail("BT1", "1", "BAT+", [(0, -5.08)])
to_rail("BT1", "2", "GND", [(0, 5.08)])

# Battery sense divider on GPIO3 / ADC1_CH3
R("R7", "1M", 175, 100, LC["1M"])
R("R8", "1M", 175, 114, LC["1M"])
to_rail("R7", "1", "BAT+", [(0, -2.54)])
sch.wire(*pin("R7", "2"), *pin("R8", "1"))
sch.junction(*pin("R8", "1"))
sch.label("BAT_SENSE", *pin("R8", "1"))
to_rail("R8", "2", "GND", [(0, 2.54)])
C("C2", "100nF", 192, 114, LC["100n"])
to_label("C2", "1", "BAT_SENSE", [(0, -2.54)])
to_rail("C2", "2", "GND", [(0, 2.54)])

# ============================================================================
# BLOCK C — Linear regulators 3.3 V and 1.8 V
# ============================================================================
sch.box(316, 20, 446, 125)
title("C  Linear regulators", 319, 26)

sch.place("Regulator_Linear:ME6211C33M5", 355, 50, ref="U4",
          value="ME6211C33M5G-N", footprint="Package_TO_SOT_SMD:SOT-23-5",
          extra_props=(("LCSC", "C82942"),))
to_rail("U4", "1", "VSYS", [(-5.08, 0), (0, -7.62)])
to_rail("U4", "3", "VSYS", [(-5.08, 0), (0, -5.08)])
to_rail("U4", "2", "GND", [(0, 5.08)])
to_rail("U4", "5", "3V3", [(5.08, 0), (0, -7.62)])
sch.text("CE tied to VIN. Floating CE = no output, board looks dead.", 319, 68, 1.6)

decap("C3", "1uF", 330, 82, "VSYS", LC["1u"])
decap("C4", "1uF", 385, 82, "3V3", LC["1u"])

sch.place("Regulator_Linear:XC6206PxxxMR", 355, 105, ref="U5",
          value="XC6206P182MR", footprint="Package_TO_SOT_SMD:SOT-23",
          extra_props=(("LCSC", "C21659"),))
to_rail("U5", "3", "3V3", [(-5.08, 0), (0, -5.08)])
to_rail("U5", "1", "GND", [(0, 5.08)])
to_rail("U5", "2", "1V8", [(5.08, 0), (0, -5.08)])

decap("C5", "1uF", 330, 112, "3V3", LC["1u"])
decap("C6", "1uF", 400, 112, "1V8", LC["1u"])

# ============================================================================
# BLOCK D — TPS61099 4.7 V boost for the green LED rail
# ============================================================================
sch.box(454, 20, 584, 125)
title("D  4.7 V green-LED boost", 457, 26)

sch.place("wearable_v2:TPS61099DRVR", 505, 58, ref="U6", value="TPS61099DRVR",
          footprint="Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
          extra_props=(("LCSC", "C2842395"),))
to_rail("U6", "6", "VSYS", [(-5.08, 0), (0, -7.62)])
to_label("U6", "4", "PPG_PWR_EN", [(-10.16, 0)], rot=180)
to_label("U6", "3", "FB_PPG", [(-10.16, 0)], rot=180)
to_label("U6", "5", "SW_PPG", [(5.08, 0)])
to_rail("U6", "2", "4V7", [(7.62, 0), (0, -7.62)])
to_rail("U6", "1", "GND", [(0, 5.08)])

sch.place("Device:L", 480, 40, ref="L1", value="2.2uH 1.5A",
          footprint="pcb_v2:L_MAKK2016T_2.0x1.6mm",
          extra_props=(("LCSC", "C92923"),))
to_rail("L1", "1", "VSYS", [(0, -2.54)])
to_label("L1", "2", "SW_PPG", [(0, 2.54)])

decap("C7", "10uF", 463, 58, "VSYS", LC["10u"], C0603)
decap("C8", "10uF", 550, 58, "4V7", LC["10u"], C0603)
decap("C9", "10uF", 566, 58, "4V7", LC["10u"], C0603)

R("R9", "1M", 480, 88, LC["1M"])
to_rail("R9", "1", "4V7", [(0, -2.54)])
sch.label("FB_PPG", *pin("R9", "2"))
R("R10", "270k", 480, 102, LC["270k"])
to_label("R10", "1", "FB_PPG", [(0, -2.54)])
to_rail("R10", "2", "GND", [(0, 2.54)])
sch.wire(*pin("R9", "2"), *pin("R10", "1"))

pulldown("R11", "100k", 510, 95, LC["100k"], "PPG_PWR_EN")
sch.text("VOUT = 1.0 V x (1M + 270k) / 270k = 4.704 V nominal.", 457, 116, 1.6)
sch.text("EN low through reset: MAX30101 VDD must rise before VLED+.", 457, 120, 1.6)

# ============================================================================
# BLOCK E — MCU
# ============================================================================
sch.box(15, 140, 235, 295)
title("E  ESP32-C3-MINI-1 (N4)", 18, 146)

sch.place("wearable_v2:ESP32-C3-MINI-1", 110, 200, ref="U1",
          value="ESP32-C3-MINI-1-N4", footprint="pcb_v2:ESP32-C3-MINI-1",
          extra_props=(("LCSC", "C2838502"),))
to_rail("U1", "3", "3V3", [(-7.62, 0), (0, -5.08)])
to_rail("U1", "1", "GND", [(0, 7.62)])
to_label("U1", "8", "EN", [(-10.16, 0)], rot=180)
to_label("U1", "5", "IO2_STRAP", [(-12.7, 0)], rot=180)
to_label("U1", "6", "BAT_SENSE", [(-12.7, 0)], rot=180)
for _p in ("12", "13", "18"):
    nc("U1", _p, [(-2.54, 0)])
to_label("U1", "16", "PPG_PWR_EN", [(-12.7, 0)], rot=180)
nc("U1", "19", [(2.54, 0)])
to_label("U1", "20", "SDA", [(7.62, 0)])
to_label("U1", "21", "SCL", [(7.62, 0)])
to_label("U1", "22", "IO8_STRAP", [(7.62, 0)])
to_label("U1", "23", "IO9_BOOT", [(7.62, 0)])
to_label("U1", "26", "IO18_USB_DM", [(7.62, 0)])
to_label("U1", "27", "IO19_USB_DP", [(7.62, 0)])
for _p in ("30", "31"):
    nc("U1", _p, [(2.54, 0)])

decap("C11", "10uF", 40, 165, "3V3", LC["10u"], C0603)
decap("C12", "100nF", 56, 165, "3V3", LC["100n"])

# EN reset RC
pullup("R12", "10k", 40, 235, LC["10k"], "EN")
C("C10", "1uF", 56, 245, LC["1u"])
to_label("C10", "1", "EN", [(0, -2.54)])
to_rail("C10", "2", "GND", [(0, 2.54)])

# Strapping-pin pull-ups
pullup("R13", "10k", 175, 165, LC["10k"], "IO2_STRAP")
pullup("R14", "10k", 191, 165, LC["10k"], "IO8_STRAP")
pullup("R15", "10k", 207, 165, LC["10k"], "IO9_BOOT")

# USB series resistors, close to the module
R("R3", "22R", 175, 255, LC["22R"])
to_label("R3", "1", "IO18_USB_DM", [(0, -2.54)])
to_label("R3", "2", "USB_DM", [(0, 2.54)])
R("R4", "22R", 200, 255, LC["22R"])
to_label("R4", "1", "IO19_USB_DP", [(0, -2.54)])
to_label("R4", "2", "USB_DP", [(0, 2.54)])

# Shared I2C pull-ups (the bare chips have none; the old breakouts did)
pullup("R16", "4.7k", 40, 275, LC["4k7"], "SDA")
pullup("R17", "4.7k", 60, 275, LC["4k7"], "SCL")
sch.text("GPIO2/8/9 are strapping pins: pulled up, no peripherals on them.", 18, 290, 1.6)

# ============================================================================
# BLOCK F — Sensors, one shared I2C bus
# ============================================================================
sch.box(243, 140, 478, 295)
title("F  Sensors  (SHT40 0x44 / TMP117 0x48 / MAX30101 0x57 / LSM6DS3TR-C 0x6A)",
      246, 146)

# --- MAX30101 (PPG) ---
sch.place("wearable_v2:MAX30101EFD", 300, 185, ref="U7", value="MAX30101EFD+T",
          footprint="OptoDevice:Maxim_OLGA-14_3.3x5.6mm_P0.8mm",
          extra_props=(("LCSC", "C2859066"),))
to_label("U7", "2", "SCL", [(-7.62, 0)], rot=180)
to_label("U7", "3", "SDA", [(-7.62, 0)], rot=180)
nc("U7", "13", [(-7.62, 0)])
to_rail("U7", "9", "4V7", [(7.62, 0), (0, -5.08)])
to_rail("U7", "11", "1V8", [(0, -5.08)])
to_rail("U7", "12", "GND", [(0, 7.62)])
to_rail("U7", "4", "GND", [(0, 7.62)])

decap("C13", "100nF", 258, 215, "1V8", LC["100n"])
decap("C14", "1uF", 274, 215, "1V8", LC["1u"])
decap("C15", "4.7uF", 330, 215, "4V7", LC["4u7"], C0603)
decap("C16", "100nF", 346, 215, "4V7", LC["100n"])
sch.text("C15 4.7uF on VLED+ is mandatory: 200 mA LED pulses.", 258, 232, 1.6)

# --- TMP117 (skin temperature) ---
sch.place("Sensor_Temperature:TMP117xxDRV", 400, 180, ref="U8",
          value="TMP117AIDRVR", footprint="Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
          extra_props=(("LCSC", "C699536"),))
to_label("U8", "1", "SCL", [(-7.62, 0)], rot=180)
to_label("U8", "6", "SDA", [(-7.62, 0)], rot=180)
to_rail("U8", "4", "GND", [(-7.62, 0), (0, 7.62)])
to_rail("U8", "5", "3V3", [(0, -5.08)])
to_rail("U8", "2", "GND", [(0, 5.08)])
nc("U8", "3", [(7.62, 0)])
decap("C17", "100nF", 440, 180, "3V3", LC["100n"])

# --- LSM6DS3TR-C (IMU) ---
sch.place("Sensor_Motion:LSM6DS3", 320, 262, ref="U9", value="LSM6DS3TR-C",
          footprint="Package_LGA:LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y",
          extra_props=(("LCSC", "C967633"),))
# Pins 1/2/3 sit ABOVE centre and 12/13/14 below: route the ties upward so
# they never cross the SDA/SCL stubs (doing so shorts the I2C bus to GND).
to_rail("U9", "1", "GND", [(-10.16, 0), (0, -7.62)])
to_rail("U9", "2", "GND", [(-12.7, 0), (0, -7.62)])
to_rail("U9", "3", "GND", [(-15.24, 0), (0, -7.62)])
to_rail("U9", "12", "3V3", [(-10.16, 0), (0, 7.62)])
to_label("U9", "13", "SCL", [(-5.08, 0)], rot=180)
to_label("U9", "14", "SDA", [(-5.08, 0)], rot=180)
to_rail("U9", "5", "3V3", [(0, -5.08)])
to_rail("U9", "8", "3V3", [(2.54, 0), (0, -7.62)])
to_rail("U9", "6", "GND", [(0, 5.08)])
nc("U9", "4", [(5.08, 0)])
nc("U9", "9", [(5.08, 0)])
decap("C18", "100nF", 370, 250, "3V3", LC["100n"])
decap("C19", "100nF", 386, 250, "3V3", LC["100n"])
sch.text("CS tied high or the part boots SPI. SDO/SA0 low = 0x6A. SDx/SCx must not float.",
         258, 288, 1.6)

# --- SHT40 (ambient) ---
sch.place("Sensor_Humidity:SHT4x", 430, 250, ref="U10", value="SHT40-AD1B-R3",
          footprint="Sensor_Humidity:Sensirion_DFN-4_1.5x1.5mm_P0.8mm_SHT4x_NoCentralPad",
          extra_props=(("LCSC", "C2848306"),))
to_label("U10", "1", "SDA", [(-7.62, 0)], rot=180)
to_label("U10", "2", "SCL", [(-7.62, 0)], rot=180)
to_rail("U10", "3", "3V3", [(0, -5.08)])
to_rail("U10", "4", "GND", [(0, 5.08)])
decap("C20", "100nF", 462, 250, "3V3", LC["100n"])

# ---- PWR_FLAGs -------------------------------------------------------------
# GND, VBUS and VSYS are fed only by passive pins (connector shell, Schottky,
# MOSFET), so ERC needs an explicit power source on each. BAT+ is already
# driven by the TP4054 BAT pin, so it must NOT get a flag as well.
for _i, (_n, _fx) in enumerate([("GND", 500), ("VBUS", 520), ("VSYS", 540)]):
    _r = f"#FLG{_i+1:03d}"
    sch.place("power:PWR_FLAG", _fx, 320, ref=_r, value="PWR_FLAG",
              fields_hidden=("Reference", "Value"), in_bom=False)
    to_rail(_r, "1", _n, [(0, -5.08)])
sch.text("PWR_FLAGs: these three rails are driven only by passive pins.", 500, 330, 1.6)

# ============================================================================
# BLOCK G — Bring-up test pads (no LED, no buttons: this is the only way in)
# ============================================================================
sch.box(486, 140, 584, 295)
title("G  Test pads", 489, 146)
sch.text("No LEDs and no buttons. Recovery = hold IO9 low, pulse EN.", 489, 152, 1.6)
sch.text("1V8 and 4V7 pads replace the declined debug LED.", 489, 156, 1.6)

pads = [("GND", None), ("3V3", None), ("1V8", None), ("4V7", None),
        ("VSYS", None), ("BAT+", None), ("EN", "EN"), ("IO9_BOOT", "IO9_BOOT"),
        ("USB_DM", "USB_DM"), ("USB_DP", "USB_DP"),
        ("SDA", "SDA"), ("SCL", "SCL")]
for i, (nm, lab) in enumerate(pads):
    px = 500 + (i % 2) * 40
    py = 170 + (i // 2) * 20
    ref = f"TP{i+1}"
    sch.place("Connector:TestPoint", px, py, ref=ref, value=nm,
              footprint="TestPoint:TestPoint_Pad_D1.0mm", in_bom=False)
    if lab:
        to_label(ref, "1", lab, [(0, 5.08)], rot=270)
    else:
        to_rail(ref, "1", nm, [(0, 5.08)], )

sch.render(os.path.join(ROOT, "wearable_v2.kicad_sch"), sch.root)
print("components placed:", sum(1 for i in sch.items if i.startswith("  (symbol")))
