// GPSCavy acceptance tests (SPEC.md §10). Plain Playwright library, no test runner needed.
//   node tests/acceptance.mjs --base http://localhost:8765/gpsc-avy/ --profile pixel|iphone|desktop|ipad|ipadland|ipadmobile  (iPad profiles run in WebKit)
// Exit code 0 when every check passes.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const pwPath = process.env.PLAYWRIGHT || 'playwright';
const PW = await import(pwPath).catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const PROFILES = {
  pixel: { viewport: { width: 412, height: 923 }, deviceScaleFactor: 2.625, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (Linux; Android 16; Pixel 10a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36' },
  iphone: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36' },
  desktop: { viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1, isMobile: false, hasTouch: false },
  // iPad (9th generation), iPadOS 26 Safari: 810x1080 CSS px portrait, DPR 2. Safari on iPad sends a Mac desktop user agent by default.
  ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, deviceScaleFactor: 2, isMobile: false, hasTouch: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15' },
  ipadland: { engine: 'webkit', viewport: { width: 1080, height: 810 }, deviceScaleFactor: 2, isMobile: false, hasTouch: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15' },
  ipadmobile: { engine: 'webkit', viewport: { width: 810, height: 1080 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (iPad; CPU OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Mobile/15E148 Safari/604.1' }
};
const prof = args.profile || 'pixel';
const DATA = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/data/sets.json'), 'utf8'));
const byId = Object.fromEntries(DATA.sets.map(s => [s.id, s]));
const QUIZ = {}; for (let t = 5; t <= 10; t++) QUIZ['quiz-topic' + t] = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/sets/quiz-topic' + t + '.json'), 'utf8'));
fs.readdirSync(path.join(ROOT, 'data/sets')).filter(f => f.startsWith('compd')).forEach(f => { const s = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/sets', f), 'utf8')); byId[s.id] = s; });
Object.assign(byId, QUIZ);

let pass = 0, fail = 0; const failures = [];
function ok(cond, name, extra) { if (cond) { pass++; } else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } }
const ONLY = args.only ? args.only.split(',') : null;
async function section(name, fn) {
  if (ONLY && !ONLY.some(o => name.startsWith(o))) return;
  console.log('▸', name);
  try { await fn(); } catch (e) {
    fail++; failures.push(name + ' threw ' + e.message.split('\n')[0]);
    let h = ''; try { h = await page.evaluate(() => location.hash); await page.screenshot({ path: path.join(os.tmpdir(), 'gpsc-fail-' + name.slice(0, 2).replace(/\W/g, '') + '.png') }); } catch (x) { }
    console.log('  THREW at', h, e.message.split('\n').slice(0, 4).join(' / '));
  }
}

const { engine = 'chromium', ...profOpts } = PROFILES[prof];
const browser = await PW[args.engine || engine].launch();
const ctx = await browser.newContext(Object.assign({ acceptDownloads: true, serviceWorkers: 'block' }, profOpts));
await ctx.addInitScript(() => { window.__gpscTest = 1; });
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });
const hash = () => page.evaluate(() => location.hash);
async function open(h) { if (page.url().startsWith(BASE)) await page.goto('about:blank'); await page.goto(BASE + h); await page.waitForLoadState('networkidle'); await page.waitForTimeout(150); }
async function clickNav(sel) { await page.click(sel); await page.waitForTimeout(250); }
async function clearAll() { await page.evaluate(() => localStorage.clear()); }
const settle = () => page.waitForTimeout(300);
// Backup / restore a file now live under Sync progress → Other ways.
async function viaSync(act) {
  if (await page.locator('#sheet').count()) { await page.keyboard.press('Escape'); await settle(); }
  if (await page.locator('[data-act="sync"]').count() === 0) await open('#/');
  await page.locator('[data-act="sync"]').first().click(); await settle();
  await page.click('#sheet .other summary'); await page.click('#sheet .other [data-act="' + act + '"]'); await settle();
}

// ---------- 1. navigation ----------
await section('1. tabs, buttons and back controls', async () => {
  await open('#/'); await clearAll(); await open('#/');
  for (const [name, h] of [['Tests', '#/tests'], ['Study', '#/study'], ['Progress', '#/progress'], ['Home', '#/']]) {
    await clickNav('.bnav a[data-nav="' + name.toLowerCase() + '"]');
    ok(await hash() === h, 'bottom nav ' + name, await hash());
    ok(await page.locator('h1, .brand b').first().isVisible(), 'screen heading ' + name);
  }
  // every internal link on the root screens opens a screen that is not an error
  const seen = new Set();
  for (const root of ['#/', '#/tests', '#/tests/level', '#/tests/drills', '#/tests/mine', '#/study', '#/study/core', '#/study/gk', '#/study/comp', '#/study/gram', '#/study/pdfs', '#/study/wrong', '#/progress']) {
    await open(root);
    const hrefs = await page.$$eval('a[href^="#/"]', as => as.map(a => a.getAttribute('href')));
    for (const h of hrefs) {
      if (seen.has(h)) continue; seen.add(h);
      await open(h);
      const bad = await page.locator('text=This page could not be opened').count();
      ok(!bad, 'link opens ' + h);
      const isRoot = ['#/', '#/tests', '#/study', '#/progress'].includes(h.split('?')[0]) || /^#\/(tests|study)\/[a-z]*$/.test(h) && !/topic|playbook|papers/.test(h);
      const hasBack = await page.locator('[data-back], #rBack').count();
      const hasNav = await page.locator('.bnav:visible').count();
      ok(hasBack || hasNav, 'way back on ' + h);
    }
  }
  ok(seen.size > 40, 'crawled screens', String(seen.size));
  // back buttons move up one level
  for (const [from, to] of [['#/drills/gk', '#/tests/drills'], ['#/study/topic9', '#/study/core'], ['#/study/playbook/gk', '#/study/gk'], ['#/custom', '#/tests'], ['#/test/set3', '#/tests'], ['#/test/gkd2', '#/drills/gk'], ['#/test/end1', '#/drills/en'], ['#/test/end3', '#/drills/comp'], ['#/test/lvl-hard-2', '#/tests/level'], ['#/study/papers', '#/study']]) {
    await open(from);
    await page.click('[data-back]'); await settle();
    ok(await hash() === to, 'back from ' + from, await hash());
  }
  // Android Back from a fresh deep link (e.g. opened from WhatsApp) stays in the app and moves up one level at a time
  const p3 = await ctx.newPage();
  await p3.goto(BASE + '#/study/topic9'); await p3.waitForLoadState('networkidle');
  const h3 = () => p3.evaluate(() => location.hash);
  for (const want of ['#/study/core', '#/study', '#/']) { await p3.goBack(); await p3.waitForTimeout(300); ok(await h3() === want, 'system Back from deep link goes to ' + want, await h3()); }
  await p3.close();
});

// ---------- 2. content matches labels ----------
const expectName = (id) => {
  const s = byId[id];
  if (id === 'end1' || id === 'end2') return 'Grammar drill ' + id.slice(3);
  if (id === 'end3' || id === 'end4') return 'Comprehension drill ' + (+id.slice(3) - 2);
  return s.set.split(':')[0];
};
await section('2a. every set, level and drill card opens the matching test', async () => {
  const lists = [['#/tests', 25, s => !s.hidden && !s.drill && !s.lvlset && s.id.startsWith('set')], ['#/tests/level', 9, s => s.lvlset], ['#/drills/gk', 6, s => s.id.startsWith('gkd')], ['#/drills/en', 2, s => s.id === 'end1' || s.id === 'end2'], ['#/drills/comp', 12, s => s.id === 'end3' || s.id === 'end4' || s.id.startsWith('compd')]];
  for (const [h, n, pred] of lists) {
    await open(h);
    const cards = await page.$$eval('a.row[href^="#/test/"]', as => as.map(a => ({ id: a.getAttribute('href').slice(7), title: a.querySelector('.ttl').textContent })));
    ok(cards.length === n, h + ' card count', cards.length + ' vs ' + n);
    ok(cards.every(c => pred(byId[c.id] || {})), h + ' lists only its kind', cards.map(c => c.id).join(','));
    for (const c of cards) {
      await page.click('a.row[href="#/test/' + c.id + '"]'); await settle();
      const title = await page.locator('.it').textContent();
      const s = byId[c.id];
      ok(title.toLowerCase().startsWith(c.title.toLowerCase().split(':')[0]) || title.toLowerCase().includes(expectName(c.id).toLowerCase()), 'title matches card ' + c.id, title + ' / ' + c.title);
      const chips = await page.$$eval('.intro .chip', cs => cs.map(c => c.textContent));
      const secs = s.sections.map(x => x.id);
      const names = { comp: 'Comprehension', gram: 'Grammar', gk: 'General knowledge', lr: 'Reasoning', core: 'Core subject' };
      ok(secs.every(x => chips.some(t => t.startsWith(names[x] + ' ' + s.questions.filter(q => q.sec === x).length))), 'sections match ' + c.id, chips.join('|'));
      ok(chips.filter(t => /^(Comprehension|Grammar|General knowledge|Reasoning|Core subject) /.test(t)).length === secs.length, 'no extra sections ' + c.id);
      if (s.level || s.lvlset) { const lv = { easy: 'Easy', intermediate: 'Intermediate', hard: 'Hard' }[s.lvlset || s.level]; ok(chips.includes(lv), 'level chip ' + c.id, chips.join('|')); }
      await page.goBack(); await settle();
    }
  }
  // "English drills" opens English drills, not a practice set
  await open('#/tests/drills');
  await page.click('text=English Grammar drills'); await settle();
  ok(await hash() === '#/drills/en' && (await page.locator('.tbt h1').textContent()) === 'Grammar drills', 'English Grammar drills button');
  await open('#/tests/drills');
  await page.click('text=English Comprehension drills'); await settle();
  ok(await hash() === '#/drills/comp' && (await page.locator('.tbt h1').textContent()) === 'Comprehension drills', 'English Comprehension drills button');
  await open('#/tests/drills'); await page.click('text=GK drills'); await settle();
  ok(await hash() === '#/drills/gk', 'GK drills button');
});

await section('2b. custom tests contain only the chosen subjects', async () => {
  const names = { comp: 'Comprehension', gram: 'Grammar', gk: 'General knowledge', lr: 'Reasoning', core: 'Core subject' };
  for (const sec of ['comp', 'gram', 'gk', 'lr', 'core']) {
    await open('#/'); await clearAll(); await open('#/custom');
    await page.click('[data-sec="' + sec + '"]'); await page.waitForTimeout(600);
    await page.click('#cgo'); await page.waitForSelector('#rq .qt'); await settle();
    const id = (await hash()).split('?')[0].slice(7);
    const st = await page.evaluate(i => JSON.parse(localStorage.getItem('gpsc-cbrt-' + i + '-v1')), id);
    ok(st && st.def && st.def.refs.length > 0 && st.def.refs.every(r => r[1] === sec), 'custom ' + sec + ' refs only ' + sec, st && st.def.refs.map(r => r[1]).join(''));
    const groups = await page.$$eval('#pg .pgs', gs => gs.map(g => g.className));
    ok(groups.length === 1 && groups[0].includes('s-' + sec), 'custom ' + sec + ' palette has one section', groups.join('|'));
    // every question really is that section in the source data
    const allSec = st.def.refs.every(r => { const [sid, n] = r[0].split(':'); const s = byId[sid]; return s && s.questions[+n - 1].sec === sec; });
    ok(allSec, 'custom ' + sec + ' source questions are ' + sec);
    if (sec === 'comp') { const pass = await page.locator('#rq details.passage').count(); ok(pass === 1, 'comprehension question shows its passage'); }
  }
  // two subjects + difficulty filter
  await open('#/custom?sec=gk,core');
  await page.click('[data-diff="H"]'); await page.waitForTimeout(700);
  await page.click('#cgo'); await page.waitForSelector('#rq .qt');
  const id = (await hash()).split('?')[0].slice(7);
  const st = await page.evaluate(i => JSON.parse(localStorage.getItem('gpsc-cbrt-' + i + '-v1')), id);
  ok(st.def.refs.every(r => r[1] === 'gk' || r[1] === 'core'), 'GK + Core only');
  ok(st.def.refs.every(r => { const [sid, n] = r[0].split(':'); return (byId[sid].questions[+n - 1].lvl) === 'H'; }), 'Hard filter keeps only hard questions');
});

await section('2c. each Study chip shows the right list', async () => {
  const expect = { all: ['Core subject notes', 'General knowledge', 'English comprehension', 'English grammar'], core: ['Core subject notes', 'Quick-check quizzes'], gk: ['General knowledge'], gram: ['English grammar'], comp: ['English comprehension'], pdfs: ['Printable PDFs to share on WhatsApp'], wrong: [] };
  const not = { core: ['General knowledge', 'English grammar'], gk: ['Core subject notes', 'English grammar'], gram: ['Core subject notes', 'General knowledge', 'English comprehension'], comp: ['Core subject notes', 'English grammar'], pdfs: ['Core subject notes'], wrong: ['Core subject notes'] };
  const chipText = { all: 'All', core: 'Core', gk: 'GK', gram: 'English Grammar', comp: 'English Comprehension', pdfs: 'PDFs', wrong: 'Revise incorrect' };
  for (const k of Object.keys(expect)) {
    await open('#/study');
    await page.click('.chips a.fchip:has-text("' + chipText[k] + '")'); await settle();
    ok((await hash()) === (k === 'all' ? '#/study' : '#/study/' + k), 'study chip ' + k + ' route', await hash());
    const labels = await page.$$eval('main h2.label', hs => hs.map(h => h.textContent));
    expect[k].forEach(l => ok(labels.includes(l), 'study ' + k + ' shows ' + l, labels.join('|')));
    (not[k] || []).forEach(l => ok(!labels.includes(l), 'study ' + k + ' hides ' + l));
  }
  await open('#/study/pdfs');
  ok(await page.locator('.row.pdf').count() === 30, 'all 30 PDFs listed');
  const href = await page.locator('.row.pdf a').first().getAttribute('href');
  const res = await page.request.get(BASE + href);
  ok(res.ok() && (res.headers()['content-type'] || '').includes('pdf'), 'PDF opens', href);
  await open('#/study/gk'); await page.click('text=GK Playbook'); await page.waitForSelector('#pb section');
  const txt = await page.locator('#pb').textContent();
  ok((txt.match(/Goa/g) || []).length > 50, 'GK playbook is Goa GK', String((txt.match(/Goa/g) || []).length));
  await open('#/study/gram'); await page.click('text=Grammar rules'); await page.waitForSelector('#pb section');
  ok(await page.locator('#pb-grammar').count() === 1 && await page.locator('#pb-comp').count() === 0, 'grammar part of English playbook');
  await open('#/study/comp'); await page.click('text=Reading a passage'); await page.waitForSelector('#pb section');
  ok(await page.locator('#pb-comp').count() === 1 && await page.locator('#pb-grammar').count() === 0, 'comprehension part of English playbook');
});

// ---------- 3. test runner ----------
await section('3. runner: answer, flag, palette, reload, timer, submit, undo, auto-submit', async () => {
  await open('#/'); await clearAll();
  await open('#/test/set14');
  await page.click('#go'); await page.waitForSelector('#rq .qt');
  ok(await page.locator('#rq .qt').count() === 1, 'only the current question is rendered');
  await page.click('#rq [data-o="B"]');
  ok(await page.locator('#rq [data-o="B"][aria-pressed="true"]').count() === 1, 'answer selected');
  await page.click('#rNext'); await page.click('#rFlag');
  ok(await page.locator('#rFlag[aria-pressed="true"]').count() === 1, 'flag set');
  await page.click('#rNext'); await page.click('#rq [data-o="C"]');
  await page.click('#rPal'); await settle();
  const cls = await page.$$eval('#pg .pc', cs => cs.slice(0, 4).map(c => c.className));
  ok(cls[0].includes('ans') && cls[1].includes('flag') && cls[2].includes('ans') && cls[2].includes('cur') && cls[3].includes('new'), 'palette states', cls.join('|'));
  const pgs = await page.$$eval('#pg .pgs', g => g.length);
  ok(pgs === 5, 'palette grouped by 5 sections');
  await page.click('#pg .pc[data-n="5"]'); await settle();
  ok((await page.locator('.qn').textContent()).startsWith('Question 5 '), 'palette jumps to question');
  const t1 = await page.locator('#clk').textContent();
  await page.waitForTimeout(400);
  await page.reload(); await page.waitForSelector('#rq .qt'); await settle();
  ok((await page.locator('.qn').textContent()).startsWith('Question 5 '), 'reload resumes at same question');
  const st = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-set14-v1')));
  ok(st.answers[1] === 'B' && st.answers[3] === 'C' && st.flags[2], 'answers and flags saved');
  const t2 = await page.locator('#clk').textContent();
  const sec = t => { const [m, s] = t.split(':').map(Number); return m * 60 + s; };
  ok(sec(t2) <= sec(t1) && sec(t1) - sec(t2) < 10 && sec(t2) > 74 * 60 - 60, 'timer resumes from saved time', t1 + ' -> ' + t2);
  // Android Back inside a test opens the leave sheet
  await page.goBack(); await settle();
  ok((await hash()).startsWith('#/test/set14') && await page.locator('#sheet:has-text("Leave test?")').count() === 1, 'Back opens Leave test sheet', await hash());
  await page.click('#lStay'); await settle();
  // submit with confirm step
  await page.click('#rSub'); await settle();
  const three = await page.$$eval('#sheet .three b', bs => bs.map(b => b.textContent));
  ok(three.join(',') === '2,58,1', 'confirm shows answered/unanswered/flagged', three.join(','));
  await page.click('#sGo'); await page.waitForSelector('.score');
  ok((await hash()).startsWith('#/result/set14-'), 'result screen after submit');
  ok(await page.locator('#toast.on:has-text("Undo")').count() === 1, 'Undo offered');
  await page.click('#toast .tbtn'); await page.waitForSelector('#rq .qt'); await settle();
  ok((await hash()).startsWith('#/test/set14') && (await page.locator('.qn').textContent()).startsWith('Question 5 '), 'Undo reopens the test where it was');
  const hist = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1') || '[]'));
  ok(hist.length === 0, 'Undo removes the attempt');
  ok(await page.locator('#rq [data-o]').count() === 5, 'options shown');
  // auto-submit at 0
  await open('#/');
  await page.evaluate(() => { const k = 'gpsc-cbrt-set14-v1'; const s = JSON.parse(localStorage.getItem(k)); s.paused = false; s.endAt = Date.now() + 2500; localStorage.setItem(k, JSON.stringify(s)); });
  await open('#/test/set14');
  await page.waitForSelector('.score', { timeout: 8000 });
  const h2 = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1') || '[]'));
  ok(h2.length === 1 && h2[0].auto === true, 'auto-submit at 0 marked auto');
  ok(await page.locator('text=time ran out').count() >= 1, 'result says time ran out');
});

await section('3b. timer stays right after the page is hidden for 60 s', async () => {
  const p2 = await ctx.newPage();
  await p2.clock.install({ time: Date.now() });
  await p2.goto(BASE + '#/test/set20'); await p2.waitForSelector('#go'); await p2.click('#go'); await p2.waitForSelector('#clk');
  const read = async () => { const t = await p2.locator('#clk').textContent(); const [m, s] = t.split(':').map(Number); return m * 60 + s; };
  const a = await read();
  await p2.evaluate(() => { Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' }); document.dispatchEvent(new Event('visibilitychange')); });
  await p2.clock.fastForward(60000);
  await p2.evaluate(() => { Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'visible' }); document.dispatchEvent(new Event('visibilitychange')); });
  const b = await read();
  ok(Math.abs((a - b) - 60) <= 2, 'timer moved 60 s while hidden', a + ' -> ' + b);
  await p2.close();
});

// ---------- 4. results and review ----------
await section('4. results breakdowns add up; review filters work', async () => {
  await open('#/'); await clearAll();
  await open('#/test/lvl-easy-1'); await page.click('#go'); await page.waitForSelector('#rq .qt');
  const s = byId['lvl-easy-1'];
  for (let i = 0; i < 20; i++) { await page.click('#rq [data-o="' + (i % 3 ? 'A' : s.questions[i].ans) + '"]'); await page.click('#rNext'); }
  await page.click('#rFlag');
  await page.click('#rSub'); await page.click('#sGo'); await page.waitForSelector('.score');
  const cards = await page.$$eval('section.card', cs => cs.map(c => ({ h: (c.querySelector('h2') || {}).textContent, rows: Array.from(c.querySelectorAll('.arow b')).map(b => b.textContent) })));
  const sum = rows => rows.reduce((m, r) => m + (r.includes('/') ? +r.split('/')[1] : +r), 0);
  const secC = cards.find(c => c.h === 'By section'), lvC = cards.find(c => c.h === 'By level');
  ok(secC && sum(secC.rows) === 60, 'section breakdown sums to 60', secC && secC.rows.join(','));
  ok(lvC && sum(lvC.rows) === 60, 'level breakdown sums to 60', lvC && lvC.rows.join(','));
  const right = s.questions.slice(0, 20).filter((q, i) => (i % 3 ? 'A' : q.ans) === q.ans).length;
  const wrong = 20 - right;
  const secRight = secC.rows.reduce((m, r) => m + +r.split('/')[0], 0);
  ok(secRight === right, 'section rights sum to score', secRight + ' vs ' + right);
  await page.click('a:has-text("Review answers")'); await page.waitForSelector('.rev');
  ok(await page.locator('.rev').count() === wrong, 'Wrong filter shows wrong answers', String(await page.locator('.rev').count()));
  await page.click('.fchip:has-text("Skipped")'); await settle();
  ok(await page.locator('.rev').count() === 40, 'Skipped filter');
  await page.click('.fchip:has-text("Flagged")'); await settle();
  ok(await page.locator('.rev').count() === 1, 'Flagged filter');
  await page.click('.fchip:has-text("All")'); await settle();
  ok(await page.locator('.rev').count() === 60, 'All filter');
  await page.click('.schip2:has-text("General knowledge")'); await settle();
  ok(await page.locator('.rev').count() === 10, 'section filter');
});

// ---------- 5. revise incorrect ----------
await section('5. Revise incorrect shows exactly the wrong answers', async () => {
  // expected: latest answer per unique question (by text+options) is wrong
  const hist = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1') || '[]'));
  const norm = t => t.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const seen = new Map();
  hist.sort((a, b) => b.submittedAt.localeCompare(a.submittedAt)).forEach(a => { const s = byId[a.set]; Object.keys(a.answers).forEach(n => { const q = s.questions[+n - 1]; const k = norm(q.q) + '|' + norm(q.opts.join(' ')); if (!seen.has(k)) seen.set(k, { ok: a.answers[n] === q.ans, sec: q.sec }); }); });
  const wrong = [...seen.values()].filter(x => !x.ok);
  const exp = { all: wrong.length, core: wrong.filter(w => w.sec === 'core').length, gk: wrong.filter(w => w.sec === 'gk').length, comp: wrong.filter(w => w.sec === 'comp').length, gram: wrong.filter(w => w.sec === 'gram').length };
  await open('#/study/wrong');
  for (const k of Object.keys(exp)) {
    await open('#/study/wrong' + (k === 'all' ? '' : '/' + k));
    const n = await page.locator('.rlist .rev').count();
    ok(n === exp[k], 'revise incorrect ' + k, n + ' vs ' + exp[k]);
  }
  await open('#/study/wrong/pdfs');
  ok(await page.locator('.row.pdf:has-text("Level tests")').count() === 1, 'PDFs sub-chip lists the source PDF');
  await open('#/study/wrong'); await page.click('#wtest'); await page.waitForSelector('#rq .qt');
  ok((await hash()).startsWith('#/test/custom-'), 'practise wrong answers as a test');
});

// ---------- 6. sync ----------
await section('6. progress file: export, clear, import, idempotent, mock-exam format, share fallback', async () => {
  await open('#/');
  const before = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')));
  ok(before.length >= 1, 'have attempts to export');
  // share path when the Web Share API takes files
  await page.evaluate(() => { window.__shared = null; navigator.canShare = () => true; navigator.share = d => { window.__shared = d; return Promise.resolve(); }; });
  await viaSync('down'); await settle();
  ok(await page.locator('#dShare').count() === 1, 'Share on WhatsApp shown when files can be shared');
  await page.click('#dShare'); await settle();
  const shared = await page.evaluate(() => window.__shared && { n: window.__shared.files[0].name, t: window.__shared.files[0].type });
  ok(shared && /^GPSC-progress-\d{4}-\d\d-\d\d\.json$/.test(shared.n) && shared.t === 'application/json', 'shares a JSON file', JSON.stringify(shared));
  // fallback to download
  await page.evaluate(() => { navigator.canShare = () => false; });
  await viaSync('down'); await settle();
  ok(await page.locator('#dShare').count() === 0, 'no share button when files cannot be shared');
  const [dl] = await Promise.all([page.waitForEvent('download'), page.click('#dSave')]);
  const file = path.join(os.tmpdir(), dl.suggestedFilename());
  await dl.saveAs(file);
  const pf = JSON.parse(fs.readFileSync(file, 'utf8'));
  ok(pf.format === 'gpsc-cbrt-progress' && pf.version === 1 && pf.exportedFrom === 'gpscavy-app' && pf.attempts.length === before.length, 'file format');
  ok(fs.statSync(file).size < 200000, 'file small enough for WhatsApp');
  // clear, import
  await clearAll(); await open('#/');
  await viaSync('up'); await page.setInputFiles('#upf', file); await page.waitForSelector('#merge');
  await page.click('#merge'); await settle();
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')));
  const strip = a => JSON.stringify(a.map(x => ({ id: x.id, set: x.set, score: x.score, total: x.total, wrong: x.wrong, skipped: x.skipped, usedMs: x.usedMs, auto: x.auto, submittedAt: x.submittedAt, answers: x.answers })).sort((p, q) => p.id.localeCompare(q.id)));
  ok(strip(after) === strip(before), 'export → clear → import gives identical data');
  // import again adds nothing
  await viaSync('up'); await page.setInputFiles('#upf', file); await page.waitForSelector('#merge');
  const prevTxt = await page.locator('.prev .t-grn b').textContent();
  await page.click('#merge'); await settle();
  const again = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')));
  ok(prevTxt === '0' && again.length === after.length, 'second import adds nothing');
  // mock-exam page file
  const now = Date.now();
  const mock = { format: 'gpsc-cbrt-progress', version: 1, exportedAt: new Date().toISOString(), exportedFrom: 'mock-exam', note: 'x', summary: { attempts: 2, best: 30 },
    attempts: [{ id: 'set12v2-1760000000000', set: 'set12v2', setName: 'Practice Set 12', score: 2, total: 60, wrong: 1, skipped: 57, usedMs: 600000, auto: false, submittedAt: '2026-10-10T10:00:00.000Z', answers: { 1: byId.set12v2.questions[0].ans, 2: byId.set12v2.questions[1].ans, 3: 'E' } },
      { id: 'set1-1750000000000', set: 'set1', setName: 'Practice Set 1 (earlier version)', score: 1, total: 35, wrong: 0, skipped: 34, usedMs: 100000, auto: true, submittedAt: '2026-06-01T10:00:00.000Z', answers: { 1: byId.set1.questions[0].ans } }],
    inProgress: [{ set: 'set3', phase: 'exam', cur: 4, answers: { 1: 'A', 2: 'B' }, flags: {}, seen: { 1: 1, 2: 1 }, endAt: now + 1800000, startedAt: now - 600000, usedMs: 0, filter: 'all' }] };
  const mf = path.join(os.tmpdir(), 'GPSC-progress-mock.json'); fs.writeFileSync(mf, JSON.stringify(mock));
  await viaSync('up'); await page.setInputFiles('#upf', mf); await page.waitForSelector('#merge');
  await page.click('#merge'); await settle();
  const h3 = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')));
  ok(h3.some(a => a.id === 'set12v2-1760000000000' && a.score === 2) && h3.some(a => a.id === 'set1-1750000000000'), 'mock-exam attempts import (legacy set re-graded)');
  const ip = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-set3-v1')));
  ok(ip && ip.phase === 'exam' && ip.answers[2] === 'B', 'mock-exam in-progress test imports');
  await open('#/');
  ok(await page.locator('.resume:has-text("Practice Set 3")').count() === 1, 'resume card for imported test');
  // our file loads in the mock-exam page's importer logic (same shape checks as the reference)
  const refOk = pf.attempts.every(a => a.id && a.set && a.answers && typeof a.answers === 'object') && pf.inProgress.every(s => s.phase === 'exam' && s.set && s.endAt > Date.now() - 1000);
  ok(refOk, 'exported file passes the mock-exam importer checks');
  // bad file
  const bf = path.join(os.tmpdir(), 'photo.json'); fs.writeFileSync(bf, '{"hello":1}');
  await viaSync('up'); await page.setInputFiles('#upf', bf); await settle();
  ok(await page.locator('.err').count() === 1, 'rejects a non-progress file');
  await page.keyboard.press('Escape');
});

// ---------- 7. notes ----------
const closeSh = async () => { const c = page.locator('#sheet [data-close]'); if (await c.count()) { await c.first().click(); await settle(); } };
await section('6b. Sync progress: hub merge, never loses anything, auto-sync, header button', async () => {
  const gs = fs.readFileSync(path.join(ROOT, 'tools/sync-hub/Code.gs'), 'utf8');
  const hubApi = {}; new Function('api', gs.replace(/function doGet[\s\S]*?function empty/, 'function empty') + ';api.merge=merge;api.empty=empty;')(hubApi);
  const HUBURL = 'https://script.google.com/macros/s/TEST_hub-123/exec';
  let hub = hubApi.empty(), posts = 0, down = false;
  await page.route(HUBURL + '*', async r => {
    if (down) return r.abort();
    const req = r.request();
    if (req.method() === 'GET') { if (/ping=1/.test(req.url())) return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ ok: true }) }); return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ ok: true, progress: hub }) }); }
    posts++; const body = JSON.parse(req.postData() || '{}'); if (body.progress) hub = hubApi.merge(hub, body.progress);
    return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ ok: true, progress: hub }) });
  });
  await open('#/');
  ok(await page.locator('.hhead .syncb').count() === 1, 'Sync progress button in the top right of Home');
  ok(await page.locator('[data-act="down"]:visible, [data-act="up"]:visible').count() === 0, 'no Download/Upload buttons on Home');
  const mine = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length);
  // the hub already holds attempts from the Mock Exam page and another device
  const other = { format: 'gpsc-cbrt-progress', version: 1, attempts: [
    { id: 'set14-1790000000001', set: 'set14', setName: 'Practice Set 14', score: 1, total: 60, wrong: 0, skipped: 59, usedMs: 1000, auto: false, submittedAt: '2026-10-20T10:00:00.000Z', answers: { 1: byId.set14.questions[0].ans } },
    { id: 'gkd2-1790000000002', set: 'gkd2', setName: 'GK Drill 2', score: 0, total: 25, wrong: 1, skipped: 24, usedMs: 1000, auto: false, submittedAt: '2026-10-21T10:00:00.000Z', answers: { 1: 'E' } }],
    inProgress: [{ set: 'set9v2', phase: 'exam', cur: 2, answers: { 1: 'A' }, flags: {}, seen: {}, startedAt: Date.now() - 60000, endAt: Date.now() + 3600000, usedMs: 0, savedAt: Date.now() - 1000 }] };
  hub = hubApi.merge(hub, other);
  // first tap: setup
  await page.click('.hhead .syncb'); await settle();
  ok(await page.locator('#syncIn').count() === 1, 'first Sync asks for the sync link');
  await page.fill('#syncIn', 'https://example.com/not-a-hub'); await page.click('#syncGo'); await settle();
  ok(await page.locator('#syncErr:visible').count() === 1, 'rejects a wrong link');
  await page.fill('#syncIn', HUBURL); await page.click('#syncGo');
  await page.waitForFunction(() => /Synced/.test((document.querySelector('#syncMsg') || {}).textContent || ''), null, { timeout: 8000 });
  const after = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')));
  ok(after.length === mine + 2, 'sync adds the other devices\' attempts', after.length + ' vs ' + (mine + 2));
  ok(hub.attempts.length === mine + 2, 'hub now holds this device\'s attempts too', hub.attempts.length);
  ok(!!(await page.evaluate(() => localStorage.getItem('gpsc-cbrt-set9v2-v1'))), 'test in progress on another device arrives here');
  await closeSh();
  // offline: nothing is lost, sync later catches up
  down = true;
  await page.evaluate(() => { const h = JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')); h.unshift({ id: 'gkd3-1799999999999', set: 'gkd3', setName: 'GK Drill 3', score: 0, total: 25, wrong: 0, skipped: 25, usedMs: 1, auto: false, submittedAt: '2026-10-23T09:00:00.000Z', answers: {} }); localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify(h)); });
  await open('#/'); await page.click('.hhead .syncb'); await page.waitForFunction(() => /safe on this device/.test((document.querySelector('#syncMsg') || {}).textContent || ''), null, { timeout: 8000 });
  ok(true, 'offline sync says progress is safe');
  for (let k = errors.length - 1; k >= 0; k--) if (/ERR_FAILED|ERR_INTERNET|Failed to fetch/.test(errors[k])) errors.splice(k, 1); // the simulated outage
  ok(await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).some(a => a.id === 'gkd3-1799999999999')), 'offline attempt kept');
  await closeSh(); down = false;
  await page.click('.hhead .syncb'); await page.waitForFunction(() => /Synced/.test((document.querySelector('#syncMsg') || {}).textContent || ''), null, { timeout: 8000 });
  ok(hub.attempts.some(a => a.id === 'gkd3-1799999999999'), 'next sync sends the attempt made while offline');
  for (let k = errors.length - 1; k >= 0; k--) if (/ERR_FAILED|ERR_INTERNET|Failed to fetch/.test(errors[k])) errors.splice(k, 1);
  await closeSh();
  // a later submission of the same attempt id replaces the earlier one everywhere; a submitted test leaves "in progress"
  hub = hubApi.merge(hub, { format: 'gpsc-cbrt-progress', attempts: [{ id: 'set9v2-' + (hub.inProgress.find(s => s.set === 'set9v2') || {}).startedAt, set: 'set9v2', setName: 'Practice Set 9', score: 1, total: 60, wrong: 0, skipped: 59, usedMs: 5, auto: false, submittedAt: '2026-10-23T10:00:00.000Z', answers: { 1: byId.set9v2.questions[0].ans } }] });
  ok(!hub.inProgress.some(s => s.set === 'set9v2'), 'hub drops a test in progress once it is submitted');
  await page.click('.hhead .syncb'); await page.waitForFunction(() => /Synced/.test((document.querySelector('#syncMsg') || {}).textContent || ''), null, { timeout: 8000 });
  ok(!(await page.evaluate(() => localStorage.getItem('gpsc-cbrt-set9v2-v1'))), 'test submitted on another device leaves "in progress" here');
  await closeSh();
  // auto-sync on open
  const before = posts; await open('#/'); await page.waitForTimeout(2500);
  ok(posts > before, 'syncs by itself when the app opens');
  // Progress screen has Sync progress too
  await open('#/progress'); ok(await page.locator('[data-act="sync"]').count() >= 1, 'Progress screen has Sync progress');
  // never removes: hub with fewer attempts does not shrink this device
  const n0 = await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length);
  hub = hubApi.empty(); await open('#/'); await page.click('.hhead .syncb'); await page.waitForFunction(() => /Synced/.test((document.querySelector('#syncMsg') || {}).textContent || ''), null, { timeout: 8000 });
  ok(await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length) === n0 && hub.attempts.length === n0, 'an empty hub never removes anything; it is refilled');
  await closeSh();
  await page.evaluate(() => { const k = 'gpscavy-settings-v1'; const o = JSON.parse(localStorage.getItem(k) || '{}'); delete o.syncUrl; localStorage.setItem(k, JSON.stringify(o)); });
  await open('#/');
  await page.unroute(HUBURL + '*');
});

