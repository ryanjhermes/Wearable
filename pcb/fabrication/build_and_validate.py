#!/usr/bin/env python3
"""Build JLCPCB BOM/CPL files from accepted KiCad exports and validate artifacts.

This script does not run ERC, DRC, schematic parity, or PCB analysis.  It treats
pcb/bom_from_schematic.csv and KiCad's raw position exports as authoritative.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FAB = ROOT / "pcb" / "fabrication" / "jlcpcb_standard_pcba"
ASSEMBLY = FAB / "assembly"
GERBERS = FAB / "gerbers"
DRILL = FAB / "drill"
BOM_SOURCE = ROOT / "pcb" / "bom_from_schematic.csv"
BOARD = ROOT / "pcb" / "wearable_v2.kicad_pcb"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(rows)


def expand_refs(text: str) -> list[str]:
    return [ref.strip() for ref in text.split(",") if ref.strip()]


def outline_centerline_bbox(path: Path) -> tuple[float, float, float, float]:
    text = path.read_text()
    fmt = re.search(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%", text)
    if not fmt or fmt.group(2) != fmt.group(4):
        raise ValueError("Unsupported Gerber coordinate format")
    decimal_places = int(fmt.group(2))
    scale = 10**decimal_places
    points = [
        (int(x) / scale, int(y) / scale)
        for x, y in re.findall(r"X(-?\d+)Y(-?\d+)D0[12]\*", text)
    ]
    if not points:
        raise ValueError("No outline centerline points found")
    xs, ys = zip(*points)
    return min(xs), min(ys), max(xs), max(ys)


def main() -> None:
    source_rows = read_csv(BOM_SOURCE)
    bom_refs: list[str] = []
    qty_total = 0
    jlc_bom_rows: list[dict[str, str]] = []
    for row in source_rows:
        refs = expand_refs(row["Refs"])
        bom_refs.extend(refs)
        qty_total += int(row["Qty"])
        if len(refs) != int(row["Qty"]):
            raise SystemExit(f"BOM quantity mismatch for {row['Refs']}")
        jlc_bom_rows.append(
            {
                "Comment": row["Value"],
                "Designator": row["Refs"],
                "Footprint": row["Footprint"],
                "LCSC Part #": row["LCSC"],
            }
        )

    write_csv(
        ASSEMBLY / "jlcpcb_bom.csv",
        ["Comment", "Designator", "Footprint", "LCSC Part #"],
        jlc_bom_rows,
    )

    raw_top = read_csv(ASSEMBLY / "top_cpl_raw.csv")
    raw_bottom = read_csv(ASSEMBLY / "bottom_cpl_raw.csv")
    bom_ref_set = set(bom_refs)

    def convert_cpl(raw_rows: list[dict[str, str]], expected_side: str) -> list[dict[str, str]]:
        converted = []
        for row in raw_rows:
            if row["Ref"] not in bom_ref_set:
                continue
            if row["Side"] != expected_side:
                raise SystemExit(f"Unexpected side for {row['Ref']}: {row['Side']}")
            converted.append(
                {
                    "Designator": row["Ref"],
                    "Mid X": f"{float(row['PosX']):.6f}mm",
                    "Mid Y": f"{float(row['PosY']):.6f}mm",
                    "Layer": "Top" if expected_side == "top" else "Bottom",
                    "Rotation": f"{float(row['Rot']):.6f}",
                }
            )
        return converted

    top_cpl = convert_cpl(raw_top, "top")
    bottom_cpl = convert_cpl(raw_bottom, "bottom")
    cpl_fields = ["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]
    write_csv(ASSEMBLY / "jlcpcb_top_cpl.csv", cpl_fields, top_cpl)
    write_csv(ASSEMBLY / "jlcpcb_bottom_cpl.csv", cpl_fields, bottom_cpl)

    placed = {row["Designator"] for row in top_cpl + bottom_cpl}
    excluded = sorted(({row["Ref"] for row in raw_top + raw_bottom}) - placed)
    expected_excluded = {"BT1", *(f"TP{i}" for i in range(1, 13))}

    outline = outline_centerline_bbox(GERBERS / "wearable_v2-Edge_Cuts.gm1")
    outline_w = round(outline[2] - outline[0], 6)
    outline_h = round(outline[3] - outline[1], 6)

    gerber_names = {path.name for path in GERBERS.iterdir() if path.is_file()}
    expected_copper = {
        "wearable_v2-F_Cu.gtl",
        "wearable_v2-In1_Cu.g1",
        "wearable_v2-In2_Cu.g2",
        "wearable_v2-B_Cu.gbl",
    }
    expected_fab_layers = expected_copper | {
        "wearable_v2-F_Paste.gtp",
        "wearable_v2-B_Paste.gbp",
        "wearable_v2-F_Silkscreen.gto",
        "wearable_v2-B_Silkscreen.gbo",
        "wearable_v2-F_Mask.gts",
        "wearable_v2-B_Mask.gbs",
        "wearable_v2-Edge_Cuts.gm1",
    }

    board_text = BOARD.read_text()
    critical_expected = {
        "J1": ("Top", 0.0),
        "U1": ("Top", 0.0),
        "U6": ("Top", 0.0),
        "U7": ("Bottom", 180.0),
        "U8": ("Bottom", 180.0),
        "U10": ("Top", 0.0),
    }
    cpl_by_ref = {row["Designator"]: row for row in top_cpl + bottom_cpl}
    critical_review = {}
    for ref, (expected_layer, expected_rotation) in critical_expected.items():
        row = cpl_by_ref.get(ref)
        critical_review[ref] = {
            "layer": row["Layer"] if row else None,
            "rotation_deg": float(row["Rotation"]) if row else None,
            "matches_expected": bool(
                row
                and row["Layer"] == expected_layer
                and float(row["Rotation"]) == expected_rotation
            ),
        }

    checks = {
        "gerber_outline_is_24x46_mm": [outline_w, outline_h] == [24.0, 46.0],
        "all_required_gerber_layers_present": expected_fab_layers <= gerber_names,
        "exactly_four_copper_layers_exported": len(expected_copper & gerber_names) == 4,
        "board_file_declares_1_0_mm_thickness": "(thickness 1)" in board_text,
        "drill_files_present": (DRILL / "wearable_v2-PTH.drl").exists()
        and (DRILL / "wearable_v2-NPTH.drl").exists(),
        "bom_has_25_line_items": len(source_rows) == 25,
        "bom_has_51_parts": qty_total == 51 and len(bom_refs) == 51,
        "cpl_has_exactly_51_bom_refs": placed == bom_ref_set and len(top_cpl) + len(bottom_cpl) == 51,
        "cpl_split_is_45_top_6_bottom": len(top_cpl) == 45 and len(bottom_cpl) == 6,
        "battery_and_testpoints_excluded": set(excluded) == expected_excluded,
        "critical_orientations_match_kicad": all(item["matches_expected"] for item in critical_review.values()),
        "gerber_viewer_top_evidence_exists": (ASSEMBLY / "gerber_view_top.png").exists(),
        "gerber_viewer_bottom_evidence_exists": (ASSEMBLY / "gerber_view_bottom.png").exists(),
        "pcb_step_exists": (ASSEMBLY / "wearable_v2_pcb.step").exists(),
        "assembly_drawings_exist": (ASSEMBLY / "top_assembly.pdf").exists()
        and (ASSEMBLY / "bottom_assembly.pdf").exists(),
    }

    report = {
        "result": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "outline_centerline_bbox_mm": outline,
        "outline_size_mm": [outline_w, outline_h],
        "bom": {"line_items": len(source_rows), "placed_parts": qty_total},
        "cpl": {
            "top_parts": len(top_cpl),
            "bottom_parts": len(bottom_cpl),
            "excluded_nonplacement_refs": excluded,
        },
        "critical_orientation_review": critical_review,
        "drill_report": "drill/drill_report.rpt",
        "gerber_viewer_evidence": [
            "assembly/gerber_view_top.png",
            "assembly/gerber_view_bottom.png",
        ],
        "open_cart_gates": [
            "Confirm JLCPCB four-layer 1.0 mm Standard PCBA availability in the live cart.",
            "Select Panel by JLCPCB with 5 mm process rails and confirm factory fiducials/tooling holes for both assembly sides in DFM.",
            "Confirm current stock, lifecycle, assembly class and price for every exact LCSC order code; permit no similar substitutions.",
        ],
        "open_release_gates": [
            "Manufacturer evidence that EEMB LP502030-PCM permits 100 mA charging.",
            "Independent power/thermal margin validation, including ME6211 dropout and TPS61099 4V7 ripple under PPG pulses.",
            "Physical enclosure print/PCB/battery fit and selected optical/thermal interface materials.",
            "Explicit user authorization to order.",
        ],
    }
    (FAB / "artifact_validation.json").write_text(json.dumps(report, indent=2) + "\n")

    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise SystemExit("Artifact validation failed: " + ", ".join(failed))


if __name__ == "__main__":
    main()
