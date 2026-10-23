from lib import *
import math, random


def field(uid, bg='#F3EEF6'):
    return f'<clipPath id="fc{uid}"><circle r="74"/></clipPath><circle r="78" fill="#2B2F3A"/><circle r="74" fill="{bg}"/>', f'clip-path="url(#fc{uid})"'


def rng(seed):
    r = random.Random(seed)
    return r


def microscope():
    W, H = 760, 690
    P, N, RED, BLUE = '#5B2C83', '#D2557A', '#C8323C', '#7FA7D9'
    fields = []
    # 1 cocci in clusters
    r = rng(1); s = ''
    for cx, cy in [(-30, -20), (24, 10), (-10, 34), (30, -36)]:
        for k in range(9):
            a = r.random() * 6.28; d = r.random() * 14
            s += f'<circle cx="{cx + d * math.cos(a):.0f}" cy="{cy + d * math.sin(a):.0f}" r="5" fill="{P}"/>'
    fields.append(('Gram-positive cocci in clusters', 'Staphylococcus aureus', 'pur', s, '#F3EEF6'))
    # 2 lancet diplococci
    r = rng(2); s = ''
    for k in range(9):
        x, y, a = r.uniform(-50, 50), r.uniform(-50, 50), r.uniform(0, 180)
        s += g(f'<path d="M-12 0 C-10 -6 -4 -6 -1 0 C-4 6 -10 6 -12 0 Z M12 0 C10 -6 4 -6 1 0 C4 6 10 6 12 0 Z" fill="{P}"/><ellipse rx="16" ry="9" fill="none" stroke="{P}" stroke-width=".8" opacity=".5"/>', round(x), round(y), round(a))
    fields.append(('Lancet-shaped diplococci', 'Streptococcus pneumoniae', 'pur', s, '#F3EEF6'))
    # 3 gram-negative rods
    r = rng(3); s = ''
    for k in range(18):
        x, y, a = r.uniform(-60, 60), r.uniform(-60, 60), r.uniform(0, 180)
        s += g(f'<rect x="-9" y="-3.5" width="18" height="7" rx="3.5" fill="{N}"/>', round(x), round(y), round(a))
    fields.append(('Gram-negative rods', 'E. coli: lactose fermenter', 'red', s, '#FBF2F4'))
    # 4 AFB
    r = rng(4); s = ''
    for k in range(12):
        x, y, a = r.uniform(-50, 50), r.uniform(-50, 50), r.uniform(0, 180)
        s += g(f'<path d="M-10 0 Q-4 -2 0 0 T10 0" stroke="{RED}" stroke-width="3.2" stroke-linecap="round" fill="none"/>', round(x), round(y), round(a))
    fields.append(('Acid-fast bacilli (Ziehl–Neelsen)', 'M. tuberculosis: red rods on blue', 'red', s, '#DCE8F7'))
    # 5 chinese letters
    r = rng(5); s = ''
    for k in range(7):
        x, y = r.uniform(-44, 44), r.uniform(-44, 44)
        for j in range(3):
            a = r.uniform(0, 180)
            s += g(f'<rect x="-10" y="-2.5" width="20" height="5" rx="2.5" fill="#7FA36B"/><circle cx="-7" r="2.6" fill="#2B2F6E"/><circle cx="7" r="2.6" fill="#2B2F6E"/>', round(x + j * 8 * math.cos(a)), round(y + j * 8 * math.sin(a)), round(a))
    fields.append(('Albert stain: "Chinese letters"', 'C. diphtheriae, volutin granules', 'grn', s, '#F2F6EE'))
    # 6 spirochaetes
    r = rng(6); s = ''
    for k in range(6):
        x, y, a = r.uniform(-40, 40), r.uniform(-50, 50), r.uniform(0, 180)
        wave = 'M-30 0' + ''.join(f' q2.5 {-5 if i % 2 == 0 else 5} 5 0' for i in range(12))
        s += g(f'<path d="{wave}" stroke="#F2E7C9" stroke-width="1.8" fill="none"/>', round(x), round(y), round(a))
    fields.append(('Spirochaetes (dark ground)', 'Treponema pallidum, Leptospira', 'amb', s, '#16181F'))
    # 7 india ink
    r = rng(7); s = ''
    for k in range(5):
        x, y = r.uniform(-40, 40), r.uniform(-40, 40)
        s += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="17" fill="#F7F4EC"/><circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="#C9BFA6" stroke="#8F846A"/>'
    fields.append(('India ink: clear capsule', 'Cryptococcus neoformans in CSF', 'ink', s, '#2A2A2E'))
    b = ''
    for k, (name, org, c, art, bg) in enumerate(fields):
        col, row = k % 4, k // 4
        x0, y0 = 24 + col * 181, 76 + row * 298
        b += card(x0, y0, 169, 286, 'pn')
        f0, clip = field(k, bg)
        b += g(f0 + f'<g {clip}>{art}</g>', x0 + 84, y0 + 98)
        words = name.split(' ')
        l1, l2 = '', ''
        for w in words:
            if len(l1 + ' ' + w) <= 20 and not l2: l1 = (l1 + ' ' + w).strip()
            else: l2 = (l2 + ' ' + w).strip()
        b += T(x0 + 14, y0 + 202, l1, f'l b {c}') + T(x0 + 14, y0 + 220, l2, f'l b {c}')
        ol = org.split(': ') if ': ' in org else [org[:22].rsplit(' ', 1)[0], org[len(org[:22].rsplit(' ', 1)[0]) + 1:]] if len(org) > 22 else [org]
        b += TL(x0 + 14, y0 + 242, ol, 'n sm', 16)
    # gram stain steps tile
    x0, y0 = 24 + 3 * 181, 76 + 298
    b += card(x0, y0, 169, 286, 'pn2') + T(x0 + 14, y0 + 28, 'Gram stain: 4 steps', 'l b')
    steps = [('Crystal violet', '#5B2C83'), ("Gram's iodine", '#8A5A34'), ('Decolourise', '#B7C3D0'), ('Safranin', '#D2557A')]
    for j, (sn, col) in enumerate(steps):
        yy = y0 + 58 + j * 42
        b += f'<rect x="{x0 + 14}" y="{yy - 14}" width="22" height="22" rx="6" fill="{col}"/>' + T(x0 + 46, yy + 2, sn, 'l sm')
    b += TL(x0 + 14, y0 + 236, ['Positive stays purple', '(thick wall); negative', 'turns pink (LPS)'], 'n sm', 15)
    alt = 'What common organisms look like down the microscope: Gram-positive cocci in clusters (Staphylococcus aureus), lancet-shaped diplococci (Streptococcus pneumoniae), Gram-negative rods (E. coli), red acid-fast bacilli on blue with Ziehl-Neelsen (M. tuberculosis), Chinese-letter arrangement with volutin granules on Albert stain (C. diphtheriae), spirochaetes on dark ground (Treponema, Leptospira) and a clear capsule on India ink (Cryptococcus), with the four Gram stain steps.'
    return plate(W, H, 'Down the microscope', 'Shape, arrangement and stain identify the organism', b, alt), alt


