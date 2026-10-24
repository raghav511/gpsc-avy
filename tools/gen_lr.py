#!/usr/bin/env python3
"""Logical reasoning questions with computed (not guessed) answers, in the GPSC CBRT style.

  python3 tools/gen_lr.py OUT.json [count_easy count_intermediate count_hard]

Every answer is worked out by the code that writes the question, so it is right by construction; the explanation shows
the working. Distractors are near misses. Seeded, so the same command gives the same questions.
"""
import datetime, itertools, json, math, random, string, sys
from fractions import Fraction

R = random.Random(20261024)
L = string.ascii_uppercase
NAMES = ['Ravi', 'Meera', 'Anil', 'Sita', 'Kiran', 'Pooja', 'Rahul', 'Neha', 'Vijay', 'Asha', 'Suresh', 'Priya', 'Manoj', 'Kavita', 'Deepak', 'Rekha', 'Ajay', 'Lata', 'Sunil', 'Geeta']
WORDS = ['PATIENT', 'REMEDY', 'DOCTOR', 'NURSING', 'HEALTH', 'MEDICAL', 'CLINIC', 'POTENCY', 'TABLET', 'SYMPTOM', 'GARDEN', 'FOREST', 'MARKET', 'WINTER', 'SUMMER', 'PLANET', 'SCHOOL', 'BRIDGE', 'CANDLE', 'FLOWER', 'KNIGHT', 'MOTHER', 'SILVER', 'TEMPLE', 'VILLAGE', 'HOSPITAL', 'COUNTRY', 'PENCIL']


def opts_from(correct, wrong):
    """four options: the answer and three distinct wrong ones, shuffled; returns (opts, letter)"""
    w = []
    for x in wrong:
        if str(x) != str(correct) and str(x) not in map(str, w):
            w.append(x)
        if len(w) == 3:
            break
    assert len(w) == 3, (correct, wrong)
    o = [correct] + w
    R.shuffle(o)
    return [str(x) for x in o], 'ABCD'[o.index(correct)]


def near(n, spread=(1, 2, 3, 4, 5, 6)):
    c = [n + d for d in spread] + [n - d for d in spread]
    R.shuffle(c)
    return [x for x in c if x > 0]


Q = []


def add(lvl, typ, q, correct, wrong, why):
    o, a = opts_from(correct, wrong)
    Q.append({'q': q, 'opts': o, 'ans': a, 'why': why + ' GPSC-style practice item.', 'lvl': lvl, 'type': typ, 'src': ''})


