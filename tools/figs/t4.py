from lib import *
import math


def kent_page():
    W, H = 760, 640
    b = ''
    # page
    b += '<rect x="24" y="80" width="400" height="534" rx="6" fill="#FBF6EA" stroke="#C9B98E" stroke-width="1.6"/>'
    b += '<rect x="24" y="80" width="400" height="534" rx="6" fill="none" stroke="#000" stroke-opacity=".05" stroke-width="8"/>'
    PAGE = 'style="fill:#2B2418"'
    b += f'<text x="224" y="118" text-anchor="middle" class="l b" style="fill:#2B2418;letter-spacing:4px;font-size:18px">MIND</text>'
    b += '<path d="M60 130 H388" stroke="#C9B98E"/>'
    y = 166
    b += f'<text x="44" y="{y}" class="l" style="fill:#B3261E;font-weight:800">RUBRIC:</text>'
    b += f'<text x="122" y="{y}" style="font:700 14px Georgia,serif;fill:#2B2418">ABC.</text><text x="166" y="{y}" style="font:italic 14px Georgia,serif;fill:#2B2418">def.,</text><text x="206" y="{y}" style="font:14px Georgia,serif;fill:#2B2418">ghi., jkl., mno.</text>'
    subs = [('Side', 'left · right'), ('Time', 'morning · forenoon · noon · afternoon ·'), ('', 'evening · night · midnight'), ('Conditions', 'the modalities: < and >'), ('Extension', 'to other parts'), ('Location', 'where exactly'), ('Character', 'the sensation')]
    y += 30
    for k, (a, v) in enumerate(subs):
        if a:
            b += f'<text x="62" y="{y}" style="font:14px Georgia,serif;fill:#2B2418">{a.lower()}:</text>'
            b += f'<text x="160" y="{y}" style="font:13px Georgia,serif;fill:#6E6250">{esc(v)}</text>'
        else:
            b += f'<text x="160" y="{y}" style="font:13px Georgia,serif;fill:#6E6250">{esc(v)}</text>'
        y += 26
    b += '<path d="M48 186 V' + str(y - 18) + '" stroke="#B3261E" stroke-width="2" stroke-dasharray="3 3"/>'
    b += f'<text x="44" y="{y + 20}" style="font:12px Georgia,serif;fill:#6E6250">… then the next rubric, alphabetically</text>'
    b += f'<text x="224" y="596" text-anchor="middle" style="font:12px Georgia,serif;fill:#8C7E62">— 37 chapters, Mind first, Generalities last —</text>'
    # explanations
    x = 448
    b += T(x, 104, 'Reading a page of Kent', 'h')
    b += T(x, 132, 'GRADES', 'n sm b')
    for k, (txt, st, m) in enumerate((('ABC.', '700', 'bold = 3 marks'), ('def.', 'italic', 'italic = 2 marks'), ('ghi.', '400', 'roman = 1 mark'))):
        yy = 160 + k * 30
        stl = f'font:{"italic " if st == "italic" else ""}{st if st != "italic" else "400"} 18px Georgia,serif'
        b += f'<rect x="{x}" y="{yy - 20}" width="70" height="28" rx="6" class="pn"/><text x="{x + 35}" y="{yy}" text-anchor="middle" class="l" style="{stl}">{txt}</text>' + T(x + 84, yy - 2, m, 'l sm')
    b += T(x, 270, 'SUB-RUBRIC ORDER', 'n sm b')
    order = ['Side', 'Time', 'Conditions', 'Extension', 'Location', 'Character']
    for k, o in enumerate(order):
        yy = 296 + k * 30
        b += f'<circle cx="{x + 12}" cy="{yy - 5}" r="11" class="fred"/>' + T(x + 12, yy, str(k + 1), 'l sm b red', 'middle') + T(x + 32, yy, o, 'l')
    b += TL(x, 498, ['Plan: general to particular,', 'head to foot (Hahnemann).', 'Desires, aversions, thirst: Stomach.', 'Food aggravations: Generalities.'], 'n sm', 18)
    b += T(x, 590, 'Remedy names on the page are placeholders.', 'n sm')
    alt = "A mock page of Kent's Repertory: the chapter heading MIND, a rubric in red with remedies printed in three typefaces (bold = 3 marks, italic = 2, roman = 1), and sub-rubrics in the fixed order side, time (morning to midnight), conditions or modalities, extension, location and character; the book runs general to particular, Mind first and Generalities last, with desires, aversions and thirst in Stomach and food aggravations in Generalities."
    return plate(W, H, "Kent's Repertory: how a page works", 'Grades by typeface; sub-rubrics in a fixed order', b, alt), alt


