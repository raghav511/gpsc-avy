from lib import *
from hands import strokes
import math, random

BODY_O, BODY_I = '#B7C2D0', '#E7EDF4'


def person():
    paths = ['M-32 -76 L-46 -28 L-50 18', 'M32 -76 L46 -28 L50 18', 'M-14 26 L-16 84 L-17 142', 'M14 26 L16 84 L17 142']
    o = ''.join(f'<path d="{d}" stroke="{BODY_O}" stroke-width="{19 if i < 2 else 25}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for i, d in enumerate(paths))
    i_ = ''.join(f'<path d="{d}" stroke="{BODY_I}" stroke-width="{16 if i < 2 else 22}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>' for i, d in enumerate(paths))
    torso = f'<path d="M-36 -82 C-20 -90 20 -90 36 -82 L32 -10 C30 14 26 30 0 32 C-26 30 -30 14 -32 -10 Z" fill="{BODY_I}" stroke="{BODY_O}" stroke-width="1.6"/>'
    head = f'<rect x="-6" y="-100" width="12" height="16" fill="{BODY_I}"/><circle cy="-116" r="19" fill="{BODY_I}" stroke="{BODY_O}" stroke-width="1.6"/>'
    return o + torso + i_ + head


def spot(x, y, r, col, op=.55):
    return f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * .8:.1f}" fill="{col}" opacity="{op}"/>'


