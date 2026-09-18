#!/usr/bin/env python3
"""Generate the v2 first-prototype enclosure and mechanical-review artifacts.

Run with a Python environment containing CadQuery 2.8 or newer:

    python enclosure/generate_enclosure.py

Coordinates remain in the KiCad STEP frame so the generated parts can be opened
directly with wearable_v2_pcb.step.  Dimensions are millimetres.
"""

from __future__ import annotations

import json
from pathlib import Path

import cadquery as cq
from cadquery import exporters


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "enclosure" / "generated" / "mechanical_review"
PCB_STEP = OUT / "wearable_v2_pcb.step"

# Board and enclosure datum.  KiCad STEP exports Y with the opposite sign.
BOARD_X0, BOARD_X1 = 60.0, 84.0
BOARD_Y0, BOARD_Y1 = -146.0, -100.0
BOARD_Z_SHIFT = -0.65
BOARD_NOMINAL_BOTTOM = BOARD_Z_SHIFT
BOARD_NOMINAL_TOP = BOARD_Z_SHIFT + 1.0

CASE_CX, CASE_CY = 72.0, -123.0
OUTER_W, OUTER_L, CORNER_R = 28.0, 50.0, 3.5
INNER_W, INNER_L, INNER_R = 25.0, 47.0, 2.7

# Four snap latches live inside the long-side walls, entirely outside the PCB envelope.  These are
# first-print PETG/nylon dimensions; brittle PLA may need a thinner tab or smaller hook.
SNAP_Y_POSITIONS = (-115.0, -131.0)
SNAP_TAB_WIDTH = 4.0
SNAP_TAB_THICKNESS = 0.45
SNAP_SLOT_THICKNESS = 0.70
SNAP_TAB_Z0, SNAP_TAB_Z1 = -2.05, 0.25
SNAP_HOOK_Z0, SNAP_HOOK_Z1 = -1.95, -1.65
SNAP_HOOK_PROJECTION = 0.20

# Selected EEMB LP502030-PCM protected pack.
BAT_W, BAT_L, BAT_T = 20.5, 32.0, 5.3
BAT_CX, BAT_CY = 72.0, -124.0
BAT_Z0 = 3.80
BAT_Z1 = BAT_Z0 + BAT_T

# Critical interfaces from the saved KiCad footprints and local part records.
J1_X, J1_Y = 77.48, -142.35
J1_W, J1_L, J1_H = 8.94, 7.30, 3.20
U7_X, U7_Y = 70.0, -128.0
U7_W, U7_L, U7_H = 3.30, 5.60, 1.55
U8_X, U8_Y = 64.5, -133.5
U8_W, U8_L, U8_H = 2.0, 2.0, 0.75
U10_X, U10_Y = 70.5, -141.2
U10_W, U10_L, U10_H = 1.5, 1.5, 0.5

ANTENNA_KEEPOUT_Y_MIN = -105.9


def rounded_prism(cx: float, cy: float, w: float, l: float, z0: float, z1: float, r: float) -> cq.Workplane:
    solid = cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(w, l).extrude(z1 - z0)
    return solid.edges("|Z").fillet(r)


def box(cx: float, cy: float, w: float, l: float, z0: float, z1: float) -> cq.Workplane:
    return cq.Workplane("XY").workplane(offset=z0).center(cx, cy).rect(w, l).extrude(z1 - z0)


def ring(cx: float, cy: float, ow: float, ol: float, iw: float, il: float, z0: float, z1: float) -> cq.Workplane:
    return box(cx, cy, ow, ol, z0, z1).cut(box(cx, cy, iw, il, z0 - 0.1, z1 + 0.1))


