#!/usr/bin/env python3
"""GPSCavy build: splits content/ into small files the app loads on demand.

Reads   content/data/sets.json, content/notes/*.html, content/playbooks/*.html, content/pdfs/*.pdf
Writes  data/index.json        set list, papers, pdfs (small, precached)
        data/keys.json         per set: answer key, section, level, topic and canonical id per question
        data/sets/<id>.json    one file per set (questions + passages), fetched when a test opens
        data/pool/<sec>.json   per-section question pools for the custom builder
        data/notes/topicN.html cleaned notes, data/playbooks/*.html restyled playbook bodies
        data/search.json       search index (questions, notes headings, sets)
Question ids and set ids are never changed.
"""
import json, os, re, html, hashlib, shutil
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stylize import stylize
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figs'))
import make as figmake
FIGS = {}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(ROOT, 'content')
OUT = os.path.join(ROOT, 'data')

SEC_CODE = {'comp': 'c', 'gram': 'g', 'gk': 'k', 'lr': 'r', 'core': 'o'}
SEC_ORDER = ['comp', 'gram', 'gk', 'lr', 'core']
TOPICS = {
    1: 'Organon and Philosophy', 2: 'Materia Medica', 3: 'Pharmacy', 4: 'Repertory',
    5: 'Anatomy and Physiology', 6: 'Pathology and Diagnostics', 7: 'Practice of Medicine',
    8: 'Obs, Gynae and Paeds', 9: 'Surgery, ENT and Eye', 10: 'Community and Forensic'}
NOTE_TITLES = {1: 'Organon & Philosophy', 2: 'Materia Medica', 3: 'Pharmacy', 4: 'Repertory', 5: 'Anatomy & Physiology', 6: 'Pathology & Diagnostics', 7: 'Practice of Medicine',
               8: 'Obs, Gynae & Paeds', 9: 'Surgery, ENT, Eye & First Aid', 10: 'Community & Forensic'}


def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))


def level_of(qs):
    v = [{'E': 1, 'I': 2, 'H': 3}[q['lvl']] for q in qs if q.get('lvl')]
    if not v:
        return None
    m = sum(v) / len(v)
    return 'easy' if m <= 1.75 else 'intermediate' if m <= 1.95 else 'hard'


def topic_of(s, q):
    if q['sec'] != 'core':
        return None
    m = re.match(r'Topic (\d+)', q['why'])
    if m:
        return int(m.group(1))
    core = (s.get('core') or '').lower()
    if s['id'].startswith('quiz-topic'):
        return int(s['id'][10:])
    if 'repertory' in core:
        return 4
    if 'anatomy' in core:
        return 5
    if 'pathology' in core:
        return 6
    if 'practice of medicine' in core:
        return 7
    if core.startswith('obg'):
        return 8 if q['n'] <= 48 else 9
    if core == 'materia medica':
        return 2
    return None


def norm(t):
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


# ---------------- notes ----------------
def strip_tags(t):
    return html.unescape(re.sub(r'<[^>]+>', ' ', t))


def parse_quiz(topic, src):
    """The practice MCQs at the end of each note, with the answer key, as a set."""
    i = src.find('practice-mcqs')
    if i < 0:
        i = src.find('id="20-practice-mcqs"')
    seg = src[i:]
    items = re.findall(r'<li><p>(.*?)</p></li>', seg, re.S)
    qs = []
    for raw in items:
        t = re.sub(r'\s+', ' ', strip_tags(raw)).strip()
        m = re.match(r'(.*?)\s*\(?([aA])[\).]\s+(.*?)\s+\(?([bB])[\).]\s+(.*?)\s+\(?([cC])[\).]\s+(.*?)\s+\(?([dD])[\).]\s+(.*)$', t)
        if not m:
            continue
        stem = m.group(1).strip()
        opts = [m.group(3).strip(), m.group(5).strip(), m.group(7).strip(), m.group(9).strip()]
        qs.append({'stem': stem, 'opts': opts})
    # keys: table rows  <tr><td>1</td><td>b</td><td>why</td></tr>   or  "1 B · 2 B ..."
    keys = {}
    for n, a, why in re.findall(r'<tr><td>(\d+)</td><td>([a-dA-D])</td><td>(.*?)</td></tr>', seg, re.S):
        keys[int(n)] = (a.upper(), strip_tags(why).strip())
    if not keys:
        m = re.search(r'Answer key:</strong>(.*?)</p>', seg, re.S)
        for n, a in re.findall(r'(\d+)\s+([A-D])', strip_tags(m.group(1))):
            keys[int(n)] = (a, '')
        tricky = re.search(r'Why the tricky ones:</strong>(.*?)</p>', seg, re.S)
        if tricky:
            for n, why in re.findall(r'Q(\d+),\s*([^.]*\.)', strip_tags(tricky.group(1))):
                if int(n) in keys:
                    keys[int(n)] = (keys[int(n)][0], why.strip())
    out = []
    for k, q in enumerate(qs, 1):
        if k not in keys:
            continue
        a, why = keys[k]
        out.append({'n': len(out) + 1, 'sec': 'core', 'q': q['stem'], 'opts': q['opts'], 'ans': a,
                    'why': why or ('Answer ' + a + ': ' + q['opts']['ABCD'.index(a)] + '.')})
    return out