def skin_lesions():
    W, H = 760, 660
    R = random.Random(3)
    cols = []
    # eczema
    s = spot(-45, -30, 9, '#D2453D') + spot(45, -30, 9, '#D2453D') + spot(-49, 12, 7, '#D2453D') + spot(49, 12, 7, '#D2453D') + spot(0, -94, 9, '#D2453D') + spot(-10, -110, 5, '#D2453D', .35) + spot(10, -110, 5, '#D2453D', .35)
    s += f'<path d="M-24 84 h-14 M24 84 h14" stroke="#D2453D" stroke-width="3" stroke-dasharray="3 3"/>'
    close = '<circle r="54" fill="#F2C2AE"/>' + ''.join(f'<circle cx="{R.uniform(-36, 36):.0f}" cy="{R.uniform(-36, 36):.0f}" r="{R.uniform(3, 6):.1f}" fill="#E4675D" stroke="#C2463E"/>' for _ in range(16)) + ''.join(f'<circle cx="{R.uniform(-30, 30):.0f}" cy="{R.uniform(-30, 30):.0f}" r="3" fill="#FCEFC0" stroke="#D8B347"/>' for _ in range(7)) + '<path d="M-20 30 c4 6 10 10 18 8" stroke="#E8C64A" stroke-width="4" fill="none" opacity=".8"/>'
    cols.append(('Eczema (atopic)', 'red', s, close, [('Lesion', 'Itchy papulovesicles, oozing;'), ('', 'chronic: thick, lichenified'), ('Sites', 'FLEXURES: elbow and knee'), ('', 'folds; cheeks in infants')]))
    # psoriasis
    s = spot(-47, -24, 9, '#C2463E', .7) + spot(47, -24, 9, '#C2463E', .7) + spot(-16, 76, 10, '#C2463E', .7) + spot(16, 76, 10, '#C2463E', .7) + spot(0, -128, 12, '#C2463E', .6)
    s += '<path d="M-12 18 h24" stroke="#C2463E" stroke-width="4" stroke-dasharray="3 3"/>'
    close = '<circle r="54" fill="#F2C2AE"/><path d="M-38 -14 C-30 -36 10 -40 30 -26 C46 -14 44 18 26 30 C4 44 -30 36 -40 14 Z" fill="#D25A52" stroke="#A8322B" stroke-width="2"/>' + ''.join(f'<path d="M{R.uniform(-30, 24):.0f} {R.uniform(-26, 24):.0f} l{R.uniform(6, 14):.0f} {R.uniform(-3, 3):.0f}" stroke="#F4F2EC" stroke-width="{R.uniform(3, 6):.1f}" stroke-linecap="round" opacity=".95"/>' for _ in range(22))
    cols.append(('Psoriasis', 'pur', s, close, [('Lesion', 'Well-defined red plaques,'), ('', 'silvery-white scales'), ('Sites', 'EXTENSORS: elbows, knees;'), ('', 'scalp, lower back, nails')]))
    # urticaria
    s = ''.join(spot(round(R.uniform(-30, 30)), round(R.uniform(-80, 20)), round(R.uniform(5, 9)), '#E46F67', .55) for _ in range(9)) + spot(-44, -10, 7, '#E46F67') + spot(15, 90, 8, '#E46F67') + spot(0, -110, 8, '#E46F67', .45)
    close = '<circle r="54" fill="#F2C2AE"/><circle r="40" fill="#EC8E86" opacity=".6"/><path d="M-26 -8 C-20 -26 10 -30 24 -14 C34 0 22 22 4 24 C-16 28 -32 12 -26 -8 Z" fill="#FBE3D8" stroke="#E7A190" stroke-width="2"/>'
    cols.append(('Urticaria', 'amb', s, close, [('Lesion', 'Itchy raised wheals with a'), ('', 'red flare; each fades < 24 h'), ('Sites', 'Anywhere; angio-oedema of'), ('', 'lips and eyelids')]))
    b = ''
    for k, (name, c, sites, close, rows) in enumerate(cols):
        x0 = 24 + k * 240
        b += card(x0, 76, 228, 512, 'pn')
        b += T(x0 + 16, 106, name, f'l b {c}', 'start', ' style="font-size:17px"')
        b += g(person() + sites, x0 + 78, 290, sc=1.0)
        b += g(close, x0 + 176, 190)
        b += f'<path d="M{x0 + 176} 246 L{x0 + 176} 260" class="ln"/>' + T(x0 + 176, 274, 'close-up', 'n sm', 'middle')
        for j, (lab, val) in enumerate(rows):
            yy = 466 + j * 20 + (16 if j >= 2 else 0)
            if lab: b += T(x0 + 16, yy - 2, lab.upper(), 'n sm b')
            b += T(x0 + 16, yy + 16, val, 'n sm')
    b += T(x0 + 0, 0, '', 'n')
    b += TL(24, 618, ['Psoriasis is silvery scales on extensors with Auspitz and Koebner signs; eczema is', 'itchy, flexural and oozing; urticaria is wheals that vanish within 24 hours.'], 'n sm', 18)
    alt = 'Three common skin conditions with body maps and close-ups: atopic eczema with itchy, oozing papulovesicles in the flexures (elbow and knee folds, face in infants); psoriasis with well-defined red plaques and silvery scales on the extensors (elbows, knees), scalp, lower back and nails; and urticaria with itchy wheals and flare anywhere on the body, each lasting under 24 hours, sometimes with angio-oedema of the lips and eyelids.'
    return plate(W, H, 'Eczema, psoriasis, urticaria', 'Where it appears, and what the lesion looks like', b, alt), alt


FIGS = {'t7-skin': skin_lesions}


