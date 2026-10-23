from lib import *
import math


def petals(n, rx, ry, fill, stroke, off=0, dist=0):
    return ''.join(f'<ellipse cx="0" cy="{-dist - ry}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="1.2" transform="rotate({off + k * 360 / n:.1f})"/>' for k in range(n))


LEAF = lambda x, y, r, s=1, col='#5E9E4F': f'<path d="M0 0 C10 -14 30 -16 44 0 C30 16 10 14 0 0 Z" fill="{col}" stroke="#3E7A34" stroke-width="1.2" transform="translate({x} {y}) rotate({r}) scale({s})"/><path d="M0 0 L40 0" stroke="#3E7A34" stroke-width="1" transform="translate({x} {y}) rotate({r}) scale({s})"/>'

ART = {
    'bell': ('<path d="M0 40 C-4 10 -20 -10 -30 -20" stroke="#4E7F3E" stroke-width="3" fill="none"/>' + LEAF(-6, 30, -150, .9) +
             '<path d="M-44 -38 C-46 -20 -40 -6 -30 -4 C-20 -6 -14 -20 -16 -38 C-24 -44 -36 -44 -44 -38 Z" fill="#7B4A8C" stroke="#4E2A5C" stroke-width="1.4"/>' +
             '<path d="M0 40 C6 16 18 0 26 -6" stroke="#4E7F3E" stroke-width="3" fill="none"/><circle cx="30" cy="-12" r="15" fill="#1B1520"/><circle cx="25" cy="-17" r="4" fill="#fff" opacity=".7"/>' +
             '<path d="M30 3 l-10 8 M30 3 l10 8 M30 3 l0 11 M30 3 l-14 2 M30 3 l14 2" stroke="#4E7F3E" stroke-width="2.4"/>'),
    'puls': ('<path d="M0 48 C2 20 0 0 0 -6" stroke="#6E8B5A" stroke-width="3.4" fill="none"/>' + ''.join(f'<path d="M0 {k * 10 + 4} l{5 if k % 2 else -5} -3" stroke="#B9C4A8" stroke-width="1"/>' for k in range(4)) +
             '<path d="M-30 -26 C-34 -46 -16 -54 -8 -40 C-4 -58 10 -58 12 -40 C20 -54 36 -46 30 -26 C20 -8 -20 -8 -30 -26 Z" fill="#8E62C4" stroke="#5C3A8C" stroke-width="1.4"/>' +
             '<ellipse cx="0" cy="-28" rx="12" ry="8" fill="#F2C531"/>'),
    'arn': ('<path d="M0 50 L0 6" stroke="#5E8E46" stroke-width="3"/>' + g(petals(16, 5, 16, '#F6C02B', '#C89310', 0, 6) + '<circle r="11" fill="#D9771E"/>', 0, -14)),
    'rhus': ('<path d="M0 50 L0 0" stroke="#7A4A2A" stroke-width="3"/>' + LEAF(0, 0, -90, 1.2, '#4C8F3A') + LEAF(0, 0, -160, 1.0, '#B5502F') + LEAF(0, 0, -20, 1.0, '#6FA13B')),
    'cinch': ('<path d="M-46 -6 C-46 -22 40 -26 46 -10 L46 6 C40 -10 -46 -6 -46 10 Z" fill="#8A5A34" stroke="#5E3A1E" stroke-width="1.4"/>'
              '<ellipse cx="-46" cy="2" rx="6" ry="8" fill="#C79A6A" stroke="#5E3A1E"/>'
              '<path d="M-40 18 C-40 6 34 0 40 14 L40 28 C34 14 -40 20 -40 32 Z" fill="#A0693D" stroke="#5E3A1E" stroke-width="1.4"/><ellipse cx="-40" cy="25" rx="6" ry="7" fill="#C79A6A" stroke="#5E3A1E"/>'),
    'nux': ''.join(f'<g transform="translate({x} {y})"><circle r="17" fill="#B9B2A3" stroke="#7E7666" stroke-width="1.4"/><circle r="11" fill="none" stroke="#9A9282" stroke-width="1" stroke-dasharray="2 2"/><circle r="2.5" fill="#7E7666"/></g>' for x, y in ((-24, 6), (16, -10), (22, 22))),
    'apis': ('<ellipse cx="-12" cy="-22" rx="22" ry="12" fill="#DDEEF8" stroke="#8FB3C9" stroke-width="1.2" transform="rotate(-20 -12 -22)"/><ellipse cx="10" cy="-24" rx="20" ry="11" fill="#DDEEF8" stroke="#8FB3C9" stroke-width="1.2" transform="rotate(20 10 -24)"/>'
             '<ellipse cx="14" cy="4" rx="26" ry="16" fill="#F2B632" stroke="#5A3A12" stroke-width="1.4"/>' + ''.join(f'<path d="M{8 + k * 9} -10 C{12 + k * 9} -2 {12 + k * 9} 10 {8 + k * 9} 18" stroke="#3A2A12" stroke-width="4" fill="none"/>' for k in range(3)) +
             '<circle cx="-18" cy="2" r="12" fill="#5A3A12"/><circle cx="-34" cy="0" r="8" fill="#3A2A12"/><path d="M40 4 l10 0" stroke="#3A2A12" stroke-width="2"/>'),
    'lach': ('<path d="M-40 30 C-60 10 -30 -6 0 6 C30 18 50 4 40 -14" stroke="#B88C4A" stroke-width="16" fill="none" stroke-linecap="round"/>'
             + ''.join(f'<path d="M{-40 + k * 14} {28 - (k % 3) * 8} l6 -6 l6 6 l-6 6 z" fill="#5E3A1E"/>' for k in range(6)) +
             '<path d="M30 -22 C40 -40 66 -40 70 -24 C72 -12 56 -6 40 -8 Z" fill="#B88C4A" stroke="#5E3A1E" stroke-width="1.4"/><circle cx="56" cy="-26" r="3" fill="#1B1520"/>'
             '<path d="M64 -14 l-2 10 M58 -12 l-2 9" stroke="#F4F2EC" stroke-width="2.4" stroke-linecap="round"/>'),
    'canth': ('<path d="M-6 -36 C10 -36 14 -10 12 20 C10 40 -10 40 -12 20 C-14 -10 -10 -36 -6 -36 Z" fill="#2E9E6E" stroke="#13603F" stroke-width="1.6"/>'
              '<path d="M-1 -30 L0 38" stroke="#13603F" stroke-width="1.4"/><ellipse cx="-1" cy="-44" rx="8" ry="7" fill="#1E7A52"/>'
              + ''.join(f'<path d="M{-10 if s < 0 else 8} {y} l{s * 14} {d}" stroke="#13603F" stroke-width="2"/>' for s in (-1, 1) for y, d in ((-20, -8), (0, 0), (18, 8))) +
              '<path d="M-4 -50 l-10 -14 M2 -50 l10 -14" stroke="#13603F" stroke-width="1.6"/>'),
    'sep': ('<path d="M20 10 C30 30 10 50 -10 44 C-40 40 -50 20 -40 4 C-30 -10 0 -20 20 10 Z" fill="#2B2B3A" opacity=".35"/>'
            '<path d="M-36 -10 C-36 -34 30 -40 44 -20 C54 -6 44 8 30 6 C10 4 -36 10 -36 -10 Z" fill="#C9A6C9" stroke="#7E5A7E" stroke-width="1.4"/>'
            + ''.join(f'<path d="M-34 {-8 + k * 4} C-48 {-4 + k * 6} -54 {k * 8} -60 {4 + k * 8}" stroke="#7E5A7E" stroke-width="2" fill="none"/>' for k in range(4)) +
            '<circle cx="-24" cy="-14" r="3" fill="#1B1520"/>'),
    'spong': ('<path d="M-40 10 C-50 -14 -30 -40 -6 -36 C10 -46 40 -36 42 -14 C56 4 42 34 18 34 C0 44 -30 38 -40 10 Z" fill="#D9A94E" stroke="#9E7524" stroke-width="1.6"/>'
              + ''.join(f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * .8:.1f}" fill="#9E7524" opacity=".55"/>' for x, y, r in ((-20, -14, 5), (4, -20, 4), (24, -8, 5), (-10, 6, 4), (12, 14, 6), (-28, 18, 3), (30, 18, 3)))),
    'noso': ('<rect x="-12" y="-44" width="24" height="84" rx="10" fill="url(#glass)" stroke="#8FB3C9" stroke-width="1.6"/><rect x="-10" y="-4" width="20" height="42" rx="8" fill="#E9DFA6"/>'
             + ''.join(f'<circle cx="{-4 + (k % 3) * 4}" cy="{6 + k * 6}" r="2" fill="#B9A25A"/>' for k in range(5)) + '<rect x="-14" y="-50" width="28" height="10" rx="3" fill="#C9D1D9"/>'),
}


def sources():
    W, H = 760, 818
    tiles = [('bell', 'Belladonna', 'deadly nightshade · Solanaceae', ['Sudden heat, redness,', 'throbbing; dilated pupils']),
             ('puls', 'Pulsatilla', 'wind flower · Ranunculaceae', ['Mild, weepy, thirstless;', 'better in open air']),
             ('arn', 'Arnica', "leopard's bane · Compositae", ['Bruised soreness; says', 'he is well when very ill']),
             ('rhus', 'Rhus tox', 'poison ivy · Anacardiaceae', ['Stiff; worse first motion,', 'better continued motion']),
             ('cinch', 'Cinchona (China)', 'Peruvian bark · Rubiaceae', ['Weakness from loss of', 'fluids; first drug proved']),
             ('nux', 'Nux vomica', 'poison nut (seeds) · Loganiaceae', ['Irritable, chilly; urging', 'without result']),
             ('apis', 'Apis', 'honey bee · ANIMAL', ['Oedema, stinging pains,', 'thirstless']),
             ('lach', 'Lachesis', 'snake venom · ANIMAL', ['Worse after sleep', '']),
             ('canth', 'Cantharis', 'Spanish fly, a beetle · ANIMAL', ['Burning cystitis;', 'burns and scalds']),
             ('sep', 'Sepia', 'cuttlefish ink · ANIMAL', ['Complements Nat mur', '']),
             ('spong', 'Spongia', 'roasted sponge · ANIMAL', ['Dry, sawing croup cough', 'like a saw through pine']),
             ('noso', 'Nosodes', 'disease products', ['Psorinum, Medorrhinum,', 'Pyrogenium, Bacillinum'])]
    b = ''
    for k, (key, name, src, lines) in enumerate(tiles):
        col, row = k % 4, k // 4
        x0, y0 = 24 + col * 181, 76 + row * 238
        animal = 'ANIMAL' in src
        b += card(x0, y0, 169, 226, 'fpur' if animal else ('famb' if key == 'noso' else 'fgrn'))
        b += g(ART[key], x0 + 84, y0 + 74, sc=1.05)
        c = 'pur' if animal else ('amb' if key == 'noso' else 'grn')
        b += T(x0 + 12, y0 + 148, name, f'l b {c}', 'start', ' style="font-size:16px"')
        b += T(x0 + 12, y0 + 168, src.replace(' · ANIMAL', ''), 'n sm', 'start', ' textLength="146" lengthAdjust="spacingAndGlyphs"' if len(src.replace(' · ANIMAL', '')) > 24 else '')
        b += TL(x0 + 12, y0 + 190, [l for l in lines if l], 'l sm', 16)
    b += T(24, 802, 'Trap: Apis, Cantharis and Spongia are ANIMAL remedies even when listed with the minerals (purple tiles).', 'n sm')
    alt = 'Where common remedies come from: plants (green tiles) Belladonna (deadly nightshade, Solanaceae), Pulsatilla (wind flower, Ranunculaceae), Arnica (leopard’s bane, Compositae), Rhus tox (poison ivy, Anacardiaceae), Cinchona (Peruvian bark, Rubiaceae) and Nux vomica (poison nut seeds, Loganiaceae); animals (purple tiles) Apis (honey bee), Lachesis (snake venom), Cantharis (a beetle), Sepia (cuttlefish ink) and Spongia (roasted sponge); and nosodes from disease products; each with its keynote.'
    return plate(W, H, 'Where the remedies come from', 'Source, family and one keynote to hang it on', b, alt), alt


FIGS = {'t2-sources': sources}