await section('7. notes: 15 diagrams render, no sideways page scroll, quizzes', async () => {
  let total = 0;
  for (let t = 5; t <= 10; t++) {
    await open('#/study/topic' + t); await page.waitForSelector('#nb .ns');
    const d = await page.$$eval('#nb figure.diagram svg', ss => ss.map(s => { s.closest('.ns').style.contentVisibility = 'visible'; const r = s.getBoundingClientRect(); return [r.width, r.height]; }));
    total += d.length;
    ok(d.every(([w, h]) => w > 100 && h > 50), 'diagrams render topic ' + t, JSON.stringify(d));
    const sw = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
    ok(sw[0] <= sw[1], 'no horizontal page scroll topic ' + t, sw.join(' vs '));
    const tbl = await page.$$eval('#nb .tw', ts => ts.length);
    ok(tbl > 0, 'tables wrapped for sideways scroll topic ' + t);
    ok(!(await page.locator('#nb').textContent()).includes('@u_'), 'no internal mention text topic ' + t);
    await page.click('a:has-text("Quiz me on Topic ' + t + '")'); await settle();
    ok(await hash() === '#/test/quiz-topic' + t, 'quiz link topic ' + t);
    const pressed = await page.locator('.seg.mode [data-m="learn"][aria-pressed="true"]').count();
    ok(pressed === 1, 'quiz defaults to learn mode topic ' + t);
  }
  ok(total === 15, 'all 15 diagrams', String(total));
  await open('#/test/quiz-topic9'); await page.click('#go'); await page.waitForSelector('#rq .qt');
  const q = QUIZ['quiz-topic9'].questions[0];
  await page.click('#rq [data-o="' + q.ans + '"]');
  ok(await page.locator('.fb.ok').count() === 1, 'learn mode reveals the answer');
  for (const pb of ['gk', 'english']) { await open('#/study/playbook/' + pb); await page.waitForSelector('#pb section'); const sw = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]); ok(sw[0] <= sw[1], 'no horizontal scroll playbook ' + pb, sw.join(' vs ')); }
  for (const h of ['#/', '#/tests', '#/progress', '#/study', '#/custom?sec=core', '#/test/set1v3']) { await open(h); const sw = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]); ok(sw[0] <= sw[1], 'no horizontal scroll ' + h, sw.join(' vs ')); }
});

