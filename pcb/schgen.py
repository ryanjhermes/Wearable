"""Minimal KiCad 8-format schematic writer."""
import uuid as _uuid
import libtool
from sexp import parse, get, s, dump

PROJECT = "wearable_v2"


def uid():
    return str(_uuid.uuid4())


class Sch:
    def __init__(self, paper="A2"):
        self.paper = paper
        self.libs = {}           # lib_id -> symbol body text
        self.items = []          # rendered s-expr strings
        self.pins = {}           # ref -> {pinnum: (x, y)}
        self.refs = {}           # prefix -> counter
        self.nets = {}           # netname -> [(x, y)]

    # ---- library handling ---------------------------------------------
    def _need(self, lib_id):
        if lib_id in self.libs:
            return
        libname, name = lib_id.split(":", 1)
        if libname == PROJECT:
            body = _local_sym(name)
        else:
            _, node = libtool.flat(name)
            node = [c for c in node]
            node[1] = ('str', lib_id)
            body = dump(node)
        self.libs[lib_id] = body

    def pinmap(self, lib_id):
        libname, name = lib_id.split(":", 1)
        if libname == PROJECT:
            return _local_pins(name)
        return {k: (v[0], v[1]) for k, v in libtool.pinmap(name).items()}

    # ---- placement ----------------------------------------------------
    def place(self, lib_id, x, y, ref=None, value=None, footprint="",
              rot=0, mirror=None, fields_hidden=(), extra_props=(),
              in_bom=True, dnp=False, snap=True):
        # Snap every origin to the 2.54 mm grid so all pin endpoints land on
        # KiCad's 1.27 mm connection grid (otherwise ERC floods endpoint_off_grid).
        if snap:
            x = round(round(x / 2.54) * 2.54, 4)
            y = round(round(y / 2.54) * 2.54, 4)
        self._need(lib_id)
        prefix = ref.rstrip("0123456789") if ref else "U"
        if ref is None:
            self.refs[prefix] = self.refs.get(prefix, 0) + 1
            ref = f"{prefix}{self.refs[prefix]}"
        pm = self.pinmap(lib_id)
        world = {}
        for num, (px, py) in pm.items():
            if rot == 0:
                wx, wy = x + px, y - py
            elif rot == 90:
                wx, wy = x + py, y + px
            elif rot == 180:
                wx, wy = x - px, y + py
            else:
                wx, wy = x - py, y - px
            world[num] = (round(wx, 4), round(wy, 4))
        self.pins[ref] = world

        u = uid()
        props = [("Reference", ref, x, y - 1.27),
                 ("Value", value or "", x, y + 1.27),
                 ("Footprint", footprint, x, y),
                 ("Datasheet", "", x, y),
                 ("Description", "", x, y)]
        props += [(k, v, x, y) for k, v in extra_props]
        ptxt = ""
        for i, (k, v, px_, py_) in enumerate(props):
            hide = " (hide yes)" if (i >= 2 or k in fields_hidden) else ""
            ptxt += (f'    (property "{k}" "{v}" (at {px_} {py_} 0)\n'
                     f'      (effects (font (size 1.27 1.27)){hide})\n    )\n')
        pintxt = "".join(f'    (pin "{n}" (uuid {uid()}))\n' for n in sorted(pm))
        mir = f" (mirror {mirror})" if mirror else ""
        self.items.append(
            f'  (symbol (lib_id "{lib_id}") (at {x} {y} {rot}){mir} (unit 1)\n'
            f'    (exclude_from_sim no) (in_bom {"yes" if in_bom else "no"}) '
            f'(on_board yes) (dnp {"yes" if dnp else "no"})\n'
            f'    (uuid {u})\n{ptxt}{pintxt}'
            f'    (instances (project "{PROJECT}"\n'
            f'      (path "/{self.root}" (reference "{ref}") (unit 1))))\n  )\n')
        return ref

    # ---- connectivity -------------------------------------------------
    def wire(self, x1, y1, x2, y2):
        self.items.append(
            f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2}))\n'
            f'    (stroke (width 0) (type default)) (uuid {uid()}))\n')

    def junction(self, x, y):
        self.items.append(
            f'  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0) (uuid {uid()}))\n')

    def label(self, name, x, y, rot=0):
        just = "left bottom" if rot in (0, 90) else "right bottom"
        self.items.append(
            f'  (label "{name}" (at {x} {y} {rot}) (fields_autoplaced yes)\n'
            f'    (effects (font (size 1.27 1.27)) (justify {just})) (uuid {uid()}))\n')

    def nc(self, x, y):
        self.items.append(f'  (no_connect (at {x} {y}) (uuid {uid()}))\n')

    def text(self, t, x, y, size=2.0, bold=False):
        b = " (bold yes)" if bold else ""
        self.items.append(
            f'  (text "{t}" (at {x} {y} 0)\n'
            f'    (effects (font (size {size} {size}){b}) (justify left bottom)) (uuid {uid()}))\n')

    def box(self, x1, y1, x2, y2):
        self.items.append(
            f'  (rectangle (start {x1} {y1}) (end {x2} {y2})\n'
            f'    (stroke (width 0.2) (type dash)) (fill (type none)) (uuid {uid()}))\n')

    # ---- output -------------------------------------------------------
    def render(self, path, root_uuid):
        libtxt = "".join("    " + self.libs[k].replace("\n", "\n    ") + "\n"
                         for k in sorted(self.libs))
        out = (f'(kicad_sch (version 20231120) (generator "wearable_v2_gen") '
               f'(generator_version "8.0")\n'
               f'  (uuid {root_uuid})\n  (paper "{self.paper}")\n'
               f'  (lib_symbols\n{libtxt}  )\n'
               + "".join(self.items) +
               f'  (sheet_instances (path "/" (page "1")))\n)\n')
        open(path, "w").write(out)


# ---- local (project) symbol access -------------------------------------
_LOCAL = None


def _load_local(path):
    global _LOCAL
    _LOCAL = parse(open(path, encoding="utf-8").read())


def _local_node(name):
    for sym in get(_LOCAL, "symbol"):
        if s(sym[1]) == name:
            return sym
    raise KeyError(name)


def _local_sym(name):
    node = [c for c in _local_node(name)]
    node[1] = ('str', f"{PROJECT}:{name}")
    return dump(node)


def _local_pins(name):
    node = _local_node(name)
    out = {}
    for sub in get(node, "symbol"):
        for p in get(sub, "pin"):
            at = get(p, "at")[0]
            out[s(get(p, "number")[0][1])] = (float(s(at[1])), float(s(at[2])))
    return out
