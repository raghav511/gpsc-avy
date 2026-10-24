// Whole-app audit: visits every screen reachable by links (breadth-first from Home), and on each one checks for
// page errors, sideways scroll, broken pictures, cut-off text, small tap targets, words like "undefined"/"NaN",
// and "could not be opened" pages. Then presses every button on each screen once and reports any that throw.
//   node tests/audit.mjs --base http://localhost:8765/gpsc-avy/ --profile pixel|ipad [--max 400] [--press 1]
import fs from 'node:fs';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const prof = args.profile || 'pixel', MAX = +(args.max || 400), PRESS = args.press !== '0';
const PROFILES = {
  pixel: { engine: 'chromium', viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 },
  small: { engine: 'chromium', viewport: { width: 360, height: 740 }, isMobile: true, hasTouch: true, deviceScaleFactor: 1 },
  ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true },
  ipadland: { engine: 'webkit', viewport: { width: 1080, height: 810 }, hasTouch: true },
  dark: { engine: 'chromium', viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true, colorScheme: 'dark' }
};
const { engine, ...opts } = PROFILES[prof];
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block' }, opts));
await ctx.addInitScript(() => { try { if (!localStorage.getItem('gpscavy-settings-v1')) localStorage.setItem('gpscavy-settings-v1', JSON.stringify({ a2hs: 1, welcomed: 1 })); } catch (e) { } window.alert = window.confirm = window.prompt = () => { throw new Error('native dialog used'); }; });
await ctx.route(/^https?:\/\/(?!localhost)/, r => r.abort()); // stay offline from the outside world
const page = await ctx.newPage();
const issues = []; const add = (route, kind, detail) => issues.push({ route, kind, detail: String(detail).slice(0, 220) });
let cur = '';
page.on('pageerror', e => add(cur, 'page error', e.message));
page.on('console', m => { if (m.type() === 'error' && !/Failed to load resource|net::ERR|preload/.test(m.text())) add(cur, 'console error', m.text()); });

// seed some history so result, review and progress screens have something to show
await page.goto(BASE + '#/'); await page.waitForFunction(() => window.__gpsBooted, null, { timeout: 30000 });
const seeded = await page.evaluate(async () => {
  const idx = await (await fetch('data/index.json')).json();
  const sets = (idx.sets || idx).slice ? (idx.sets || idx) : Object.values(idx);
  return Array.isArray(sets) ? sets.slice(0, 3).map(s => s.id || s.set || s) : [];
});
const pick = seeded.filter(x => typeof x === 'string');
if (pick.length) {
  await page.evaluate(ids => {
    const h = ids.map((id, i) => ({ id: id + '-t' + i, set: id, setName: id, score: 30 + i * 7, total: 60, wrong: 20, skipped: 10 - i, usedMs: 3000000, auto: false, submittedAt: new Date(Date.now() - i * 86400000).toISOString(), answers: { 1: 'A', 2: 'B', 3: 'C' } }));
    localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify(h));
  }, pick);
}

