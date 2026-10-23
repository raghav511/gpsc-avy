from lib import *
import math

# ---------- distal radius, lateral view (local origin = fracture site on the dorsal-volar midline) ----------
L0 = -210
SHAFT_J = lambda: f'M{L0} -13 C-150 -15 -60 -15 0 -17 L' + pts(jag(0, -17, 17, 6, 4)) + f' C-60 15 -150 15 {L0} 13 C{L0-12} 12 {L0-14} -12 {L0} -13 Z'
DIST_J = lambda: 'M' + pts(jag(4, -17, 17, 6, 4)) + ' C30 20 50 26 62 30 C70 10 70 -14 64 -36 C44 -30 22 -22 4 -17 Z'
RIDGE = f'<path d="M{L0+30} -4 C-120 -6 -50 -6 -6 -8" stroke="#B49A72" stroke-width="1.2" fill="none" opacity=".7"/>'
ARM = 'M-236 -38 C-150 -36 -60 -34 -2 -33 C14 -20 14 22 -2 35 C-60 36 -150 38 -236 40 C-242 14 -242 -12 -236 -38 Z'
HAND = 'M-14 -32 C30 -38 70 -36 110 -30 C150 -25 175 -22 210 -16 C240 -12 262 -10 272 -4 C277 0 273 6 262 8 C240 10 214 11 190 13 C150 19 100 31 60 37 C30 41 8 39 -14 34 C-24 14 -24 -14 -14 -32 Z'
SK = 'fill="#F6DDCB" stroke="#C99A82" stroke-width="3"'
SKF = 'fill="#F6DDCB"'


def carpus():
    # lunate, capitate and the third metacarpal, simplified side view
    return (f'<path d="M70 -26 C84 -30 92 -18 90 -4 C88 10 82 22 70 24 C78 10 79 -12 70 -26 Z" {BONE}/>'
            f'<path d="M92 -16 C104 -24 124 -22 128 -8 C132 6 122 18 106 16 C96 14 90 4 92 -16 Z" {BONE}/>'
            f'<path d="M132 -12 C160 -11 186 -10 198 -8 C205 -7 205 5 198 6 C186 7 160 9 132 10 C128 4 128 -6 132 -12 Z" {BONE}/>'
            f'<path d="M206 -6 C220 -6 230 -5 236 -3 C240 -1 240 5 236 6 C228 7 218 7 206 7 C203 4 203 -3 206 -6 Z" {BONE}/>'
            f'<path d="M240 -2 C248 -2 254 -1 258 1 C261 3 260 7 257 8 C251 8 246 8 240 8 C238 5 238 1 240 -2 Z" {BONE}/>'
            f'<path d="M261 2 C265 2 268 3 269 5 C269 7 267 8 263 8 C261 6 260 4 261 2 Z" {BONE}/>')


def limb(hand_g, arm_extra=''):
    """Skin outline of forearm + hand (outer stroke only), then the bones."""
    return (f'<path d="{ARM}" {SK}/>' + hand_g(f'<path d="{HAND}" {SK}/>') +
            f'<path d="{ARM}" {SKF}/>' + hand_g(f'<path d="{HAND}" {SKF}/>'))


def radius_row(kind):
    if kind in ('colles', 'smith'):
        sgn = -1 if kind == 'colles' else 1
        hg = lambda inner: g(inner, 4, 6 * sgn, 15 * sgn, 1, 0, 17 * sgn)
        return limb(hg) + f'<path d="{SHAFT_J()}" {BONE}/>' + RIDGE + hg(f'<path d="{DIST_J()}" {BONE}/>' + carpus())
    # Barton: oblique fracture through the dorsal articular rim; the rim and the carpus slip dorsally together
    main = f'M{L0} -13 C-150 -15 -60 -15 0 -17 C10 -19 18 -21 24 -23 L' + pts([(30, -18), (36, -16), (42, -10), (48, -9), (54, -3), (66, -2)]) + f' C68 10 66 20 62 30 C50 26 30 20 0 17 C-60 15 -150 15 {L0} 13 C{L0-12} 12 {L0-14} -12 {L0} -13 Z'
    rim = 'M24 -23 C40 -28 52 -32 64 -36 C68 -24 68 -10 66 -2 L' + pts([(54, -3), (48, -9), (42, -10), (36, -16), (30, -18)]) + ' Z'
    hg = lambda inner: g(inner, 4, -14)
    return limb(hg) + f'<path d="{main}" {BONE}/>' + RIDGE + hg(f'<path d="{rim}" {BONE}/>' + carpus())


