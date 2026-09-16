"""Pull stock KiCad symbols and flatten `extends` so they stand alone in a .kicad_sch."""
import os, copy
from sexp import parse, get, s, dump

LIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
_files, _cache = {}, {}

def _load(f):
    if f not in _files:
        _files[f] = parse(open(os.path.join(LIB, f), encoding='utf-8').read())
    return _files[f]

def _find(name):
    for f in sorted(os.listdir(LIB)):
        if not f.endswith('.kicad_sym'):
            continue
        for sym in get(_load(f), 'symbol'):
            if s(sym[1]) == name:
                return f[:-10], sym
    raise KeyError(name)

def flat(name):
    """Return (libname, flattened symbol node) with extends resolved."""
    if name in _cache:
        return _cache[name]
    libname, sym = _find(name)
    sym = copy.deepcopy(sym)
    ext = get(sym, 'extends')
    if ext:
        _, parent = flat(s(ext[0][1]))
        sym = [c for c in sym if not (isinstance(c, list) and c and c[0] == 'extends')]
        pprops = {s(p[1]): p for p in get(parent, 'property')}
        cprops = {s(p[1]): p for p in get(sym, 'property')}
        merged = dict(pprops); merged.update(cprops)
        head = [sym[0], sym[1]]
        opts = [c for c in sym[2:] if isinstance(c, list) and c[0] in
                ('pin_numbers', 'pin_names', 'exclude_from_sim', 'in_bom', 'on_board')]
        if not opts:
            opts = [c for c in parent[2:] if isinstance(c, list) and c[0] in
                    ('pin_numbers', 'pin_names', 'exclude_from_sim', 'in_bom', 'on_board')]
        subs = []
        for sub in get(parent, 'symbol'):
            sub = copy.deepcopy(sub)
            pn = s(sub[1])
            sub[1] = ('str', s(sym[1]) + pn[pn.rindex('_', 0, pn.rindex('_')):])
            subs.append(sub)
        sym = head + opts + list(merged.values()) + subs
    _cache[name] = (libname, sym)
    return _cache[name]

def pinmap(name):
    """{pin number: (x, y, name, etype)} in symbol coordinates."""
    _, sym = flat(name)
    out = {}
    for sub in get(sym, 'symbol'):
        for p in get(sub, 'pin'):
            at = get(p, 'at')[0]
            out[s(get(p, 'number')[0][1])] = (
                float(s(at[1])), float(s(at[2])),
                s(get(p, 'name')[0][1]), s(p[1]))
    return out