FIGS = {'t6-microscope': microscope}


def rbc(x, y, r=13, kind='norm', rot=0):
    if kind == 'norm':
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E98E86"/><circle cx="{x}" cy="{y}" r="{r * .42:.1f}" fill="#F6C9C2"/>'
    if kind == 'micro':
        return f'<circle cx="{x}" cy="{y}" r="{r * .72:.1f}" fill="#F0B4AD"/><circle cx="{x}" cy="{y}" r="{r * .5:.1f}" fill="#FBE4E0"/>'
    if kind == 'pencil':
        return g(f'<ellipse rx="{r * 1.2:.0f}" ry="{r * .38:.1f}" fill="#F0B4AD"/>', x, y, rot)
    if kind == 'target':
        return f'<circle cx="{x}" cy="{y}" r="{r}" fill="#E98E86"/><circle cx="{x}" cy="{y}" r="{r * .66:.1f}" fill="#F8D6D1"/><circle cx="{x}" cy="{y}" r="{r * .3:.1f}" fill="#E07A71"/>'
    if kind == 'macro':
        return g(f'<ellipse rx="{r * 1.3:.0f}" ry="{r * .95:.1f}" fill="#E07A71"/>', x, y, rot)
    if kind == 'sphero':
        return f'<circle cx="{x}" cy="{y}" r="{r * .78:.1f}" fill="#C9473F"/>'
    if kind == 'sickle':
        return g(f'<path d="M-{r * 1.3:.0f} 0 C-{r * .6:.0f} -{r * .9:.0f} {r * .6:.0f} -{r * .9:.0f} {r * 1.3:.0f} 0 C{r * .6:.0f} -{r * .35:.0f} -{r * .6:.0f} -{r * .35:.0f} -{r * 1.3:.0f} 0 Z" fill="#D9584F"/>', x, y, rot)
    if kind == 'bite':
        return g(f'<path d="M{r} 0 A{r} {r} 0 1 1 {r * .5:.1f} -{r * .86:.1f} A{r * .45:.1f} {r * .45:.1f} 0 0 0 {r} 0 Z" fill="#E98E86"/>', x, y, rot)