def expand_figs(src):
    """<figure class="illus" data-fig="ID"><figcaption>..</figcaption></figure> -> a lazy, zoomable picture."""
    def rep(m):
        fid, cap = m.group(1), m.group(2)
        f = FIGS[fid]
        f['used'] = True
        return ('<figure class="illus"><button type="button" class="zoom" aria-label="Enlarge picture">'
                '<img src="data/figs/%s.svg?v=%s" width="%d" height="%d" alt="%s" loading="lazy" decoding="async"></button>'
                '<figcaption>%s</figcaption></figure>') % (fid, f['v'], f['w'], f['h'], html.escape(f['alt']), cap)
    return re.sub(r'<figure class="illus" data-fig="([\w-]+)"><figcaption>(.*?)</figcaption></figure>', rep, src, flags=re.S)


def slim_svg(src):
    """Drop editor-only attributes from the inline diagrams: they are never used by the app."""
    src = re.sub(r' data-claude-[a-z-]+="[^"]*"', '', src)
    return src


def clean_note(topic, src):
    src = re.sub(r'<h1[^>]*>.*?</h1>\s*', '', src, count=1, flags=re.S)
    src = expand_figs(slim_svg(src))
    # the byline with an internal user mention and an atom date
    src = re.sub(r'<p>[^<]*<time data-atom[^>]*>[^<]*</time>\s*·\s*<span data-atom="mention"[^>]*>[^<]*</span></p>\s*', '', src, count=1)
    src = re.sub(r'<span data-atom="mention"[^>]*>[^<]*</span>', '', src)
    src = re.sub(r'<table>', '<div class="tw"><table>', src)
    src = re.sub(r'</table>', '</table></div>', src)
    # the two LaTeX formulas in topic 5, written out so they read on a phone
    src = src.replace('<pre><code class="language-latex">C = \\frac{U \\times V}{P}</code></pre>', '<p class="formula">C = (U × V) ÷ P</p>')
    src = src.replace('<pre><code class="language-latex">pH = 6.1 + \\log \\frac{[HCO_3^-]}{0.03 \\times PaCO_2}</code></pre>', '<p class="formula">pH = 6.1 + log ( [HCO₃⁻] ÷ (0.03 × PaCO₂) )</p>')
    assert 'language-latex' not in src
    # split into h2 sections
    parts = re.split(r'(?=<h2 id=")', src)
    head, secs = parts[0], parts[1:]
    toc = []
    body = []
    if head.strip():
        body.append('<div class="nintro">' + head + '</div>')
    for si, p in enumerate(secs):
        m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>', p, re.S)
        sid, title = m.group(1), strip_tags(m.group(2)).strip()
        rest = p[m.end():]
        if 'practice-mcqs' not in sid:
            rest = stylize(rest, seed=si)
        short = title
        mm = re.match(r'(\d+\.\d+)\s', title)
        if mm:
            short = title
        toc.append([sid, short])
        body.append('<section class="ns" id="' + sid + '"><h2><button type="button" class="nh" aria-expanded="true" data-ns="' + sid + '">' +
                    badge(title) + '</button></h2><div class="nb">' + rest + '</div></section>')
    diagrams = src.count('<figure class="diagram"')
    pics = src.count('<figure class="illus"')
    return '\n'.join(body), toc, (diagrams, pics)


def badge(title):
    m = re.match(r'(\d+\.\d+)\s+(.*)', title)
    if m:
        return '<span class="nnum">' + m.group(1) + '</span><span>' + html.escape(m.group(2)) + '</span>'
    return html.escape(title)