def wrist_fracs():
    W, H = 760, 690
    rows = [('colles', "Colles'", 'red', 'Fragment tilts DORSALLY', ['Distal radius, 2.5 cm', 'above the wrist; fall on', 'the outstretched hand;', 'elderly women'], 'Dinner-fork deformity'),
            ('smith', "Smith's", 'blu', 'Fragment tilts VOLARLY', ['Distal radius, the', '"reverse Colles\'": the', 'fragment and hand drop', 'towards the palm'], 'Garden-spade deformity'),
            ('barton', "Barton's", 'grn', 'The joint rim breaks off', ['Intra-articular distal', 'radius; the carpus slips', 'with the fragment', '(wrist subluxation)'], 'Joint surface involved')]
    b = ''
    b += arrow(30, 150, 30, 76, 'samb', 2.4) + T(42, 78, 'DORSAL · back of the hand', 'l sm b amb')
    b += f'<path d="M30 150 L30 590" class="ln" stroke-width="1.4" stroke-dasharray="3 5"/>'
    b += arrow(30, 590, 30, 664, 'spur', 2.4) + T(42, 668, 'VOLAR · palm side', 'l sm b pur')
    for i, (k, name, c, head, lines, tag) in enumerate(rows):
        y0 = 90 + i * 188
        b += card(50, y0, 690, 174, 'pn')
        b += g(radius_row(k), 272, y0 + 90, sc=0.78)
        b += f'<path d="M532 {y0 + 16}L532 {y0 + 158}" class="ln" stroke-width="1"/>'
        b += T(548, y0 + 36, name, f'h xl {c}') + ''
        b += T(548, y0 + 60, head, f'l sm b {c}')
        b += TL(548, y0 + 80, lines, 'n sm', 15)
        b += pill(548, y0 + 156, tag, c)
    b += lead(150, 90 + 30, 150, 90 + 78) + T(150, 90 + 22, 'radius', 'n sm', 'middle')
    b += T(300, 90 + 164, 'fracture line', 'n sm', 'middle') + lead(300, 90 + 152, 274, 90 + 104, True)
    b += lead(420, 90 + 150, 404, 90 + 84) + T(420, 90 + 164, 'carpus and hand', 'n sm', 'middle')
    alt = "Colles', Smith's and Barton's fractures of the distal radius, side view of forearm and hand: in Colles' the distal fragment and hand tilt dorsally (dinner-fork deformity), in Smith's they tilt towards the palm (garden-spade deformity), and in Barton's the rim of the joint breaks off and the carpus slips with it."
    return plate(W, H, "Wrist fractures: Colles', Smith's and Barton's", 'Same bone, same place, different direction · side view of the right forearm', b, alt), alt


FIGS = {'t9-wrist-fractures': wrist_fracs}


# ---------- fracture types ----------
LB = 'M-20 -95 C-27 -88 -25 -72 -11 -64 C-10 -30 -10 30 -11 64 C-25 72 -27 88 -20 95 C-8 103 8 103 20 95 C27 88 25 72 11 64 C10 30 10 -30 11 -64 C25 -72 27 -88 20 -95 C8 -103 -8 -103 -20 -95 Z'
MARROW = '<path d="M-3 -58 C-4 -20 -4 20 -3 58" stroke="#C7AE84" stroke-width="2" fill="none" opacity=".6"/>'


def bone_piece(cid, poly, tx=0, ty=0, rot=0, cx=0, cy=0):
    clip = f'<clipPath id="{cid}"><path d="M{pts(poly)}Z"/></clipPath>'
    return clip + g(f'<g clip-path="url(#{cid})"><path d="{LB}" {BONE}/>{MARROW}</g><path d="M{pts(poly)}" fill="none" stroke="#8A7150" stroke-width="1.4" clip-path="url(#{cid}o)"/>', tx, ty, rot, 1, cx, cy)


def cut_line(points):
    return f'<path d="M{pts(points)}" fill="none" stroke="#8A7150" stroke-width="1.5" stroke-linejoin="round"/>'


def two_pieces(cid, cut, lower_t=(0, 0, 0, 0, 0), upper_t=(0, 0, 0, 0, 0)):
    up = [(-40, -120)] + cut + [(40, -120)]
    lo = [(-40, 120)] + cut + [(40, 120)]
    s = ''
    for k, poly, t in (('u', up, upper_t), ('l', lo, lower_t)):
        s += f'<clipPath id="{cid}{k}"><path d="M{pts(poly)}Z"/></clipPath>'
        s += g(f'<g clip-path="url(#{cid}{k})"><path d="{LB}" {BONE}/>{MARROW}<path d="M{pts(cut)}" fill="none" stroke="#8A7150" stroke-width="2.4" clip-path="url(#lbc)"/></g>', *t[:2], t[2], 1, t[3], t[4])
    return s


