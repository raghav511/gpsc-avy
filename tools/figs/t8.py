from lib import *
import math

TORSO = ('M-150 -250 C-110 -262 110 -262 150 -250 C140 -200 120 -150 112 -100 C106 -60 116 -10 128 40 C138 90 136 140 120 196 '
         'L40 214 C20 190 -20 190 -40 214 L-120 196 C-136 140 -138 90 -128 40 C-116 -10 -106 -60 -112 -100 C-120 -150 -140 -200 -150 -250 Z')


def fundal():
    W, H = 760, 636
    b = ''
    t = f'<path d="{TORSO}" fill="url(#skin)" stroke="#B9826A" stroke-width="2"/>'
    # landmarks
    t += '<path d="M-96 -236 C-80 -200 -40 -196 -20 -214 M96 -236 C80 -200 40 -196 20 -214" stroke="#B9826A" stroke-width="1.6" fill="none"/>'
    t += '<path d="M-18 -176 L0 -160 L18 -176" stroke="#8A7150" stroke-width="3" fill="none"/>'  # xiphisternum
    t += '<path d="M-6 -30 C-8 -24 -6 -18 0 -16 C6 -18 8 -24 6 -30 C2 -34 -2 -34 -6 -30 Z" fill="#C9886C" stroke="#9C6248"/>'  # umbilicus
    t += '<path d="M-34 140 C-20 150 20 150 34 140" stroke="#8A7150" stroke-width="5" fill="none" stroke-linecap="round"/>'  # pubic symphysis
    # uterus outlines
    for wk, top, c in ((36, -170, '#7845C8'), (24, -24, '#2E68D8'), (12, 136, '#16824F')):
        w = 26 + (140 - top) * .22
        t += f'<path d="M{-w:.0f} 140 C{-w:.0f} {top + 40} {-w * .6:.0f} {top} 0 {top} C{w * .6:.0f} {top} {w:.0f} {top + 40} {w:.0f} 140" fill="{c}" fill-opacity=".08" stroke="{c}" stroke-width="2.6" stroke-dasharray="7 5"/>'
    b += g(t, 250, 330, sc=0.95)
    marks = [(-170, '36 weeks', 'xiphisternum', 'pur'), (-24, '24 weeks', 'umbilicus', 'blu'), (136, '12 weeks', 'pubic symphysis', 'grn')]
    for y, wk, lm, c in marks:
        yy = round(330 + y * .95)
        b += f'<path d="M370 {yy}L470 {yy}" class="s{c}" stroke-width="1.6" stroke-dasharray="3 3"/>'
        b += T(486, yy - 2, wk, f'h {c}') + T(486, yy + 18, 'fundus at the ' + lm, 'n sm')
    b += card(470, 508, 266, 104, 'pn') + T(486, 530, 'Also asked', 'l b') + TL(486, 550, ['Quickening: 18–20 weeks (primi),', '16–18 weeks (multi)', 'Fetal heart: 110–160/min', 'Trimesters: to 12, 13–28, 29–40'], 'n sm', 16)
    alt = 'Fundal height on the abdomen of a pregnant woman: the top of the uterus reaches the pubic symphysis at 12 weeks, the umbilicus at 24 weeks and the xiphisternum at 36 weeks; quickening is felt at 18 to 20 weeks in a first pregnancy and the fetal heart rate is 110 to 160 per minute.'
    return plate(W, H, 'Fundal height: weeks you can feel', 'Where the top of the uterus lies as pregnancy advances', b, alt), alt