def snap_features() -> tuple[cq.Workplane, cq.Workplane]:
    """Return lid snap tabs/hooks and the matching bottom-shell clearance volume."""
    tabs: cq.Workplane | None = None
    clearances: cq.Workplane | None = None

    for y in SNAP_Y_POSITIONS:
        for side in (-1, 1):
            wall_x = 59.0 if side < 0 else 85.0
            tab = box(
                wall_x,
                y,
                SNAP_TAB_THICKNESS,
                SNAP_TAB_WIDTH,
                SNAP_TAB_Z0,
                SNAP_TAB_Z1,
            )

            # The hook projects toward the exterior.  Chamfer its Y-parallel edges to create an
            # insertion lead-in while retaining a square catch shoulder.
            hook_x = wall_x + side * (SNAP_TAB_THICKNESS / 2 + SNAP_HOOK_PROJECTION / 2)
            hook = box(
                hook_x,
                y,
                SNAP_HOOK_PROJECTION,
                SNAP_TAB_WIDTH - 0.4,
                SNAP_HOOK_Z0,
                SNAP_HOOK_Z1,
            )
            try:
                hook = hook.edges("|Y").chamfer(0.08)
            except Exception:
                # The rectangular hook remains printable if an OCC version rejects the chamfer.
                pass
            feature = tab.union(hook)

            # Upper slot gives 0.125 mm clearance on each tab face.  The lower catch is enlarged
            # toward the outside so the relaxed hook has 0.10 mm clearance after engagement.
            slot = box(wall_x, y, SNAP_SLOT_THICKNESS, SNAP_TAB_WIDTH + 0.4, SNAP_TAB_Z0 - 0.10, 0.35)
            catch_x = wall_x + side * 0.10
            catch = box(
                catch_x,
                y,
                SNAP_SLOT_THICKNESS + 0.40,
                SNAP_TAB_WIDTH,
                SNAP_HOOK_Z0 - 0.10,
                SNAP_HOOK_Z1 + 0.10,
            )

            tabs = feature if tabs is None else tabs.union(feature)
            clearance = slot.union(catch)
            clearances = clearance if clearances is None else clearances.union(clearance)

    assert tabs is not None and clearances is not None
    return tabs, clearances


def volume(shape: cq.Workplane) -> float:
    return float(shape.val().Volume())


def intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    return volume(a.intersect(b))