def frac_types():
    W, H = 760, 700
    tiles = [
        ('Closed (simple)', 'blu', ['Skin intact over', 'the break']),
        ('Open (compound)', 'red', ['Bone end reaches the', 'outside: infection risk']),
        ('Greenstick', 'grn', ['Incomplete break of a', "soft, bendy child's bone"]),
        ('Comminuted', 'amb', ['More than two', 'fragments']),
        ('Impacted', 'pur', ['One fragment driven', 'into the other']),
        ('Pathological', 'tea', ['Through weakened bone:', 'tumour, osteoporosis']),
        ('Stress ("march")', 'blu', ['Repeated small loads;', '2nd metatarsal, soldiers']),
    ]
    b = f'<clipPath id="lbc"><path d="{LB}"/></clipPath>'
    for i, (name, c, lines) in enumerate(tiles):
        col, row = i % 4, i // 4
        x0, y0 = 24 + col * 181, 76 + row * 306
        b += card(x0, y0, 169, 294, 'pn')
        cx, cy = x0 + 84.5, y0 + 134
        art = ''
        if i == 0:
            art += f'<rect x="-44" y="-110" width="88" height="216" rx="38" fill="#F6DDCB" stroke="#C99A82" stroke-width="2.5" opacity=".9"/>'
            art += two_pieces('fa', jag(0, 0, 0, 1, 0) and [(-30, 2), (-12, -3), (-4, 4), (6, -2), (14, 3), (30, -1)], (3, 4, 0, 0, 0))
        elif i == 1:
            art += f'<path d="M-44 -72 C-44 -94 -28 -110 0 -110 C28 -110 44 -94 44 -72 L44 70 C44 92 28 106 0 106 C-28 106 -44 92 -44 70 Z" fill="#F6DDCB" stroke="#C99A82" stroke-width="2.5" opacity=".9"/>'
            art += two_pieces('fb', [(-30, -22), (-10, -8), (0, -2), (10, 6), (30, 22)], (-8, 6, 0, 0, 0), (26, -6, -16, 0, 0))
            art += '<path d="M36 -10 C44 -6 50 0 52 8 C48 10 44 8 40 2" fill="#D33A3F" opacity=".85"/><circle cx="50" cy="20" r="3.5" fill="#D33A3F"/><circle cx="47" cy="31" r="2.4" fill="#D33A3F"/>'
        elif i == 2:
            art += two_pieces('fc', [(-30, 2), (11, 2)], (0, 0, -9, 11, 2))
            art += '<path d="M-11 2 L-4 -2 L1 3 L5 0" fill="none" stroke="#8A7150" stroke-width="2"/>'
            art += f'<path d="M-9 -2 C-6 -10 -3 -14 0 -16" stroke="#8A7150" stroke-width="1" fill="none" stroke-dasharray="2 2"/>'
        elif i == 3:
            cut1 = [(-30, -14), (-12, -18), (0, -10), (12, -18), (30, -14)]
            cut2 = [(-30, 14), (-12, 18), (0, 10), (12, 18), (30, 14)]
            art += f'<clipPath id="fdu"><path d="M{pts([(-40, -120)] + cut1 + [(40, -120)])}Z"/></clipPath><g clip-path="url(#fdu)"><path d="{LB}" {BONE}/>{MARROW}</g>'
            art += f'<clipPath id="fdl"><path d="M{pts([(-40, 120)] + cut2 + [(40, 120)])}Z"/></clipPath>' + g(f'<g clip-path="url(#fdl)"><path d="{LB}" {BONE}/>{MARROW}</g>', 4, 10)
            art += g(f'<path d="M-11 -16 L0 -9 L-2 4 L-11 10 Z" {BONE}/>', -9, 2, -12)
            art += g(f'<path d="M1 -9 L11 -16 L11 12 L2 9 Z" {BONE}/>', 9, 4, 14)
            art += g(f'<path d="M-3 4 L2 9 L-2 14 L-8 11 Z" {BONE}/>', 0, 6)
            art += f'<g clip-path="url(#lbc)">{cut_line(cut1)}</g>' + g(f'<g clip-path="url(#lbc)">{cut_line(cut2)}</g>', 4, 10)
        elif i == 4:
            cut = [(-30, 4), (-10, -2), (0, 3), (10, -2), (30, 4)]
            art += two_pieces('fe', cut, (0, -9, 0, 0, 0))
            art += '<path d="M-12 -7 L-6 -2 L-2 -8 L3 -2 L8 -7 L12 -3" fill="none" stroke="#6F5A3D" stroke-width="2.6"/><path d="M-12 -3 L12 -3" stroke="#6F5A3D" stroke-width="1" stroke-dasharray="1.5 2"/>'
            art += arrow(-30, 60, -18, 20, 'spur', 2.2) + arrow(-30, -64, -18, -26, 'spur', 2.2)
        elif i == 5:
            art += two_pieces('ff', [(-30, -2), (-10, 3), (0, -3), (10, 3), (30, -1)], (2, 3, 0, 0, 0))
            art += '<ellipse cx="0" cy="0" rx="9" ry="24" fill="#7A4FA8" opacity=".45"/><path d="M-6 -16 C2 -20 8 -8 4 2 C0 12 -8 14 -6 4" fill="#7A4FA8" opacity=".35"/>'
        elif i == 6:
            sc = 0.8
            art += g(f'<path d="{LB}" {BONE}/>{MARROW}' + '<path d="M-10 -6 L-2 -2 L4 -5 L10 -1" fill="none" stroke="#8A7150" stroke-width="1.4"/>' +
                     '<path d="M-16 -14 C-22 -6 -22 4 -16 10 M16 -14 C22 -6 22 4 16 10" stroke="#C9A06A" stroke-width="5" fill="none" opacity=".55" stroke-linecap="round"/>', 0, 0, 0, sc)
        b += g(art, cx, cy - 12, sc=1.06)
        b += T(x0 + 14, y0 + 252, name, f'l b {c}') + TL(x0 + 14, y0 + 270, lines, 'n sm', 15)
        if False: pass
    # healing tile
    x0, y0 = 24 + 3 * 181, 76 + 306
    b += card(x0, y0, 169, 294, 'pn2')
    b += T(x0 + 14, y0 + 30, 'Healing stages', 'l b')
    st = [('Haematoma', 'red'), ('Inflammation', 'amb'), ('Soft callus', 'grn'), ('Hard callus', 'tea'), ('Remodelling', 'blu')]
    for j, (sname, sc_) in enumerate(st):
        yy = y0 + 64 + j * 38
        b += f'<circle cx="{x0 + 26}" cy="{yy - 5}" r="9" class="f{sc_}"/>' + T(x0 + 26, yy - 0.5, str(j + 1), f'l sm b {sc_}', 'middle') + T(x0 + 44, yy, sname, 'l')
        if j < 4: b += f'<path d="M{x0 + 26} {yy + 6}L{x0 + 26} {yy + 22}" class="ln" stroke-width="1.4"/>'
    b += TL(x0 + 14, y0 + 254, ['Upper limb 6–8 weeks,', 'lower limb 12 weeks;', 'children: half the time'], 'n sm', 15)
    alt = 'Types of fracture drawn on a long bone: closed (skin intact), open or compound (bone end through the skin), greenstick (incomplete, children), comminuted (more than two fragments), impacted (one fragment driven into the other), pathological (through weakened bone) and stress or march fracture (second metatarsal), with the five healing stages from haematoma to remodelling.'
    return plate(W, H, 'Types of fracture', 'A fracture is a break in the continuity of bone', b, alt), alt


