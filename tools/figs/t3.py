from lib import *
import math

MORTAR = ('<path d="M-46 -10 L46 -10 C44 22 24 40 0 40 C-24 40 -44 22 -46 -10 Z" fill="#E6E2DA" stroke="#8C877C" stroke-width="2"/>'
          '<path d="M-24 40 L-30 52 L30 52 L24 40" fill="#D3CEC4" stroke="#8C877C" stroke-width="2"/>'
          '<ellipse cx="0" cy="-10" rx="46" ry="9" fill="#F7F5F0" stroke="#8C877C" stroke-width="2"/><ellipse cx="0" cy="-8" rx="36" ry="6" fill="#FFFFFF"/>'
          '<path d="M14 -60 L28 -58 L8 0 C4 6 -6 4 -4 -2 Z" fill="#D3CEC4" stroke="#8C877C" stroke-width="2"/>')


def vial(level=.6, label='', col='#EFE4B8', cork=True):
    h = 70
    s = f'<rect x="-14" y="{-h / 2}" width="28" height="{h}" rx="8" fill="url(#glass)" stroke="#8FB3C9" stroke-width="1.6"/>'
    s += f'<rect x="-12" y="{h / 2 - h * level}" width="24" height="{h * level - 2}" rx="6" fill="{col}" opacity=".9"/>'
    if cork: s += f'<rect x="-11" y="{-h / 2 - 10}" width="22" height="12" rx="3" fill="#B98A5A" stroke="#7E5A36"/>'
    if label: s += T(0, h / 2 + 18, label, 'l sm b', 'middle')
    return s


def potentise():
    W, H = 760, 760
    b = ''
    # trituration row
    b += card(24, 76, 712, 300, 'pn') + T(40, 104, 'Solids: TRITURATION with sugar of milk', 'l b amb') + T(40, 124, 'for insoluble drugs: metals, most minerals, many animal products', 'n sm')
    for k, lab in enumerate(['1C', '2C', '3C']):
        x = 110 + k * 150
        b += g(MORTAR, x, 230)
        b += T(x, 300, lab, 'h', 'middle') + T(x, 320, '1 hour', 'n sm', 'middle')
        if k < 2: b += arrow(x + 56, 230, x + 92, 230, 'samb', 2.6)
    b += T(260, 352, 'each hour = 3 rounds of 20 minutes: grind, then scrape', 'n sm', 'middle')
    b += arrow(530, 230, 574, 230, 'sred', 3)
    beaker = ('<path d="M-30 -40 L-30 36 C-30 44 -24 48 -16 48 L16 48 C24 48 30 44 30 36 L30 -40" fill="url(#glass)" stroke="#8FB3C9" stroke-width="2"/>'
              '<path d="M-28 0 L28 0 L28 36 C28 42 24 46 16 46 L-16 46 C-24 46 -28 42 -28 36 Z" fill="#CFE6F3"/>')
    b += g(beaker, 640, 222) + TL(640, 300, ['CONVERSION', 'dissolve the 3C in', 'water, then add alcohol'], 'n sm', 16, 'middle')
    b += T(640, 290 - 4, '', 'n')
    # liquid row
    b += card(24, 392, 712, 344, 'pn') + T(40, 420, 'Liquids: DILUTION + SUCCUSSION (vigorous shaking)', 'l b blu') + T(40, 440, 'centesimal step: 1 part of the previous potency + 99 parts of alcohol, then succussed', 'n sm')
    # hand shaking
    hand = vial(.5, '', '#E9DFA6') + ''.join(f'<path d="M{20 + k * 6} {-20 + k * 4} q8 6 0 12" stroke="#2E68D8" stroke-width="2" fill="none"/>' for k in range(3))
    b += g(hand, 90, 520, -20) + T(90, 590, 'succuss', 'n sm', 'middle')
    b += T(240, 476, 'HAHNEMANNIAN (multi-vial)', 'l sm b blu') + T(240, 494, 'a fresh vial for every potency · official, most accurate', 'n sm')
    for k, lab in enumerate(['1C', '2C', '3C', '…']):
        x = 260 + k * 70
        b += g(vial(.6 - k * .1 if k < 3 else .3, lab, ['#E9DFA6', '#F0E8C2', '#F6F1DA', '#FAF7EC'][k]), x, 548) if k < 3 else T(x, 556, '…', 'h', 'middle')
        if k < 2: b += arrow(x + 18, 548, x + 50, 548, 'sblu', 2)
    b += T(240, 634, 'KORSAKOVIAN (single-vial)', 'l sm b pur') + T(240, 652, 'the same vial is emptied and refilled each step · faster, marked K', 'n sm')
    b += g(vial(.55, '', '#F0E8C2'), 290, 690, sc=.6)
    b += '<path d="M318 676 A26 22 0 1 1 318 704" class="spur" stroke-width="2.4" fill="none" marker-end="url(#ah)"/>'
    b += T(380, 694, 'empty → refill → succuss → repeat', 'n sm')
    b += T(24, 754, 'Ratio per step: X 1 : 10 (Hering) · C 1 : 100 (Hahnemann) · LM 1 : 50,000 (6th edition, 100 succussions).', 'n sm', 'start', ' textLength="712" lengthAdjust="spacingAndGlyphs"')
    alt = 'How potencies are made: insoluble drugs are triturated with sugar of milk, one hour per step made of three 20-minute rounds of grinding and scraping, to the 3C, which is then dissolved in water and alcohol is added (conversion); liquids are diluted one part in a hundred and succussed, either in a fresh vial for every potency (Hahnemannian, official) or in the same vial emptied and refilled (Korsakovian, faster, marked K).'
    return plate(W, H + 16, 'From drug to potency', 'Trituration for solids, succussion for liquids', b, alt), alt