def uterus(kind):
    s = '<path d="M-80 -110 C-120 -80 -124 30 -80 90 C-60 116 -36 124 -20 130 L-16 170 L16 170 L20 130 C36 124 60 116 80 90 C124 30 120 -80 80 -110 C40 -140 -40 -140 -80 -110 Z" fill="#E7A9A1" stroke="#A8574F" stroke-width="3"/>'
    s += '<path d="M-68 -98 C-102 -70 -104 26 -68 80 C-50 104 -30 112 -10 116 L10 116 C30 112 50 104 68 80 C104 26 102 -70 68 -98 C34 -124 -34 -124 -68 -98 Z" fill="#F8E3D6"/>'
    s += '<path d="M-10 116 L-8 168 M10 116 L8 168" stroke="#A8574F" stroke-width="2"/>'  # cervical canal
    # fetus, head down
    fet = ('<circle cx="0" cy="64" r="30" fill="#F2C9AE" stroke="#B9826A" stroke-width="2"/>'
           '<path d="M-26 46 C-46 10 -40 -50 0 -70 C40 -60 50 -10 30 40 C20 30 -10 30 -26 46 Z" fill="#F2C9AE" stroke="#B9826A" stroke-width="2"/>'
           '<path d="M24 -10 C40 0 44 20 30 26 M-20 -40 C-36 -30 -38 -10 -26 0" stroke="#B9826A" stroke-width="7" fill="none" stroke-linecap="round"/>')
    if kind == 'praevia':
        s += '<path d="M-58 88 C-40 112 40 112 58 88 C40 104 -40 104 -58 88 Z M-56 86 C-40 120 40 120 56 86 L50 98 C30 124 -30 124 -50 98 Z" fill="#8E2A3C"/>'
        s += '<path d="M-60 80 C-50 120 50 120 60 80 C50 100 -50 100 -60 80 Z" fill="#B23A4E" stroke="#7E1F2F" stroke-width="2"/>'
        s += g(fet, 0, -26, sc=0.9)
        s += '<path d="M-4 172 C-8 184 -2 196 -6 206 M6 172 C10 186 4 196 8 208" stroke="#D9271E" stroke-width="4" fill="none" stroke-linecap="round"/>'
    else:
        s += '<path d="M-60 -92 C-30 -118 30 -118 60 -92 C30 -100 -30 -100 -60 -92 Z" fill="#B23A4E" stroke="#7E1F2F" stroke-width="2"/>'
        s += '<path d="M-56 -94 C-36 -116 36 -116 56 -94 L48 -84 C24 -100 -24 -100 -48 -84 Z" fill="#B23A4E"/>'
        s += '<path d="M-30 -112 C-10 -122 20 -120 34 -110 C16 -100 -12 -100 -30 -112 Z" fill="#5A1220"/>'  # retroplacental clot
        s += g(fet, 0, 18, sc=0.9)
        s += '<path d="M-2 172 C-4 182 0 190 -2 198" stroke="#7E1F2F" stroke-width="4" fill="none" stroke-linecap="round"/>'
        s += ''.join(f'<path d="M{110 * math.cos(a):.0f} {-10 + 110 * math.sin(a):.0f}l{10 * math.cos(a):.0f} {10 * math.sin(a):.0f}" stroke="#D33A3F" stroke-width="3" stroke-linecap="round"/>' for a in (-2.4, -1.9, -1.2, -.7, -.2, .3))
    return s


