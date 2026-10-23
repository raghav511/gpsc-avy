from lib import *
from hands import front_hand, side_hand
import math


def nerve_hands():
    W, H = 760, 760
    tiles = [
        ('Wrist drop', 'Radial nerve (C5–T1)', 'red', ['Spiral-groove fracture of the humerus', 'or "Saturday night palsy"', 'Wrist and finger extensors fail']),
        ('Claw hand', 'Ulnar nerve (C8, T1)', 'blu', ['Ring and little fingers: knuckles', 'bent back, finger joints curled', 'Medial epicondyle injury; Froment\'s sign']),
        ('Hand of benediction', 'Median nerve at the elbow', 'pur', ['On trying to make a fist, the index', 'and middle fingers stay straight', '']),
        ('Ape-thumb hand', 'Median nerve at the wrist', 'grn', ['Carpal tunnel syndrome: thenar', 'muscles waste, the thumb lies flat', 'in line with the fingers']),
    ]
    b = ''
    for k, (name, nerve, c, lines) in enumerate(tiles):
        col, row = k % 2, k // 2
        x0, y0 = 24 + col * 362, 76 + row * 336
        b += card(x0, y0, 350, 324, 'pn')
        cx, cy = x0 + 175, y0 + 120
        if k == 0:
            art, _ = side_hand(mcp=10, pip=12, dip=8, wrist=70)
            b += g(art, cx + 30, cy - 46, sc=0.95) + arrow(cx + 100, cy - 30, cx + 92, cy + 30, 'sred', 2.4, (cx + 112, cy))
        elif k == 1:
            art, _ = side_hand(mcp=-22, pip=78, dip=55, wrist=0)
            b += g(art, cx + 20, cy - 4, sc=0.95)
            b += lead(cx + 116, cy - 76, cx + 82, cy - 20) + T(cx + 116, cy - 82, 'knuckle bent back', 'n sm', 'middle')
            b += lead(cx + 140, cy + 60, cx + 120, cy + 14) + T(cx + 140, cy + 74, 'fingers curled', 'n sm', 'middle')
        elif k == 2:
            b += g(front_hand({'ring': 'flex', 'little': 'flex'}), cx, cy + 16, sc=0.9)
        else:
            b += g(front_hand({}, thumb='ape', thenar=False), cx, cy + 16, sc=0.9)
            b += lead(cx - 110, cy + 60, cx - 38, cy + 34) + TL(cx - 110, cy + 76, ['flat, wasted', 'thenar'], 'n sm', 14, 'middle')
        b += T(x0 + 18, y0 + 236, name, f'l b {c}', 'start', ' style="font-size:17px"') + T(x0 + 18, y0 + 256, nerve, 'l sm')
        b += TL(x0 + 18, y0 + 278, [l for l in lines if l], 'n sm', 16)
    alt = 'Hand deformities from nerve injuries: wrist drop from radial nerve injury (spiral-groove fracture, Saturday night palsy); claw hand from ulnar nerve injury with the ring and little fingers bent back at the knuckles and curled at the finger joints; hand of benediction from median nerve injury at the elbow, where the index and middle fingers stay straight on trying to make a fist; and ape-thumb hand from median nerve injury at the wrist (carpal tunnel), with a wasted thenar eminence and the thumb lying flat beside the fingers.'
    return plate(W, H, 'Nerve injuries you can see in the hand', 'Radial drops the wrist, ulnar claws, median blesses or flattens the thumb', b, alt), alt


FIGS = {'t5-nerve-hands': nerve_hands}


