from lib import *
import math

PROFILE = ('M24 -150 C-24 -158 -64 -134 -72 -100 C-75 -88 -74 -80 -78 -72 C-84 -64 -94 -58 -92 -52 C-90 -48 -82 -48 -78 -46 '
           'C-82 -42 -84 -38 -80 -35 C-84 -30 -82 -24 -78 -22 C-80 -14 -78 -6 -70 -2 C-62 2 -52 2 -46 4 '
           'C-46 14 -48 20 -54 28 C-50 36 -46 40 -46 52 C-46 70 -48 84 -52 96 L70 96 C60 70 52 44 50 20 '
           'C58 4 74 -20 78 -56 C82 -96 68 -142 24 -150 Z')


def neck(kind, uid):
    s = f'<path d="{PROFILE}" {SKIN}/>'
    s += '<path d="M-2 -70 C8 -82 26 -78 28 -62 C30 -48 20 -38 8 -40 C14 -48 14 -60 -2 -70 Z" fill="#E3B293" stroke="#B9826A" stroke-width="1.4"/>'  # ear
    s += '<path d="M-58 -82 C-54 -86 -48 -86 -44 -82" stroke="#5B4636" stroke-width="2.2" fill="none" stroke-linecap="round"/>'  # eye
    if kind != 'hang':
        s += f'<clipPath id="pf{uid}"><path d="{PROFILE}"/></clipPath><g clip-path="url(#pf{uid})"><rect x="-100" y="-160" width="200" height="200" fill="#9B3B5A" opacity=".28"/></g>'
        s += ''.join(f'<circle cx="{-62 + (k * 7) % 22}" cy="{-90 + (k * 5) % 16}" r="1.6" fill="#8E1F2F"/>' for k in range(9))
    if kind == 'hang':
        s += '<path d="M-46 8 C-20 2 10 -14 30 -40" stroke="#7A3B2E" stroke-width="10" fill="none" stroke-linecap="round" opacity=".8"/>'
        s += '<path d="M-46 8 C-20 2 10 -14 30 -40" stroke="#A8574A" stroke-width="4" fill="none" stroke-dasharray="6 5" opacity=".9"/>'
        s += '<path d="M34 -46 C40 -60 46 -76 48 -100" stroke="#C9A06A" stroke-width="5" fill="none" stroke-dasharray="2 6" opacity=".7"/>'
        s += arrow(30, -40, 46, -100, 'samb', 2.2)
    else:
        s += '<path d="M-46 44 C-10 46 20 46 54 44" stroke="#7A3B2E" stroke-width="10" fill="none" stroke-linecap="round" opacity=".8"/>'
        s += '<path d="M-46 44 C-10 46 20 46 54 44" stroke="#A8574A" stroke-width="4" fill="none" stroke-dasharray="6 5" opacity=".9"/>'
        s += '<circle cx="-14" cy="50" r="3" fill="#7A3B2E"/><circle cx="6" cy="51" r="2.6" fill="#7A3B2E"/><circle cx="22" cy="49" r="3" fill="#7A3B2E"/>'
    return s


def hanging():
    W, H = 760, 620
    cols = [('hang', 'Hanging', 'amb', [('Direction', ['Oblique, rising', 'to the knot']), ('Position', ['High, above the', 'thyroid cartilage']), ('Continuity', ['Incomplete', '(gap at the knot)']), ('Face', 'Pale'), ('Saliva dribbling', 'Present: hanged while alive'), ('Usual manner', 'Suicidal')]),
            ('strang', 'Ligature strangulation', 'red', [('Direction', ['Horizontal,', 'transverse']), ('Position', ['Low, at or below', 'thyroid cartilage']), ('Continuity', ['Complete, encircles', 'the neck']), ('Face', 'Congested, petechiae'), ('Saliva dribbling', 'Absent'), ('Usual manner', 'Homicidal')])]
    b = ''
    for i, (k, name, c, rows) in enumerate(cols):
        x0 = 24 + i * 362
        b += card(x0, 76, 350, 498, 'pn')
        b += g(neck(k, i), x0 + 110, 240, sc=1.05)
        b += T(x0 + 220, 112, name.split(' ')[0], f'h xl {c}') + (T(x0 + 220, 132, name.split(' ', 1)[1], f'l b {c}') if ' ' in name else '')
        for j, (lab, val) in enumerate(rows[:3]):
            b += T(x0 + 220, 172 + j * 62, lab.upper(), 'n sm b') + TL(x0 + 220, 190 + j * 62, val, 'l sm', 16)
        for j, (lab, val) in enumerate(rows[3:]):
            b += T(x0 + 24, 418 + j * 44, lab.upper(), 'n sm b') + T(x0 + 24, 436 + j * 44, val, 'l sm')
    b += lead(160, 370, 60, 272) + T(160, 386, 'thyroid cartilage', 'n sm', 'middle')
    b += T(24, 598, 'Throttling (manual strangulation): finger-nail marks and bruises; hyoid fracture is commonest here.', 'n sm')
    alt = 'Ligature marks on the neck seen from the side: in hanging the mark is oblique, high above the thyroid cartilage and incomplete at the knot, the face is pale and saliva dribbles if hanged alive; in ligature strangulation the mark is horizontal, low at or below the thyroid cartilage and complete, and the face is congested with petechiae.'
    return plate(W, H, 'Hanging vs ligature strangulation', 'Read the ligature mark: direction, level and continuity', b, alt), alt


