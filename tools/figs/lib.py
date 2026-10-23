"""Tiny helpers for the illustrated plates in the notes. Each plate is a standalone, theme-aware SVG file."""
import math, re, html

CSS = """
.bg{fill:#FFFCF6}.pn{fill:#F5EFE3}.pn2{fill:#EEF3FB}.ink{fill:#1E2330}.mut{fill:#5A6172}.ln{stroke:#8E95A6}.lnf{fill:#8E95A6}
.t{font:700 21px system-ui,-apple-system,'Segoe UI',sans-serif;fill:#1E2330}.s{font:400 13.5px system-ui,-apple-system,sans-serif;fill:#5A6172}
.h{font:800 15px system-ui,-apple-system,sans-serif;fill:#1E2330}.l{font:600 14px system-ui,-apple-system,sans-serif;fill:#1E2330}
.n{font:400 13.5px system-ui,-apple-system,sans-serif;fill:#5A6172}.b{font-weight:700}.sm{font-size:12.5px}.xl{font-size:25px;font-weight:800}
.red{fill:#D33A3F}.blu{fill:#2E68D8}.grn{fill:#16824F}.amb{fill:#B06A00}.pur{fill:#7845C8}.tea{fill:#0B8585}
.sred{stroke:#D33A3F}.sblu{stroke:#2E68D8}.sgrn{stroke:#16824F}.samb{stroke:#B06A00}.spur{stroke:#7845C8}.stea{stroke:#0B8585}
.fred{fill:#FCE3E3}.fblu{fill:#E1EBFD}.fgrn{fill:#DDF3E7}.famb{fill:#FDF0D9}.fpur{fill:#EEE5FB}.ftea{fill:#DAF2F2}
@media (prefers-color-scheme:dark){
.bg{fill:#1A1E28}.pn{fill:#252B39}.pn2{fill:#222A3B}.ink,.l,.t,.h{fill:#ECEFF5}.mut,.n,.s{fill:#A7AFC1}.ln{stroke:#69718A}.lnf{fill:#69718A}
.red{fill:#FF7C7F}.blu{fill:#83AAFF}.grn{fill:#5FD39B}.amb{fill:#FFBE5C}.pur{fill:#BB97FF}.tea{fill:#55D3D3}
.sred{stroke:#FF7C7F}.sblu{stroke:#83AAFF}.sgrn{stroke:#5FD39B}.samb{stroke:#FFBE5C}.spur{stroke:#BB97FF}.stea{stroke:#55D3D3}
.fred{fill:#4A2A2E}.fblu{fill:#26355A}.fgrn{fill:#1F3F31}.famb{fill:#47371C}.fpur{fill:#382A55}.ftea{fill:#1C4243}}
"""
COLORS = ['red', 'blu', 'grn', 'amb', 'pur', 'tea']

DEFS = """<defs>
<linearGradient id="bone" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF3E2"/><stop offset=".55" stop-color="#EAD9B8"/><stop offset="1" stop-color="#C9B088"/></linearGradient>
<linearGradient id="skin" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7D7BF"/><stop offset="1" stop-color="#E3B293"/></linearGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#DCEBF5"/><stop offset=".5" stop-color="#F7FBFE"/><stop offset="1" stop-color="#C9DDEB"/></linearGradient>
<radialGradient id="rbc" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#F6A9A3"/><stop offset=".45" stop-color="#E9746C"/><stop offset="1" stop-color="#C9473F"/></radialGradient>
<marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker>
</defs>"""

BONE = 'fill="url(#bone)" stroke="#8A7150" stroke-width="1.6" stroke-linejoin="round"'
SKIN = 'fill="url(#skin)" stroke="#B9826A" stroke-width="1.6" stroke-linejoin="round"'


def esc(s):
    return html.escape(s, quote=False)


def T(x, y, s, cls='l', a='start', extra=''):
    a = {'start': '', 'middle': ' text-anchor="middle"', 'end': ' text-anchor="end"'}[a]
    return f'<text x="{x}" y="{y}" class="{cls}"{a}{extra}>{esc(s)}</text>'


def TL(x, y, lines, cls='n', dy=15, a='start'):
    return ''.join(T(x, y + i * dy, l, cls, a) for i, l in enumerate(lines))


def rich(x, y, parts, cls='n', a='start'):
    """parts: list of (text, extra classes)."""
    a = {'start': '', 'middle': ' text-anchor="middle"', 'end': ' text-anchor="end"'}[a]
    sp = ''.join(f'<tspan class="{c}">{esc(t)}</tspan>' if c else esc(t) for t, c in parts)
    return f'<text x="{x}" y="{y}" class="{cls}"{a}>{sp}</text>'


def lead(x1, y1, x2, y2, dot=True, cls='ln'):
    d = f'<circle cx="{x2}" cy="{y2}" r="2.6" class="lnf"/>' if dot else ''
    return f'<path d="M{x1} {y1}L{x2} {y2}" class="{cls}" stroke-width="1.2" fill="none"/>{d}'


def arrow(x1, y1, x2, y2, cls='sred', w=3, curve=None):
    if curve is None:
        d = f'M{x1} {y1}L{x2} {y2}'
    else:
        d = f'M{x1} {y1}Q{curve[0]} {curve[1]} {x2} {y2}'
    return f'<path d="{d}" class="{cls}" stroke-width="{w}" fill="none" stroke-linecap="round" marker-end="url(#ah)"/>'


def card(x, y, w, h, cls='pn', r=14):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def pill(x, y, s, color, w=None):
    w = w or (len(s) * 7.4 + 18)
    return f'<rect x="{x}" y="{y - 14}" width="{w}" height="20" rx="10" class="f{color}"/>' + T(x + w / 2, y + 0.5, s, f'l sm b {color}', 'middle')


def g(inner, tx=0, ty=0, rot=0, sc=1, cx=0, cy=0):
    t = []
    if tx or ty: t.append(f'translate({tx} {ty})')
    if rot: t.append(f'rotate({rot} {cx} {cy})')
    if sc != 1: t.append(f'scale({sc})')
    return f'<g transform="{" ".join(t)}">{inner}</g>' if t else f'<g>{inner}</g>'


def plate(w, h, title, sub, body, desc):
    head = T(24, 36, title, 't') + (T(24, 58, sub, 's') if sub else '')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{html.escape(desc)}">'
            f'<style>{CSS}</style>{DEFS}<rect width="{w}" height="{h}" rx="18" class="bg"/>{head}{body}</svg>')


def minify(s):
    s = re.sub(r'\s*\n\s*', ' ', s)
    rnd = lambda m: ('%.1f' % float(m.group(1))).rstrip('0').rstrip('.')
    s = re.sub(r'<[^>]+>', lambda t: re.sub(r'(\d+\.\d{2,})', rnd, t.group(0)), s)  # numbers inside tags only, never in text
    s = re.sub(r'>\s+<', '><', s)
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip()


def jag(x, y1, y2, n=6, amp=5, phase=1):
    """A jagged fracture line from (x,y1) to (x,y2), as path points."""
    pts = []
    for i in range(n + 1):
        y = y1 + (y2 - y1) * i / n
        dx = 0 if i in (0, n) else amp * (1 if (i + phase) % 2 else -1)
        pts.append((x + dx, y))
    return pts


def pts(p):
    return ' '.join(f'{x:.1f} {y:.1f}' for x, y in p)