def bg_rbcs(seed, n=12):
    r = rng(seed)
    return ''.join(rbc(round(r.uniform(-62, 62)), round(r.uniform(-62, 62)), 12) for _ in range(n))


def wbc(kind):
    if kind == 'neut':
        cyto = '<circle r="30" fill="#F2D9E4"/>' + ''.join(f'<circle cx="{14 * math.cos(k):.0f}" cy="{14 * math.sin(k * 1.7):.0f}" r="1.2" fill="#C98AA8"/>' for k in range(30))
        nuc = '<path d="M-16 -6 C-20 -16 -6 -18 -4 -10 C0 -18 12 -16 10 -6 C18 -4 18 8 10 10 C6 18 -6 18 -6 10 C-14 14 -22 4 -16 -6 Z" fill="#6A3D8C"/>'
        return cyto + nuc
    if kind == 'lymph':
        return '<circle r="20" fill="#A9C4EA"/><circle cx="-1" cy="-1" r="17" fill="#4E3A8C"/>'
    if kind == 'mono':
        return '<circle r="36" fill="#C9D2E6"/><path d="M-22 -10 C-20 -26 18 -26 22 -8 C26 10 12 22 0 12 C-10 22 -26 10 -22 -10 Z" fill="#7A5FA6"/>'
    if kind == 'eos':
        return ('<circle r="30" fill="#F7D2C4"/>' + ''.join(f'<circle cx="{r_ * math.cos(a):.0f}" cy="{r_ * math.sin(a):.0f}" r="3.6" fill="#E2643F"/>' for r_ in (10, 18, 24) for a in [k * 0.7 + r_ for k in range(9)])
                + '<ellipse cx="-10" cy="0" rx="9" ry="12" fill="#5B3C8C"/><ellipse cx="10" cy="0" rx="9" ry="12" fill="#5B3C8C"/>')
    if kind == 'baso':
        return ('<circle r="28" fill="#D8CCE8"/><path d="M-12 -8 C-8 -18 10 -16 12 -4 C16 8 2 14 -6 10 C-16 8 -16 -2 -12 -8 Z" fill="#6A4C99"/>'
                + ''.join(f'<circle cx="{r_ * math.cos(a):.0f}" cy="{r_ * math.sin(a):.0f}" r="4" fill="#2E1C55"/>' for r_ in (6, 14, 21) for a in [k * 0.9 + r_ for k in range(8)]))


