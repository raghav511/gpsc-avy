from lib import *
from t7 import person
import math


def hering():
    W, H = 760, 640
    b = card(24, 76, 330, 540, 'pn')
    fig = person()
    # inner organs
    fig += '<path d="M-6 -60 C-18 -72 -30 -56 -6 -36 C18 -56 6 -72 -6 -60 Z" fill="#E46F67" opacity=".9"/>'  # heart
    fig += '<ellipse cx="0" cy="-116" rx="12" ry="9" fill="#C9A6C9" opacity=".9"/>'  # brain
    fig += '<circle cx="-46" cy="-28" r="5" fill="#E8A33D"/><circle cx="46" cy="-28" r="5" fill="#E8A33D"/><circle cx="-16" cy="84" r="5" fill="#E8A33D"/><circle cx="16" cy="84" r="5" fill="#E8A33D"/>'  # joints
    fig += arrow(64, -130, 64, 120, 'sblu', 4)
    fig += arrow(-6, -20, -40, 4, 'sgrn', 3) + arrow(6, -20, 40, 4, 'sgrn', 3)
    b += g(fig, 190, 340, sc=1.45)
    b += T(296, 148, 'above', 'l sm b blu', 'middle') + T(296, 534, 'downwards', 'l sm b blu', 'middle')
    rows = [('blu', 'Above downwards', ['Symptoms clear from the head', 'towards the feet']),
            ('grn', 'Within outwards', ['From the inner organs', 'towards the skin']),
            ('pur', 'More to less important organs', ['Vital organs (heart, brain) clear', 'before joints and skin']),
            ('amb', 'Reverse order of appearance', ['The newest symptoms go first,', 'the oldest go last'])]
    for k, (c, n, ls) in enumerate(rows):
        y = 104 + k * 120
        b += card(370, y - 22, 366, 106, f'f{c}') + f'<circle cx="394" cy="{y}" r="13" class="{c}" opacity=".9"/>' + T(394, y + 5, str(k + 1), 'l sm b', 'middle', ' style="fill:#fff"')
        b += T(416, y + 5, n, f'l b {c}') + TL(394 - 8, y + 34, ls, 'n sm', 18)
    b += T(24, 634, "Constantine Hering (1800–1880), author of the Guiding Symptoms. Use it to judge whether the cure is going the right way.", 'n sm', 'start', ' textLength="712" lengthAdjust="spacingAndGlyphs"')
    alt = "Hering's law of the direction of cure on a human figure: symptoms go from above downwards, from within outwards (inner organs to skin), from more important to less important organs (heart and brain before joints and skin), and in the reverse order of their appearance."
    return plate(W, H + 12, "Hering's law: the direction of cure", 'Four arrows that tell you the case is healing', b, alt), alt


def similars():
    W, H = 760, 500
    b = ''
    steps = [
        ('1790', 'amb', 'Translating Cullen', ['Hahnemann is translating', "Cullen's Materia Medica"]),
        ('Self-test', 'red', 'Cinchona on himself', ['He takes Cinchona bark', 'himself, while healthy,', 'and notes what it does']),
        ('Provings', 'blu', 'Test on the healthy', ['One pure drug at a time', '(§122), 30th potency', '(§128), §§105–145']),
        ('Law', 'grn', 'Similia similibus curentur', ['A medicine cures the', 'disease whose symptoms', 'it produces (§26)']),
    ]
    art = [
        '<path d="M-50 -24 L0 -14 L50 -24 L50 30 L0 40 L-50 30 Z" fill="#FBF6EA" stroke="#9E927A" stroke-width="2"/><path d="M0 -14 L0 40" stroke="#9E927A" stroke-width="2"/>' + ''.join(f'<path d="M{-42 + (k // 4) * 50} {-12 + (k % 4) * 10}h32" stroke="#C9BFA6" stroke-width="2"/>' for k in range(8)),
        '<path d="M-40 -6 C-40 -20 30 -24 36 -8 L36 6 C30 -8 -40 -4 -40 10 Z" fill="#8A5A34" stroke="#5E3A1E" stroke-width="1.4"/><ellipse cx="-40" cy="2" rx="6" ry="8" fill="#C79A6A" stroke="#5E3A1E"/>' + '<path d="M-20 26 C-10 18 10 18 20 26" stroke="#D33A3F" stroke-width="2" fill="none"/><path d="M-8 34 q8 -6 16 0" stroke="#D33A3F" stroke-width="2" fill="none"/>',
        g('<circle cx="0" cy="-26" r="12" fill="#E7EDF4" stroke="#9AAFC4" stroke-width="2"/><path d="M-20 30 C-20 0 -14 -12 0 -12 C14 -12 20 0 20 30 Z" fill="#E7EDF4" stroke="#9AAFC4" stroke-width="2"/>', -24, 4) + g('<circle cx="0" cy="-26" r="12" fill="#E7EDF4" stroke="#9AAFC4" stroke-width="2"/><path d="M-20 30 C-20 0 -14 -12 0 -12 C14 -12 20 0 20 30 Z" fill="#E7EDF4" stroke="#9AAFC4" stroke-width="2"/>', 24, 4) + '<rect x="-6" y="-34" width="12" height="22" rx="4" fill="url(#glass)" stroke="#8FB3C9"/>',
        '<path d="M-44 -10 L44 -10 M0 -36 L0 30 M-30 30 L30 30" stroke="#5A6172" stroke-width="3"/><path d="M-58 -10 L-30 -10 L-44 18 Z M30 -10 L58 -10 L44 18 Z" fill="#DDF3E7" stroke="#16824F" stroke-width="2"/><circle cx="0" cy="-38" r="5" fill="#5A6172"/>',
    ]
    for k, (tag, c, name, lines) in enumerate(steps):
        x0 = 24 + k * 181
        b += card(x0, 76, 169, 330, 'pn')
        b += pill(x0 + 14, 106, tag, c)
        b += g(art[k], x0 + 84, 190)
        b += T(x0 + 14, 278, name if len(name) < 20 else name.split(' ')[0] + ' ' + name.split(' ')[1], f'l b {c}')
        if len(name) >= 20: b += T(x0 + 14, 296, ' '.join(name.split(' ')[2:]), f'l b {c}')
        b += TL(x0 + 14, 326, lines, 'n sm', 18)
        if k < 3: b += arrow(x0 + 160, 280, x0 + 190, 280, f's{c}', 2.6)
    b += TL(24, 440, ['Drug proving (§§21, 105–145): medicinal powers are learnt only by testing on healthy people.', 'Self-proving by a healthy, unprejudiced physician is best (§141).', '1805: Fragmenta de viribus, the first record of provings (27 drugs).'], 'n sm', 20)
    alt = "From one experiment to a law: in 1790, while translating Cullen's Materia Medica, Hahnemann took Cinchona bark himself and, though healthy, developed symptoms like those it cures; this led to drug proving on healthy people (one pure drug at a time, in the 30th potency, aphorisms 105 to 145) and to the law of similars, similia similibus curentur (aphorism 26)."
    return plate(W, H, 'From one experiment to the law of similars', 'How Cinchona bark started homoeopathy', b, alt), alt


FIGS = {'t1-hering': hering, 't1-similars': similars}