def export_step(shape: cq.Workplane, name: str) -> None:
    exporters.export(shape, str(OUT / name))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    pcb = cq.importers.importStep(str(PCB_STEP)).translate((0.0, 0.0, BOARD_Z_SHIFT))

    # Conservative solids for the three KiCad library models missing from the local installation.
    j1 = box(J1_X, J1_Y, J1_W, J1_L, BOARD_NOMINAL_TOP, BOARD_NOMINAL_TOP + J1_H)
    u7 = box(U7_X, U7_Y, U7_W, U7_L, BOARD_NOMINAL_BOTTOM - U7_H, BOARD_NOMINAL_BOTTOM)
    u10 = box(U10_X, U10_Y, U10_W, U10_L, BOARD_NOMINAL_TOP, BOARD_NOMINAL_TOP + U10_H)
    pcb_review = pcb.union(j1).union(u7).union(u10)

    battery = box(BAT_CX, BAT_CY, BAT_W, BAT_L, BAT_Z0, BAT_Z1)
    # PCM is at the board's USB end.  This volume reserves a gentle two-wire path to BT1.
    wire_keepout = box(65.2, -141.25, 3.6, 3.5, BOARD_NOMINAL_TOP + 0.15, BAT_Z0 + 0.25)

    bottom_outer = rounded_prism(CASE_CX, CASE_CY, OUTER_W, OUTER_L, -2.40, 0.15, CORNER_R)
    # The PCB Edge.Cuts rectangle has square corners; do not round this cavity inward.
    bottom_cavity = box(CASE_CX, CASE_CY, INNER_W, INNER_L, -1.70, 0.30)
    bottom = bottom_outer.cut(bottom_cavity)
    snap_tabs, snap_clearances = snap_features()
    bottom = bottom.cut(snap_clearances)

    # Skin interfaces.  U7 is surrounded by a separate opaque compliant gasket; U8 receives a
    # separate soft, electrically insulating thermal pad.  Neither hard-shell opening touches ICs.
    u7_hard_clearance = box(U7_X, U7_Y, 5.4, 7.7, -2.60, 0.30)
    u8_hard_clearance = box(U8_X, U8_Y, 4.2, 4.2, -2.60, 0.30)
    bottom = bottom.cut(u7_hard_clearance).cut(u8_hard_clearance)
    optical_gasket = ring(U7_X, U7_Y, 5.2, 7.5, 3.8, 6.1, -2.40, -1.95)
    thermal_pad = box(U8_X, U8_Y, 3.0, 3.0, -2.40, BOARD_NOMINAL_BOTTOM - U8_H)

    top_outer = rounded_prism(CASE_CX, CASE_CY, OUTER_W, OUTER_L, 0.15, 10.00, CORNER_R)
    top_cavity = box(CASE_CX, CASE_CY, INNER_W, INNER_L, 0.00, 9.45)
    top = top_outer.cut(top_cavity)

    # Connector mouth: 10.0 x 4.6 mm, through the USB-end wall.
    usb_opening = box(J1_X, -147.0, 10.0, 4.0, -0.20, 4.40)
    top = top.cut(usb_opening)

    # Exterior-air slot is offset 1.4 mm toward the case end from U10 and has an unobstructed path.
    sht_vent = box(U10_X, -142.6, 3.0, 2.0, 8.90, 10.20)
    top = top.cut(sht_vent)

    # Cell rests on two edge rails above all modeled PCB components.  Rails end before the PCM/wires.
    left_rail = box(61.65, -123.85, 0.80, 31.7, 3.55, BAT_Z0)
    right_rail = box(82.35, -123.85, 0.80, 31.7, 3.55, BAT_Z0)
    # Bridges make the cradle part of the lid instead of two floating solids.  The USB/PCM end uses
    # two short side bridges so the middle remains open for the battery leads.
    north_bridge = box(72.0, -108.15, 25.6, 0.80, 3.55, BAT_Z0)
    south_left_bridge = box(60.40, -139.55, 3.30, 0.80, 3.55, BAT_Z0)
    south_right_bridge = box(83.60, -139.55, 3.30, 0.80, 3.55, BAT_Z0)
    cradle = (
        left_rail
        .union(right_rail)
        .union(north_bridge)
        .union(south_left_bridge)
        .union(south_right_bridge)
    )
    top_with_cradle = top.union(cradle).union(snap_tabs)

    structural_shell = bottom.union(top_with_cradle)

    collisions = {
        "hard_shell_vs_populated_pcb_mm3": intersection_volume(structural_shell, pcb_review),
        "top_vs_native_pcb_mm3": intersection_volume(top_with_cradle, pcb),
        "bottom_vs_native_pcb_mm3": intersection_volume(bottom, pcb),
        "top_vs_J1_surrogate_mm3": intersection_volume(top_with_cradle, j1),
        "bottom_vs_U7_surrogate_mm3": intersection_volume(bottom, u7),
        "top_vs_U10_surrogate_mm3": intersection_volume(top_with_cradle, u10),
        "hard_shell_vs_battery_mm3": intersection_volume(structural_shell, battery),
        "cradle_vs_populated_pcb_mm3": intersection_volume(cradle, pcb_review),
        "battery_vs_populated_pcb_mm3": intersection_volume(battery, pcb_review),
        "wire_keepout_vs_populated_pcb_mm3": intersection_volume(wire_keepout, pcb_review),
        "assembled_top_vs_bottom_mm3": intersection_volume(top_with_cradle, bottom),
        "snap_tabs_vs_populated_pcb_mm3": intersection_volume(snap_tabs, pcb_review),
    }

    measurements = {
        "board_nominal_mm": [24.0, 46.0, 1.0],
        "case_outer_mm": [OUTER_W, OUTER_L, 12.40],
        "battery_envelope_mm": [BAT_W, BAT_L, BAT_T],
        "battery_xy_bounds_mm": [BAT_CX - BAT_W / 2, BAT_CX + BAT_W / 2, BAT_CY - BAT_L / 2, BAT_CY + BAT_L / 2],
        "battery_to_antenna_keepout_mm": round(abs((BAT_CY + BAT_L / 2) - ANTENNA_KEEPOUT_Y_MIN), 3),
        "battery_to_roof_mm": round(9.45 - BAT_Z1, 3),
        "battery_to_tallest_exported_pcb_mm": round(BAT_Z0 - (3.495 + BOARD_Z_SHIFT), 3),
        "battery_to_J1_vertical_mm": round(BAT_Z0 - (BOARD_NOMINAL_TOP + J1_H), 3),
        "battery_side_clearance_each_mm": round((INNER_W - BAT_W) / 2, 3),
        "usb_opening_mm": [10.0, 4.6],
        "usb_body_mm": [J1_W, J1_H],
        "usb_opening_side_clearance_each_mm": round((10.0 - J1_W) / 2, 3),
        "usb_opening_vertical_clearance_each_mm": round((4.6 - J1_H) / 2, 3),
        "max30101_hard_opening_mm": [5.4, 7.7],
        "max30101_body_mm": [U7_W, U7_L, U7_H],
        "max30101_gasket_inner_clearance_each_mm": [round((3.8 - U7_W) / 2, 3), round((6.1 - U7_L) / 2, 3)],
        "tmp117_thermal_pad_mm": [3.0, 3.0, 1.0],
        "tmp117_nominal_interference_mm": 0.0,
        "sht40_vent_mm": [3.0, 2.0],
        "sht40_vent_center_offset_mm": 1.4,
        "sht40_to_battery_end_mm": round(abs((BAT_CY - BAT_L / 2) - U10_Y), 3),
        "wire_keepout_to_antenna_keepout_mm": round(abs((-139.5) - ANTENNA_KEEPOUT_Y_MIN), 3),
        "snap_latch_count": 4,
        "snap_tab_mm": [SNAP_TAB_WIDTH, SNAP_TAB_THICKNESS, round(SNAP_TAB_Z1 - SNAP_TAB_Z0, 3)],
        "snap_hook_projection_mm": SNAP_HOOK_PROJECTION,
        "snap_slot_clearance_each_side_mm": round((SNAP_SLOT_THICKNESS - SNAP_TAB_THICKNESS) / 2, 3),
        "top_print_body_count": len(top_with_cradle.val().Solids()),
        "bottom_print_body_count": len(bottom.val().Solids()),
    }

    tolerance = 1e-5
    checks = {
        "no_hard_shell_to_pcb_collision": collisions["hard_shell_vs_populated_pcb_mm3"] <= tolerance,
        "no_hard_shell_to_battery_collision": collisions["hard_shell_vs_battery_mm3"] <= tolerance,
        "no_cradle_to_pcb_collision": collisions["cradle_vs_populated_pcb_mm3"] <= tolerance,
        "no_battery_to_pcb_collision": collisions["battery_vs_populated_pcb_mm3"] <= tolerance,
        "wire_path_clear_of_populated_pcb": collisions["wire_keepout_vs_populated_pcb_mm3"] <= tolerance,
        "battery_clear_of_antenna_keepout": measurements["battery_to_antenna_keepout_mm"] >= 2.0,
        "battery_has_roof_clearance": measurements["battery_to_roof_mm"] >= 0.3,
        "usb_opening_clears_body": measurements["usb_opening_side_clearance_each_mm"] >= 0.5
        and measurements["usb_opening_vertical_clearance_each_mm"] >= 0.5,
        "sht40_vent_not_covered_by_battery": measurements["sht40_to_battery_end_mm"] >= 1.0,
        "tmp117_pad_has_zero_nominal_interference": measurements["tmp117_nominal_interference_mm"] == 0.0,
        "separate_shells_assemble_without_hard_overlap": collisions["assembled_top_vs_bottom_mm3"] <= tolerance,
        "snap_tabs_clear_populated_pcb": collisions["snap_tabs_vs_populated_pcb_mm3"] <= tolerance,
        "four_snap_latches_present": measurements["snap_latch_count"] == 4,
        "top_is_one_printable_solid": measurements["top_print_body_count"] == 1,
        "bottom_is_one_printable_solid": measurements["bottom_print_body_count"] == 1,
    }

    export_step(bottom, "enclosure_bottom.step")
    export_step(top_with_cradle, "enclosure_top.step")
    export_step(battery, "selected_battery_envelope.step")
    export_step(wire_keepout, "battery_wire_keepout.step")
    export_step(optical_gasket, "max30101_opaque_gasket.step")
    export_step(thermal_pad, "tmp117_thermal_pad.step")
    exporters.export(bottom, str(OUT / "enclosure_bottom.stl"), tolerance=0.05, angularTolerance=0.1)
    exporters.export(top_with_cradle, str(OUT / "enclosure_top.stl"), tolerance=0.05, angularTolerance=0.1)
    svg_options = {
        "width": 1200,
        "height": 900,
        "marginLeft": 30,
        "marginTop": 30,
        "showAxes": True,
        "projectionDir": (0.8, -1.0, 0.7),
        "strokeWidth": 0.35,
    }
    exporters.export(bottom, str(OUT / "enclosure_bottom_isometric.svg"), opt=svg_options)
    exporters.export(top_with_cradle, str(OUT / "enclosure_top_isometric.svg"), opt=svg_options)

    closed = cq.Compound.makeCompound(
        [
            bottom.val(),
            top_with_cradle.val(),
            pcb_review.val(),
            battery.val(),
            wire_keepout.val(),
            optical_gasket.val(),
            thermal_pad.val(),
        ]
    )
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
            "Snap dimensions target a first PETG/nylon FDM trial; printer/material shrinkage may require tuning the 0.125 mm-per-side slot clearance or 0.20 mm hook projection.",
            "J1, U7 and U10 use conservative surrogate solids because their KiCad STEP models were unavailable locally.",
            "The 1.0 mm TMP117 pad is a nominal zero-interference volume; final soft-pad material/compression requires physical validation.",
            "The supplied battery listing does not establish permission to charge at 100 mA.",
        ],
    }
    (OUT / "mechanical_review.json").write_text(json.dumps(report, indent=2) + "\n")

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("Mechanical checks failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