FIGS['t9-fracture-types'] = frac_types


# ---------- burn depth ----------
def skin_block(x0, y0, w):
    """Skin cross-section: epidermis, dermis, fat, muscle. y0 = skin surface."""
    E, D, F, M = 16, 78, 50, 34
    s = (f'<rect x="{x0}" y="{y0 + E + D + F}" width="{w}" height="{M}" fill="#C8574F"/>'
         + ''.join(f'<path d="M{x0} {y0 + E + D + F + 8 + k * 9}H{x0 + w}" stroke="#A9413A" stroke-width="1.2"/>' for k in range(3))
         + f'<rect x="{x0}" y="{y0 + E + D}" width="{w}" height="{F}" fill="#F7DC86"/>'
         + ''.join(f'<ellipse cx="{x0 + 14 + k * 26 + (8 if (k % 2) else 0)}" cy="{y0 + E + D + 14 + (k % 3) * 12}" rx="12" ry="9" fill="#FBE7A8" stroke="#E2BE5C" stroke-width="1"/>' for k in range(int(w / 26)))
         + f'<rect x="{x0}" y="{y0 + E}" width="{w}" height="{D}" fill="#F3C1B3"/>'
         + f'<rect x="{x0}" y="{y0}" width="{w}" height="{E}" fill="#EDB79A"/>'
         + f'<path d="M{x0} {y0 + E}H{x0 + w}" stroke="#C98D78" stroke-width="1.5" stroke-dasharray="4 3"/>')
    # hair follicles, sweat glands, nerves, vessels
    for k in range(int(w / 90)):
        hx = x0 + 30 + k * 90
        s += f'<path d="M{hx} {y0 - 22}C{hx + 2} {y0 - 6} {hx - 1} {y0 + 40} {hx + 4} {y0 + E + D - 8}" stroke="#5B4636" stroke-width="2" fill="none"/>'
        s += f'<ellipse cx="{hx + 4}" cy="{y0 + E + D - 6}" rx="6" ry="8" fill="#E39A86" stroke="#B5705C"/>'
        gx = hx + 46
        s += f'<path d="M{gx} {y0}C{gx} {y0 + 30} {gx + 2} {y0 + 50} {gx} {y0 + E + D - 12}" stroke="#7DA7C9" stroke-width="1.6" fill="none"/>'
        s += f'<path d="M{gx - 8} {y0 + E + D - 10}c4 -8 12 -8 14 0s-10 8 -12 0s8 -10 12 -2" stroke="#7DA7C9" stroke-width="2" fill="none"/>'
        nx = hx + 22
        s += f'<path d="M{nx} {y0 + E + D + 40}L{nx} {y0 + E + 10}M{nx} {y0 + E + 22}l-8 -10M{nx} {y0 + E + 22}l8 -10" stroke="#E0A800" stroke-width="1.8" fill="none"/>'
    s += f'<path d="M{x0} {y0 + E + D - 4}C{x0 + w * .3} {y0 + E + D - 12} {x0 + w * .6} {y0 + E + D + 2} {x0 + w} {y0 + E + D - 6}" stroke="#C7463E" stroke-width="3" fill="none"/>'
    return s


def burns():
    W, H = 760, 640
    x0, y0, w = 24, 150, 712
    cw = w / 4
    b = ''
    b += f'<clipPath id="skc"><rect x="{x0}" y="{y0 - 40}" width="{w}" height="260" rx="10"/></clipPath><g clip-path="url(#skc)">{skin_block(x0, y0, w)}'
    # depth overlays
    b += f'<rect x="{x0}" y="{y0}" width="{cw}" height="16" fill="#E2453C" opacity=".55"/>'
    b += f'<rect x="{x0 + cw}" y="{y0}" width="{cw}" height="44" fill="#E2453C" opacity=".38"/>'
    b += f'<path d="M{x0 + cw + 30} {y0}C{x0 + cw + 40} {y0 - 30} {x0 + cw + 130} {y0 - 30} {x0 + cw + 140} {y0}Z" fill="#FFF6C9" stroke="#D8B347" stroke-width="1.6" opacity=".95"/>'
    b += f'<rect x="{x0 + 2 * cw}" y="{y0}" width="{cw}" height="88" fill="#F6EFEA" opacity=".8"/>'
    b += ''.join(f'<circle cx="{x0 + 2 * cw + 14 + (k * 37) % 160}" cy="{y0 + 12 + (k * 23) % 70}" r="{4 + k % 3}" fill="#D9675C" opacity=".55"/>' for k in range(14))
    b += f'<rect x="{x0 + 3 * cw}" y="{y0 - 2}" width="{cw}" height="98" fill="#3B2A22" opacity=".92"/>'
    b += ''.join(f'<path d="M{x0 + 3 * cw + 10 + k * 22} {y0 + 4}l8 18l-6 14l10 20" stroke="#6E5547" stroke-width="1.4" fill="none"/>' for k in range(8))
    b += '</g>'
    for k in range(1, 4):
        b += f'<path d="M{x0 + k * cw} {y0 - 40}V{y0 + 220}" stroke="#FFFFFF" stroke-width="3"/><path d="M{x0 + k * cw} {y0 - 40}V{y0 + 220}" class="ln" stroke-width="1.2" stroke-dasharray="4 4"/>'
    # layer labels at right edge
    for lab, yy in (('epidermis', y0 + 12), ('dermis', y0 + 56), ('fat', y0 + 120), ('muscle', y0 + 166)):
        b += T(x0 + 8, yy, lab, 'l sm b', 'start', ' style="fill:#3B2A22" paint-order="stroke" stroke="#FFFFFFC0" stroke-width="3"')
    cols = [('Superficial', '1st degree', 'red', 'Epidermis only', 'Red, no blisters', 'Painful', '5–7 days, no scar'),
            ('Superficial partial', '2nd degree', 'amb', 'Upper dermis', 'Blisters, moist, pink', 'Very painful', '2–3 weeks'),
            ('Deep partial', 'thickness', 'pur', 'Deep dermis', 'Pale, mottled', 'Less painful', 'Over 3 weeks, scars'),
            ('Full thickness', '3rd degree', 'ink', 'Whole skin', 'White/charred, leathery', 'Painless: nerves gone', 'Needs grafting')]
    for k, (n1, n2, c, lay, look, pain, heal) in enumerate(cols):
        cx = x0 + k * cw + 10
        b += T(cx, 84, n1, f'l b {c}') + T(cx, 100, n2, 'n sm')
        yy = y0 + 250
        b += card(x0 + k * cw + 4, yy - 22, cw - 8, 196, 'pn')
        for j, (lab, val) in enumerate((('Reaches', lay), ('Looks', look), ('Pain', pain), ('Heals', heal))):
            b += T(cx + 4, yy + j * 44, lab.upper(), 'n sm b') + T(cx + 4, yy + 18 + j * 44, val, 'l sm', 'start', ' textLength="150" lengthAdjust="spacingAndGlyphs"' if len(val) > 21 else '')
    b += T(x0, H - 22, 'First aid: cool under running tap water for 20 minutes; no ice, butter or oil. Blisters = superficial partial thickness.', 'n sm')
    alt = 'Burn depth on a cross-section of skin: superficial (first degree) burns reach only the epidermis and are red and painful; superficial partial thickness burns reach the upper dermis and blister; deep partial thickness burns reach the deep dermis and look pale and mottled; full thickness burns destroy the whole skin, look white or charred and are painless because the nerves are destroyed.'
    return plate(W, H, 'Burns: how deep is the damage?', 'Depth decides the look, the pain and the healing', b, alt), alt


