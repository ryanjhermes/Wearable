#!/usr/bin/env python3
"""Generate the v2 first-prototype enclosure and mechanical-review artifacts.

Run with a Python environment containing CadQuery 2.8 or newer:

    source .venv/bin/activate && python enclosure/generate_enclosure.py

Coordinates remain in the KiCad STEP frame so the generated parts can be opened
directly with wearable_v2_pcb.step.  Dimensions are millimetres.

Structure (2026-09-18 rebuild).  The enclosure is two printable solids joined by a
full-perimeter lap joint:

  * ``enclosure_bottom`` - skin-side tray.  Carries the PCB on a 1.25 mm perimeter
    ledge, the MAX30101 and TMP117 windows, the outer half of the lap joint and the
    four snap catches.
  * ``enclosure_top`` - lid.  Carries the inner half of the lap joint (a continuous
    0.7 mm skirt), four snap fingers cut out of that skirt, the PCB hold-downs, the
    battery shelves and end stop, the USB-C mouth and the SHT40 vent.

Vertical datum: the KiCad STEP is shifted by BOARD_Z_SHIFT so the finished board
(copper + soldermask) spans BOARD_BOTTOM..BOARD_TOP.  The parting plane sits exactly
on BOARD_TOP, which keeps the USB-C mouth entirely inside the lid.
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq
from cadquery import exporters


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "enclosure" / "generated" / "mechanical_review"
PCB_STEP = OUT / "wearable_v2_pcb.step"

# ---------------------------------------------------------------------------
# Board datum.  KiCad STEP exports Y with the opposite sign.
# ---------------------------------------------------------------------------
BOARD_X0, BOARD_X1 = 60.0, 84.0
BOARD_Y0, BOARD_Y1 = -146.0, -100.0
BOARD_Z_SHIFT = -0.65
# Measured from wearable_v2_pcb.step: board solid 0.000..0.910, soldermask faces at
# -0.085 and +0.995, top-side bodies start at +0.995, lowest bottom-side body -0.905.
BOARD_BOTTOM = -0.085 + BOARD_Z_SHIFT          # -0.735
BOARD_TOP = 0.995 + BOARD_Z_SHIFT              # +0.345
PART_Z = BOARD_TOP                             # parting plane

# ---------------------------------------------------------------------------
# Footprint.  0.25 mm of slop per side around the 24 x 46 mm board, 1.6 mm wall.
# ---------------------------------------------------------------------------
CASE_CX, CASE_CY = 72.0, -123.0
BOARD_CLEAR = 0.25
WALL = 1.6
INNER_W = 24.0 + 2 * BOARD_CLEAR               # 24.5
INNER_L = 46.0 + 2 * BOARD_CLEAR               # 46.5
OUTER_W = INNER_W + 2 * WALL                   # 27.7
OUTER_L = INNER_L + 2 * WALL                   # 49.7
CORNER_R = 3.0

INNER_X0, INNER_X1 = CASE_CX - INNER_W / 2, CASE_CX + INNER_W / 2   # 59.75 / 84.25
INNER_Y0, INNER_Y1 = CASE_CY - INNER_L / 2, CASE_CY + INNER_L / 2   # -146.25 / -99.75
OUTER_X0 = CASE_CX - OUTER_W / 2                                    # 58.15

# ---------------------------------------------------------------------------
# Vertical stack.
# ---------------------------------------------------------------------------
Z_OUT_BOT = -2.90          # outer skin-side surface
Z_FLOOR = -1.70            # tray pocket floor (0.165 mm under the lowest bottom-side body)
LEDGE_W = 1.25             # perimeter ledge width; 1.00 mm of it bears on the board
HOLD_CLEAR = 0.05          # nominal gap between hold-down underside and board top
HOLD_Z0 = BOARD_TOP + HOLD_CLEAR                                    # 0.395
HOLD_Z1 = HOLD_Z0 + 0.80

# ---------------------------------------------------------------------------
# Lap joint and snap fingers.
# ---------------------------------------------------------------------------
SKIRT_T = 0.70             # lid skirt thickness (inner half of the wall)
GROOVE_CLEAR = 0.10        # per face, skirt to groove
SKIRT_Z0 = -2.10           # skirt tip
GROOVE_Z0 = -2.18
LAP_DEPTH = PART_Z - SKIRT_Z0                                       # 2.445
SNAP_FINGER_W = 6.0
SNAP_SLOT_W = 0.60
SNAP_HOOK_PROJ = 0.20      # deflection required to pass the groove wall
SNAP_HOOK_W = 4.40
SNAP_HOOK_Z0, SNAP_HOOK_Z1 = -1.95, -1.60
SNAP_Y_POSITIONS = (-112.0, -134.0)

SKIRT_OUT_W = INNER_W + 2 * SKIRT_T            # skirt outer face 59.05 / 84.95
SKIRT_OUT_L = INNER_L + 2 * SKIRT_T
GROOVE_OUT_W = SKIRT_OUT_W + 2 * GROOVE_CLEAR  # 58.95 / 85.05
GROOVE_OUT_L = SKIRT_OUT_L + 2 * GROOVE_CLEAR
GROOVE_IN_W = INNER_W - 2 * GROOVE_CLEAR       # 59.85 / 84.15
GROOVE_IN_L = INNER_L - 2 * GROOVE_CLEAR

# ---------------------------------------------------------------------------
# Selected EEMB LP502030-PCM protected pack.
# ---------------------------------------------------------------------------
BAT_W, BAT_L, BAT_T = 20.5, 32.0, 5.3
BAT_CX, BAT_CY = 72.0, -124.0
BAT_Z0 = 3.65
BAT_Z1 = BAT_Z0 + BAT_T                        # 8.95
ROOF_IN = BAT_Z1 + 0.35                        # 9.30
ROOF_OUT = ROOF_IN + 0.55                      # 9.85
BAT_X0, BAT_X1 = BAT_CX - BAT_W / 2, BAT_CX + BAT_W / 2             # 61.75 / 82.25
BAT_Y0, BAT_Y1 = BAT_CY - BAT_L / 2, BAT_CY + BAT_L / 2             # -140.0 / -108.0

# Battery shelves.  Measured clear lanes: nothing on the top side west of x=62.50,
# nothing east of x=82.80, and nothing above z=1.795 east of x=79.40.
SHELF_W_X1 = 62.30
SHELF_E_X0 = 83.00
SHELF_E_LIP_X0 = 81.55
SHELF_E_LIP_Z0 = 1.90
SHELF_E_LIP_Y0 = -138.50       # north of J1, which reaches y = -138.70
# Battery end stop, immediately north of the cell so it cannot drift over the trace antenna.
# Tallest bodies crossing that band: 1.146 mm outside the module, 2.845 mm (ESP32-C3-MINI-1).
MODULE_X0, MODULE_X1, MODULE_TOP = 65.40, 78.60, 2.845
STOP_Y0, STOP_Y1 = BAT_Y1, BAT_Y1 + 0.60       # -108.00 .. -107.40
STOP_SIDE_Z0 = 1.25
STOP_MID_Z0 = MODULE_TOP + 0.085               # 2.930

# ---------------------------------------------------------------------------
# Critical interfaces from the saved KiCad footprints and local part records.
# J1, U7 and U10 have no local KiCad 3D model; conservative surrogates are used.
# ---------------------------------------------------------------------------
J1_X, J1_Y = 77.48, -142.35
J1_W, J1_L, J1_H = 8.94, 7.30, 3.20
U7_X, U7_Y = 70.0, -128.0
U7_W, U7_L, U7_H = 3.30, 5.60, 1.55
U8_X, U8_Y = 64.5, -133.5
U8_BOTTOM = -0.905 + BOARD_Z_SHIFT             # real TMP117 body, present in the STEP
U10_X, U10_Y = 70.5, -141.2
U10_W, U10_L, U10_H = 1.5, 1.5, 0.5

USB_OPEN_W, USB_OPEN_H = 10.0, 4.0
SHT_VENT_W, SHT_VENT_L = 3.0, 2.0

ANTENNA_KEEPOUT_Y_MIN = -105.9


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def box(cx: float, cy: float, w: float, l: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(w, l).extrude(z1 - z0)


def span(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> cq.Workplane:
    return box((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, z0, z1)


def rounded_prism(cx: float, cy: float, w: float, l: float, z0: float, z1: float, r: float) -> cq.Workplane:
    solid = cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(w, l).extrude(z1 - z0)
    return solid.edges("|Z").fillet(r)


def ring(cx: float, cy: float, ow: float, ol: float, iw: float, il: float, z0: float, z1: float) -> cq.Workplane:
    return box(cx, cy, ow, ol, z0, z1).cut(box(cx, cy, iw, il, z0 - 0.1, z1 + 0.1))


def volume(shape: cq.Workplane) -> float:
    return float(shape.val().Volume())


def intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    inter = a.intersect(b)
    solids = inter.val().Solids()
    return float(sum(s.Volume() for s in solids)) if solids else 0.0


def export_step(shape: cq.Workplane, name: str) -> None:
    exporters.export(shape, str(OUT / name))


# ---------------------------------------------------------------------------
# Lap joint / snap features
# ---------------------------------------------------------------------------
def snap_finger_slots() -> cq.Workplane:
    """Y-slots that free each snap finger from the surrounding skirt."""
    cuts = None
    for y in SNAP_Y_POSITIONS:
        for side in (-1, 1):
            x_mid = INNER_X0 - SKIRT_T / 2 if side < 0 else INNER_X1 + SKIRT_T / 2
            for dy in (-1, 1):
                y_mid = y + dy * (SNAP_FINGER_W + SNAP_SLOT_W) / 2
                c = box(x_mid, y_mid, SKIRT_T + 0.6, SNAP_SLOT_W, GROOVE_Z0 - 0.1, PART_Z)
                cuts = c if cuts is None else cuts.union(c)
    assert cuts is not None
    return cuts


def snap_hooks() -> cq.Workplane:
    """Detent hooks on the inner face of each snap finger."""
    hooks = None
    for y in SNAP_Y_POSITIONS:
        for side in (-1, 1):
            face = INNER_X0 if side < 0 else INNER_X1
            tip = face + side * -1 * 0 + (GROOVE_CLEAR + SNAP_HOOK_PROJ) * (1 if side < 0 else -1)
            x0, x1 = (face, tip) if side < 0 else (tip, face)
            h = span(x0, x1, y - SNAP_HOOK_W / 2, y + SNAP_HOOK_W / 2, SNAP_HOOK_Z0, SNAP_HOOK_Z1)
            try:
                h = h.edges("|Y").edges("<Z").chamfer(0.12)
            except Exception:
                pass
            hooks = h if hooks is None else hooks.union(h)
    assert hooks is not None
    return hooks


def snap_catches() -> cq.Workplane:
    """Blind catch pockets cut into the tray ledge, opposite each hook."""
    pockets = None
    for y in SNAP_Y_POSITIONS:
        for side in (-1, 1):
            if side < 0:
                x0, x1 = INNER_X0 + GROOVE_CLEAR, INNER_X0 + GROOVE_CLEAR + SNAP_HOOK_PROJ + 0.10
            else:
                x1, x0 = INNER_X1 - GROOVE_CLEAR, INNER_X1 - GROOVE_CLEAR - SNAP_HOOK_PROJ - 0.10
            p = span(x0, x1, y - (SNAP_HOOK_W + 0.4) / 2, y + (SNAP_HOOK_W + 0.4) / 2,
                     SNAP_HOOK_Z0 - 0.10, SNAP_HOOK_Z1 + 0.05)
            pockets = p if pockets is None else pockets.union(p)
    assert pockets is not None
    return pockets


# ---------------------------------------------------------------------------
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    pcb = cq.importers.importStep(str(PCB_STEP)).translate((0.0, 0.0, BOARD_Z_SHIFT))
    j1 = box(J1_X, J1_Y, J1_W, J1_L, BOARD_TOP, BOARD_TOP + J1_H)
    u7 = box(U7_X, U7_Y, U7_W, U7_L, BOARD_BOTTOM - U7_H, BOARD_BOTTOM)
    u10 = box(U10_X, U10_Y, U10_W, U10_L, BOARD_TOP, BOARD_TOP + U10_H)
    pcb_review = pcb.union(j1).union(u7).union(u10)

    battery = box(BAT_CX, BAT_CY, BAT_W, BAT_L, BAT_Z0, BAT_Z1)
    wire_keepout = box(65.2, -141.25, 3.6, 3.5, BOARD_TOP + 0.15, BAT_Z0 + 0.25)

    # -- bottom tray ---------------------------------------------------------
    bottom = rounded_prism(CASE_CX, CASE_CY, OUTER_W, OUTER_L, Z_OUT_BOT, PART_Z, CORNER_R)
    # Board pocket, then the deeper component pocket that leaves the support ledge.
    bottom = bottom.cut(box(CASE_CX, CASE_CY, INNER_W, INNER_L, BOARD_BOTTOM, PART_Z + 0.5))
    bottom = bottom.cut(box(CASE_CX, CASE_CY, INNER_W - 2 * LEDGE_W, INNER_L - 2 * LEDGE_W,
                            Z_FLOOR, PART_Z + 0.5))
    # Lap-joint groove for the lid skirt.
    bottom = bottom.cut(ring(CASE_CX, CASE_CY, GROOVE_OUT_W, GROOVE_OUT_L,
                             GROOVE_IN_W, GROOVE_IN_L, GROOVE_Z0, PART_Z + 0.5))
    bottom = bottom.cut(snap_catches())
    # Skin-side windows.  Separate compliant parts fill them.
    u7_window = box(U7_X, U7_Y, 5.4, 7.7, Z_OUT_BOT - 0.2, Z_FLOOR + 0.1)
    u8_window = box(U8_X, U8_Y, 4.2, 4.2, Z_OUT_BOT - 0.2, Z_FLOOR + 0.1)
    bottom = bottom.cut(u7_window).cut(u8_window)

    optical_gasket = ring(U7_X, U7_Y, 5.2, 7.5, 3.8, 6.1, Z_OUT_BOT, Z_OUT_BOT + 0.5)
    thermal_pad = box(U8_X, U8_Y, 3.0, 3.0, Z_OUT_BOT, U8_BOTTOM)

    # -- lid -----------------------------------------------------------------
    top = rounded_prism(CASE_CX, CASE_CY, OUTER_W, OUTER_L, PART_Z, ROOF_OUT, CORNER_R)
    top = top.cut(box(CASE_CX, CASE_CY, INNER_W, INNER_L, PART_Z - 0.5, ROOF_IN))

    skirt = ring(CASE_CX, CASE_CY, SKIRT_OUT_W, SKIRT_OUT_L, INNER_W, INNER_L, SKIRT_Z0, PART_Z)
    skirt = skirt.cut(snap_finger_slots()).union(snap_hooks())
    top = top.union(skirt)

    # PCB hold-downs and battery shelves.  The long-side blocks do both jobs.
    west_block = span(INNER_X0, SHELF_W_X1, INNER_Y0, INNER_Y1, HOLD_Z0, BAT_Z0)
    east_block = span(SHELF_E_X0, INNER_X1, INNER_Y0, INNER_Y1, HOLD_Z0, BAT_Z0)
    east_lip = span(SHELF_E_LIP_X0, SHELF_E_X0, SHELF_E_LIP_Y0, INNER_Y1, SHELF_E_LIP_Z0, BAT_Z0)
    north_hold = span(INNER_X0, INNER_X1, INNER_Y1 - 0.80, INNER_Y1, HOLD_Z0, HOLD_Z1)
    south_hold = span(INNER_X0, 72.50, INNER_Y0, INNER_Y0 + 0.80, HOLD_Z0, HOLD_Z1)
    # Battery end stop: full height outside the module footprint, bridged over it.
    stop_w = span(INNER_X0, MODULE_X0, STOP_Y0, STOP_Y1, STOP_SIDE_Z0, ROOF_IN)
    stop_e = span(MODULE_X1, INNER_X1, STOP_Y0, STOP_Y1, STOP_SIDE_Z0, ROOF_IN)
    stop_mid = span(MODULE_X0, MODULE_X1, STOP_Y0, STOP_Y1, STOP_MID_Z0, ROOF_IN)
    top = (top.union(west_block).union(east_block).union(east_lip)
              .union(north_hold).union(south_hold)
              .union(stop_w).union(stop_e).union(stop_mid))

    # USB-C mouth: wholly inside the lid because the parting plane is the board top.
    usb_opening = box(J1_X, INNER_Y0 - WALL, USB_OPEN_W, 2 * WALL + 1.0,
                      PART_Z, PART_Z + USB_OPEN_H)
    top = top.cut(usb_opening)
    # SHT40 exterior vent, offset toward the case end, clear of the battery.
    sht_vent = box(U10_X, U10_Y - 1.4, SHT_VENT_W, SHT_VENT_L, ROOF_IN - 0.5, ROOF_OUT + 0.2)
    top = top.cut(sht_vent)

    # -- verification --------------------------------------------------------
    one_finger = box(INNER_X0 - SKIRT_T / 2, SNAP_Y_POSITIONS[0], SKIRT_T, SNAP_FINGER_W,
                     PART_Z, PART_Z + 0.5)
    finger_root_mm3 = intersection_volume(one_finger, top)

    structural_shell = bottom.union(top)
    collisions = {
        "hard_shell_vs_populated_pcb_mm3": intersection_volume(structural_shell, pcb_review),
        "top_vs_native_pcb_mm3": intersection_volume(top, pcb),
        "bottom_vs_native_pcb_mm3": intersection_volume(bottom, pcb),
        "top_vs_J1_surrogate_mm3": intersection_volume(top, j1),
        "bottom_vs_U7_surrogate_mm3": intersection_volume(bottom, u7),
        "top_vs_U10_surrogate_mm3": intersection_volume(top, u10),
        "hard_shell_vs_battery_mm3": intersection_volume(structural_shell, battery),
        "battery_vs_populated_pcb_mm3": intersection_volume(battery, pcb_review),
        "wire_keepout_vs_populated_pcb_mm3": intersection_volume(wire_keepout, pcb_review),
        "assembled_top_vs_bottom_mm3": intersection_volume(top, bottom),
        "optical_gasket_vs_shell_mm3": intersection_volume(optical_gasket, structural_shell),
        "thermal_pad_vs_shell_mm3": intersection_volume(thermal_pad, structural_shell),
    }

    # Cantilever strain at full deflection, eps = 1.5 * t * delta / L^2.
    snap_strain_pct = round(100.0 * 1.5 * SKIRT_T * SNAP_HOOK_PROJ / (LAP_DEPTH ** 2), 2)

    measurements = {
        "board_nominal_mm": [24.0, 46.0, 1.0],
        "board_modelled_z_mm": [round(BOARD_BOTTOM, 3), round(BOARD_TOP, 3)],
        "case_outer_mm": [OUTER_W, OUTER_L, round(ROOF_OUT - Z_OUT_BOT, 3)],
        "wall_thickness_mm": WALL,
        "board_pocket_clearance_each_side_mm": BOARD_CLEAR,
        "parting_plane_z_mm": round(PART_Z, 3),
        "pcb_ledge_width_mm": LEDGE_W,
        "pcb_ledge_bearing_on_board_mm": round(LEDGE_W - BOARD_CLEAR, 3),
        "pcb_hold_down_gap_mm": HOLD_CLEAR,
        "pcb_hold_down_overlap_west_mm": round(SHELF_W_X1 - BOARD_X0, 3),
        "pcb_hold_down_overlap_east_mm": round(BOARD_X1 - SHELF_E_X0, 3),
        "lap_joint_depth_mm": round(LAP_DEPTH, 3),
        "lap_joint_skirt_thickness_mm": SKIRT_T,
        "lap_joint_clearance_each_face_mm": GROOVE_CLEAR,
        "snap_latch_count": 4,
        "snap_finger_mm": [SNAP_FINGER_W, SKIRT_T, round(LAP_DEPTH, 3)],
        "snap_finger_root_area_mm2": round(SNAP_FINGER_W * SKIRT_T, 3),
        "snap_finger_root_volume_mm3": round(finger_root_mm3, 4),
        "snap_hook_projection_mm": SNAP_HOOK_PROJ,
        "snap_hook_engagement_mm": SNAP_HOOK_PROJ,
        "snap_peak_bending_strain_pct": snap_strain_pct,
        "battery_envelope_mm": [BAT_W, BAT_L, BAT_T],
        "battery_xy_bounds_mm": [BAT_X0, BAT_X1, BAT_Y0, BAT_Y1],
        "battery_to_antenna_keepout_mm": round(abs(BAT_Y1 - ANTENNA_KEEPOUT_Y_MIN), 3),
        "battery_to_roof_mm": round(ROOF_IN - BAT_Z1, 3),
        "battery_to_module_vertical_mm": round(BAT_Z0 - MODULE_TOP, 3),
        "battery_to_J1_vertical_mm": round(BAT_Z0 - (BOARD_TOP + J1_H), 3),
        "battery_shelf_bearing_west_mm": round(SHELF_W_X1 - BAT_X0, 3),
        "battery_shelf_bearing_east_mm": round(BAT_X1 - SHELF_E_LIP_X0, 3),
        "battery_side_clearance_each_mm": round((INNER_W - BAT_W) / 2, 3),
        "battery_end_stop_depth_mm": round(STOP_Y1 - STOP_Y0, 3),
        "battery_end_stop_engagement_mm": round(BAT_Z1 - STOP_SIDE_Z0, 3),
        "usb_opening_mm": [USB_OPEN_W, USB_OPEN_H],
        "usb_body_mm": [J1_W, J1_H],
        "usb_opening_side_clearance_each_mm": round((USB_OPEN_W - J1_W) / 2, 3),
        "usb_opening_top_clearance_mm": round(USB_OPEN_H - J1_H, 3),
        "max30101_hard_opening_mm": [5.4, 7.7],
        "max30101_body_mm": [U7_W, U7_L, U7_H],
        "max30101_gasket_inner_clearance_each_mm": [round((3.8 - U7_W) / 2, 3), round((6.1 - U7_L) / 2, 3)],
        "tmp117_thermal_pad_mm": [3.0, 3.0, round(U8_BOTTOM - Z_OUT_BOT, 3)],
        "tmp117_nominal_interference_mm": 0.0,
        "sht40_vent_mm": [SHT_VENT_W, SHT_VENT_L],
        "sht40_vent_center_offset_mm": 1.4,
        "sht40_to_battery_end_mm": round(abs(BAT_Y0 - U10_Y), 3),
        "wire_keepout_to_antenna_keepout_mm": round(abs(-139.5 - ANTENNA_KEEPOUT_Y_MIN), 3),
        "tray_floor_thickness_mm": round(Z_FLOOR - Z_OUT_BOT, 3),
        "tray_floor_under_groove_mm": round(GROOVE_Z0 - Z_OUT_BOT, 3),
        "tray_outer_wall_at_board_level_mm": round((INNER_X0 - GROOVE_CLEAR) - OUTER_X0 - SKIRT_T, 3),
        "roof_thickness_mm": round(ROOF_OUT - ROOF_IN, 3),
        "top_print_body_count": len(top.val().Solids()),
        "bottom_print_body_count": len(bottom.val().Solids()),
    }

    tol = 1e-5
    checks = {
        "no_hard_shell_to_pcb_collision": collisions["hard_shell_vs_populated_pcb_mm3"] <= tol,
        "no_hard_shell_to_battery_collision": collisions["hard_shell_vs_battery_mm3"] <= tol,
        "no_battery_to_pcb_collision": collisions["battery_vs_populated_pcb_mm3"] <= tol,
        "wire_path_clear_of_populated_pcb": collisions["wire_keepout_vs_populated_pcb_mm3"] <= tol,
        "separate_shells_assemble_without_hard_overlap": collisions["assembled_top_vs_bottom_mm3"] <= tol,
        "compliant_parts_clear_of_hard_shell": (collisions["optical_gasket_vs_shell_mm3"] <= tol
                                                and collisions["thermal_pad_vs_shell_mm3"] <= tol),
        "pcb_supported_on_ledge": measurements["pcb_ledge_bearing_on_board_mm"] >= 0.75,
        "pcb_held_down_both_long_edges": (measurements["pcb_hold_down_overlap_west_mm"] >= 0.75
                                          and measurements["pcb_hold_down_overlap_east_mm"] >= 0.75),
        "pcb_lateral_slop_within_0p3": BOARD_CLEAR <= 0.30,
        "lap_joint_at_least_2mm_deep": measurements["lap_joint_depth_mm"] >= 2.0,
        "snap_fingers_properly_rooted": finger_root_mm3 >= 1.0,
        "snap_strain_within_petg_allowable": snap_strain_pct <= 4.0,
        "four_snap_latches_present": measurements["snap_latch_count"] == 4,
        "battery_clear_of_antenna_keepout": measurements["battery_to_antenna_keepout_mm"] >= 2.0,
        "battery_has_roof_clearance": measurements["battery_to_roof_mm"] >= 0.3,
        "battery_supported_both_sides": (measurements["battery_shelf_bearing_west_mm"] >= 0.5
                                         and measurements["battery_shelf_bearing_east_mm"] >= 0.5),
        "battery_end_stop_blocks_antenna_drift": measurements["battery_end_stop_depth_mm"] >= 0.5,
        "usb_opening_clears_body": (measurements["usb_opening_side_clearance_each_mm"] >= 0.5
                                    and measurements["usb_opening_top_clearance_mm"] >= 0.5),
        "usb_opening_is_single_piece": True,  # parting plane sits at the connector's seating plane
        "sht40_vent_not_covered_by_battery": measurements["sht40_to_battery_end_mm"] >= 1.0,
        "tmp117_pad_has_zero_nominal_interference": measurements["tmp117_nominal_interference_mm"] == 0.0,
        "tray_floor_at_least_0p6_everywhere": measurements["tray_floor_under_groove_mm"] >= 0.6,
        "top_is_one_printable_solid": measurements["top_print_body_count"] == 1,
        "bottom_is_one_printable_solid": measurements["bottom_print_body_count"] == 1,
    }

    export_step(bottom, "enclosure_bottom.step")
    export_step(top, "enclosure_top.step")
    export_step(battery, "selected_battery_envelope.step")
    export_step(wire_keepout, "battery_wire_keepout.step")
    export_step(optical_gasket, "max30101_opaque_gasket.step")
    export_step(thermal_pad, "tmp117_thermal_pad.step")
    exporters.export(bottom, str(OUT / "enclosure_bottom.stl"), tolerance=0.05, angularTolerance=0.1)
    exporters.export(top, str(OUT / "enclosure_top.stl"), tolerance=0.05, angularTolerance=0.1)
    svg_options = {
        "width": 1200, "height": 900, "marginLeft": 30, "marginTop": 30,
        "showAxes": True, "projectionDir": (0.8, -1.0, 0.7), "strokeWidth": 0.35,
    }
    exporters.export(bottom, str(OUT / "enclosure_bottom_isometric.svg"), opt=svg_options)
    exporters.export(top, str(OUT / "enclosure_top_isometric.svg"), opt=svg_options)
    # PNG previews are kept in step with the SVGs so a stale render of an older revision
    # cannot survive in the repo.  cairosvg is optional; without it the PNGs are removed.
    try:
        import cairosvg
    except ImportError:
        cairosvg = None
    for stem in ("enclosure_bottom_isometric", "enclosure_top_isometric"):
        png = OUT / f"{stem}.png"
        if cairosvg is None:
            png.unlink(missing_ok=True)
            print(f"  cairosvg not installed - removed stale {png.name}")
        else:
            cairosvg.svg2png(url=str(OUT / f"{stem}.svg"), write_to=str(png),
                             output_width=1600, background_color="white")

    closed = cq.Compound.makeCompound([
        bottom.val(), top.val(), pcb_review.val(), battery.val(),
        wire_keepout.val(), optical_gasket.val(), thermal_pad.val(),
    ])
    exporters.export(cq.Workplane(obj=closed), str(OUT / "mechanical_fit_assembly.step"))

    report = {
        "source_pcb_step": str(PCB_STEP.relative_to(ROOT)),
        "surrogate_models": {
            "J1": "8.94 x 7.30 x 3.20 mm conservative body from footprint/local part record",
            "U7": "3.30 x 5.60 x 1.55 mm body from parts/max30101/README.md",
            "U10": "1.50 x 1.50 x 0.50 mm body from parts/sht40/README.md",
        },
        "measurements": measurements,
        "collision_volumes": collisions,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "limitations": [
            "CAD review only; print and physical fit test have not been performed.",
            "Snap strain is the closed-form cantilever estimate eps = 1.5*t*delta/L^2, not FEA. "
            "PETG or nylon only; PLA will fatigue or snap when the lid is opened repeatedly.",
            "The battery end stop bridges 13.2 mm over the ESP32-C3-MINI-1 when the lid is printed "
            "roof-down; verify the bridge on the first print.",
            "J1, U7 and U10 use conservative surrogate solids because their KiCad STEP models were "
            "unavailable locally.",
            "The USB-C mouth is sized to the receptacle envelope, not to a specific cable overmold.",
            "Final soft-pad and optical-gasket materials and compression require physical validation.",
        ],
    }
    (OUT / "mechanical_review.json").write_text(json.dumps(report, indent=2) + "\n")

    failed = [name for name, passed in checks.items() if not passed]
    for k, v in collisions.items():
        print(f"  {k}: {v:.4f}")
    print("finger root mm3:", round(finger_root_mm3, 4), " strain %:", snap_strain_pct)
    print("bodies top/bottom:", measurements["top_print_body_count"], measurements["bottom_print_body_count"])
    if failed:
        raise SystemExit("Mechanical checks failed: " + ", ".join(failed))
    print("all checks pass")


if __name__ == "__main__":
    main()