def heart_conduction():
    W, H = 760, 640
    hx, hy = 250, 360
    heart = ''
    # great vessels
    heart += '<path d="M-20 -96 C-22 -150 40 -176 92 -150 C110 -140 118 -120 116 -100 L94 -100 C94 -130 50 -146 18 -126 C8 -118 6 -106 8 -96 Z" fill="#D9534C" stroke="#A8322B" stroke-width="2"/>'
    heart += '<path d="M-112 -76 L-112 -160 L-78 -160 L-78 -80 Z" fill="#6E8FC9" stroke="#43629E" stroke-width="2"/>'
    heart += '<path d="M-40 -60 C-44 -110 -10 -128 30 -126 L34 -104 C4 -104 -14 -92 -14 -60 Z" fill="#7FA0D6" stroke="#43629E" stroke-width="2"/>'
    # chambers
    heart += '<path d="M-128 -40 C-132 40 -70 120 34 152 C120 100 150 20 126 -36 C90 -60 -90 -64 -128 -40 Z" fill="#E59A93" stroke="#A8322B" stroke-width="2.4"/>'
    heart += '<ellipse cx="-80" cy="-52" rx="58" ry="44" fill="#E59A93" stroke="#A8322B" stroke-width="2.4"/><ellipse cx="74" cy="-62" rx="54" ry="38" fill="#E59A93" stroke="#A8322B" stroke-width="2.4"/>'
    # cut-away cavities
    heart += '<ellipse cx="-80" cy="-50" rx="42" ry="28" fill="#C7D6EE"/><ellipse cx="74" cy="-60" rx="38" ry="24" fill="#F6D2CC"/>'
    heart += '<path d="M-108 -6 C-110 40 -70 92 -14 116 C-6 80 -10 30 -16 -6 Z" fill="#C7D6EE"/>'
    heart += '<path d="M8 -6 C14 40 20 90 30 128 C90 92 112 40 104 -6 Z" fill="#F6D2CC"/>'
    heart += '<path d="M-124 -16 L120 -20" stroke="#A8322B" stroke-width="2" opacity=".5"/>'
    # conduction system
    Y = '#E0A800'
    heart += f'<path d="M-92 -78 C-70 -60 -50 -40 -24 -22" stroke="{Y}" stroke-width="2.4" stroke-dasharray="5 5" fill="none"/>'
    heart += f'<path d="M-24 -22 L-6 4" stroke="{Y}" stroke-width="7" stroke-linecap="round"/>'
    heart += f'<path d="M-6 4 C-14 40 -22 80 -18 110 C-40 100 -80 70 -100 20" stroke="{Y}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    heart += f'<path d="M-6 4 C2 40 12 80 26 122 C64 100 96 60 110 10" stroke="{Y}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
    for (x, y, a) in [(-60, 92, 200), (-86, 56, 210), (-100, 24, 230), (60, 104, -20), (86, 76, -40), (104, 40, -60), (-34, 108, 160), (40, 118, 10)]:
        r = math.radians(a)
        heart += f'<path d="M{x} {y}l{12 * math.cos(r):.0f} {12 * math.sin(r):.0f}M{x} {y}l{12 * math.cos(r + .7):.0f} {12 * math.sin(r + .7):.0f}" stroke="{Y}" stroke-width="2" stroke-linecap="round"/>'
    heart += f'<circle cx="-92" cy="-78" r="9" fill="#2FA36B" stroke="#fff" stroke-width="2"/><circle cx="-24" cy="-22" r="8" fill="#2E68D8" stroke="#fff" stroke-width="2"/>'
    b = g(heart, hx, hy, sc=1.18)
    for lab, (x, y) in {'RA': (-80, -48), 'LA': (74, -58), 'RV': (-62, 44), 'LV': (62, 44), 'Aorta': (60, -150), 'SVC': (-95, -168)}.items():
        b += T(hx + x * 1.18, hy + y * 1.18 + 4, lab, 'l sm b', 'middle', ' style="fill:#5A2A26"' if lab in ('RA', 'LA', 'RV', 'LV') else '')
    steps = [('SA node', 'grn', 'The pacemaker: 70–80/min', (hx - 92 * 1.18, hy - 78 * 1.18)),
             ('AV node', 'blu', 'Delays about 0.1 s so the atria', (hx - 24 * 1.18, hy - 22 * 1.18), 'empty first; own rate 40–60/min'),
             ('Bundle of His', 'amb', 'Through the septum', (hx - 14 * 1.18, hy - 6 * 1.18)),
             ('Right and left bundle branches', 'amb', 'Down each side of the septum', (hx + 4 * 1.18, hy + 60 * 1.18)),
             ('Purkinje fibres', 'red', 'Fastest conduction, 4 m/s;', (hx + 86 * 1.18, hy + 76 * 1.18), 'own rate 20–40/min')]
    for i, st in enumerate(steps):
        name, c, l1, (px, py) = st[:4]
        y = 110 + i * 100
        b += f'<circle cx="474" cy="{y - 5}" r="13" class="f{c}"/>' + T(474, y, str(i + 1), f'l sm b {c}', 'middle')
        b += T(496, y, name, f'l b {c}') + T(496, y + 20, l1, 'n sm') + (T(496, y + 36, st[4], 'n sm') if len(st) > 4 else '')
        b += f'<path d="M460 {y - 5}L{px + 12:.0f} {py:.0f}" class="ln" stroke-width="1" stroke-dasharray="2 3" fill="none"/>'
        if i < 4: b += f'<path d="M474 {y + 10}L474 {y + 82}" class="ln" stroke-width="1.4"/>'
    b += T(24, 620, 'Front view, chambers opened. The impulse runs top to bottom: SA → AV → His → branches → Purkinje.', 'n sm')
    alt = 'The conducting system of the heart in a front view: the SA node in the right atrium is the pacemaker at 70 to 80 per minute; the impulse crosses the atria to the AV node, which delays it about 0.1 second and has its own rate of 40 to 60; then the bundle of His, the right and left bundle branches down the septum, and the Purkinje fibres, which conduct fastest at 4 metres per second and have an intrinsic rate of 20 to 40.'
    return plate(W, H, 'How the heartbeat spreads', 'The conducting system, from pacemaker to ventricular wall', b, alt), alt


