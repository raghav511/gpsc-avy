"""Build data/figs/*.svg from the plate definitions in tools/figs/t*.py. Run by tools/build.py."""
import importlib, json, os, re, sys, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from lib import minify
OUT = os.path.join(HERE, '..', '..', 'data', 'figs')


def build(only=None):
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for t in range(1, 11):
        p = os.path.join(HERE, f't{t}.py')
        if not os.path.exists(p): continue
        mod = importlib.import_module(f't{t}')
        for fid, fn in mod.FIGS.items():
            if only and fid not in only: continue
            svg, alt = fn()
            svg = minify(svg)
            import xml.dom.minidom; xml.dom.minidom.parseString(svg)  # fails the build on broken markup
            w, h = map(int, re.search(r'viewBox="0 0 (\d+) (\d+)"', svg).groups())
            open(os.path.join(OUT, fid + '.svg'), 'w').write(svg)
            meta[fid] = {'w': w, 'h': h, 'alt': alt, 'v': hashlib.sha1(svg.encode()).hexdigest()[:8], 'kb': round(len(svg) / 1024, 1)}
    if not only:
        for f in os.listdir(OUT):
            if f.endswith('.svg') and f[:-4] not in meta: os.remove(os.path.join(OUT, f))
    return meta


if __name__ == '__main__':
    m = build(sys.argv[1:] or None)
    for k, v in m.items(): print(k, v['w'], v['h'], v['kb'], 'KB')
