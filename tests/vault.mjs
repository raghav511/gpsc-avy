// The published (encrypted) copy: content unlocks only with the keys the owner's access script hands out.
//   sh tools/publish.sh DIST KEYFILE; CONTENT_KEY=$(cat KEYFILE) node tests/vault.mjs --base http://localhost:8765/<dist>/ --profile pixel|ipad
import fs from 'node:fs';
import { licenceSim } from './licence-sim.mjs';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base, prof = args.profile || 'pixel';
const PROFILES = { pixel: { engine: 'chromium', viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true }, ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true } };
const { engine, ...opts } = PROFILES[prof];
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const CID = '1-x.apps.googleusercontent.com', LURL = 'https://script.google.com/macros/s/VAULT/exec', tokens = {};
const LIC = licenceSim({ owner: 'owner@gmail.com', clientId: CID, tokens, contentKey: process.env.CONTENT_KEY });
const H = { 'access-control-allow-origin': '*' };
async function device(email) {
  const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block', acceptDownloads: true }, opts));
  await ctx.addInitScript(e => { if (location.protocol === 'about:') return; const P = /-staging\//.test(location.pathname) ? 'stg:' : ''; if (!localStorage.getItem(P + 'gpscavy-settings-v1')) { localStorage.setItem(P + 'gpscavy-settings-v1', JSON.stringify(Object.assign({ a2hs: 1, welcomed: 1 }, e ? { account: { email: e } } : {}))); if (e) localStorage.setItem(P + 'gpscavy-gtoken', JSON.stringify({ token: 'T-' + e, exp: Date.now() + 3e6 })); } }, email || '');
  if (email) tokens['T-' + email] = email;
  await ctx.route(/\/js\/config\.js/, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: "export const GOOGLE_CLIENT_ID = '" + CID + "';\nexport const LICENCE_URL = '" + LURL + "';" }));
  await ctx.route('https://www.googleapis.com/**', r => r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: '{"files":[],"id":"f"}' }));
  await ctx.route(LURL, r => r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: JSON.stringify(LIC.post(r.request().postData())) }));
  const page = await ctx.newPage(); const errs = []; page.on('pageerror', e => errs.push(e.message));
  return { ctx, page, errs };
}
const go = async (p, h) => { await p.goto('about:blank'); await p.goto(BASE + h); await p.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }); await p.waitForTimeout(2500); };
const screen = p => p.evaluate(() => document.body.dataset.screen);

// the files on the website really are scrambled
const raw = await (await fetch(BASE + 'data/sets/set2v3.json')).text().catch(() => '');
ok(raw.startsWith('GPSCAVY1') && !/"questions"/.test(raw), 'a mock file on the website is scrambled');
const rawN = await (await fetch(BASE + 'data/notes/topic5.html')).text().catch(() => '');
ok(rawN.startsWith('GPSCAVY1') && !/<h2/.test(rawN), 'a notes file on the website is scrambled');

const V = await device(''); // a visitor, not signed in
await go(V.page, '#/study/topic1');
const n1 = (await V.page.locator('#nb').textContent().catch(() => '')).length;
ok(n1 > 2000, 'free Topic 1 notes unlock for a visitor', n1 + ' characters');
await go(V.page, '#/test/set1v3');
ok(/Practice Set 1/.test(await V.page.locator('#app').textContent()) && await screen(V.page) !== 'pay', 'free Practice Set 1 opens');
await go(V.page, '#/study/topic5');
ok(await screen(V.page) === 'pay', 'Topic 5 asks for a plan');
const vkeys = await V.page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('gpscavy-licence')).keys || {}));
ok(vkeys.length === 2 && !vkeys.includes('*'), 'a visitor only holds keys for the free picks', vkeys.join(','));

const O = await device('owner@gmail.com');
await go(O.page, '#/study/topic5');
const n5 = (await O.page.locator('#nb').textContent().catch(() => '')).length;
ok(n5 > 2000, 'the owner reads Topic 5', n5 + ' characters');
await go(O.page, '#/study/playbook/gk');
ok((await O.page.locator('#pb').textContent().catch(() => '')).length > 2000, 'playbook unlocks');
await go(O.page, '#/study/cheat/reasoning');
ok((await O.page.locator('#nb').textContent().catch(() => '')).length > 2000, 'the reasoning cheat sheet unlocks');
await go(V.page, '#/study/cheat/grammar');
ok(await screen(V.page) === 'pay', 'a visitor is asked to pay for the grammar cheat sheet');
await go(O.page, '#/search?q=ledum');
ok(await O.page.locator('#app').textContent().then(t => /Ledum/i.test(t)), 'search works on the scrambled search file');
await go(O.page, '#/test/set7');
ok(/Practice Set 7/.test(await O.page.locator('#app').textContent()), 'a paid mock opens for the owner');
// start it and see a real question
const st = O.page.locator('#tGo, .wide.pri:has-text("Start")').first();
if (await st.count()) { await st.click(); await O.page.waitForTimeout(1500); }
ok(await screen(O.page) === 'runner' && (await O.page.locator('#rq').textContent().catch(() => '')).length > 40, 'questions show in the test');
// a PDF downloads as a real PDF
await go(O.page, '#/study/pdfs');
const link = O.page.locator('a[download][href*="Topic-5-"]').first();
if (await link.count()) {
  const [dl] = await Promise.all([O.page.waitForEvent('download', { timeout: 20000 }), link.click()]);
  const pth = await dl.path(); const head = fs.readFileSync(pth).subarray(0, 5).toString();
  ok(head === '%PDF-', 'a downloaded PDF is the real file', head);
} else ok(false, 'topic PDF download link found');
for (const d of [V, O]) ok(!d.errs.length, 'no page errors', d.errs.join(' | '));
await browser.close();
console.log(`\nvault ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