# ---------- number series ----------
def series(lvl):
    k = R.choice({'E': ['ap', 'gp', 'sq'], 'I': ['sq+', 'diff2', 'alt', 'mulsub'], 'H': ['diff2', 'alt', 'fib', 'cube-', 'mulsub2']}[lvl])
    if k == 'ap':
        a, d = R.randint(2, 40), R.randint(3, 15); s = [a + i * d for i in range(6)]; why = 'Each term adds %d.' % d
    elif k == 'gp':
        a, r = R.randint(2, 7), R.choice([2, 3]); s = [a * r ** i for i in range(6)]; why = 'Each term is multiplied by %d.' % r
    elif k == 'sq':
        b = R.randint(2, 6); s = [(b + i) ** 2 for i in range(6)]; why = 'Squares of %d, %d, %d, ….' % (b, b + 1, b + 2)
    elif k == 'sq+':
        b, c = R.randint(1, 5), R.choice([1, -1, 2, 3]); s = [(b + i) ** 2 + c for i in range(6)]; why = 'n² %s %d for n = %d, %d, ….' % ('+' if c > 0 else '−', abs(c), b, b + 1)
    elif k == 'cube-':
        b, c = R.randint(1, 4), R.choice([1, 2, -1]); s = [(b + i) ** 3 - c for i in range(6)]; why = 'n³ %s %d for n = %d, %d, ….' % ('−' if c > 0 else '+', abs(c), b, b + 1)
    elif k == 'diff2':
        a, d, e = R.randint(2, 20), R.randint(2, 6), R.randint(1, 4); s = [a]; dd = d
        for i in range(5):
            s.append(s[-1] + dd); dd += e
        why = 'The differences go up by %d each time (%s).' % (e, ', '.join(str(s[i + 1] - s[i]) for i in range(5)))
    elif k == 'alt':
        a, d1, d2 = R.randint(5, 30), R.randint(3, 9), R.randint(1, 5); s = [a]
        for i in range(5):
            s.append(s[-1] + (d1 if i % 2 == 0 else -d2))
        why = 'Alternately add %d and subtract %d.' % (d1, d2)
    elif k == 'mulsub':
        a, m = R.randint(3, 6), 2; c = R.randint(1, a - 2); s = [a]
        for i in range(5):
            s.append(s[-1] * m - c)
        why = 'Each term is ×%d − %d.' % (m, c)
    elif k == 'mulsub2':
        a, c = R.randint(2, 5), R.randint(1, 3); s = [a]
        for i in range(5):
            s.append(s[-1] * (i + 2) - c)
        why = 'Multiply by 2, 3, 4, … and subtract %d each time.' % c
    else:  # fib
        a, b = R.randint(1, 5), R.randint(2, 7); s = [a, b]
        while len(s) < 6:
            s.append(s[-1] + s[-2])
        why = 'Each term is the sum of the two before it.'
    ans = s[-1]
    add(lvl, 'number-series', 'What comes next in the series? ' + ', '.join(map(str, s[:-1])) + ', …', ans, near(ans, (1, 2, 3, 4, 6, 8, 10)), why + ' Next: %d.' % ans)