def ulcers():
    W, H = 760, 640
    st = ('<path d="M-60 -150 L-46 -150 L-40 -96 C-20 -120 30 -126 54 -100 C78 -74 76 -20 60 20 C44 60 0 92 -46 96 C-70 98 -90 90 -104 82 L-110 102 C-120 104 -132 100 -134 92 C-150 84 -160 70 -150 58 C-140 50 -126 56 -120 62 C-100 62 -84 60 -72 50 C-60 40 -56 20 -60 0 C-64 -30 -60 -70 -56 -98 Z" fill="#F1B7B0" stroke="#B9665E" stroke-width="2.4"/>'
          '<path d="M-56 -98 C-60 -60 -64 -20 -60 0 C-56 24 -64 44 -80 54" stroke="#B9665E" stroke-width="1.4" fill="none" stroke-dasharray="4 4"/>'
          '<path d="M-134 92 C-150 120 -160 160 -146 200 C-136 222 -110 222 -96 200 C-86 186 -90 168 -100 160" fill="none" stroke="#E9B98A" stroke-width="26" stroke-linecap="round"/>'
          '<path d="M-134 92 C-150 120 -160 160 -146 200 C-136 222 -110 222 -96 200 C-86 186 -90 168 -100 160" fill="none" stroke="#C99A62" stroke-width="1.4"/>')
    st += '<ellipse cx="-62" cy="-8" rx="9" ry="7" fill="#7E1F1F" stroke="#F7E3C9" stroke-width="2"/>'
    st += '<ellipse cx="-142" cy="104" rx="8" ry="7" fill="#7E1F1F" stroke="#F7E3C9" stroke-width="2"/>'
    b = g(st, 300, 300)
    labs = [(150, 120, 'oesophagus', 'start', 246, 168), (420, 176, 'fundus', 'middle', 336, 210), (430, 430, 'greater curvature', 'middle', 360, 360),
            (40, 262, 'lesser curvature', 'start', 236, 286), (40, 340, 'pylorus', 'start', 184, 364), (40, 500, 'duodenum', 'start', 162, 470)]
    for tx, ty, l, a, px, py in labs:
        b += lead(tx + (30 if a == 'start' else 0), ty + 6, px, py) + T(tx, ty, l, 'n sm', a)
    b += T(330, 300, 'body', 'n sm', 'middle')
    badge = lambda x, y, L, c: f'<circle cx="{x}" cy="{y}" r="13" class="f{c}"/>' + T(x, y + 5, L, f'l b {c}', 'middle')
    b += badge(264, 278, 'G', 'red') + badge(128, 424, 'D', 'blu')
    b += card(488, 84, 248, 196, 'fblu') + badge(512, 112, 'D', 'blu') + T(534, 117, 'Duodenal ulcer', 'h blu') + TL(504, 144, ['Commoner (about 4 : 1)', '1st part of duodenum,', 'anterior wall commonest', 'H. pylori in ~90%; high acid', 'Almost never malignant'], 'n sm', 18)
    b += card(488, 296, 248, 162, 'fred') + badge(512, 324, 'G', 'red') + T(534, 329, 'Gastric ulcer', 'h red') + TL(504, 356, ['Lesser curvature', 'H. pylori ~70%, NSAIDs', 'Biopsy every gastric ulcer:', 'it can be malignant'], 'n sm', 18)
    # pain timing
    y0 = 568
    b += T(24, y0, 'PAIN AND FOOD', 'n sm b')
    b += pill(24, y0 + 30, 'Duodenal: relieved by food, hunger pain, wakes at night', 'blu', 404) + pill(24, y0 + 58, 'Gastric: worse after food, weight loss', 'red', 290)
    b += T(470, y0 + 30, '"Gastric Gets worse with food;', 'n sm') + T(470, y0 + 48, 'Duodenal is Dulled by food."', 'n sm')
    alt = 'The stomach and duodenum with the two common sites of peptic ulcer: a duodenal ulcer in the first part of the duodenum, anterior wall commonest, about four times commoner, H. pylori in about 90 percent, almost never malignant, pain relieved by food and waking the patient at night; and a gastric ulcer on the lesser curvature, H. pylori about 70 percent or NSAIDs, can be malignant so always biopsied, pain worse after food with weight loss.'
    return plate(W, H, 'Peptic ulcer: duodenal or gastric?', 'Site, cause and how food changes the pain', b, alt), alt


FIGS['t7-ulcers'] = ulcers


BRAIN = 'M-128 12 C-136 -44 -92 -98 -20 -104 C52 -110 116 -76 130 -24 C140 14 122 44 92 54 C70 66 40 70 18 64 C0 74 -50 74 -80 60 C-112 52 -126 36 -128 12 Z'