FIGS['t9-burn-depth'] = burns


# ---------- the three red eyes ----------
ALM = 'M-84 0 C-46 -46 46 -46 84 0 C46 42 -46 42 -84 0 Z'


def eye_front(kind, uid):
    s = f'<clipPath id="al{uid}"><path d="{ALM}"/></clipPath>'
    s += f'<path d="M-104 -6 C-60 -76 60 -76 104 -6 C60 -54 -60 -54 -104 -6 Z" fill="url(#skin)" opacity=".9"/>'  # upper lid fold
    s += f'<path d="M-100 4 C-60 60 60 60 100 4 C60 50 -60 50 -100 4 Z" fill="url(#skin)" opacity=".9"/>'
    s += f'<g clip-path="url(#al{uid})"><rect x="-90" y="-50" width="180" height="100" fill="#FBFBF8"/>'
    if kind == 'conj':
        s += f'<radialGradient id="cj{uid}" cx=".5" cy=".5" r=".6"><stop offset=".35" stop-color="#E3463C" stop-opacity="0"/><stop offset="1" stop-color="#E3463C" stop-opacity=".75"/></radialGradient><rect x="-90" y="-50" width="180" height="100" fill="url(#cj{uid})"/>'
        for k in range(14):
            a = k / 14 * 6.283
            x1, y1 = 90 * math.cos(a), 50 * math.sin(a)
            x2, y2 = 46 * math.cos(a + .15), 34 * math.sin(a + .15)
            s += f'<path d="M{x1:.0f} {y1:.0f}Q{(x1 + x2) / 2 + 6:.0f} {(y1 + y2) / 2 - 5:.0f} {x2:.0f} {y2:.0f}" stroke="#C7302A" stroke-width="1.3" fill="none" opacity=".8"/>'
    else:
        s += f'<radialGradient id="cf{uid}" cx="0" cy="0" r="56" gradientUnits="userSpaceOnUse"><stop offset=".45" stop-color="#C92E2A" stop-opacity=".9"/><stop offset=".62" stop-color="#E3463C" stop-opacity=".45"/><stop offset="1" stop-color="#E3463C" stop-opacity="0"/></radialGradient><circle r="56" fill="url(#cf{uid})"/>'
    s += f'<circle r="27" fill="#8A5A34"/><circle r="27" fill="none" stroke="#5A391F" stroke-width="2"/>'
    s += ''.join(f'<path d="M{9 * math.cos(k * .52):.1f} {9 * math.sin(k * .52):.1f}L{25 * math.cos(k * .52):.1f} {25 * math.sin(k * .52):.1f}" stroke="#A97A4F" stroke-width="1.2"/>' for k in range(12))
    if kind == 'conj':
        s += '<circle r="9" fill="#111"/>'
    elif kind == 'glau':
        s += '<ellipse rx="11" ry="16" fill="#111"/><circle r="27" fill="#E8EEF2" opacity=".55"/>'
    else:
        s += '<path d="M-5 -4 L-1 -6 L5 -3 L4 3 L0 5 L-5 2 Z" fill="#111"/>'
        s += ''.join(f'<circle cx="{-12 + k * 6}" cy="{16 + (k % 2) * 4}" r="1.6" fill="#F1F1EA" opacity=".9"/>' for k in range(5))
    s += '<circle cx="-9" cy="-10" r="4" fill="#fff" opacity=".85"/></g>'
    s += f'<path d="{ALM}" fill="none" stroke="#9C6B55" stroke-width="2"/>'
    s += ''.join(f'<path d="M{-64 + k * 13} {-24 - (4 if 2 < k < 8 else 0)}l{-2 + k * .4:.1f} -13" stroke="#3A2A20" stroke-width="2" stroke-linecap="round"/>' for k in range(11))
    if kind == 'conj':
        s += '<path d="M-84 0 C-78 8 -66 12 -58 10 C-62 6 -70 2 -84 0 Z" fill="#E8C64A" opacity=".9"/><path d="M-30 31 C-10 36 10 36 26 31" stroke="#E8C64A" stroke-width="4" fill="none" stroke-linecap="round" opacity=".85"/>'
    return s