def wrong_number(lvl):
    a, d = R.randint(10, 60), R.randint(4, 13)
    s = [a + i * d * (i + 1) // 2 if lvl == 'H' else a + i * d for i in range(7)]
    i = R.randint(2, 5); bad = s[i] + R.choice([-3, -2, 2, 3, 5])
    t = s[:]; t[i] = bad
    rule = 'the differences increase by %d each time' % d if lvl == 'H' else 'each term adds %d' % d
    add(lvl, 'wrong-number', 'Find the wrong number in the series: ' + ', '.join(map(str, t)), bad, [t[1], t[i - 1], t[i + 1], t[-1], t[0]], 'In the correct series %s, so %d should be %d.' % (rule, bad, s[i]))


# ---------- letters and codes ----------
def shift(word, k):
    return ''.join(L[(L.index(c) + k) % 26] for c in word)


def coding(lvl):
    w1, w2 = R.sample(WORDS, 2)
    if lvl == 'E':
        k = R.choice([1, 2, 3]); c1, c2 = shift(w1, k), shift(w2, k); rule = 'each letter moves %d place%s forward' % (k, '' if k == 1 else 's')
    elif lvl == 'I':
        k = R.choice([1, 2]); c1, c2 = shift(w1, k)[::-1], shift(w2, k)[::-1]; rule = 'each letter moves %d place%s forward and the word is then reversed' % (k, '' if k == 1 else 's')
    else:
        f = lambda w: ''.join(shift(c, i + 1) for i, c in enumerate(w)); c1, c2 = f(w1), f(w2); rule = 'the 1st letter moves 1 place, the 2nd 2 places, the 3rd 3 places, and so on'
    wrong = [shift(w2, 1), shift(w2, 2)[::-1], c2[:-1] + shift(c2[-1], 1), c2[1:] + c2[0], shift(c2, 1), c2[::-1]]
    add(lvl, 'coding', 'If %s is written as %s in a certain code, how is %s written in that code?' % (w1, c1, w2), c2, wrong, 'In the code %s: %s → %s.' % (rule, w2, c2))


def letter_series(lvl):
    d = R.choice([2, 3]) if lvl == 'E' else R.choice([3, 4, 5]); a = R.randint(0, 26 - 4 * d - (3 if lvl != 'H' else 5))  # no wrapping past Z
    grp = lambda i: ''.join(L[(a + i * d + j * (1 if lvl != 'H' else 2)) % 26] for j in range(3))
    s = [grp(i) for i in range(5)]
    ans = s[-1]
    wrong = [ans[0] + ans[2] + ans[1], shift(ans, 1), shift(ans, -1), ans[::-1], shift(ans, 2)]
    add(lvl, 'letter-series', 'What comes next? ' + ', '.join(s[:-1]) + ', …', ans, wrong, 'Each group starts %d letters after the last one, with the same pattern inside: %s.' % (d, ans))


def odd_letters(lvl):
    d = R.choice([2, 3])
    good = []
    while len(good) < 3:
        a = R.randint(0, 26 - 2 * d - 1); g = L[a] + L[a + d] + L[a + 2 * d]
        if g not in good:
            good.append(g)
    a = R.randint(0, 26 - 2 * d - 2); bad = L[a] + L[a + d] + L[a + 2 * d + 1]
    add(lvl, 'odd-one-out', 'Find the odd one out:', bad, good + [L[:3]], 'In the others each letter is %d after the one before; in %s the last step is %d.' % (d, bad, d + 1))


# ---------- order, direction, time ----------
def ranking(lvl):
    a, b = R.randint(5, 25), R.randint(5, 25)
    if lvl == 'E':
        n = a + b - 1
        add(lvl, 'ranking', '%s is %s from the top and %s from the bottom in a class. How many students are in the class?' % (R.choice(NAMES), ordn(a), ordn(b)), n, [n + 1, n - 1, n + 2, a + b], 'Total = %d + %d − 1 = %d.' % (a, b, n))
    else:
        n = a + b + R.randint(8, 20); x, y = R.sample(NAMES, 2); g = n - a - b
        add(lvl, 'ranking', 'In a row of %d students, %s is %s from the left and %s is %s from the right. How many students sit between them?' % (n, x, ordn(a), y, ordn(b)), g, [g + 1, g - 1, g + 2, n - a - b + 2], 'Between them = %d − (%d + %d) = %d.' % (n, a, b, g))


def ordn(n):
    return '%d%s' % (n, 'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


DIRS = ['North', 'East', 'South', 'West']


def direction(lvl):
    trip = R.choice([(3, 4), (6, 8), (5, 12), (9, 12), (8, 15)])
    name = R.choice(NAMES)
    if lvl == 'E':
        a, b = trip; d1 = R.choice(DIRS); turn = R.choice(['right', 'left'])
        d2 = DIRS[(DIRS.index(d1) + (1 if turn == 'right' else -1)) % 4]
        dist = int(math.hypot(a, b))
        add(lvl, 'direction', '%s walks %d km %s, then turns %s and walks %d km. How far is %s from the starting point?' % (name, a, d1, turn, b, name), '%d km' % dist, ['%d km' % (a + b), '%d km' % abs(a - b), '%d km' % (dist + 1), '%d km' % (dist + 2)], 'The two legs are at right angles: √(%d² + %d²) = %d km.' % (a, b, dist))
    else:
        x = y = 0; d = R.randint(0, 3); legs = []
        for i in range(4 if lvl == 'H' else 3):
            if i:
                t = R.choice(['right', 'left']); d = (d + (1 if t == 'right' else -1)) % 4; legs.append('turns %s and walks' % t)
            else:
                legs.append('walks')
            k = R.randint(2, 9); legs[-1] += ' %d m' % k + (' %s' % DIRS[d] if i == 0 else '')
            x += [0, 1, 0, -1][d] * k; y += [1, 0, -1, 0][d] * k
        face = DIRS[d]
        add(lvl, 'direction', '%s %s. Which direction is %s facing now?' % (name, ', then '.join(legs), name), face, [z for z in DIRS if z != face] + ['North-East'], 'Follow each turn from the first direction: the last leg is towards the %s.' % face)


def clock(lvl):
    h, m = R.randint(1, 11), R.choice([0, 10, 15, 20, 25, 30, 40, 45, 50]) if lvl != 'H' else R.choice([5, 10, 20, 35, 40, 55])
    ang = abs(Fraction(60 * h - 11 * m, 2))
    if ang > 180:
        ang = 360 - ang
    fmt = lambda x: ('%d' % x if x.denominator == 1 else '%s' % (str(float(x)).rstrip('0').rstrip('.'))) + '°'
    add(lvl, 'clock', 'What is the angle between the hands of a clock at %d:%02d?' % (h, m), fmt(ang), [fmt(ang + 5), fmt(abs(ang - 5)), fmt(ang + Fraction(15, 2)), fmt(abs(360 - ang)), fmt(ang + 10)], 'Angle = |30×%d − 5.5×%d| = %s.' % (h, m, fmt(ang)))


def calendar(lvl):
    y = R.randint(2019, 2027); d1 = datetime.date(y, R.randint(1, 12), R.randint(1, 28))
    gap = R.randint(20, 100) if lvl != 'H' else R.randint(150, 400)
    d2 = d1 + datetime.timedelta(days=gap)
    W = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ans = W[d2.weekday()]
    add(lvl, 'calendar', 'If %s was a %s, what day of the week was %s?' % (d1.strftime('%-d %B %Y'), W[d1.weekday()], d2.strftime('%-d %B %Y')), ans, [w for w in W if w != ans], '%d days later; %d mod 7 = %d, so count %d day%s on from %s.' % (gap, gap, gap % 7, gap % 7, '' if gap % 7 == 1 else 's', W[d1.weekday()]))


# ---------- relations and sets ----------
REL = [  # (template, answer, wrong, level)
    ('{a} is the brother of {b}. {b} is the mother of {c}. How is {a} related to {c}?', 'Maternal uncle', ['Paternal uncle', 'Father', 'Cousin'], 'E'),
    ('{a} is the sister of {b}. {b} is the father of {c}. How is {a} related to {c}?', 'Paternal aunt', ['Maternal aunt', 'Mother', 'Sister'], 'E'),
    ('{a} is the father of {b}. {b} is the son of {c}. {c} is the wife of {a}. How is {c} related to {b}?', 'Mother', ['Sister', 'Aunt', 'Grandmother'], 'E'),
    ('Pointing to a man, {a} said, "His only brother is the father of my daughter." How is the man related to {a}?', 'Brother-in-law', ['Brother', 'Father', 'Uncle'], 'I'),
    ('Pointing to a woman, {a} (a man) said, "She is the daughter of my grandfather\'s only son." How is the woman related to {a}?', 'Sister', ['Cousin', 'Aunt', 'Niece'], 'I'),
    ('{a} is the son of {b}. {c} is the daughter of {b}. {d} is the husband of {c}. How is {d} related to {a}?', 'Brother-in-law', ['Brother', 'Uncle', 'Father-in-law'], 'I'),
    ('{a} is the mother of {b}. {b} is the sister of {c}. {c} is the father of {d}. How is {a} related to {d}?', 'Grandmother', ['Mother', 'Aunt', 'Great-grandmother'], 'I'),
    ('Introducing a man, a woman said, "He is the only son of my mother\'s mother." How is the man related to the woman?', 'Maternal uncle', ['Uncle (father\'s brother)', 'Grandfather', 'Brother'], 'H'),
    ('{a} is the brother of {b}. {c} is the father of {a}. {d} is the brother of {e}. {e} is the daughter of {b}. Who is the uncle of {d}?', '{a}', ['{c}', '{b}', '{e}'], 'H'),
    ('Pointing to a photograph, {a} (a man) said, "Her mother\'s father is the only son of my father." How is the girl in the photograph related to {a}?', 'Granddaughter', ['Daughter', 'Niece', 'Sister'], 'H'),
    ('{a}\'s mother is the only daughter of {b}\'s father. How is {b} related to {a} if {b} is a man?', 'Maternal uncle', ['Father', 'Brother', 'Grandfather'], 'H'),
]


def relation(lvl):
    t, ans, wrong, lv = R.choice([r for r in REL if r[3] == lvl])
    nm = dict(zip('abcde', R.sample(NAMES, 5)))
    f = lambda s: s.format(**nm)
    add(lvl, 'blood-relation', f(t), f(ans), [f(w) for w in wrong] + ['Cousin', 'Nephew'], 'Draw the family tree from the statements; the answer is %s.' % f(ans))


def venn(lvl):
    n = R.randint(4, 12) * 10; a = R.randint(n // 3, n * 2 // 3); b = R.randint(n // 3, n * 2 // 3)
    both = R.randint(max(1, a + b - n + 1), min(a, b) - 1); neither = n - (a + b - both)
    l1, l2 = R.choice([('Konkani', 'Marathi'), ('cricket', 'football'), ('tea', 'coffee'), ('Hindi', 'English'), ('chess', 'carrom')])
    if lvl == 'E':
        add(lvl, 'sets', 'In a group of %d people, %d like %s, %d like %s and %d like both. How many like neither?' % (n, a, l1, b, l2, both), neither, near(neither) + [both], 'Neither = %d − (%d + %d − %d) = %d.' % (n, a, b, both, neither))
    else:
        add(lvl, 'sets', 'In a group of %d people, %d like %s, %d like %s and %d like neither. How many like only %s?' % (n, a, l1, b, l2, neither, l1), a - both, near(a - both) + [both, a], 'Both = %d + %d − (%d − %d) = %d; only %s = %d − %d = %d.' % (a, b, n, neither, both, l1, a, both, a - both))


# ---------- syllogisms, checked against every possible arrangement ----------
def models(premises):
    """every way three sets A, B, C can overlap (8 regions empty or not) that satisfies the premises"""
    out = []
    for bits in itertools.product([0, 1], repeat=8):
        reg = [r for r, on in zip(itertools.product([0, 1], repeat=3), bits) if on]
        if not reg:
            continue
        S = lambda i: [r for r in reg if r[i]]
        if any(not S(i) for i in range(3)):
            continue  # every term names something that exists
        if all(holds(p, reg) for p in premises):
            out.append(reg)
    return out


def holds(p, reg):
    kind, x, y = p
    inx = [r for r in reg if r[x]]
    if kind == 'all':
        return all(r[y] for r in inx)
    if kind == 'no':
        return not any(r[y] for r in inx)
    if kind == 'some':
        return any(r[y] for r in inx)
    if kind == 'somenot':
        return any(not r[y] for r in inx)


def say(p, T):
    k, x, y = p
    return {'all': 'All %s are %s.', 'no': 'No %s are %s.', 'some': 'Some %s are %s.', 'somenot': 'Some %s are not %s.'}[k] % (T[x], T[y])


TERMS = [('doctors', 'teachers', 'singers'), ('pens', 'books', 'bags'), ('roses', 'flowers', 'plants'), ('cats', 'dogs', 'pets'), ('remedies', 'tablets', 'liquids'), ('rivers', 'lakes', 'ponds'), ('chairs', 'tables', 'desks')]


def syllogism(lvl):
    T = R.choice(TERMS)
    for _ in range(200):
        prem = [(R.choice(['all', 'some', 'no']), 0, 1), (R.choice(['all', 'some', 'no']), 1, 2)]
        ms = models(prem)
        cands = [(k, x, y) for k in ['all', 'some', 'no', 'somenot'] for x, y in [(0, 2), (2, 0)]]
        follows = [c for c in cands if all(holds(c, m) for m in ms)]
        notf = [c for c in cands if c not in follows]
        if lvl == 'E' and follows and notf:
            c1, c2 = R.choice(follows), R.choice(notf)
        elif lvl != 'E' and len(follows) >= 1 and len(notf) >= 2:
            c1, c2 = (R.sample(notf, 2) if R.random() < 0.4 else (R.choice(follows), R.choice(notf)))
        else:
            continue
        if R.random() < 0.5:
            c1, c2 = c2, c1
        f1, f2 = c1 in follows, c2 in follows
        ans = 'Both I and II follow' if f1 and f2 else 'Only I follows' if f1 else 'Only II follows' if f2 else 'Neither I nor II follows'
        q = 'Statements: %s %s Conclusions: I. %s II. %s' % (say(prem[0], T), say(prem[1], T), say(c1, T), say(c2, T))
        add(lvl, 'syllogism', q, ans, ['Only I follows', 'Only II follows', 'Neither I nor II follows', 'Both I and II follow'],
            'Checked against every possible diagram of the statements: I %s, II %s.' % ('must be true' if f1 else 'need not be true', 'must be true' if f2 else 'need not be true'))
        return


# ---------- arithmetic reasoning ----------
def ages(lvl):
    a, b = R.randint(2, 6), R.randint(2, 6)
    while a == b:
        b = R.randint(2, 6)
    k = R.randint(3, 8); x, y = a * k, b * k; t = R.randint(2, 10)
    g = math.gcd(x + t, y + t)
    p, q = (x + t) // g, (y + t) // g
    n1, n2 = R.sample(NAMES, 2)
    add(lvl, 'ages', 'The present ages of %s and %s are in the ratio %d : %d. After %d years the ratio will be %d : %d. What is %s\'s present age?' % (n1, n2, a, b, t, p, q, n2), y, near(y, (2, 3, 4, 5, 6)) + [x], 'Let the ages be %dk and %dk: (%dk + %d)/(%dk + %d) = %d/%d gives k = %d, so %s is %d.' % (a, b, a, t, b, t, p, q, k, n2, y))


def percent(lvl):
    p1, p2 = R.choice([10, 20, 25, 30, 40, 50]), R.choice([10, 20, 25])
    net = Fraction((100 + p1) * (100 - p2), 100) - 100
    s = ('%g%%' % float(net)) if net >= 0 else ('%g%% loss' % float(-net))
    sg = lambda v: ('%g%%' % v) if v >= 0 else ('%g%% loss' % -v)
    add(lvl, 'percentage', 'A shopkeeper marks an item %d%% above cost and gives a %d%% discount. What is the overall gain?' % (p1, p2), sg(float(net)), [sg(float(net) + 2), sg(p1 - p2), sg(float(net) - 2), sg(float(net) + 5)], 'Net = (1 + %d/100)(1 − %d/100) − 1 = %g%%.' % (p1, p2, float(net)))


def arrangements(lvl):
    w = R.choice(['APPLE', 'LETTER', 'BANANA', 'GARDEN', 'NURSE', 'CANCER', 'SCHOOL', 'PEPPER', 'TABLET', 'REMEDY', 'MEDICINE'])
    from collections import Counter
    n = math.factorial(len(w))
    for c in Counter(w).values():
        n //= math.factorial(c)
    add(lvl, 'arrangement', 'In how many different ways can the letters of the word %s be arranged?' % w, n, [x for x in [math.factorial(len(w)), n * 2, n * 3, n // 2 if n % 2 == 0 else n + 6, n + 60] if x != n], '%d letters%s: %d!%s = %d.' % (len(w), ' with repeats' if n != math.factorial(len(w)) else '', len(w), ''.join(' ÷ %d!' % c for c in Counter(w).values() if c > 1), n))


MAKERS = {
    'E': [series, coding, letter_series, ranking, direction, clock, relation, venn, syllogism, odd_letters, percent],
    'I': [series, coding, letter_series, ranking, direction, clock, calendar, relation, venn, syllogism, ages, wrong_number, percent, arrangements],
    'H': [series, coding, direction, clock, calendar, relation, venn, syllogism, ages, wrong_number, arrangements],
}


def main(out, ne=48, ni=151, nh=51):
    seen = set()
    for lvl, n in [('E', ne), ('I', ni), ('H', nh)]:
        got = 0; makers = MAKERS[lvl]; i = 0
        while got < n:
            before = len(Q)
            makers[i % len(makers)](lvl); i += 1
            if len(Q) > before:
                key = Q[-1]['q']
                if key in seen:
                    Q.pop(); continue
                seen.add(key); got += 1
    json.dump(Q, open(out, 'w'), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(Q), Counter(q['lvl'] for q in Q), Counter(q['type'] for q in Q))


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[0], *(int(x) for x in a[1:4]))