FIGS['t5-heart-conduction'] = heart_conduction


def gas_exchange():
    W, H = 760, 560
    b = ''
    # alveolus
    b += '<circle cx="380" cy="236" r="116" fill="#EAF3FB" stroke="#9DB7D2" stroke-width="10"/>'
    b += '<path d="M380 122 L380 74" stroke="#9DB7D2" stroke-width="40"/><path d="M380 128 L380 74" stroke="#EAF3FB" stroke-width="22"/>'
    b += T(424, 96, 'air in', 'n sm')
    b += '<ellipse cx="300" cy="158" rx="18" ry="11" fill="#C6A3D9" stroke="#8D62A8" stroke-width="1.4"/><circle cx="300" cy="158" r="4" fill="#5E3D78"/>'
    b += ''.join(f'<circle cx="{292 + k * 6}" cy="{140 - (k % 2) * 4}" r="2.4" fill="#C6A3D9"/>' for k in range(4))
    b += T(380, 206, 'ALVEOLUS', 'n sm b', 'middle', ' style="fill:#4A5266"') + '<text x="380" y="232" text-anchor="middle" style="font:700 15px system-ui,sans-serif;fill:#1E2330">PO₂ <tspan style="fill:#2E68D8">104</tspan> · PCO₂ <tspan style="fill:#D33A3F">40</tspan></text>' + T(380, 250, 'mmHg', 'n sm', 'middle', ' style="fill:#4A5266"')
    # capillary
    b += '<linearGradient id="cap" x1="0" x2="1"><stop offset="0" stop-color="#6E8FC9"/><stop offset=".55" stop-color="#B05A8C"/><stop offset="1" stop-color="#D9534C"/></linearGradient>'
    b += '<path d="M40 374 C200 374 250 352 380 352 C510 352 560 374 720 374 L720 430 C560 430 510 408 380 408 C250 408 200 430 40 430 Z" fill="url(#cap)" opacity=".9"/>'
    for x in (120, 250, 380, 510, 640):
        b += f'<ellipse cx="{x}" cy="{392 if x in (250, 510) else 400}" rx="20" ry="10" fill="url(#rbc)" stroke="#9E2B24" stroke-width="1"/>'
    b += arrow(56, 456, 140, 456, 'sblu', 2.4) + arrow(620, 456, 704, 456, 'sred', 2.4)
    b += T(40, 484, 'from the body (venous)', 'l sm b blu') + rich(40, 502, [('PO₂ 40 · PCO₂ 45–46', '')], 'n sm')
    b += T(720, 484, 'to the body (arterial)', 'l sm b red', 'end') + rich(720, 502, [('PO₂ 95–100 · PCO₂ 40', '')], 'n sm', 'end')
    # diffusion arrows
    b += arrow(330, 290, 330, 360, 'sblu', 4) + T(318, 320, 'O₂', 'l b blu', 'end')
    b += arrow(430, 360, 430, 290, 'sred', 4) + T(442, 320, 'CO₂', 'l b red')
    b += T(442, 338, '20× faster', 'n sm')
    # side notes
    b += card(24, 84, 200, 150, 'pn') + T(38, 110, 'Type II cells', 'l b pur') + TL(38, 130, ['secrete surfactant', '(from ~24 weeks of', 'gestation): keeps small', 'alveoli open'], 'n sm', 16)
    b += lead(224, 150, 284, 156)
    b += card(536, 84, 200, 150, 'pn') + T(550, 110, 'How O₂ travels', 'l b blu') + TL(550, 130, ['97–98% on haemoglobin', '1.5–3% dissolved', '1 g Hb carries 1.34 mL', 'P50 about 27 mmHg'], 'n sm', 16)
    b += card(536, 248, 200, 92, 'pn') + T(550, 272, 'How CO₂ travels', 'l b red') + TL(550, 292, ['70% bicarbonate', '23% carbamino, 7% dissolved'], 'n sm', 16)
    b += T(24, 540, 'The thin alveolar wall and capillary wall together form the respiratory membrane.', 'n sm')
    alt = 'Gas exchange between an alveolus and a pulmonary capillary: alveolar PO2 104 and PCO2 40 mmHg; venous blood arrives with PO2 40 and PCO2 45 to 46 and leaves as arterial blood with PO2 95 to 100 and PCO2 40; oxygen diffuses into the blood and carbon dioxide out, about 20 times faster; type II cells secrete surfactant; oxygen travels 97 to 98 percent on haemoglobin, carbon dioxide 70 percent as bicarbonate.'
    return plate(W, H, 'Gas exchange in the lung', 'Partial pressures across one alveolus and its capillary (mmHg)', b, alt), alt