const seen = new Set(), queue = ['#/'];
const extra = ['#/tests', '#/tests/level', '#/tests/drills', '#/tests/mine', '#/study', '#/progress', '#/custom', '#/search', '#/study/papers'];
extra.forEach(h => queue.push(h));
if (pick.length) queue.push('#/result/' + pick[0] + '-t0', '#/review/' + pick[0] + '-t0');
const routes = [];
while (queue.length && routes.length < MAX) {
  const h = queue.shift(); if (seen.has(h)) continue; seen.add(h); routes.push(h); cur = h;
  await page.goto('about:blank'); await page.goto(BASE + h);
  await page.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }).catch(() => add(h, 'did not start', ''));
  await page.waitForTimeout(700);
  const r = await page.evaluate(() => {
    const app = document.getElementById('app'), out = {};
    out.notFound = /could not be opened|not found/i.test((app.querySelector('main') || app).innerText.slice(0, 400)) && !/no .* found|nothing found/i.test(app.innerText.slice(0, 400));
    out.sideways = app.scrollWidth > app.clientWidth + 1 ? app.scrollWidth + '>' + app.clientWidth : '';
    out.badWords = (app.innerText.match(/\b(undefined|NaN|null|\[object Object\])\b/g) || []).slice(0, 3).join(',');
    out.brokenImg = [...document.images].filter(i => i.complete && !i.naturalWidth && i.loading !== 'lazy').map(i => i.getAttribute('src')).slice(0, 3);
    // cut-off text: a box that hides overflowing text without an ellipsis
    out.cut = [...app.querySelectorAll('*')].filter(el => {
      if (!el.offsetParent || el.closest('.chips,.ptabs,svg,pre,table,.formula,.zs,.tbl,.nb .tw,.scrollx')) return false;
      const cs = getComputedStyle(el);
      if (!/hidden|clip/.test(cs.overflowX) || cs.textOverflow === 'ellipsis') return false;
      return el.scrollWidth > el.clientWidth + 2 && el.innerText && el.innerText.trim().length > 1;
    }).slice(0, 3).map(el => el.className + ': ' + el.innerText.slice(0, 40));
    // tap targets: buttons and links that are not inside running text
    out.small = [...app.querySelectorAll('button, a[href], [role=button], input:not([type=hidden]), select')].filter(el => {
      if (!el.offsetParent) return false;
      if (el.closest('p, li, td, .sub, .tby, figcaption, .nsrc, .lnk-in')) return false;
      if (el.tagName === 'INPUT' && el.closest('label') && el.closest('label').getBoundingClientRect().height >= 40) return false;
      const b = el.getBoundingClientRect(); return b.width > 0 && (b.height < 40 || b.width < 40);
    }).slice(0, 4).map(el => (el.className || el.tagName) + ' ' + Math.round(el.getBoundingClientRect().width) + 'x' + Math.round(el.getBoundingClientRect().height) + ' "' + (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 20) + '"');
    out.links = [...document.querySelectorAll('a[href^="#/"]')].map(a => a.getAttribute('href'));
    out.unlabelled = [...app.querySelectorAll('button, a[href]')].filter(el => el.offsetParent && !(el.textContent || '').trim() && !el.getAttribute('aria-label') && !el.title).length;
    return out;
  }).catch(e => ({ err: e.message }));
  if (r.err) { add(h, 'audit failed', r.err); continue; }
  if (r.notFound) add(h, 'could not be opened', '');
  if (r.sideways) add(h, 'sideways scroll', r.sideways);
  if (r.badWords) add(h, 'bad words on screen', r.badWords);
  if (r.brokenImg.length) add(h, 'broken picture', r.brokenImg.join(' '));
  if (r.cut.length) add(h, 'cut-off text', r.cut.join(' | '));
  if (r.small.length) add(h, 'small tap target', r.small.join(' | '));
  if (r.unlabelled) add(h, 'button without a label', r.unlabelled);
  for (const l of r.links) if (!seen.has(l) && !queue.includes(l) && !/\/run$|#\/test\/[^/]+\/(start|go)/.test(l)) queue.push(l);
  if (PRESS) {
    // press each button once (fresh page each time); anything that throws is a bug
    const n = await page.locator('#app button:visible').count();
    for (let i = 0; i < Math.min(n, 14); i++) {
      await page.goto('about:blank'); await page.goto(BASE + h); await page.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }).catch(() => { }); await page.waitForTimeout(400);
      const b = page.locator('#app button:visible').nth(i);
      const label = ((await b.getAttribute('aria-label').catch(() => '')) || (await b.innerText().catch(() => '')) || '').trim().slice(0, 30);
      cur = h + ' [press ' + label + ']';
      await b.click({ timeout: 3000 }).catch(e => add(cur, 'button not clickable', e.message.split('\n')[0]));
      await page.waitForTimeout(350);
      await page.keyboard.press('Escape').catch(() => { });
    }
    cur = h;
  }
}
await browser.close();
const byKind = {};
issues.forEach(i => { (byKind[i.kind] = byKind[i.kind] || []).push(i); });
console.log(`audit ${prof}: ${routes.length} screens, ${issues.length} issues`);
for (const [k, v] of Object.entries(byKind)) { console.log('\n## ' + k + ' (' + v.length + ')'); const uniq = new Map(); v.forEach(i => { const key = i.detail.replace(/\d+/g, '#'); if (!uniq.has(key)) uniq.set(key, i); }); [...uniq.values()].slice(0, 12).forEach(i => console.log(' -', i.route, '::', i.detail)); }
fs.writeFileSync('/tmp/claude-0/audit-' + prof + '.json', JSON.stringify({ routes, issues }, null, 1));