def face(kind):
    s = '<ellipse cx="0" cy="0" rx="62" ry="78" fill="url(#skin)" stroke="#B9826A" stroke-width="2"/>'
    s += '<path d="M-58 -36 C-70 -110 70 -110 58 -36 C50 -70 -50 -70 -58 -36 Z" fill="#4A3426"/>'
    # forehead wrinkles: left side of the picture = patient's right
    lw = 'M-40 -40 q10 -4 20 0 M-40 -32 q10 -4 20 0'
    rw = 'M20 -40 q10 -4 20 0 M20 -32 q10 -4 20 0'
    s += f'<path d="{lw}" stroke="#B9826A" stroke-width="1.6" fill="none"/>'
    if kind == 'umn':
        s += f'<path d="{rw}" stroke="#B9826A" stroke-width="1.6" fill="none"/>'
    # eyes
    s += '<ellipse cx="-24" cy="-12" rx="11" ry="6" fill="#fff" stroke="#5B4636"/><circle cx="-24" cy="-12" r="4" fill="#3A2A20"/>'
    if kind == 'lmn':
        s += '<ellipse cx="24" cy="-10" rx="12" ry="8" fill="#fff" stroke="#5B4636"/><circle cx="24" cy="-14" r="4" fill="#3A2A20"/>'
    else:
        s += '<ellipse cx="24" cy="-12" rx="11" ry="6" fill="#fff" stroke="#5B4636"/><circle cx="24" cy="-12" r="4" fill="#3A2A20"/>'
    s += '<path d="M-36 -24 q12 -6 24 0 M12 -24 q12 -6 24 0" stroke="#4A3426" stroke-width="2.4" fill="none"/>'
    s += '<path d="M0 -6 L-6 18 L6 18" stroke="#B9826A" stroke-width="1.6" fill="none"/>'
    s += '<path d="M-24 10 C-30 20 -30 28 -24 34" stroke="#B9826A" stroke-width="1.4" fill="none"/>'  # nasolabial fold, normal side
    s += '<path d="M-22 40 C-8 44 6 46 22 52" stroke="#A8322B" stroke-width="3" fill="none" stroke-linecap="round"/>'  # mouth droops to the weak side
    return s