def blood_cells():
    W, H = 760, 820
    cells = [('neut', 'Neutrophil', '40–75%', 'pur', ['3–5 lobes; leads', 'acute inflammation.', 'Neutrophilia:', 'bacteria']),
             ('lymph', 'Lymphocyte', '20–40%', 'blu', ['Round nucleus fills', 'the cell. Raised in', 'viruses, TB,', 'pertussis']),
             ('mono', 'Monocyte', '2–10%', 'tea', ['Largest white cell;', 'kidney-shaped', 'nucleus']),
             ('eos', 'Eosinophil', '1–6%', 'amb', ['Two lobes, red', 'granules.', 'Eosinophilia:', 'allergy, parasites']),
             ('baso', 'Basophil', 'under 1%', 'ink', ['Dark granules hide', 'the nucleus;', 'rarest white cell', ''])]
    b = T(24, 90, 'WHITE CELLS · normal differential count', 'n sm b')
    for k, (kd, name, pct, c, lines) in enumerate(cells):
        x0 = 24 + k * 145
        b += card(x0, 102, 135, 318, 'pn')
        f0, clip = field('w%d' % k, '#FBF4F2')
        b += g(f0 + f'<g {clip}>{bg_rbcs(10 + k, 10)}<g transform="scale(1.3)">{wbc(kd)}</g></g>', x0 + 67, 186, sc=0.8)
        b += T(x0 + 12, 282, name, f'l b {c}') + T(x0 + 12, 304, pct, 'h', 'start', ' style="font-size:20px"')
        b += TL(x0 + 12, 328, [l for l in lines if l], 'n sm', 16)
    # red cells
    b += T(24, 452, 'RED CELLS · what anaemia does to their shape', 'n sm b')
    reds = [('norm', 'Normal', 'blu', ['Biconcave disc,', 'pale centre']),
            ('micro', 'Microcytic, hypochromic', 'red', ['Iron deficiency:', 'small, pale, pencil cells']),
            ('target', 'Target cells', 'amb', ['Thalassaemia trait:', 'Mentzer index < 13']),
            ('macro', 'Macro-ovalocytes', 'pur', ['B12 / folate; with', 'neutrophils > 5 lobes']),
            ('sphero', 'Spherocytes', 'tea', ['Hereditary spherocytosis:', 'no pale centre']),
            ('sickle', 'Sickle cells', 'red', ['HbS: glutamate → valine', 'at β6']),
            ('bite', 'Bite cells', 'grn', ['G6PD deficiency after', 'oxidant drugs, fava beans'])]
    for k, (kd, name, c, lines) in enumerate(reds):
        col, row = k % 4, k // 4
        x0, y0 = 24 + col * 181, 464 + row * 170
        b += card(x0, y0, 169, 158, 'pn')
        r_ = rng(40 + k); cells_ = ''
        for j in range(5):
            cells_ += rbc(round(-44 + (j % 3) * 44 + r_.uniform(-4, 4)), round(-12 + (j // 3) * 30 + r_.uniform(-3, 3)), 13, kd, round(r_.uniform(0, 180)))
        if kd == 'micro': cells_ += rbc(28, 22, 13, 'pencil', 20)
        if kd == 'macro': cells_ += g('<circle r="16" fill="#F2D9E4"/>' + ''.join(f'<circle cx="{8 * math.cos(a):.0f}" cy="{8 * math.sin(a):.0f}" r="4.4" fill="#6A3D8C"/>' for a in [k2 * 1.05 for k2 in range(6)]), 44, 18)
        b += g(cells_, x0 + 84, y0 + 42)
        b += T(x0 + 12, y0 + 100, name, f'l sm b {c}', 'start', ' textLength="146" lengthAdjust="spacingAndGlyphs"' if len(name) > 19 else '') + TL(x0 + 12, y0 + 120, lines, 'n sm', 15)
    x0, y0 = 24 + 3 * 181, 464 + 170
    b += card(x0, y0, 169, 158, 'pn2') + T(x0 + 12, y0 + 26, 'Inclusions', 'l b') + TL(x0 + 12, y0 + 48, ['Howell–Jolly: asplenia', 'Basophilic stippling:', '  lead, thalassaemia', 'Heinz bodies: G6PD', 'Ring sideroblasts:', '  sideroblastic (marrow)'], 'n sm', 16)
    alt = 'Blood film. White cells with their normal share: neutrophil 40 to 75 percent (multilobed, raised in bacterial infection), lymphocyte 20 to 40 (round nucleus, raised in viral infection, TB, pertussis), monocyte 2 to 10 (largest, kidney-shaped nucleus), eosinophil 1 to 6 (two lobes, red granules, raised in allergy and parasites), basophil under 1 (dark granules). Red cell changes: normal discs, microcytic hypochromic cells and pencil cells in iron deficiency, target cells in thalassaemia trait, macro-ovalocytes with hypersegmented neutrophils in B12 or folate deficiency, spherocytes, sickle cells and bite cells.'
    return plate(W, H, 'Reading a blood film', 'Normal white cells, and what anaemia does to red cells', b, alt), alt


FIGS['t6-blood-film'] = blood_cells


def ring(x, y, r=5, dots=1, rot=0):
    s = f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#4B5BA8" stroke-width="1.8"/>'
    a = math.radians(rot)
    s += f'<circle cx="{x + r * math.cos(a):.1f}" cy="{y + r * math.sin(a):.1f}" r="2.2" fill="#B3264A"/>'
    if dots == 2: s += f'<circle cx="{x + r * math.cos(a + .7):.1f}" cy="{y + r * math.sin(a + .7):.1f}" r="2.2" fill="#B3264A"/>'
    return s


def malaria():
    W, H = 760, 860
    b = ''
    # vivax field
    v = ''
    r_ = rng(21)
    for _ in range(9): v += rbc(round(r_.uniform(-66, 66)), round(r_.uniform(-66, 66)), 13)
    def vcell(x, y, inner, R=21):
        dots = ''.join(f'<circle cx="{x + (R - 4) * math.cos(a) * f:.1f}" cy="{y + (R - 4) * math.sin(a) * f:.1f}" r=".9" fill="#C2414F"/>' for a in [k * .5 for k in range(13)] for f in (.45, .85))
        return f'<circle cx="{x}" cy="{y}" r="{R}" fill="#F6C8C2"/>' + dots + inner
    v += vcell(-30, -26, ring(-30, -26, 8, 1, 40))
    v += vcell(28, -10, f'<path d="M18 -16 C24 -24 36 -20 34 -10 C40 -4 32 6 26 2 C18 6 14 -4 18 -16 Z" fill="none" stroke="#4B5BA8" stroke-width="2.4"/><circle cx="20" cy="-12" r="2.4" fill="#B3264A"/>')
    v += vcell(-14, 34, ''.join(f'<circle cx="{-14 + 11 * math.cos(k * .785):.1f}" cy="{34 + 11 * math.sin(k * .785):.1f}" r="3" fill="#6A3D8C"/>' for k in range(8)) + '<circle cx="-14" cy="34" r="3" fill="#8A6A2B"/>', 23)
    v += vcell(40, 42, '<circle cx="40" cy="42" r="15" fill="#8E7CC3"/><circle cx="40" cy="42" r="5" fill="#B3264A"/>', 22)
    # falciparum field
    f = ''
    r_ = rng(22)
    pts_ = [(-40, -36), (-6, -44), (30, -30), (-48, 4), (-12, -6), (24, 10), (52, -2), (-30, 40), (4, 34), (38, 46)]
    for k, (x, y) in enumerate(pts_):
        f += rbc(x, y, 14)
        if k in (1, 4, 6):
            f += ring(x - 4, y - 3, 4.5, 1, 30) + ring(x + 5, y + 4, 4.5, 2 if k == 4 else 1, 200)
        if k == 2:
            f += ring(x, y - 13, 4, 1, 270) + '<path d="M{0} {1}l6 2M{2} {3}l5 -3" stroke="#B3264A" stroke-width="1.4"/>'.format(x - 6, y + 4, x + 2, y + 7)
        if k == 8:
            f += f'<path d="M{x - 6} {y - 4}l5 2M{x + 2} {y + 5}l6 -1M{x - 2} {y + 1}l2 5" stroke="#B3264A" stroke-width="1.6"/>'
    f += '<path d="M-38 -8 C-30 -20 -6 -22 4 -12 C-6 -14 -26 -12 -34 2 Z" fill="none"/>'
    f += g('<path d="M-22 0 C-14 -12 14 -12 22 0 C14 -4 -14 -4 -22 0 Z" fill="#7E62B8" stroke="#4E3A8C" stroke-width="1.2"/><circle cx="0" cy="-5" r="2.6" fill="#B3264A"/>', 0, 60, -8, 1.3)
    S, CY = 1.6, 300
    for k, (fld, name, c, x0) in enumerate([(v, 'Plasmodium vivax', 'blu', 24), (f, 'Plasmodium falciparum', 'red', 392)]):
        b += card(x0, 104, 344, 404, 'pn')
        f0, clip = field('m%d' % k, '#FBF1EE')
        b += g(f0 + f'<g {clip}>{fld}</g>', x0 + 172, CY, sc=S)
        b += T(x0 + 4, 94, name, f'l b {c}', 'start', ' style="font-size:17px"')
    P = lambda cx, x, y: (round(cx + x * S), round(CY + y * S))
    def lab(tx, ty, lines, cls, anchor, pt):
        return lead(tx + (0 if anchor == 'start' else 0), ty + (8 if ty < CY else -24), *pt) + TL(tx, ty, lines, cls, 16, anchor) if False else lead(tx, ty + (22 if ty < CY else -16), *pt) + TL(tx, ty, lines, cls, 16, anchor)
    b += lab(40, 128, ["Schüffner's dots,", 'enlarged pale cell'], 'n sm b', 'start', P(196, -30, -26))
    b += lab(352, 128, ['amoeboid', 'trophozoite'], 'n sm', 'end', P(196, 26, -10))
    b += lab(40, 462, ['schizont'], 'n sm', 'start', P(196, -14, 34))
    b += lab(352, 462, ['round', 'gametocyte'], 'n sm', 'end', P(196, 40, 42))
    b += lab(408, 128, ['many rings per cell,', 'double chromatin'], 'n sm b', 'start', P(564, -12, -6))
    b += lab(720, 128, ['accolé form', '(on the edge)'], 'n sm', 'end', P(564, 30, -43))
    b += lab(408, 462, ['banana-shaped', 'gametocyte'], 'n sm b', 'start', P(564, -6, 54))
    b += lab(720, 462, ["Maurer's", 'clefts'], 'n sm', 'end', P(564, 4, 34))
    # comparison table
    rows = [('RBC size', 'Enlarged, pale', 'Normal'), ('Dots', "Schüffner's dots", "Maurer's clefts"), ('Rings', 'Single, one per RBC', 'Many per RBC, accolé, double chromatin'),
            ('Gametocyte', 'Round', 'Crescent / banana (diagnostic)'), ('Schizonts in smear', 'Seen', 'Usually not (sequestered)'), ('Fever', 'Tertian, 48 h', 'Malignant tertian; cerebral malaria')]
    y = 560
    b += T(24, y - 14, '', 'n')
    for k, (a, v_, f_) in enumerate(rows):
        yy = y + k * 34
        if k % 2 == 0: b += f'<rect x="24" y="{yy - 22}" width="712" height="34" rx="8" class="pn"/>'
        b += T(36, yy, a, 'n sm b') + T(212, yy, v_, 'l sm blu') + T(452, yy, f_, 'l sm red')
    b += TL(24, 786, ['Relapse: vivax and ovale hide in the liver as hypnozoites → primaquine.', 'Infective to man: sporozoite (mosquito bite). Infective to mosquito: gametocyte.', 'Thick smear detects, thin smear identifies the species (Giemsa, JSB, Leishman).'], 'n sm', 20)
    alt = 'Thin blood smears of malaria. Plasmodium vivax: enlarged pale red cells with Schüffner’s dots, a single ring per cell, amoeboid trophozoite, schizonts and round gametocytes, tertian 48-hour fever. Plasmodium falciparum: normal-sized cells with many rings per cell, double chromatin dots, accolé forms, Maurer’s clefts and the diagnostic banana-shaped gametocyte; schizonts usually not seen; malignant tertian fever and cerebral malaria.'
    return plate(W, H, 'Malaria smear: vivax vs falciparum', 'Thin film, Giemsa stain', b, alt), alt


FIGS['t6-malaria'] = malaria


def thrombosis():
    W, H = 760, 820
    b = ''
    # vessel, longitudinal section
    v = ('<path d="M-220 -46 L220 -46 L220 46 L-220 46 Z" fill="#7C2F3A"/>'
         '<path d="M-220 -38 L220 -38 L220 38 L-220 38 Z" fill="#F4D7D3"/>'
         '<path d="M-60 -38 C-40 -20 -20 -8 -4 -4 L-6 -38 Z M-60 38 C-40 20 -20 8 -4 4 L-6 38 Z" fill="#E7B6AF" stroke="#B9776B" stroke-width="1.2"/>')
    for x in range(-200, 220, 46):
        v += f'<ellipse cx="{x}" cy="{(x * 7) % 22 - 11}" rx="11" ry="5" fill="url(#rbc)" opacity=".85"/>'
    th = '<path d="M-60 -38 C-56 -22 -40 -14 -20 -12 C-6 -12 20 -14 40 -22 C56 -28 72 -34 90 -38 Z" fill="#9E2B24"/>'
    th += ''.join(f'<path d="M{-50 + k * 14} -36 C{-46 + k * 14} -28 {-40 + k * 14} -22 {-30 + k * 14} -16" stroke="#F1E3C2" stroke-width="2.4" fill="none" opacity=".85"/>' for k in range(8))
    v += th
    b += g(v, 380, 250)
    b += lead(520, 166, 460, 224) + TL(522, 156, ['thrombus at a valve pocket;', 'pale and red layers = lines of Zahn'], 'n sm', 15)
    # triad corners
    tri = [('I', 'Endothelial injury', 'red', ['Most important: alone', 'can cause thrombosis'], 110, 120),
           ('S', 'Stasis or turbulence', 'blu', ['Abnormal flow: blood', 'pooling or swirling'], 110, 380),
           ('H', 'Hypercoagulability', 'pur', ['Factor V Leiden (inherited);', 'pregnancy, OCPs, cancer,', 'immobilisation, surgery'], 650, 380)]
    b += '<path d="M140 132 L140 352 L620 352" class="ln" stroke-width="1.4" stroke-dasharray="4 5" fill="none"/>'
    for L, name, c, lines, x, y in tri:
        b += f'<circle cx="{x + 30}" cy="{y + 2}" r="22" class="f{c}"/>' + T(x + 30, y + 10, L, f'h xl {c}', 'middle')
        tx = x + 62 if x < 400 else x - 36
        a = 'start' if x < 400 else 'end'
        b += T(tx, y + 2, name, f'l b {c}', a) + TL(tx, y + 20, lines, 'n sm', 15, a)
    b += T(380, 108, "VIRCHOW'S TRIAD", 'n sm b', 'middle')
    # bottom: embolus and infarcts
    b += card(24, 452, 348, 344, 'pn') + card(388, 452, 348, 344, 'pn')
    b += T(40, 482, 'Embolus: a clot that travels', 'l b')
    body = ('<path d="M0 -120 C14 -120 20 -108 18 -96 C30 -90 40 -80 40 -60 L40 30 L24 30 L22 120 L6 120 L2 40 L-2 40 L-6 120 L-22 120 L-24 30 L-40 30 L-40 -60 C-40 -80 -30 -90 -18 -96 C-20 -108 -14 -120 0 -120 Z" fill="#E9F0F7" stroke="#9AAFC4" stroke-width="2"/>'
            '<path d="M-28 -64 C-34 -40 -30 -20 -14 -16 C-6 -30 -8 -56 -14 -66 Z M28 -64 C34 -40 30 -20 14 -16 C6 -30 8 -56 14 -66 Z" fill="#F2B8B3" stroke="#C7766E" stroke-width="1.2"/>'
            '<path d="M-14 100 C-14 60 -12 30 -4 -2 C0 -20 2 -34 -2 -44" stroke="#4B6FB5" stroke-width="3" fill="none" stroke-dasharray="6 4" marker-end="url(#ah)"/>'
            '<ellipse cx="-14" cy="92" rx="5" ry="9" fill="#9E2B24"/><path d="M-4 -44 L-18 -50" stroke="#9E2B24" stroke-width="5" stroke-linecap="round"/>')
    b += g(body, 120, 650, sc=1.05)
    b += TL(196, 534, ['Pulmonary embolism:', 'commonest embolism;', '> 95% from deep leg', 'veins (popliteal and', 'above)'], 'n sm', 16)
    b += TL(196, 640, ['Saddle embolus at the', 'bifurcation can kill', 'instantly'], 'n sm', 16)
    b += TL(196, 718, ['Others: fat (long-bone', 'fractures), air,', 'amniotic fluid'], 'n sm', 16)
    b += T(404, 482, 'Infarct: wedge-shaped, apex at the block', 'l b', 'start', ' textLength="316" lengthAdjust="spacingAndGlyphs"')
    kid = ('<path d="M-40 -60 C-10 -76 40 -60 44 -10 C48 30 30 70 -6 70 C-30 70 -50 50 -40 20 C-30 10 -26 -4 -36 -14 C-50 -26 -54 -50 -40 -60 Z" fill="#B5544B" stroke="#7E3029" stroke-width="2"/>'
           '<path d="M14 -58 L-14 -6 L40 -24 C38 -40 30 -52 14 -58 Z" fill="#F1E3C2" stroke="#C9A867" stroke-width="1.2"/>'
           '<path d="M-14 -6 L-30 4" stroke="#7E3029" stroke-width="4"/><circle cx="-14" cy="-6" r="4" fill="#3A1A16"/>')
    lung = ('<path d="M-6 -70 C-30 -66 -50 -30 -50 20 C-50 60 -30 72 -6 66 C4 50 6 -40 -6 -70 Z" fill="#E7A9B4" stroke="#B5687A" stroke-width="2"/>'
            '<path d="M-36 30 L-12 14 L-20 60 C-30 58 -38 48 -36 30 Z" fill="#8E1F2F" opacity=".85"/><circle cx="-12" cy="14" r="4" fill="#3A1A16"/>')
    b += g(kid, 480, 590) + g(lung, 650, 590)
    b += T(480, 690, 'White (pale) infarct', 'l sm b', 'middle') + TL(480, 708, ['arterial block in solid', 'organs with end-arteries:', 'heart, kidney, spleen'], 'n sm', 15, 'middle')
    b += T(650, 690, 'Red infarct', 'l sm b red', 'middle') + TL(650, 708, ['venous block, loose tissue', 'or dual supply: lung,', 'liver, small intestine'], 'n sm', 15, 'middle')
    alt = "Thrombosis and its consequences: Virchow's triad of endothelial injury (most important), stasis or turbulent flow and hypercoagulability, around a vein with a thrombus at a valve pocket showing lines of Zahn; a clot from the deep leg veins travelling to the lungs as a pulmonary embolus (over 95 percent come from there); and wedge-shaped infarcts with the apex at the block, pale in solid organs with end-arteries such as the kidney and red in the lung."
    return plate(W, H, 'Thrombosis, embolism and infarction', 'Why clots form, where they travel, what they kill', b, alt), alt


FIGS['t6-thrombosis'] = thrombosis