def red_eyes():
    W, H = 760, 650
    cols = [('conj', 'Acute conjunctivitis', 'grn', [('Pain', 'Gritty, little pain'), ('Vision', 'Normal'), ('Redness', 'Worst at the fornices'), ('Discharge', 'Present'), ('Cornea', 'Clear'), ('Pupil', 'Normal, reacting'), ('Pressure', 'Normal')], 'Hygiene, treat at home'),
            ('glau', 'Acute angle-closure glaucoma', 'red', [('Pain', 'Severe, headache, vomiting'), ('Vision', 'Much reduced, halos'), ('Redness', 'Ciliary flush'), ('Discharge', 'None, watering'), ('Cornea', 'Hazy, oedematous'), ('Pupil', 'Mid-dilated, oval, fixed'), ('Pressure', 'Very high, stony hard')], 'EMERGENCY referral'),
            ('irit', 'Acute iritis (anterior uveitis)', 'pur', [('Pain', 'Moderate ache, photophobia'), ('Vision', 'Mildly blurred'), ('Redness', 'Ciliary flush'), ('Discharge', 'None, watering'), ('Cornea', 'Clear; keratic precipitates'), ('Pupil', 'Small, irregular, sluggish'), ('Pressure', 'Normal or low')], 'Refer for slit lamp')]
    b = ''
    for i, (k, name, c, rows, act) in enumerate(cols):
        x0 = 24 + i * 240
        b += card(x0, 76, 228, 548, 'pn')
        b += g(eye_front(k, i), x0 + 114, 168, sc=0.98)
        b += T(x0 + 14, 262, name if len(name) < 26 else name.split(' (')[0], f'l b {c}')
        if '(' in name: b += T(x0 + 14, 278, '(' + name.split(' (')[1], 'n sm')
        for j, (lab, val) in enumerate(rows):
            yy = 306 + j * 40
            b += T(x0 + 14, yy, lab.upper(), 'n sm b') + T(x0 + 14, yy + 17, val, 'l sm', 'start', ' textLength="200" lengthAdjust="spacingAndGlyphs"' if len(val) > 26 else '')
        b += pill(x0 + 14, 600, act, c, 200)
    alt = 'The three common red eyes seen from the front: acute conjunctivitis with redness worst at the fornices, discharge and a normal pupil; acute angle-closure glaucoma with ciliary flush, a hazy cornea and a fixed, mid-dilated, vertically oval pupil; and acute iritis with ciliary flush and a small irregular pupil.'
    return plate(W, H, 'Three red eyes: look at the pupil', 'A red eye with a fixed mid-dilated pupil is glaucoma until proved otherwise', b, alt), alt


FIGS['t9-red-eyes'] = red_eyes


# ---------- eye in section: cataract and glaucoma ----------
def eyeball(kind, uid):
    s = '<path d="M-80 -44 A92 92 0 1 1 -80 44 Z" fill="#F6F1E8" stroke="#B9AE9C" stroke-width="2.4"/>'
    s += '<path d="M-72 -46 A86 86 0 1 1 -72 46 Z" fill="#EAF4EF"/>'
    s += f'<path d="M-8 -86 A86 86 0 0 1 -8 86" fill="none" stroke="#D9655B" stroke-width="3"/>'  # retina
    # cornea and anterior chamber
    s += '<path d="M-80 -44 C-104 -30 -106 30 -80 44 L-76 40 C-96 26 -96 -26 -76 -40 Z" fill="#CFE6F3" stroke="#7FA9C4" stroke-width="1.6"/>'
    s += '<path d="M-76 -40 C-96 -26 -96 26 -76 40 L-70 40 L-70 -40 Z" fill="#E3F2FA"/>'
    if kind == 'glau':
        s += '<path d="M-82 -46 C-80 -30 -74 -16 -64 -12 L-62 -16 C-70 -22 -76 -34 -78 -46 Z M-82 46 C-80 30 -74 16 -64 12 L-62 16 C-70 22 -76 34 -78 46 Z" fill="#8A5A34"/>'
    else:
        s += '<path d="M-76 -46 L-70 -46 L-68 -12 L-74 -12 Z M-76 46 L-70 46 L-68 12 L-74 12 Z" fill="#8A5A34"/>'
    s += '<path d="M-70 -50 L-56 -56 L-60 -40 Z M-70 50 L-56 56 L-60 40 Z" fill="#B9776B"/>'  # ciliary body
    s += ''.join(f'<path d="M-60 {sy * 46}L-56 {sy * 26}" stroke="#9AA6AE" stroke-width="1"/>' for sy in (-1, 1))
    lens_fill = '#D4CDBD' if kind == 'cat' else '#F4FAFD'
    s += f'<ellipse cx="-56" cy="0" rx="14" ry="30" fill="{lens_fill}" stroke="#93A9B8" stroke-width="1.6"/>'
    if kind == 'cat':
        s += ''.join(f'<circle cx="{-62 + (k * 7) % 14}" cy="{-22 + k * 6}" r="{3 + k % 3}" fill="#B8AE98" opacity=".6"/>' for k in range(8))
    # optic nerve
    s += '<path d="M86 -12 C100 -14 120 -16 150 -16 L150 16 C120 16 100 14 86 12 Z" fill="#F1D9A6" stroke="#C9A867" stroke-width="1.6"/>'
    if kind == 'glau':
        s += '<path d="M84 -12 C76 -8 74 8 84 12" fill="#EAF4EF" stroke="#D9655B" stroke-width="2"/>'
        for ang in range(-150, 180, 60):
            a = math.radians(ang)
            s += f'<path d="M{10 + 26 * math.cos(a):.0f} {26 * math.sin(a):.0f}L{10 + 56 * math.cos(a):.0f} {56 * math.sin(a):.0f}" class="sred" stroke-width="2.2" marker-end="url(#ah)" stroke-linecap="round" opacity=".8"/>'
        s += '<text x="10" y="5" class="l sm b red" text-anchor="middle">IOP &gt; 21</text>'
    # light rays
    if kind == 'cat':
        s += '<path d="M-150 -18 L-60 -10 M-150 0 L-60 0 M-150 18 L-60 10" stroke="#E5B93B" stroke-width="2" stroke-dasharray="5 4"/>'
        s += '<path d="M-40 -6 L20 -30 M-40 0 L30 4 M-40 8 L10 40" stroke="#E5B93B" stroke-width="1.6" stroke-dasharray="2 5" opacity=".7"/>'
    elif kind == 'norm':
        s += '<path d="M-150 -18 L-56 -14 L86 0 M-150 0 L86 0 M-150 18 L-56 14 L86 0" stroke="#E5B93B" stroke-width="2" fill="none"/>'
    return s