def stroke_face():
    W, H = 760, 760
    b = ''
    # lateral brain
    lat = f'<path d="{BRAIN}" fill="#F3E1DC" stroke="#A88A84" stroke-width="2"/>'
    lat += '<clipPath id="brc"><path d="' + BRAIN + '"/></clipPath><g clip-path="url(#brc)">'
    lat += '<path d="M-120 -40 C-90 -70 -20 -84 40 -78 C80 -70 104 -40 110 -10 C96 20 60 40 20 44 C-20 50 -70 44 -110 30 Z" fill="#E46F67" opacity=".55"/>'
    lat += '<path d="M-60 -104 C-20 -110 30 -110 60 -100 L50 -84 C10 -92 -30 -92 -56 -88 Z" fill="#2E68D8" opacity=".45"/>'
    lat += '<path d="M96 -60 C120 -40 136 -10 130 20 C118 40 100 50 88 54 C92 20 92 -20 96 -60 Z" fill="#7845C8" opacity=".45"/></g>'
    lat += '<path d="M-110 20 C-70 0 -20 -8 30 -4" stroke="#A88A84" stroke-width="2" fill="none"/><path d="M10 -104 C0 -70 -6 -40 -2 -10" stroke="#A88A84" stroke-width="2" fill="none"/>'
    lat += '<path d="M60 60 C80 80 110 84 124 64 C130 52 120 46 104 50 Z" fill="#E7CFC9" stroke="#A88A84" stroke-width="1.6"/><path d="M30 64 L34 104 L50 104 L52 66" fill="#E7CFC9" stroke="#A88A84" stroke-width="1.6"/>'
    b += card(24, 76, 712, 300, 'pn')
    b += g(lat, 190, 236, sc=1.1)
    b += T(40, 104, 'Side view of the left hemisphere', 'n sm b')
    b += lead(118, 340, 140, 260) + T(118, 356, 'MCA territory: face and arm', 'n sm b red', 'middle')
    b += lead(260, 110, 210, 128) + T(266, 108, 'ACA strip: leg area', 'n sm b blu')
    b += lead(330, 338, 300, 246) + T(330, 354, 'PCA: occipital, vision', 'n sm b pur', 'middle')
    rows = [('red', 'Middle cerebral artery', ['COMMONEST site. Opposite-side weakness,', 'face and arm > leg; aphasia if dominant side']),
            ('blu', 'Anterior cerebral artery', ['Leg > arm weakness']),
            ('pur', 'Posterior cerebral artery', ['Homonymous hemianopia, macular sparing']),
            ('amb', 'Internal capsule', ['Dense weakness of face, arm AND leg', '(lenticulostriate; hypertensive bleed)'])]
    for k, (c, n, ls) in enumerate(rows):
        y = 112 + k * 66
        b += f'<rect x="420" y="{y - 12}" width="14" height="14" rx="4" class="{c}" opacity=".7"/>' + T(442, y, n, f'l b {c}') + TL(442, y + 18, ls, 'n sm', 16)
    # faces
    b += card(24, 392, 350, 344, 'pn') + card(386, 392, 350, 344, 'pn')
    b += g(face('umn'), 199, 520) + g(face('lmn'), 561, 520)
    b += T(40, 420, 'Stroke (UMN facial palsy)', 'l b red') + T(402, 420, "Bell's palsy (LMN)", 'l b pur')
    b += TL(40, 636, ['Lower face droops on one side', 'FOREHEAD SPARED: wrinkles on', 'both sides'], 'n sm', 17)
    b += TL(402, 636, ['WHOLE half of the face, forehead', 'too: no wrinkles, eye will not close.', 'Steroids within 72 h'], 'n sm', 17)
    b += T(24, 754, 'Non-contrast CT first in every acute stroke: it rules out bleeding before a clot-buster.', 'n sm')
    alt = "Stroke territories on a side view of the brain: the middle cerebral artery supplies most of the lateral surface including the face and arm areas (commonest site; contralateral weakness, face and arm more than leg, aphasia if dominant), the anterior cerebral artery the leg area along the top (leg more than arm), and the posterior cerebral artery the occipital lobe (homonymous hemianopia with macular sparing). Two faces compare facial palsy: in a stroke (upper motor neurone) the forehead is spared, in Bell's palsy (lower motor neurone) the whole half of the face including the forehead is weak and the eye does not close."
    return plate(W, H + 14, 'Stroke territories and facial palsy', 'Which artery, which weakness; does the forehead move?', b, alt), alt


FIGS['t7-stroke'] = stroke_face


def airway(kind):
    """Cross-section of a small airway."""
    s = ''
    if kind == 'norm':
        s += '<circle r="62" fill="#F3C9C2" stroke="#C7867D" stroke-width="2"/><circle r="50" fill="#E7A39A"/><circle r="40" fill="#FFF8F0" stroke="#D49A90" stroke-width="2"/>'
    elif kind == 'asth':
        s += '<circle r="66" fill="#F0B4AA" stroke="#C7867D" stroke-width="2"/>'
        s += ''.join(f'<path d="M{58 * math.cos(a):.0f} {58 * math.sin(a):.0f}A58 58 0 0 1 {58 * math.cos(a + .35):.0f} {58 * math.sin(a + .35):.0f}" stroke="#B5453C" stroke-width="10" fill="none"/>' for a in [k * .52 for k in range(12)])
        s += '<path d="M-26 -8 C-30 -26 -12 -34 0 -22 C12 -36 34 -24 26 -6 C40 6 24 26 8 18 C0 32 -24 30 -22 14 C-36 8 -38 -2 -26 -8 Z" fill="#FFF8F0" stroke="#D49A90" stroke-width="2"/>'
        s += '<path d="M-10 -6 C-4 -14 8 -12 10 -2 C12 8 -2 12 -8 6 Z" fill="#E9DFA6" stroke="#C9B85A"/>'
        s += ''.join(f'<circle cx="{40 * math.cos(a):.0f}" cy="{40 * math.sin(a):.0f}" r="3" fill="#E2643F"/>' for a in [k * .9 for k in range(7)])
    else:
        s += '<circle r="64" fill="#F3C9C2" stroke="#C7867D" stroke-width="2"/><circle r="52" fill="#E7A39A"/>'
        s += ''.join(f'<ellipse cx="{50 * math.cos(a):.0f}" cy="{50 * math.sin(a):.0f}" rx="9" ry="7" fill="#EFE7C9" stroke="#C9B85A"/>' for a in [k * .7 for k in range(9)])
        s += '<circle r="34" fill="#FFF8F0" stroke="#D49A90" stroke-width="2"/><path d="M-26 6 C-14 -10 10 -14 26 2 C18 18 -14 24 -26 6 Z" fill="#E9DFA6" opacity=".9"/>'
    return s


