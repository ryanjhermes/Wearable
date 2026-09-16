import mksym as M

P = '/Users/ryanhermes/Desktop/BIZTECH/Wearable/pcb_v2/symbols/wearable_v2.kicad_sym'
S = []

# ---- ESP32-C3-MINI-1 (datasheet v2.2 Table 3-1) -----------------------------
esp_left = [("3", "3V3", "power_in"), ("8", "EN", "input"), None,
            ("5", "IO2", "bidirectional"), ("6", "IO3", "bidirectional"),
            ("12", "IO0", "bidirectional"), ("13", "IO1", "bidirectional"),
            ("16", "IO10", "bidirectional"), ("18", "IO4", "bidirectional")]
esp_right = [("19", "IO5", "bidirectional"), ("20", "IO6", "bidirectional"),
             ("21", "IO7", "bidirectional"), ("22", "IO8", "bidirectional"),
             ("23", "IO9", "bidirectional"), ("26", "IO18", "bidirectional"),
             ("27", "IO19", "bidirectional"), ("30", "RXD0", "bidirectional"),
             ("31", "TXD0", "bidirectional")]
gnd = "1+2+11+14+" + "+".join(str(n) for n in range(36, 54))
nc = "4+7+9+10+15+17+24+25+28+29+32+33+34+35"
S.append(M.make("ESP32-C3-MINI-1", "U", "ESP32-C3-MINI-1-N4",
                "RF_Module:ESP32-C3-MINI-1", "parts/esp32-c3-mini-1/datasheet.pdf",
                "RISC-V SoC module, 4MB flash, PCB trace antenna, LCSC C2838502",
                esp_left, esp_right, [], [(gnd, "GND", "power_in")],
                hidden=[(nc, "NC", "no_connect")], w=35.56))

# ---- MAX30101EFD+T (OLGA-14) ------------------------------------------------
S.append(M.make("MAX30101EFD", "U", "MAX30101EFD+T",
                "OptoDevice:MAX30101EFD", "parts/max30101/datasheet.pdf",
                "PPG red/IR/green pulse-ox + HR sensor, VDD 1.8V, LCSC C2859066",
                [("2", "SCL", "input"), ("3", "SDA", "bidirectional"),
                 ("13", "INT", "open_collector")],
                [("9+10", "VLED+", "power_in")],
                [("11", "VDD", "power_in")],
                [("12", "GND", "power_in"), ("4", "PGND", "power_in")],
                hidden=[("1+5+6+7+8+14", "NC", "no_connect")], w=30.48))

# ---- TPS61099DRVR (WSON-6 + exposed pad) ------------------------------------
S.append(M.make("TPS61099DRVR", "U", "TPS61099DRVR",
                "Package_DFN_QFN:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm",
                "parts/tps61099/datasheet.pdf",
                "Sync boost converter, adjustable, LCSC C2842395",
                [("6", "VIN", "power_in"), ("4", "EN", "input"), ("3", "FB", "input")],
                [("5", "SW", "output"), ("2", "VOUT", "power_out")],
                [], [("1+7", "GND", "power_in")], w=25.4))

# ---- TP4054 (SOT-23-5) ------------------------------------------------------
S.append(M.make("TP4054", "U", "TP4054-42-SOT25R",
                "Package_TO_SOT_SMD:SOT-23-5", "parts/tp4054/datasheet.pdf",
                "Single-cell Li-ion linear charger, 4.2V, LCSC C32574",
                [("4", "VCC", "power_in"), ("5", "PROG", "passive")],
                [("3", "BAT", "power_out"), ("1", "CHRG", "open_collector")],
                [], [("2", "GND", "power_in")], w=25.4))

# ---- USBLC6-2SC6 (SOT-23-6) -------------------------------------------------
S.append(M.make("USBLC6-2SC6", "U", "USBLC6-2SC6",
                "Package_TO_SOT_SMD:SOT-23-6", "parts/usblc6/datasheet.pdf",
                "Dual-line USB ESD protection array, LCSC C7519",
                [("1", "I/O1", "bidirectional"), ("3", "I/O2", "bidirectional")],
                [("6", "I/O1", "bidirectional"), ("4", "I/O2", "bidirectional")],
                [("5", "VBUS", "power_in")], [("2", "GND", "power_in")], w=22.86))

for n in ("VSYS", "+4V7", "BAT+"):
    S.append(M.power(n))

open(P, 'w').write(
    '(kicad_symbol_lib (version 20231120) (generator "wearable_v2_gen") '
    '(generator_version "8.0")\n' + ''.join(S) + ')\n')
print("wrote", P)