FIGS = {'t10-hanging': hanging}


def swatch(uid):
    return f'<rect x="-70" y="-50" width="140" height="100" rx="12" fill="url(#skin)"/>'


def wounds():
    W, H = 760, 760
    tiles = []
    # abrasion: scraped epidermis with direction streaks
    a = swatch(0) + '<path d="M-48 -18 C-20 -26 20 -24 46 -10 C30 6 -10 10 -46 4 Z" fill="#E0796B" opacity=".75"/>' + ''.join(f'<path d="M{-44 + k * 9} {-14 + (k % 3) * 5}l18 -3" stroke="#B6493E" stroke-width="1.5"/>' for k in range(10)) + '<path d="M40 -12 l14 2 l-4 6" stroke="#B6493E" stroke-width="2" fill="none"/>'
    tiles.append(('Abrasion', 'amb', a, ['Only the epidermis is lost;', 'shows direction of force;', 'heals without a scar']))
    # contusion
    c = swatch(1) + '<ellipse cx="0" cy="0" rx="40" ry="28" fill="#5B4BA0" opacity=".55"/><ellipse cx="4" cy="2" rx="24" ry="16" fill="#3D2F7A" opacity=".55"/>'
    tiles.append(('Contusion (bruise)', 'pur', c, ['Bleeding under intact skin;', 'its colour dates the injury', '(strip below)']))
    # laceration
    l = swatch(2) + '<ellipse cx="0" cy="3" rx="58" ry="24" fill="#7E5AA8" opacity=".22"/><path d="M-44 -6 L-30 2 L-22 -8 L-10 4 L0 -6 L12 6 L22 -4 L34 4 L46 -4 L34 12 L22 6 L12 16 L0 6 L-10 14 L-22 4 L-30 12 Z" fill="#8E2A2A" stroke="#6A1F1F" stroke-width="1.2"/>' + '<path d="M-8 2 L-6 10 M18 0 L20 9" stroke="#E7B9A0" stroke-width="2.4"/>' + ''
    tiles.append(('Laceration', 'red', l, ['Blunt force tears: ragged', 'margins, tissue bridges,', 'bruised edges']))
    # incised
    i_ = swatch(3) + '<path d="M-50 -2 C-20 -8 20 -8 50 -2 C20 4 -20 4 -50 -2 Z" fill="#9E2D2D"/><path d="M50 -2 L62 -3" stroke="#9E2D2D" stroke-width="1.2"/>' + T(56, 18, 'tail', 'n sm', 'middle')
    tiles.append(('Incised wound', 'blu', i_, ['Sharp edge: clean cut,', 'longer than deep; the tail', 'shows where it ended']))
    # stab
    st = swatch(4) + '<path d="M-12 -4 L12 -4 L14 0 L12 4 L-12 4 L-14 0 Z" fill="#7A2323"/><path d="M-60 34 L60 34" stroke="#8E95A6" stroke-width="1" stroke-dasharray="3 3"/>' + '<path d="M-16 0 C-10 20 -4 34 0 46 C4 34 10 20 16 0" fill="none" stroke="#8E95A6" stroke-width="1.4"/>'
    tiles.append(('Stab wound', 'tea', st, ['Depth greater than length;', 'shape tells a single- or', 'double-edged blade']))
    # firearm entry and exit
    f = ('<g transform="translate(-36 0)"><circle r="30" fill="url(#skin)"/>' + ''.join(f'<circle cx="{22 * math.cos(k * 1.1) * (0.7 + (k % 3) * .15):.1f}" cy="{22 * math.sin(k * 1.1) * (0.7 + (k % 3) * .15):.1f}" r="1.3" fill="#2B2B2B"/>' for k in range(26))
         + '<circle r="11" fill="#6E4A3A" opacity=".8"/><circle r="6" fill="#1E1414"/></g>'
         + '<g transform="translate(40 0)"><circle r="30" fill="url(#skin)"/><path d="M-14 -6 L-6 -10 L-4 -18 L2 -9 L12 -12 L8 -3 L16 4 L6 6 L4 16 L-2 7 L-12 12 L-8 2 Z" fill="#8E2A2A" stroke="#6A1F1F"/></g>'
         + T(-36, 46, 'entry', 'n sm', 'middle') + T(40, 46, 'exit', 'n sm', 'middle'))
    tiles.append(('Firearm wound', 'red', f, ['Entry: small, inverted, collar,', 'tattooing at close range.', 'Exit: larger, everted, no collar']))
    b = ''
    for k, (name, c, art, lines) in enumerate(tiles):
        col, row = k % 3, k // 3
        x0, y0 = 24 + col * 241, 76 + row * 262
        b += card(x0, y0, 229, 250, 'pn')
        b += g(art, x0 + 114, y0 + 84)
        b += T(x0 + 16, y0 + 168, name, f'l b {c}') + TL(x0 + 16, y0 + 188, lines, 'n sm', 16)
    # bruise colour strip
    y0 = 616
    b += T(24, y0, 'A bruise changes colour as it ages', 'l b')
    stages = [('Red', 'fresh', '#C0392B'), ('Blue', '1–3 days', '#3D3A8C'), ('Brown', '', '#7A4B2A'), ('Green', '5–6 days', '#5F8F3A'), ('Yellow', '7–12 days', '#D9B526'), ('Normal', '≈2 weeks', None)]
    for k, (n, d, col) in enumerate(stages):
        x = 24 + k * 120
        b += f'<rect x="{x}" y="{y0 + 14}" width="108" height="60" rx="12" fill="url(#skin)"/>'
        if col: b += f'<ellipse cx="{x + 54}" cy="{y0 + 44}" rx="34" ry="20" fill="{col}" opacity=".7"/>'
        b += T(x + 54, y0 + 96, n, 'l sm b', 'middle') + T(x + 54, y0 + 114, d, 'n sm', 'middle')
        if k < 5: b += arrow(x + 104, y0 + 44, x + 122, y0 + 44, 'ln', 1.6)
    alt = 'Mechanical injuries drawn on skin: abrasion (only epidermis lost, shows direction), contusion (bleeding under intact skin), laceration (ragged, tissue bridges, bruised edges), incised wound (clean, longer than deep, with a tail), stab wound (deeper than long) and firearm wounds (small inverted entry with abrasion collar and tattooing; larger everted exit), with a strip of bruise colours: red, blue at 1 to 3 days, brown, green at 5 to 6 days, yellow at 7 to 12 days, normal by about 2 weeks.'
    return plate(W, H, 'Mechanical injuries: read the wound', 'What each wound looks like, and how a bruise ages', b, alt), alt


