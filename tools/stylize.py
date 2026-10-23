"""Style A for notes: cards, highlights, pills, callouts. Rearranges markup only; the text is never changed."""
import re

BULB = '<span class="ico" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M9 18h6M10 22h4"/><path d="M12 2a7 7 0 00-4 12.7V16h8v-1.3A7 7 0 0012 2z"/></svg></span>'
WARN = '<span class="ico" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M12 8v5M12 17h.01"/><path d="M10.3 3.9L2.4 18a2 2 0 001.7 3h15.8a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/></svg></span>'
STAR = '<span class="ico" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linejoin="round"><path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/></svg></span>'

ABBR = {'e.g', 'i.e', 'dr', 'vs', 'st', 'mr', 'mrs', 'no', 'fig', 'approx', 'viz', 'etc', 'cf', 'al', 'ed', 'vol', 'sr', 'jr', 'rs', 'op', 'resp', 'ca', 'carb', 'phos', 'sulph', 'mur', 'tart', 'met', 'nit', 'ac', 'ars', 'calc', 'nat', 'kali', 'merc', 'sol', 'iod', 'alb', 'perf', 'tig', 'crud', 'mag', 'ammon', 'arg', 'bar', 'ferr', 'hep', 'ign', 'puls', 'sep', 'sil', 'lyc', 'bell', 'bry', 'acon', 'apis', 'rhus', 'tox', 'nux', 'v', 'aur', 'ant', 'cham', 'chin', 'coloc', 'gels', 'ipec', 'staph', 'stram', 'verat', 'hyos', 'lach', 'thuj', 'med', 'psor', 'tub', 'bac', 'syph', 'm', 'mm', 'c', 'x', 'lm', 'p', 'pp', 'cap', 'ch', 'sec'}


def blocks(h):
    """Split HTML into top-level elements."""
    out, i, n = [], 0, len(h)
    while i < n:
        while i < n and h[i].isspace():
            i += 1
        if i >= n:
            break
        m = re.match(r'<([a-zA-Z0-9]+)\b[^>]*?(/?)>', h[i:])
        if not m:
            j = h.find('<', i + 1)
            j = n if j < 0 else j
            out.append(h[i:j]); i = j; continue
        tag = m.group(1).lower()
        if m.group(2) == '/' or tag in ('br', 'hr', 'img'):
            out.append(h[i:i + m.end()]); i += m.end(); continue
        depth, k = 0, i
        pat = re.compile(r'<(/?)%s\b[^>]*>' % tag, re.I)
        for mm in pat.finditer(h, i):
            depth += -1 if mm.group(1) else 1
            if depth == 0:
                k = mm.end(); break
        else:
            raise ValueError('unbalanced ' + tag)
        out.append(h[i:k]); i = k
    return out


