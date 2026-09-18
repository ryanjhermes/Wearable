# JLCPCB fabrication package — prepared, not approved to order

Prepared 2026-09-17 from the accepted saved KiCad board, and **regenerated 2026-09-18** after the
user-approved R10 change (270 kOhm -> 249 kOhm, `C25770` -> `C11425`). ERC, DRC, schematic parity and
`analyze_pcb.py` were all rerun after that change and are unchanged from the accepted 2026-09-17
results. The gerber/drill ZIP is byte-identical to the 2026-09-17 export: R10's value appears only on
F.Fab, which is not part of the exported gerber set, so no copper, mask, silkscreen, drill or outline
data changed. The BOM, both CPL files, the raw position exports, the assembly PDFs and
`wearable_v2_pcba_bom_cpl.zip` were regenerated.

## Upload files

- `wearable_v2_gerbers_drills.zip` — 4 copper layers, paste, mask, silkscreen, 24 x 46 mm outline,
  plated and non-plated drill files.
- `assembly/jlcpcb_bom.csv` — 25 populated line items / 51 placed parts, derived from
  `pcb/bom_from_schematic.csv`.
- `assembly/jlcpcb_top_cpl.csv` — 45 top-side parts.
- `assembly/jlcpcb_bottom_cpl.csv` — 6 bottom-side parts.
- `wearable_v2_pcba_bom_cpl.zip` — the BOM and both CPL files together for transfer convenience.

Supporting review artifacts are in `assembly/`: raw KiCad position exports, top/bottom assembly
PDFs, populated PCB STEP and top/bottom Gerber-viewer renders. `artifact_validation.json` is the
machine-readable validation result.

## Required cart settings and checks

- JLCPCB **Standard PCBA**, four copper layers, **1.0 mm** finished board thickness.
- **Panel by JLCPCB** with **5 mm process rails**. Do not add local board fiducials unless JLCPCB
  rejects this workflow.
- During cart DFM, confirm factory-added fiducials and tooling holes support both top and bottom
  assembly.
- Confirm every exact LCSC order code, stock, lifecycle, assembly class and current price. Do not
  accept similar substitutions for regulators, MOSFETs or connectors.
- Inspect the cart's BOM/CPL overlay, especially J1, U1, U6, U7, U8 and U10.

## Validated locally

- Gerber outline centerline is exactly 24 x 46 mm.
- Four copper layers and 1.0 mm board configuration are present in the design/export.
- Top and bottom Gerber-viewer renders show aligned copper, mask, drill and outline data.
- BOM is 25 line items / 51 parts; CPL is the same 51 references split 45 top / 6 bottom.
- BT1 and TP1–TP12 are excluded from automated placement.
- J1/U1/U6/U10 are top at 0 degrees; U7/U8 are bottom at 180 degrees, matching KiCad.

Live-cart availability, factory panel features, current sourcing data and DFM are not local-file
checks and remain open. No order is authorized.