FIGS['t10-wounds'] = wounds


def bins():
    W, H = 760, 640
    BIO = lambda col: (f'<g transform="scale(.9)" fill="none" stroke="{col}" stroke-width="3.2"><circle cx="0" cy="-7" r="8"/><circle cx="-7" cy="5" r="8"/><circle cx="7" cy="5" r="8"/><circle r="3" fill="{col}"/></g>')
    bag = lambda fill, dark: (f'<path d="M-46 -40 C-50 -20 -54 30 -48 58 C-30 66 30 66 48 58 C54 30 50 -20 46 -40 Z" fill="{fill}" stroke="{dark}" stroke-width="2"/>'
                              f'<path d="M-46 -40 C-30 -48 -14 -44 -10 -54 C-4 -60 4 -60 10 -54 C14 -44 30 -48 46 -40" fill="{fill}" stroke="{dark}" stroke-width="2"/><path d="M-10 -54 C-6 -64 6 -64 10 -54" fill="none" stroke="{dark}" stroke-width="3"/>')
    cont_white = ('<rect x="-36" y="-44" width="72" height="104" rx="8" fill="#F4F6F8" stroke="#9AA6B2" stroke-width="2" opacity=".95"/>'
                  '<rect x="-40" y="-56" width="80" height="16" rx="5" fill="#E2E7EC" stroke="#9AA6B2" stroke-width="2"/><rect x="-12" y="-62" width="24" height="8" rx="2" fill="#C9D1D9"/>'
                  '<path d="M-20 -30 L18 40 M-8 -34 L24 30" stroke="#8E95A6" stroke-width="1.8" opacity=".5"/>')
    box_blue = ('<path d="M-48 -34 L48 -34 L48 58 L-48 58 Z" fill="#2E68D8" stroke="#1E4A9E" stroke-width="2"/><path d="M-48 -34 L-34 -50 L62 -50 L48 -34 Z" fill="#4B82E8" stroke="#1E4A9E" stroke-width="2"/>'
                '<path d="M48 -34 L62 -50 L62 42 L48 58 Z" fill="#2457B8" stroke="#1E4A9E" stroke-width="2"/>'
                '<path d="M-6 -26 h12 v10 c10 4 14 12 14 22 v38 h-40 v-38 c0 -10 4 -18 14 -22z" fill="#D9ECF8" opacity=".9"/><path d="M-16 12 l8 6 l-4 8 l10 4 l-2 12" stroke="#1E4A9E" stroke-width="1.6" fill="none"/>')
    cols = [('Yellow', 'bag', 'amb', bag('#F2C230', '#B88B00') + g(BIO('#1E2330'), 0, 10), ['Anatomical waste', 'Soiled dressings,', 'cotton', 'Expired medicines', 'Chemical waste', 'Microbiology', 'cultures'], 'Incineration or deep burial'),
            ('Red', 'bag', 'red', bag('#D9443E', '#9E2420') + g(BIO('#FFFFFF'), 0, 10), ['Recyclable plastics:', 'tubing, bottles,', 'IV sets, catheters,', 'gloves, syringes', 'WITHOUT needles'], 'Autoclave or microwave, shred, recycle'),
            ('White', 'puncture-proof, translucent', 'ink', cont_white + g(BIO('#D33A3F'), 0, 10), ['Sharps: needles,', 'syringes with fixed', 'needles, scalpels,', 'blades'], 'Autoclave, shred, sharps pit or encapsulation'),
            ('Blue', 'cardboard box', 'blu', box_blue, ['Glassware (broken', 'or discarded)', 'Metal body implants'], 'Disinfect or autoclave, then recycle')]
    b = ''
    for k, (name, sub, c, art, items, treat) in enumerate(cols):
        x0 = 24 + k * 180
        b += card(x0, 76, 170, 520, 'pn')
        b += g(art, x0 + 85, 170, sc=1.05)
        b += T(x0 + 14, 268, name, f'h xl {c}') + T(x0 + 14, 288, sub, 'n sm', 'start', ' textLength="146" lengthAdjust="spacingAndGlyphs"' if len(sub) > 20 else '')
        b += T(x0 + 14, 320, 'WHAT GOES IN', 'n sm b') + TL(x0 + 14, 340, items, 'l sm', 18)
        b += T(x0 + 14, 492, 'TREATMENT', 'n sm b')
        words = treat.split(' '); lines, cur = [], ''
        for w in words:
            if len(cur + ' ' + w) > 20: lines.append(cur.strip()); cur = w
            else: cur += ' ' + w
        lines.append(cur.strip())
        b += TL(x0 + 14, 512, lines, 'n sm', 17)
    b += T(24, 622, 'Bio-Medical Waste Management Rules, 2016 · treat within 48 hours · hook: Yellow body, Red plastic, White sharps, Blue glass', 'n sm', 'start', ' textLength="712" lengthAdjust="spacingAndGlyphs"')
    alt = 'Biomedical waste colour codes under the 2016 rules: yellow bag for anatomical waste, soiled dressings, expired medicines, chemical waste and cultures (incineration or deep burial); red bag for contaminated recyclable plastics such as tubing, bottles, IV sets, catheters, needle-free syringes and gloves (autoclave, shred, recycle); white puncture-proof translucent container for sharps (autoclave, shred, sharps pit); blue cardboard box for glassware and metal implants (disinfect, recycle).'
    return plate(W, H, 'Biomedical waste: which colour?', 'Segregate at the source, by colour', b, alt), alt


FIGS['t10-bmw'] = bins