def disc(cx, cy, cup, lab):
    return (f'<circle cx="{cx}" cy="{cy}" r="30" fill="#D9655B"/><circle cx="{cx}" cy="{cy}" r="19" fill="#F3C98D"/><circle cx="{cx}" cy="{cy}" r="{cup}" fill="#FFF3D6"/>'
            + f'<path d="M{cx + 2} {cy - cup}C{cx + 4} {cy - 22} {cx - 6} {cy - 27} {cx - 22} {cy - 20}M{cx + 2} {cy + cup}C{cx + 4} {cy + 22} {cx - 6} {cy + 27} {cx - 22} {cy + 20}" stroke="#A8322B" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
            + T(cx, cy + 46, lab, 'n sm', 'middle'))


def eye_section():
    W, H = 760, 760
    b = ''
    panels = [('norm', 'Normal eye', 'blu', ['Clear lens focuses light on the retina', 'Pressure (IOP) 10–21 mmHg'], 76),
              ('cat', 'Cataract', 'amb', ['Opacity of the LENS: light scatters', 'Painless, gradual loss of vision', 'Commonest cause of blindness in India', 'Treated by surgery (lens replacement)'], 298),
              ('glau', 'Glaucoma', 'red', ['Raised pressure damages the optic', 'nerve: the disc becomes CUPPED', 'Open-angle (commonest): painless,', 'slow field loss. Angle-closure: emergency'], 520)]
    for k, name, c, lines, y0 in panels:
        b += card(24, y0, 712, 210, 'pn')
        b += g(eyeball(k, k), 200, y0 + 105, sc=1.0)
        b += T(400, y0 + 40, name, f'h xl {c}') + TL(400, y0 + 66, lines, 'n', 19)
    # labels on the normal eye
    y0 = 76
    b += lead(70, y0 + 32, 102, y0 + 72) + T(70, y0 + 26, 'cornea', 'n sm', 'middle')
    b += lead(148, y0 + 24, 132, y0 + 62) + T(150, y0 + 18, 'iris', 'n sm', 'middle')
    b += lead(150, y0 + 192, 144, y0 + 126) + T(150, y0 + 204, 'lens', 'n sm', 'middle')
    b += lead(250, y0 + 194, 230, y0 + 170) + T(256, y0 + 206, 'vitreous', 'n sm', 'middle')
    b += lead(300, y0 + 26, 272, y0 + 52) + T(300, y0 + 20, 'retina', 'n sm', 'middle')
    b += lead(340, y0 + 150, 330, y0 + 118) + T(340, y0 + 164, 'optic nerve', 'n sm', 'middle')
    b += lead(60, 298 + 190, 140, 298 + 120) + T(60, 298 + 204, 'cloudy lens', 'n sm b amb', 'middle')
    b += lead(70, 520 + 196, 128, 520 + 132) + T(70, 520 + 208, 'narrow angle', 'n sm b red', 'middle')
    b += lead(330, 520 + 190, 284, 520 + 108) + T(330, 520 + 204, 'cupped disc', 'n sm b red', 'middle')
    b += g(disc(0, 0, 7, 'normal cup'), 560, 520 + 166, sc=0.8) + g(disc(0, 0, 16, 'glaucoma cup'), 650, 520 + 166, sc=0.8)
    alt = 'Cross-sections of the eye: a normal eye with a clear lens focusing light on the retina; a cataract with an opaque, cloudy lens that scatters light; and glaucoma with raised pressure pushing on the eye, a narrow angle and a cupped optic disc, with optic disc views of a normal small cup and an enlarged glaucoma cup.'
    return plate(W, H, 'Cataract and glaucoma', 'Cataract clouds the lens; glaucoma damages the optic nerve', b, alt), alt


FIGS['t9-eye-section'] = eye_section


