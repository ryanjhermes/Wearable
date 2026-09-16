"""Author custom KiCad symbols from a compact pin spec."""
G = 2.54

def _pin(num, name, etype, x, y, rot, length=G, hide=False):
    h = " hide" if hide else ""
    return (f'      (pin {etype} line (at {x} {y} {rot}) (length {length}){h}\n'
            f'        (name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'        (number "{num}" (effects (font (size 1.27 1.27))))\n'
            f'      )\n')

def make(name, ref, value, footprint, datasheet, desc, left, right, top, bottom,
         hidden=(), w=25.4, pin_names_offset=0.508):
    """left/right/top/bottom: lists of (num, name, etype) or None for a gap.
    Multiple nums joined by '+' stack at one location (e.g. GND '6+7')."""
    nL, nR = len(left), len(right)
    rows = max(nL, nR)
    h = (rows + 1) * G
    if top or bottom:
        h = max(h, (max(len(top), len(bottom)) + 2) * G)
    x0, x1 = -w / 2, w / 2
    y0, y1 = h / 2, -h / 2
    out = [f'  (symbol "{name}" (pin_names (offset {pin_names_offset})) '
           f'(exclude_from_sim no) (in_bom yes) (on_board yes)\n']
    props = [("Reference", ref, x0, y0 + 2.54, "left"),
             ("Value", value, x0, y1 - 2.54, "left"),
             ("Footprint", footprint, 0, 0, None),
             ("Datasheet", datasheet, 0, 0, None),
             ("Description", desc, 0, 0, None)]
    for i, (k, v, px, py, just) in enumerate(props):
        hide = " (hide yes)" if i >= 2 else ""
        j = f' (justify {just})' if just else ''
        out.append(f'    (property "{k}" "{v}" (at {px} {py} 0)\n'
                   f'      (effects (font (size 1.27 1.27)){j}{hide})\n    )\n')
    out.append(f'    (symbol "{name}_0_1"\n'
               f'      (rectangle (start {x0} {y0}) (end {x1} {y1})\n'
               f'        (stroke (width 0.254) (type default))\n'
               f'        (fill (type background))\n      )\n    )\n')
    out.append(f'    (symbol "{name}_1_1"\n')
    def emit(seq, side):
        for i, e in enumerate(seq):
            if e is None:
                continue
            num, pname, etype = e
            if side == 'L':
                x, y, rot = x0 - G, y0 - G * (i + 1), 0
            elif side == 'R':
                x, y, rot = x1 + G, y0 - G * (i + 1), 180
            elif side == 'T':
                x, y, rot = x0 + G * (i + 2), y0 + G, 270
            else:
                x, y, rot = x0 + G * (i + 2), y1 - G, 90
            for n in str(num).split('+'):
                out.append(_pin(n, pname, etype, x, y, rot))
    emit(left, 'L'); emit(right, 'R'); emit(top, 'T'); emit(bottom, 'B')
    for num, pname, etype in hidden:
        for n in str(num).split('+'):
            out.append(_pin(n, pname, etype, x1 + G, y1 - G, 180, hide=True))
    out.append('    )\n  )\n')
    return ''.join(out)

def power(name, sign="+"):
    """A power-rail symbol (arrow style)."""
    return (f'  (symbol "{name}" (power) (pin_numbers (hide yes)) '
            f'(pin_names (offset 0) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
            f'    (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'    (property "Value" "{name}" (at 0 3.556 0) (effects (font (size 1.27 1.27))))\n'
            f'    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'    (property "Description" "Power rail {name}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            f'    (symbol "{name}_0_1"\n'
            f'      (polyline (pts (xy -0.762 1.27) (xy 0 2.54) (xy 0.762 1.27))\n'
            f'        (stroke (width 0) (type default)) (fill (type none)))\n'
            f'      (polyline (pts (xy 0 0) (xy 0 2.54))\n'
            f'        (stroke (width 0) (type default)) (fill (type none)))\n'
            f'    )\n'
            f'    (symbol "{name}_1_1"\n'
            f'      (pin power_in line (at 0 0 90) (length 0)\n'
            f'        (name "{name}" (effects (font (size 1.27 1.27))))\n'
            f'        (number "1" (effects (font (size 1.27 1.27))))\n'
            f'      )\n    )\n  )\n')