def aph():
    W, H = 760, 640
    b = ''
    for k, (kd, name, c, rows) in enumerate([
            ('praevia', 'Placenta praevia', 'blu', [('Placenta', 'Low, over or near the cervix'), ('Bleeding', 'PAINLESS, causeless,'), ('', 'recurrent, bright red'), ('Uterus', 'Soft, not tender')]),
            ('abruptio', 'Abruptio placentae', 'red', [('Placenta', 'Normal site, separates early;'), ('', 'clot builds up behind it'), ('Bleeding', 'PAINFUL'), ('Uterus', 'Tense and tender')])]):
        x0 = 24 + k * 362
        b += card(x0, 76, 350, 540, 'pn')
        b += T(x0 + 18, 106, name, f'l b {c}', 'start', ' style="font-size:17px"')
        b += g(uterus(kd), x0 + 175, 286, sc=0.95)
        for j, (lab, val) in enumerate(rows):
            yy = 512 + j * 22
            if lab: b += T(x0 + 18, yy, lab.upper(), 'n sm b')
            b += T(x0 + 110, yy, val, 'l sm')
    b += lead(x0 - 260, 200, 200, 230) if False else ''
    b += lead(110, 440, 175, 380) + T(110, 456, 'placenta over the os', 'n sm b blu', 'middle')
    b += lead(470, 130, 520, 172) + T(470, 124, 'clot behind the placenta', 'n sm b red', 'middle')
    b += T(24, 634, 'Antepartum haemorrhage = bleeding after 28 weeks (India). Never do a vaginal examination until praevia is excluded.', 'n sm') if False else T(24, 632, 'Antepartum haemorrhage = bleeding after 28 weeks of pregnancy (Indian definition).', 'n sm')
    alt = 'Two causes of antepartum haemorrhage in a section of the pregnant uterus: placenta praevia, where the placenta lies low over the cervix and bleeding is painless, causeless, recurrent and bright red with a soft uterus; and abruptio placentae, where a normally placed placenta separates early with a clot behind it, and bleeding is painful with a tense, tender uterus.'
    return plate(W, H, 'Painless or painful bleeding?', 'Placenta praevia vs abruptio placentae', b, alt), alt


def skull():
    W, H = 760, 560
    sk = '<ellipse cx="0" cy="0" rx="120" ry="150" fill="#F1E4CB" stroke="#A8916B" stroke-width="2.4"/>'
    sk += '<path d="M0 -150 L0 -70 M0 70 L0 136" stroke="#A8916B" stroke-width="2.4"/>'
    sk += '<path d="M-118 -30 C-80 -54 -40 -66 -26 -70 M118 -30 C80 -54 40 -66 26 -70" stroke="#A8916B" stroke-width="2.4" fill="none"/>'
    sk += '<path d="M0 -70 L0 70" stroke="#A8916B" stroke-width="2.4"/>'
    sk += '<path d="M-110 78 C-70 100 -30 124 -12 136 M110 78 C70 100 30 124 12 136" stroke="#A8916B" stroke-width="2.4" fill="none"/>'
    sk += '<path d="M0 -112 L26 -70 L0 -28 L-26 -70 Z" fill="#9DC3E6" stroke="#2E68D8" stroke-width="2.4"/>'
    sk += '<path d="M0 124 L14 140 L-14 140 Z" fill="#F2B8B3" stroke="#D33A3F" stroke-width="2.4"/>'
    b = g(sk, 220, 300)
    b += T(220, 104, 'FRONT (face)', 'n sm b', 'middle') + T(220, 476, 'BACK (occiput)', 'n sm b', 'middle')
    b += lead(370, 160, 240, 230) + T(380, 156, 'Anterior fontanelle', 'l b blu') + T(380, 176, 'diamond-shaped; closes by 12–18 months', 'n sm')
    b += lead(370, 420, 228, 436) + T(380, 416, 'Posterior fontanelle', 'l b red') + T(380, 436, 'triangular; closes by 2–3 months', 'n sm')
    b += lead(370, 300, 222, 330) + T(380, 296, 'Sagittal suture', 'l') + T(380, 316, 'between the parietal bones', 'n sm')
    b += lead(370, 236, 300, 248) + T(380, 240, 'Coronal suture', 'l')
    b += lead(370, 372, 300, 392) + T(380, 376, 'Lambdoid suture', 'l')
    b += card(380, 470, 356, 66, 'pn2') + TL(394, 496, ['Late-closing fontanelles: rickets; in', 'homoeopathy, the Calcarea phosphorica child'], 'n sm', 18)
    alt = "The newborn skull seen from above: the diamond-shaped anterior fontanelle between the frontal and parietal bones closes by 12 to 18 months; the triangular posterior fontanelle closes by 2 to 3 months; with the sagittal, coronal and lambdoid sutures."
    return plate(W, H, 'Fontanelles of the newborn skull', 'Seen from above', b, alt), alt


FIGS = {'t8-fundal-height': fundal, 't8-aph': aph, 't8-fontanelles': skull}