def note_topics():
    ts = [t for t in range(1, 11) if os.path.exists(os.path.join(C, 'notes', 'topic%d.html' % t))]
    core = open(os.path.join(ROOT, 'js', 'core.js'), encoding='utf-8').read()
    assert 'NOTE_TOPICS = [' + ', '.join(map(str, ts)) + '];' in core, 'update NOTE_TOPICS in js/core.js to %s' % ts
    return ts
    return [t for t in range(1, 11) if os.path.exists(os.path.join(C, 'notes', 'topic%d.html' % t))]


def build_notes(index):
    FIGS.update(figmake.build())
    notes = []
    search = []
    quizzes = []
    for t in note_topics():
        src = open(os.path.join(C, 'notes', 'topic%d.html' % t), encoding='utf-8').read()
        quiz = parse_quiz(t, src)
        body, toc, (diag, pics) = clean_note(t, src)
        words = len(strip_tags(body).split())
        os.makedirs(os.path.join(OUT, 'notes'), exist_ok=True)
        open(os.path.join(OUT, 'notes', 'topic%d.html' % t), 'w', encoding='utf-8').write(body)
        notes.append({'t': t, 'title': NOTE_TITLES[t], 'toc': toc, 'diagrams': diag, 'pics': pics, 'min': max(5, round(words / 200)), 'quiz': len(quiz)})
        # search: every h2/h3 heading with a little text after it
        for m in re.finditer(r'<h([23]) id="([^"]+)">(.*?)</h\1>(.*?)(?=<h[23] id=|$)', src, re.S):
            txt = re.sub(r'\s+', ' ', strip_tags(m.group(4))).strip()
            search.append(['n', t, m.group(2), strip_tags(m.group(3)).strip(), txt[:600]])
        sid = 'quiz-topic%d' % t
        quizzes.append({'id': sid, 'set': 'Topic %d quiz · %s' % (t, NOTE_TITLES[t]), 'minutes': max(10, round(len(quiz) * 0.75)),
                        'sections': [{'id': 'core', 'name': 'Core: Topic %d' % t, 'short': 'Topic %d' % t, 'marks': len(quiz)}],
                        'passages': {}, 'questions': quiz, 'quiz': t, 'core': NOTE_TITLES[t]})
        assert len(quiz) >= 20, (t, len(quiz))
    return notes, search, quizzes


# ---------------- playbooks ----------------
def build_playbooks():
    out = {}
    for name in ['gk-playbook', 'english-playbook']:
        src = open(os.path.join(C, 'playbooks', name + '.html'), encoding='utf-8').read()
        a = src.find('<div class="wrap" id="top">')
        b = src.rfind('<script>')
        body = src[a:b]
        body = re.sub(r'^<div class="wrap" id="top">', '', body).strip()
        if body.endswith('</div>'):
            body = body[:-6]
        body = re.sub(r'<table>', '<div class="tw"><table>', body)
        body = body.replace('<div class="tbl"><div class="tw"><table>', '<div class="tbl"><table>')
        body = re.sub(r'(<div class="tbl"><table>.*?</table>)</div>', r'\1', body, flags=re.S)
        secs = [(m.group(1), re.search(r'<h2[^>]*>(.*?)</h2>', body[m.end():], re.S).group(1)) for m in re.finditer(r'<section id="([^"]+)">', body)]
        os.makedirs(os.path.join(OUT, 'playbooks'), exist_ok=True)
        open(os.path.join(OUT, 'playbooks', name + '.html'), 'w', encoding='utf-8').write(body)
        out[name] = [[i, strip_tags(t).strip()] for i, t in secs]
    return out


