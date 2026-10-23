"""Hands drawn as thick strokes: an outline pass, then a fill pass, so fingers merge cleanly."""
from lib import *

SKO, SKI = '#C99A82', '#F4D3BC'


def strokes(paths, w=22):
    o = ''.join(f'<path d="{d}" stroke="{SKO}" stroke-width="{w + 3}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for d in paths)
    i = ''.join(f'<path d="{d}" stroke="{SKI}" stroke-width="{w}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for d in paths)
    return o, i


def front_hand(fingers, thumb='normal', thenar=True):
    """fingers: dict index/middle/ring/little -> 'ext' | 'flex'. Palm towards the viewer, thumb on the left."""
    base = {'index': (-33, 78), 'middle': (-11, 86), 'ring': (11, 80), 'little': (32, 62)}
    paths, creases = [], ''
    for k, (x, L) in base.items():
        if fingers.get(k, 'ext') == 'ext':
            paths.append(f'M{x} -36 L{x + (x / 14):.0f} {-36 - L}')
            creases += ''.join(f'<path d="M{x - 7 + (x / 14) * f:.0f} {-36 - L * f:.0f}h14" stroke="{SKO}" stroke-width="1.2" opacity=".7"/>' for f in (.38, .68))
        else:
            paths.append(f'M{x} -36 L{x} -58 Q{x} -70 {x} -54')
            creases += f'<path d="M{x - 8} -50 q8 6 16 0" stroke="{SKO}" stroke-width="1.4" fill="none"/>'
    if thumb == 'normal':
        paths.append('M-44 22 L-70 -6 L-86 -30')
    else:
        paths.append('M-44 22 L-52 -14 L-54 -40')
    o, i = strokes(paths)
    palm = f'<path d="M-46 -40 C-30 -48 30 -48 46 -40 C52 -10 52 30 40 56 L36 96 L-36 96 L-40 56 C-52 30 -54 -10 -46 -40 Z" fill="{SKI}" stroke="{SKO}" stroke-width="1.6"/>'
    th = ('<path d="M-46 -6 C-26 -6 -20 30 -30 52 C-40 50 -48 30 -46 -6 Z" fill="#EBBFA4" opacity=".9"/>' if thenar else
          '<path d="M-44 -2 C-36 4 -34 30 -38 48" stroke="#C99A82" stroke-width="1.4" fill="none"/>')
    lines = f'<path d="M-30 4 C-10 -2 20 0 40 10 M-34 22 C-14 14 14 18 30 30" stroke="{SKO}" stroke-width="1.3" fill="none" opacity=".8"/>'
    return o + palm + i + th + lines + creases


def side_hand(mcp=0, pip=10, dip=8, wrist=0):
    """Side view: forearm to the left, fingers to the right. Angles in degrees, + = flexion (down)."""
    import math
    def seg(x, y, a, L):
        r = math.radians(a)
        return x + L * math.cos(r), y + L * math.sin(r)
    a = wrist
    wx, wy = 0, 0
    p1 = seg(wx, wy, a, 70)          # metacarpus
    a2 = a + mcp; p2 = seg(*p1, a2, 40)
    a3 = a2 + pip; p3 = seg(*p2, a3, 26)
    a4 = a3 + dip; p4 = seg(*p3, a4, 18)
    finger = f'M{p1[0]:.0f} {p1[1]:.0f}L{p2[0]:.0f} {p2[1]:.0f}L{p3[0]:.0f} {p3[1]:.0f}L{p4[0]:.0f} {p4[1]:.0f}'
    t0 = seg(0, 0, a, 22); t1 = seg(*t0, a + 22, 34); t2 = seg(*t1, a + 30, 24)
    thumb = f'M{t0[0]:.0f} {t0[1]:.0f}L{t1[0]:.0f} {t1[1]:.0f}L{t2[0]:.0f} {t2[1]:.0f}'
    arm = 'M-180 -26 C-120 -25 -40 -21 4 -17 C14 -8 14 8 4 17 C-40 21 -120 25 -180 26 C-188 10 -188 -10 -180 -26 Z'
    hand = f'M0 0 L{p1[0]:.0f} {p1[1]:.0f}'
    o2, i2 = strokes([hand], 32)
    o3, i3 = strokes([finger], 19)
    o4, i4 = strokes([thumb], 17)
    nail = f'<circle cx="{p4[0]:.0f}" cy="{p4[1]:.0f}" r="3" fill="#F9E7DC"/>'
    return (f'<path d="{arm}" fill="{SKI}" stroke="{SKO}" stroke-width="1.6"/>' + o2 + o3 + f'<path d="{arm}" fill="{SKI}"/>' + i2 + i3
            + f'<path d="M-120 -8 C-80 -6 -40 -4 -10 -2" stroke="{SKO}" stroke-width="1" fill="none" opacity=".5"/>'), (p4, p1)
