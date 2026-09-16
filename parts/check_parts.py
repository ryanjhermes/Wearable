#!/usr/bin/env python3
"""Sourcing check for parts/ — NOT a BOM generator.

Quantities ultimately live in the schematic, not here, so this deliberately does not try to
produce a buildable BOM (see parts/V2_BOM.md).
What it does do is answer the questions that block ordering:

  * which parts have an LCSC number recorded, and which don't
  * which folders are missing a datasheet, hold a broken one, or duplicate another part's PDF
  * whether parts documentation has unresolved merge markers or broken relative links
  * a paste-ready list of LCSC codes for a bulk JLCPCB stock/Basic check

Usage:  python3 parts/check_parts.py
"""
from __future__ import annotations
import pathlib
import re
import sys
import hashlib
from urllib.parse import unquote

ROOT = pathlib.Path(__file__).resolve().parent
LCSC_RE = re.compile(r"\bC\d{4,9}\b")
# "| Order code | ... |" / "| Candidate | ... |" / "| LCSC | ... |"
ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$", re.M)
CONFLICT_RE = re.compile(r"^(?:<{7}|={7}|>{7})(?:\s|$)", re.M)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def field(text: str, *names: str) -> str:
    wanted = {n.lower() for n in names}
    for label, value in ROW_RE.findall(text):
        if label.lower() in wanted:
            return value.strip()
    return ""


def strip_md(s: str) -> str:
    return re.sub(r"[*`]", "", s).strip()


def datasheet_state(folder: pathlib.Path) -> str:
    pdf = folder / "datasheet.pdf"
    if not pdf.exists():
        return "MISSING"
    head = pdf.open("rb").read(5)
    if head[:4] != b"%PDF":
        return "CORRUPT"
    return f"{pdf.stat().st_size // 1024} KB"


def documentation_gaps() -> list[str]:
    gaps: list[str] = []
    for path in sorted(ROOT.rglob("*.md")):
        text = path.read_text(errors="replace")
        relative = path.relative_to(ROOT)
        if CONFLICT_RE.search(text):
            gaps.append(f"{relative}: unresolved merge-conflict marker")
        for raw_target in LINK_RE.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = path.parent / unquote(target)
            if not resolved.exists():
                gaps.append(f"{relative}: broken relative link: {target}")
    return gaps


def main() -> int:
    folders = sorted(
        p for p in ROOT.iterdir()
        if p.is_dir() and not p.name.startswith("_") and (p / "README.md").exists()
    )

    rows, codes, gaps = [], [], documentation_gaps()
    datasheet_hashes: dict[str, list[str]] = {}
    for f in folders:
        text = (f / "README.md").read_text()
        mpn = strip_md(field(text, "Order code", "Candidate", "Part")) or "—"
        mpn = re.split(r"\s*[.(]|\s—", mpn)[0][:34]
        found = LCSC_RE.findall(field(text, "LCSC"))
        ds = datasheet_state(f)

        rows.append((f.name, mpn, found[0] if found else "—", len(found), ds))
        codes.extend(found[:1])
        if not found:
            gaps.append(f"{f.name}: no LCSC number recorded")
        if ds in ("MISSING", "CORRUPT"):
            gaps.append(f"{f.name}: datasheet {ds}")
        else:
            digest = hashlib.sha256((f / "datasheet.pdf").read_bytes()).hexdigest()
            datasheet_hashes.setdefault(digest, []).append(f.name)

    for names in datasheet_hashes.values():
        if len(names) > 1:
            gaps.append(
                "identical datasheet.pdf in different part folders: " + ", ".join(names)
            )

    w = max(len(r[0]) for r in rows)
    print(f"{'FOLDER'.ljust(w)}  {'MPN'.ljust(34)}  {'LCSC'.ljust(10)}  ALT  DATASHEET")
    print("-" * (w + 66))
    for name, mpn, code, n, ds in rows:
        alt = str(n - 1) if n > 1 else " "
        print(f"{name.ljust(w)}  {mpn.ljust(34)}  {code.ljust(10)}  {alt.center(3)}  {ds}")

    print(f"\n{len(rows)} part folders · {len(codes)} with an LCSC code")

    print("\nPaste into JLCPCB parts search to confirm stock + Basic/Extended:")
    print("  " + ", ".join(codes))

    if gaps:
        print(f"\nGAPS ({len(gaps)}):")
        for g in gaps:
            print(f"  - {g}")
    else:
        print("\nNo gaps.")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