# ---------- CPR ----------
def cpr():
    W, H = 760, 620
    b = card(24, 76, 330, 384, 'pn') + card(366, 76, 370, 384, 'pn')
    # top view of the patient
    tx, ty = 189, 96
    body = (f'<circle cx="0" cy="26" r="26" {SKIN}/>'
            f'<path d="M-14 48 L-14 62 L14 62 L14 48" {SKIN}/>'
            f'<path d="M-110 92 C-104 70 -60 62 -14 60 L14 60 C60 62 104 70 110 92 C114 150 108 230 92 330 L-92 330 C-108 230 -114 150 -110 92 Z" fill="#E9F0F7" stroke="#9AAFC4" stroke-width="2"/>'
            f'<path d="M-110 92 C-126 160 -128 240 -122 330 L-100 330 C-102 250 -98 170 -92 110 Z M110 92 C126 160 128 240 122 330 L100 330 C102 250 98 170 92 110 Z" fill="#DCE6F1" stroke="#9AAFC4" stroke-width="2"/>')
    ribs = ''.join(f'<path d="M-12 {104 + k * 22} C-40 {100 + k * 22} -70 {108 + k * 24} -86 {126 + k * 26}M12 {104 + k * 22} C40 {100 + k * 22} 70 {108 + k * 24} 86 {126 + k * 26}" stroke="#B8C6D6" stroke-width="3" fill="none" stroke-linecap="round"/>' for k in range(6))
    stern = '<rect x="-11" y="92" width="22" height="130" rx="9" fill="#EAD9B8" stroke="#8A7150" stroke-width="1.4"/><path d="M-7 222 L0 236 L7 222" fill="#EAD9B8" stroke="#8A7150" stroke-width="1.4"/>'
    fing = lambda col, dy: ''.join(f'<path d="M-14 {dy + k * 10}L-50 {dy + k * 10 - 3}" stroke="{col}" stroke-width="9" stroke-linecap="round"/>' for k in range(4))
    hands = ('<g transform="translate(0 180)">' + fing('#D9A587', -19) + f'<ellipse cx="6" cy="0" rx="26" ry="22" {SKIN}/>' + fing('#F2CDB4', -14)
             + '<path d="M10 -20 C22 -30 34 -30 38 -22" stroke="#E3B293" stroke-width="9" stroke-linecap="round" fill="none"/>'
             + '<path d="M28 -14 C40 -10 44 6 36 16" stroke="#B9826A" stroke-width="1.4" fill="none"/></g>')
    b += g(body + ribs + stern + hands, tx, ty, sc=0.98)
    b += lead(190, 432, 190, 290) + T(40, 448, 'Heel of the hand on the centre of the chest', 'l sm')
    b += T(40, 104, 'WHERE', 'n sm b')
    # side view: depth
    sx, sy = 551, 260
    side = ('<ellipse cx="0" cy="40" rx="150" ry="74" fill="#E9F0F7" stroke="#9AAFC4" stroke-width="2"/>'
            '<path d="M-26 -30 L26 -30 L26 -18 L-26 -18 Z" fill="#EAD9B8" stroke="#8A7150" stroke-width="1.4"/>'
            '<path d="M-26 52 C-40 20 -10 0 0 18 C12 0 40 20 24 52 C14 74 0 84 0 84 C0 84 -14 74 -26 52 Z" fill="#E06A63" stroke="#B9473F" stroke-width="1.6"/>'
            '<rect x="-16" y="94" width="32" height="20" rx="6" fill="#EAD9B8" stroke="#8A7150" stroke-width="1.4"/>'
            f'<path d="M-40 -96 L-40 -50 C-40 -40 -30 -34 -20 -34 L20 -34 C30 -34 40 -40 40 -50 L40 -96" {SKIN}/>'
            '<path d="M-150 -30 L150 -30" stroke="#9AAFC4" stroke-width="1.2" stroke-dasharray="4 4"/>')
    side += arrow(-80, -110, -80, -40, 'sred', 4) + arrow(80, -110, 80, -40, 'sred', 4)
    side += '<path d="M118 -30 L118 2" stroke="#D33A3F" stroke-width="2.4"/><path d="M110 -30 L126 -30 M110 2 L126 2" stroke="#D33A3F" stroke-width="2.4"/>'
    b += g(side, sx, sy)
    b += T(sx + 136, sy - 8, '5–6 cm', 'l b red') + T(382, 104, 'HOW DEEP · side view', 'n sm b')
    b += lead(sx - 4, sy + 158, sx, sy + 66) + T(sx - 4, sy + 172, 'heart squeezed between sternum and spine', 'n sm', 'middle')
    b += T(sx, sy - 128, 'arms straight, push hard and fast', 'l sm', 'middle')
    # sequence
    steps = [('Check', 'response and breathing', 'blu'), ('Call', 'for help', 'amb'), ('30 compressions', '100–120 per minute', 'red'), ('2 breaths', 'then repeat 30 : 2', 'grn')]
    b += T(24, 492, 'Adult basic life support: C-A-B (Circulation, Airway, Breathing)', 'l b')
    for i, (a1, a2, c) in enumerate(steps):
        x0 = 24 + i * 180
        b += card(x0, 506, 168, 72, f'f{c}', 12) + T(x0 + 14, 534, a1, f'l b {c}') + T(x0 + 14, 556, a2, 'n sm')
        if i < 3: b += arrow(x0 + 160, 542, x0 + 186, 542, f's{c}', 2.4)
    b += T(24, 602, 'Breathing but unconscious: recovery position. Continue CPR until help arrives.', 'n sm')
    alt = 'Adult CPR: the heel of the hand, with the other hand on top, goes on the centre of the chest; compress 5 to 6 cm with straight arms, squeezing the heart between sternum and spine, at 100 to 120 per minute; sequence C-A-B: check response and breathing, call for help, 30 compressions, 2 breaths, repeat.'
    return plate(W, H, 'CPR: 30 compressions, 2 breaths', 'Where to push, how deep and how fast', b, alt), alt


FIGS['t9-cpr'] = cpr