def alveoli(kind):
    if kind == 'norm':
        cells = [(x, y) for x in (-30, 0, 30) for y in (-26, 0, 26)]
        return ''.join(f'<circle cx="{x + (8 if abs(y) == 26 else 0)}" cy="{y}" r="16" fill="#FFF8F0" stroke="#D49A90" stroke-width="2.4"/>' for x, y in cells)
    return ('<path d="M-52 -40 C-30 -60 20 -56 46 -36 C62 -10 56 30 30 46 C0 60 -40 52 -54 26 C-64 0 -62 -24 -52 -40 Z" fill="#FFF8F0" stroke="#D49A90" stroke-width="2.4"/>'
            '<path d="M-20 -50 L-14 -20 M18 48 L12 20 M-56 6 L-30 2" stroke="#D49A90" stroke-width="2.4"/>')


def airways():
    W, H = 760, 700
    b = ''
    tiles = [('norm', 'Normal airway', 'grn', ['Open lumen, thin wall']),
             ('asth', 'Asthma', 'blu', ['Smooth muscle squeezes,', 'wall swells, mucus plug;', 'eosinophils, mast cells']),
             ('bron', 'Chronic bronchitis', 'amb', ['Enlarged mucus glands,', 'goblet cells (Reid index', '> 0.4); "blue bloater"'])]
    for k, (kd, name, c, ls) in enumerate(tiles):
        x0 = 24 + k * 240
        b += card(x0, 76, 228, 288, 'pn')
        b += g(airway(kd), x0 + 114, 162)
        b += T(x0 + 16, 262, name, f'l b {c}') + TL(x0 + 16, 284, ls, 'n sm', 16)
    b += card(24, 380, 348, 220, 'pn') + card(388, 380, 348, 220, 'pn')
    b += g(alveoli('norm'), 120, 480) + g(alveoli('emph'), 484, 480)
    b += T(196, 450, 'Normal alveoli', 'l b grn') + TL(196, 472, ['Many small sacs,', 'large surface for', 'gas exchange'], 'n sm', 16)
    b += T(560, 450, 'Emphysema', 'l b red') + TL(560, 472, ['Walls destroyed,', 'airspaces enlarged;', '"pink puffer"'], 'n sm', 16)
    b += TL(404, 566, ['Centriacinar: smokers, upper lobes', 'Panacinar: α-1 antitrypsin, lower lobes'], 'n sm', 16)
    b += T(24, 632, 'Asthma: variable and REVERSIBLE (FEV1 rises ≥ 12% and ≥ 200 mL after a bronchodilator).', 'l sm blu')
    b += T(24, 656, 'COPD: persistent, not fully reversible (post-bronchodilator FEV1/FVC < 0.70); smoking is the commonest cause.', 'l sm red', 'start', ' textLength="712" lengthAdjust="spacingAndGlyphs"')
    alt = 'Airways in cross-section: a normal airway with an open lumen; asthma with squeezing smooth muscle, a swollen wall, a mucus plug and eosinophils; chronic bronchitis with enlarged mucus glands and goblet cells (Reid index over 0.4). Below, normal alveoli as many small sacs versus emphysema with destroyed walls and enlarged airspaces. Asthma is variable and reversible; COPD is persistent with post-bronchodilator FEV1/FVC below 0.70.'
    return plate(W, H, 'Asthma and COPD in the airway', 'What narrows the airway, and what destroys the alveoli', b, alt), alt


FIGS['t7-airways'] = airways