def cards():
    W, H = 760, 500
    b = ''
    holes = [{1, 3, 4, 7, 9, 12, 14, 16, 18, 21}, {1, 4, 6, 7, 10, 12, 15, 18, 20}, {2, 4, 7, 8, 12, 13, 18, 19, 22}]
    common = holes[0] & holes[1] & holes[2]
    for k, hs in enumerate(holes):
        x0, y0 = 70 + k * 26, 110 + k * 24
        b += f'<rect x="{x0}" y="{y0}" width="300" height="190" rx="10" fill="{["#FCEFD2", "#E8F1FB", "#EAF6EE"][k]}" stroke="#9E927A" stroke-width="1.6"/>'
        b += f'<path d="M{x0 + 276} {y0} l24 24 v-24 z" fill="#F6F1E6" stroke="#9E927A"/>'
        b += T(x0 + 14, y0 + 24, f'Rubric {"ABC"[k]}', 'l sm b', 'start', ' style="fill:#4A3F2A"')
        for i in range(24):
            cx, cy = x0 + 30 + (i % 8) * 34, y0 + 60 + (i // 8) * 40
            if i in hs:
                b += f'<circle cx="{cx}" cy="{cy}" r="8" fill="#2A2A2E"/>'
            else:
                b += f'<circle cx="{cx}" cy="{cy}" r="8" fill="none" stroke="#C9BFA6" stroke-dasharray="2 2"/>'
    # light passing through common holes
    for i in common:
        cx, cy = 70 + 52 + 30 + (i % 8) * 34, 110 + 48 + 60 + (i // 8) * 40
        b += f'<circle cx="{cx}" cy="{cy}" r="9" fill="#FFD84A" stroke="#E3A400" stroke-width="2"/>'
    b += TL(70, 380, ['Hold the stack to the light: it shines only', 'through holes punched in every card.'], 'n sm', 18)
    x = 470
    b += T(x, 112, 'How a card repertory works', 'h')
    b += TL(x, 140, ['One card = one rubric.', 'Every remedy has a fixed,', 'numbered position on every card;', 'a hole is punched where the', 'remedy is in the rubric.'], 'n sm', 18)
    b += f'<circle cx="{x + 10}" cy="250" r="9" fill="#FFD84A" stroke="#E3A400" stroke-width="2"/>' + TL(x + 28, 255, ['Light through every card =', 'remedy common to all rubrics'], 'l sm', 18)
    b += T(x, 316, 'LIMITS', 'n sm b') + TL(x, 336, ['Ignores grades; one small rubric', 'can wrongly drop the true remedy.'], 'n sm', 18)
    b += T(x, 392, 'NAMES', 'n sm b') + TL(x, 412, ['Guernsey (first, 1888); Field (based', 'on Kent); Boger; Jugal Kishore (India).', 'Marcos Jimenez first graded cards.'], 'n sm', 18)
    alt = 'A card repertory: each card is one rubric and each remedy has a fixed numbered position; holes are punched where the remedy is present; stacking the cards for the chosen rubrics and holding them to the light shows the remedies common to all as holes that pass through every card; it ignores grades and a small rubric can drop the true remedy; Guernsey made the first in 1888.'
    return plate(W, H, 'Card repertory: let the light decide', 'Punched cards, stacked: the light passes only where every rubric agrees', b, alt), alt


FIGS = {'t4-kent-page': kent_page, 't4-cards': cards}