# ---------------- sets ----------------
def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    data = json.load(open(os.path.join(C, 'data', 'sets.json'), encoding='utf-8'))
    sets = data['sets']
    notes, nsearch, quizzes = build_notes(None)

    # comprehension passage drills from the practice sets: 5 passages (25 Q) each
    practice = [s for s in sets if not s.get('hidden') and not s.get('drill') and not s.get('lvlset')]
    pas = []
    seen = set()
    for s in practice:
        for pid, p in s['passages'].items():
            key = norm(' '.join(p['paras']))[:200]
            if key in seen:
                continue
            seen.add(key)
            qs = [q for q in s['questions'] if q.get('passage') == pid]
            pas.append((s, pid, p, qs))
    compd = []
    for i in range(0, len(pas) // 5 * 5, 5):
        grp = pas[i:i + 5]
        k = i // 5 + 1
        qs, passages, refs = [], {}, []
        for j, (s, pid, p, pq) in enumerate(grp, 1):
            np_ = 'p%d' % j
            passages[np_] = {'title': 'Passage %d' % j, 'paras': p['paras']}
            for q in pq:
                nq = dict(q)
                nq['n'] = len(qs) + 1
                nq['passage'] = np_
                qs.append(nq)
                refs.append(s['id'] + ':' + str(q['n']))
        names = ', '.join(sorted(set(g[0]['set'].replace('Practice Set ', 'Set ') for g in grp), key=lambda x: int(x.split()[1])))
        compd.append({'id': 'compd%d' % k, 'set': 'Passage drill %d' % k, 'short': 'Passages from ' + names, 'core': 'Passages from ' + names,
                      'minutes': 25, 'drill': True, 'group': 'comp', 'derived': True,
                      'sections': [{'id': 'comp', 'name': 'English (Comprehension)', 'short': 'Comprehension', 'marks': len(qs)}],
                      'passages': passages, 'questions': qs, 'refs': refs})

    allsets = sets + compd + quizzes

    # canonical question ids (dedupe by text + options) so a question repeated in a level test counts once
    canon = {}
    canon_src = []
    def canon_id(s, q):
        k = hashlib.md5((norm(q['q']) + '|' + norm(' '.join(q['opts']))).encode()).hexdigest()[:12]
        if k not in canon:
            canon[k] = len(canon)
            canon_src.append(s['id'] + ':' + str(q['n']))
        return canon[k]

    keys = {}
    order = sorted(allsets, key=lambda s: (1 if s.get('hidden') else 0))
    for s in order:
        toks, cids = [], []
        for q in s['questions']:
            t = topic_of(s, q)
            toks.append(SEC_CODE[q['sec']] + q['ans'] + (q.get('lvl') or '-') + ('-' if t is None else 'a' if t == 10 else str(t)))
            cids.append(canon_id(s, q))
        keys[s['id']] = {'k': ''.join(toks), 'c': cids}

    # index
    idx = []
    for s in allsets:
        secs = ','.join(sec['id'] + ':' + str(sum(1 for q in s['questions'] if q['sec'] == sec['id'])) for sec in s['sections'])
        e = {'id': s['id'], 'name': s['set'], 'min': s['minutes'], 'n': len(s['questions']), 'secs': secs}
        lv = s.get('lvlset') or level_of(s['questions'])
        if lv:
            e['level'] = lv
        mix = {'E': 0, 'I': 0, 'H': 0}
        for q in s['questions']:
            if q.get('lvl'):
                mix[q['lvl']] += 1
        if sum(mix.values()):
            e['mix'] = mix
        for k in ['core', 'drill', 'group', 'short', 'lvlset', 'hidden', 'quiz', 'derived']:
            if s.get(k):
                e[k] = s[k]
        if s.get('hidden'):
            e = {'id': s['id'], 'name': s['set'], 'hidden': 1}
        if e.get('core') == e.get('short'):
            e.pop('short', None)
        if e.get('drill'):
            e['drill'] = 1
        if s['id'].startswith('set') and not s.get('hidden'):
            e['num'] = int(re.match(r'Practice Set (\d+)', s['set']).group(1))
        idx.append(e)
        out = {k: v for k, v in s.items() if k in ('id', 'set', 'minutes', 'sections', 'passages', 'questions', 'refs', 'core', 'level', 'drill', 'group', 'short', 'lvlset', 'mix', 'hidden', 'quiz')}
        for q in out['questions']:
            t = topic_of(s, q)
            if t:
                q['topic'] = t
        wjson(os.path.join(OUT, 'sets', s['id'] + '.json'), out)

    # pools for the custom builder (non-hidden, deduped, practice sets first)
    pools = {k: {'q': [], 'p': {}} for k in SEC_ORDER}
    used = set()
    src_sets = [s for s in allsets if not s.get('hidden') and not s.get('derived') and not s.get('quiz')] + quizzes
    for s in src_sets:
        for q in s['questions']:
            cid = keys[s['id']]['c'][q['n'] - 1]
            if cid in used:
                continue
            used.add(cid)
            pk = None
            if q.get('passage'):
                pk = s['id'] + ':' + q['passage']
                if pk not in pools['comp']['p']:
                    p = s['passages'][q['passage']]
                    pools['comp']['p'][pk] = {'title': p['title'], 'paras': p['paras']}
            t = topic_of(s, q)
            pools[q['sec']]['q'].append([s['id'] + ':' + str(q['n']), q.get('lvl') or '', t or 0, q['q'], q['opts'], q['ans'], q['why'], pk or '', cid])
    for k, v in pools.items():
        wjson(os.path.join(OUT, 'pool', k + '.json'), v)
    pool_counts = {}
    for k, v in pools.items():
        c = {'all': len(v['q']), 'E': 0, 'I': 0, 'H': 0, 'topics': {}}
        for r in v['q']:
            if r[1]:
                c[r[1]] += 1
            if r[2]:
                c['topics'][str(r[2])] = c['topics'].get(str(r[2]), 0) + 1
        pool_counts[k] = c

    # pdfs
    pdfs = []
    for f in sorted(os.listdir(os.path.join(C, 'pdfs'))):
        if not f.endswith('.pdf'):
            continue
        kb = round(os.path.getsize(os.path.join(C, 'pdfs', f)) / 1024)
        m = re.match(r'GPSC-CBRT-Practice-Set-(\d+)\.pdf', f)
        if m:
            pdfs.append({'f': f, 'name': 'Practice Set ' + m.group(1), 'kind': 'set', 'num': int(m.group(1)), 'kb': kb})
        elif 'Sets-1-to-25' in f:
            pdfs.append({'f': f, 'name': 'Practice Sets 1 to 25 (all in one)', 'kind': 'all', 'kb': kb})
        elif 'Level-Tests' in f:
            pdfs.append({'f': f, 'name': 'Level tests: Easy, Intermediate, Hard', 'kind': 'lvl', 'kb': kb})
        elif 'GK-Drills' in f:
            pdfs.append({'f': f, 'name': 'GK drills 1 to 6', 'kind': 'gk', 'kb': kb})
        elif 'English-Drills' in f:
            pdfs.append({'f': f, 'name': 'English drills 1 to 4', 'kind': 'en', 'kb': kb})
        elif 'Topic-8' in f:
            pdfs.append({'f': f, 'name': 'Topic 8 notes: Obs, Gynae & Paeds', 'kind': 'topic', 'topic': 8, 'kb': kb})
        else:
            pdfs.append({'f': f, 'name': f[:-4].replace('-', ' '), 'kind': 'other', 'kb': kb})
    pdfs.sort(key=lambda p: ({'all': 0, 'set': 1, 'lvl': 2, 'gk': 3, 'en': 4, 'topic': 5}.get(p['kind'], 9), p.get('num', 0)))

    playbooks = build_playbooks()

    wjson(os.path.join(OUT, 'index.json'), {'v': 1, 'sets': idx})
    wjson(os.path.join(OUT, 'meta.json'), {'papers': data['papers'], 'pdfs': pdfs, 'notes': notes,
                                            'playbooks': playbooks, 'pools': pool_counts, 'topics': TOPICS})
    wjson(os.path.join(OUT, 'keys.json'), keys)

    # search: questions (canonical only), note headings, sets
    sq = []
    for s in src_sets:
        for q in s['questions']:
            if canon_src[keys[s['id']]['c'][q['n'] - 1]] == s['id'] + ':' + str(q['n']):
                sq.append(['q', s['id'], q['n'], q['q'], q['opts']['ABCDE'.index(q['ans'])] if q['ans'] != 'E' else 'None of the above', q['why'], q['sec']])
    wjson(os.path.join(OUT, 'search.json'), {'q': sq, 'n': nsearch})

    sizes = {f: os.path.getsize(os.path.join(OUT, f)) for f in ['index.json', 'meta.json', 'keys.json', 'search.json']}
    print('sets', len(allsets), 'compd', len(compd), 'quizzes', [len(q['questions']) for q in quizzes])
    print('sizes', sizes, 'pools', {k: len(v['q']) for k, v in pools.items()}, 'canon', len(canon))
    unused = [k for k, f in FIGS.items() if not f.get('used')]
    assert not unused, 'pictures not placed in any notes: %s' % unused
    print('diagrams', sum(n['diagrams'] for n in notes), 'pictures', sum(n['pics'] for n in notes), 'playbook secs', playbooks)


def stamp_sw():
    h = hashlib.sha1()
    for d in ['index.html', 'manifest.webmanifest', 'js', 'data', 'fonts', 'icons']:
        p = os.path.join(ROOT, d)
        files = [p] if os.path.isfile(p) else sorted(os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs)
        for f in files:
            h.update(f.encode()); h.update(open(f, 'rb').read())
    v = 'gpscavy-' + h.hexdigest()[:10]
    sw = os.path.join(ROOT, 'sw.js')
    s = open(sw, encoding='utf-8').read()
    s = re.sub(r"const V = '[^']*';", "const V = '" + v + "';", s, count=1)
    open(sw, 'w', encoding='utf-8').write(s)
    print('sw', v)


if __name__ == '__main__':
    main()
    stamp_sw()