def text_of(h):
    t = re.sub(r'<svg\b.*?</svg>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return ' '.join(t.split())


def balanced(s):
    for t in ('strong', 'em', 'a', 'code', 'sub', 'sup', 'span'):
        if len(re.findall(r'<%s\b' % t, s)) != len(re.findall(r'</%s>' % t, s)):
            return False
    return True


def sentences(inner):
    """Split paragraph HTML at sentence ends outside tags; None if unsafe."""
    cuts, intag = [], False
    for i, ch in enumerate(inner):
        if ch == '<': intag = True
        elif ch == '>': intag = False
        elif not intag and ch in '.?!' and inner[i + 1:i + 2] == ' ':
            nxt = inner[i + 2:i + 3]
            if not (nxt.isupper() or nxt.isdigit() or nxt in '<("§\''):
                continue
            w = re.search(r'([A-Za-z.\-]+)$', re.sub(r'<[^>]+>', '', inner[:i]))
            word = (w.group(1) if w else '').lower().strip('.')
            if word in ABBR or len(word) == 1:
                continue
            # keep a closing tag that sits right after the stop with the sentence
            cuts.append(i + 1)
    parts, last = [], 0
    for c in cuts:
        parts.append(inner[last:c].strip()); last = c
    parts.append(inner[last:].strip())
    parts = [p for p in parts if p]
    if len(parts) < 3 or not all(balanced(p) for p in parts):
        return None
    return parts


PILL = re.compile(r'[§¶#]?[\d][\d\s.,:%–\-/×x·+<>≥≤°]*[A-Za-z%°]{0,3}\.?')


def label_tables(h):
    """Give each body cell its column heading, so narrow screens can stack rows as cards."""
    def one(m):
        t = m.group(0)
        heads = [re.sub(r'<[^>]+>', '', x).strip() for x in re.findall(r'<th[^>]*>(.*?)</th>', t, re.S)]
        if not heads:
            return t
        def row(r):
            i = [0]
            def cell(c):
                k = i[0]; i[0] += 1
                lab = heads[k] if k < len(heads) else ''
                return '<td data-label="' + lab.replace('"', '&quot;') + '"' + c.group(1)
            return re.sub(r'<td(\b[^>]*)?', lambda c: cell(c) if True else c.group(0), r.group(0).replace('<td>', '<td >'))
        t = re.sub(r'<tbody>.*?</tbody>', lambda b: re.sub(r'<tr>.*?</tr>', row, b.group(0), flags=re.S), t, flags=re.S)
        return t.replace('<table>', '<table class="stk">', 1)
    return re.sub(r'<table>.*?</table>', one, h, flags=re.S)


def inline(h):
    def pill(m):
        t = m.group(1)
        if len(t) <= 14 and PILL.fullmatch(re.sub(r'&[a-z]+;', '', t).strip()):
            return '<strong class="pill">' + t + '</strong>'
        return m.group(0)
    return label_tables(re.sub(r'<strong>([^<]{1,20})</strong>', pill, h))


LABEL = re.compile(r'<p><strong>([^<]{1,80})</strong>')
TRAP = re.compile(r'<p><strong>\s*(Exam trap|Trap|Traps|Pitfall|Caution|Warning|Do not confuse|Common mistake|One key to distrust)', re.I)
TIP = re.compile(r'<p><strong>\s*(Exam tip|Tip|Remember|Note|Mnemonic|Key point|High yield)', re.I)


def para(b):
    """A long <p> becomes points, sentence by sentence."""
    m = re.fullmatch(r'<p>(.*)</p>', b, re.S)
    if not m or len(text_of(b).split()) < 45:
        return b
    parts = sentences(m.group(1))
    if not parts:
        return b
    lead = ''
    if re.fullmatch(r'<strong>[^<]*</strong>', parts[0]):
        lead = '<p class="plead">' + parts.pop(0) + '</p>'
    return lead + '<ul class="pts">' + ''.join('<li>' + p + '</li>' for p in parts) + '</ul>'


def callout(b):
    if b.startswith('<blockquote'):
        inner = re.sub(r'^<blockquote>|</blockquote>$', '', b)
        if re.search(r'Memory hook|Mnemonic', inner, re.I):
            return '<div class="hook">' + BULB + '<div>' + inner + '</div></div>'
        return '<div class="tip">' + STAR + '<div>' + inner + '</div></div>'
    if TRAP.match(b):
        return '<div class="trap">' + WARN + '<div>' + para(b) + '</div></div>'
    if TIP.match(b):
        return '<div class="tip">' + STAR + '<div>' + para(b) + '</div></div>'
    return None


def stylize(rest, seed=0):
    bl = blocks(rest)
    has_h3 = any(b.startswith('<h3') for b in bl)
    out, card, k, n = [], None, seed, 0
    lead = []

    def close():
        nonlocal card
        if card is not None:
            out.append('<div class="nc k%d">%s</div>' % (card[0], ''.join(card[1])))
            card = None

    for b in bl:
        c = callout(b)
        if c and c.startswith('<div class="hook">'):
            close()
            (out if out or not lead else lead).append(c)
            continue
        starts = b.startswith('<h3') or (not has_h3 and LABEL.match(b) and not c)
        if starts:
            close()
            if lead:
                out.append('<div class="nlead">' + ''.join(lead) + '</div>'); lead = []
            card = (k % 6 + 1, []); k += 1; n += 1
        piece = c or (para(b) if b.startswith('<p>') else b)
        piece = inline(piece)
        if card is None:
            if out:
                out.append(piece)
            else:
                lead.append(piece)
        else:
            card[1].append(piece)
    close()
    if lead:
        out.insert(0, '<div class="nlead">' + ''.join(lead) + '</div>')
    res = ''.join(out)
    assert text_of(res).replace(' ', '') == text_of(rest).replace(' ', ''), 'text changed'
    return res