def joints():
    W, H = 760, 580
    B = BONE
    items = [
        ('Plane', ['Intercarpal,', 'acromioclavicular'], f'<rect x="-40" y="-36" width="80" height="32" rx="6" {B}/><rect x="-40" y="4" width="80" height="32" rx="6" {B}/>', '<path d="M-52 0 h104" class="sblu" stroke-width="2.4" marker-end="url(#ah)" marker-start="url(#ah)"/>'),
        ('Hinge', ['Elbow, ankle,', 'interphalangeal'], f'<path d="M-14 -60 L14 -60 L14 -14 C14 4 -14 4 -14 -14 Z" {B}/><path d="M-26 6 C-26 -16 26 -16 26 6 L14 50 L-14 50 Z" {B}/>', '<path d="M40 -10 A40 40 0 0 1 40 40" class="sblu" stroke-width="2.4" fill="none" marker-end="url(#ah)"/>'),
        ('Pivot', ['Superior radio-ulnar;', 'atlanto-axial'], f'<rect x="-10" y="-50" width="20" height="100" rx="10" {B}/><path d="M-28 -18 C-28 -34 28 -34 28 -18 L28 18 C28 34 -28 34 -28 18 Z" fill="none" stroke="#8A7150" stroke-width="7"/>', '<ellipse cx="0" cy="-58" rx="28" ry="8" class="sblu" stroke-width="2.4" fill="none" marker-end="url(#ah)"/>'),
        ('Condylar', ['Knee,', 'temporomandibular'], f'<path d="M-40 -60 L40 -60 L40 -18 C40 4 18 4 10 -10 C4 -2 -4 -2 -10 -10 C-18 4 -40 4 -40 -18 Z" {B}/><path d="M-42 12 C-30 4 -16 6 -8 10 C0 6 8 6 8 10 C16 6 30 4 42 12 L36 54 L-36 54 Z" {B}/>', ''),
        ('Ellipsoid', ['Wrist (radiocarpal),', 'MCP joints'], f'<ellipse cx="0" cy="-16" rx="40" ry="20" {B}/><path d="M-48 10 C-30 -4 30 -4 48 10 L40 54 L-40 54 Z" {B}/>', '<path d="M-58 -16 h116" class="sblu" stroke-width="2" marker-end="url(#ah)" marker-start="url(#ah)"/><path d="M0 -50 v-0" />'),
        ('Saddle', ['1st carpometacarpal', '(thumb)'], f'<path d="M-40 -8 C-20 -30 20 -30 40 -8 L34 -56 L-34 -56 Z" {B}/><path d="M-40 8 C-20 -12 20 -12 40 8 L34 54 L-34 54 Z" {B}/>', '<path d="M-56 30 C-40 40 40 40 56 30" class="sblu" stroke-width="2" fill="none" marker-end="url(#ah)"/>'),
        ('Ball and socket', ['Shoulder, hip'], f'<path d="M-46 -10 C-46 40 46 40 46 -10 L36 -10 C36 26 -36 26 -36 -10 Z" {B}/><circle cx="0" cy="-12" r="30" {B}/><path d="M-8 -40 L-8 -70 L8 -70 L8 -40" {B}/>', '<ellipse cx="0" cy="-12" rx="50" ry="14" class="sblu" stroke-width="2" fill="none" marker-end="url(#ah)"/>'),
    ]
    b = ''
    for k, (name, ex, art, mv) in enumerate(items):
        col, row = k % 4, k // 4
        x0, y0 = 24 + col * 181, 76 + row * 236
        b += card(x0, y0, 169, 224, 'pn')
        b += g(art + mv, x0 + 84, y0 + 92)
        b += T(x0 + 14, y0 + 180, name, 'l b blu') + TL(x0 + 14, y0 + 198, ex, 'n sm', 15)
    x0, y0 = 24 + 3 * 181, 76 + 236
    b += card(x0, y0, 169, 224, 'pn2') + T(x0 + 14, y0 + 30, 'Not synovial', 'l b') + TL(x0 + 14, y0 + 54, ['Fibrous: sutures,', 'syndesmosis, gomphosis', '(tooth in socket)', '', 'Primary cartilaginous:', 'epiphyseal plate', '', 'Secondary: pubic', 'symphysis, discs'], 'n sm', 16)
    b += T(24, 566, 'Hook: "Saddle for the thumb, ball for the limb roots." Blue arrows show the movement each shape allows.', 'n sm')
    alt = 'The seven kinds of synovial joint drawn as bone ends: plane (intercarpal), hinge (elbow, interphalangeal, ankle), pivot (superior radio-ulnar, atlanto-axial), condylar (knee, temporomandibular), ellipsoid (wrist, metacarpophalangeal), saddle (first carpometacarpal of the thumb) and ball and socket (shoulder, hip), with the non-synovial fibrous and cartilaginous joints listed.'
    return plate(W, H, 'Synovial joints by shape', 'The shape of the bone ends decides the movement', b, alt), alt


FIGS['t5-gas-exchange'] = gas_exchange
FIGS['t5-joints'] = joints