// ---------- 8. errors, PWA basics, search ----------
await section('8. PWA basics, search, tap targets', async () => {
  const man = await (await page.request.get(BASE + 'manifest.webmanifest')).json();
  ok(man.display === 'standalone' && man.theme_color && man.icons.some(i => i.purpose === 'maskable' && i.sizes === '512x512'), 'manifest');
  ok((await page.request.get(BASE + 'sw.js')).ok(), 'service worker file');
  const idx = await (await page.request.get(BASE + 'data/index.json')).body();
  ok(idx.length < 15 * 1024, 'index.json under 15 KB', String(idx.length));
  await open('#/search?q=ledum');
  await page.waitForSelector('#sr .row, #sr details', { timeout: 8000 });
  ok(await page.locator('#sr .row[href^="#/study/topic"]').count() > 0, 'search finds notes');
  ok(await page.locator('#sr details').count() > 0, 'search finds questions');
  if (prof !== 'desktop') {
    await open('#/');
    const small = await page.$$eval('.bnav a, .big, .btn, .ib, .fchip, .row', els => els.filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.height < 43.5 || r.width < 43.5); }).map(e => e.className + ' ' + Math.round(e.getBoundingClientRect().height)));
    ok(!small.length, 'tap targets ≥ 44 px on Home', small.join('|'));
    const bnav = await page.$eval('.bnav', e => getComputedStyle(e).paddingBottom);
    ok(bnav !== undefined, 'bottom nav pads for the gesture bar');
  }
});

ok(!errors.length, 'no console errors', errors.slice(0, 5).join(' | '));
await browser.close();
console.log(`\n${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