def globules():
    W, H = 760, 530
    b = ''
    b += T(24, 90, 'The size number = the length, in mm, of 10 globules laid in a row', 'l')
    # ruler
    x0, y0, mm = 60, 120, 14.5
    b += f'<rect x="{x0 - 10}" y="{y0}" width="{40 * mm + 20}" height="34" rx="6" fill="#F6E7B8" stroke="#B89A4A" stroke-width="1.6"/>'
    for i in range(41):
        hgt = 16 if i % 10 == 0 else (11 if i % 5 == 0 else 7)
        b += f'<path d="M{x0 + i * mm:.1f} {y0}v{hgt}" stroke="#7E6A32" stroke-width="{1.6 if i % 10 == 0 else 1}"/>'
        if i % 10 == 0 and i: b += T(x0 + i * mm - 4, y0 + 30, f'{i}', 'n sm', 'end', ' style="fill:#5E4E22"')
    rows = [(10, 'No. 10'), (20, 'No. 20'), (30, 'No. 30'), (40, 'No. 40')]
    for k, (n, lab) in enumerate(rows):
        y = [190, 240, 296, 366][k]
        r = n * mm / 20
        b += ''.join(f'<circle cx="{x0 + r + j * 2 * r:.1f}" cy="{y}" r="{r:.1f}" fill="#FBFBF7" stroke="#B9B2A3" stroke-width="1.2"/>' for j in range(10))
        b += f'<path d="M{x0} {y - r - 6}h{n * mm:.1f}" class="sblu" stroke-width="1.6" marker-end="url(#ah)" marker-start="url(#ah)"/>'
        b += T(x0 + n * mm + 22, y + 5, lab, 'l b blu' if n < 40 else 'l b pur')
    b += card(24, 414, 712, 100, 'pn')
    b += TL(40, 440, ['Sizes run 5 to 80 (commonly 10 to 40); 40 to 80 are called pilules.', 'Globules are cane sugar; they are medicated with 88% dispensing alcohol, then dried.',
                      'LM potencies use tiny poppy-seed globules: one drop medicates 500 of them.'], 'n sm', 22)
    alt = 'Globule sizes on a millimetre ruler: the size number is the length in millimetres of ten globules in a row, so ten No. 10 globules span 10 mm and ten No. 40 globules span 40 mm; sizes run 5 to 80, 40 to 80 are pilules; globules are medicated with 88 percent dispensing alcohol; LM potencies use poppy-seed globules, 500 per drop.'
    return plate(W, H, 'Globule sizes: read the number', 'Cane-sugar globules on a millimetre ruler', b, alt), alt


FIGS = {'t3-potentise': potentise, 't3-globules': globules}
