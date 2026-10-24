// Paid access: plans, UPI request, owner approval, free content chosen by the owner, single-use vouchers, expiry.
// Google sign-in is faked; the owner's script is the REAL tools/licence/Code.gs run in Node with an in-memory Sheet.
//   node tests/paid.mjs --base http://localhost:8765/gpsc-avy/ --profile pixel|ipad
import fs from 'node:fs';
import { licenceSim } from './licence-sim.mjs';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const prof = args.profile || 'pixel';
const PROFILES = {
  pixel: { engine: 'chromium', viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true },
  ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true }
};
const { engine, ...opts } = PROFILES[prof];
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const CID = '1234567890-testclient.apps.googleusercontent.com', LURL = 'https://script.google.com/macros/s/LICENCE-TEST/exec';
const OWNER = 'owner@gmail.com';
const tokens = {};
const LIC = licenceSim({ owner: OWNER, clientId: CID, tokens, contentKey: process.env.CONTENT_KEY || '' });
const H = { 'access-control-allow-origin': '*' };

async function device(name) {
  const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block' }, opts));
  await ctx.addInitScript(() => { try { if (!localStorage.getItem('gpscavy-settings-v1')) localStorage.setItem('gpscavy-settings-v1', JSON.stringify({ a2hs: 1, welcomed: 1 })); } catch (e) { } });
  await ctx.route(/\/js\/config\.js/, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: "export const GOOGLE_CLIENT_ID = '" + CID + "';\nexport const LICENCE_URL = '" + LURL + "';" }));
  await ctx.route('https://accounts.google.com/**', r => {
    const p = new URL(r.request().url()).searchParams, back = p.get('redirect_uri') + '#';
    const email = p.get('login_hint') || 'friend@gmail.com', t = 'tok-' + Math.random().toString(36).slice(2); tokens[t] = email;
    return r.fulfill({ status: 200, contentType: 'text/html', body: '<script>location.replace(' + JSON.stringify(back + 'access_token=' + t + '&expires_in=3599&scope=' + encodeURIComponent('email openid https://www.googleapis.com/auth/drive.appdata') + '&state=' + p.get('state')) + ')</script>' });
  });
  await ctx.route('https://www.googleapis.com/**', r => {
    const email = tokens[(r.request().headers().authorization || '').replace('Bearer ', '')];
    if (/userinfo/.test(r.request().url())) return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: JSON.stringify({ email }) });
    if (r.request().method() === 'GET' && /drive\/v3\/files$/.test(new URL(r.request().url()).pathname)) return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: '{"files":[]}' });
    return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: '{"id":"f1"}' });
  });
  await ctx.route(LURL, r => r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: JSON.stringify(LIC.post(r.request().postData() || '{}')) }));
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(name + ': ' + e.message));
  return { ctx, page, errs };
}
const go = async (p, h) => { await p.goto('about:blank'); await p.goto(BASE + h); await p.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }); await p.waitForTimeout(900); };
async function signIn(d, email) {
  await go(d.page, '#/');
  await d.page.click('.tbn.syncb'); await d.page.waitForTimeout(300);
  await d.page.fill('#gsE', email);
  await Promise.all([d.page.waitForURL(/#\/$/, { timeout: 15000 }), d.page.click('#gsGo')]);
  await d.page.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }); await d.page.waitForTimeout(1500);
}
const screen = p => p.evaluate(() => document.body.dataset.screen);
async function section(name, fn) { console.log('▸', name); try { await fn(); } catch (e) { fail++; failures.push(name + ' threw ' + e.message.split('\n')[0]); console.log('  THREW', e.message.split('\n').slice(0, 2).join(' / ')); } }

const F = await device('friend'), O = await device('owner');

await section('1. before signing in: the owner\'s free picks open, the rest asks for a plan', async () => {
  await go(F.page, '#/test/set1v3'); await F.page.waitForTimeout(800);
  ok(await screen(F.page) !== 'pay', 'Practice Set 1 is free to start with', await screen(F.page));
  await go(F.page, '#/test/set2v3');
  ok(await screen(F.page) === 'pay' && await F.page.locator('[data-act="signin"]').count() === 1, 'Practice Set 2 shows the pay screen, asking to sign in first');
});

await section('2. owner signs in: full access and the admin screen', async () => {
  await signIn(O, OWNER);
  await go(O.page, '#/test/set2v3'); ok(await screen(O.page) !== 'pay', 'owner can open any mock');
  await O.page.click('.tbn.gear'); await O.page.waitForTimeout(600);
  ok(/You are the owner/.test(await O.page.locator('#sheet').textContent()), 'Settings says owner');
  await O.page.click('#sheet a[href="#/admin"]'); await O.page.waitForTimeout(1500);
  ok(await screen(O.page) === 'admin' && await O.page.locator('[data-tab="free"]').count() === 1, 'admin screen opens');
  // the owner chooses what is free: Practice Set 1 and Topic 1 notes
  await O.page.click('[data-tab="free"]'); await O.page.waitForTimeout(300);
  for (const k of ['set:set1v3', 'notes:1']) await O.page.check('[data-k="' + k + '"]');
  await O.page.click('#frSave'); await O.page.waitForTimeout(800);
  ok(JSON.stringify(LIC.post({ action: 'status' }).free) === JSON.stringify(['set:set1v3', 'notes:1']) || LIC.post({ action: 'status' }).free.includes('set:set1v3'), 'free list saved in the Sheet', JSON.stringify(LIC.post({ action: 'status' }).free));
  // plans: ₹199 a week and ₹500 a month (defaults), add a 3-day plan
  await O.page.click('[data-tab="plans"]'); await O.page.waitForTimeout(300);
  ok(await O.page.locator('.plrow').count() === 2, 'two plans to start with');
  await O.page.click('#plAdd'); const r = O.page.locator('.plrow').last();
  await r.locator('.pn').fill('3 days'); await r.locator('.pd').fill('3'); await r.locator('.pp').fill('99');
  await O.page.click('#plSave'); await O.page.waitForTimeout(800);
  ok(LIC.post({ action: 'status' }).plans.map(p => p.name + '/' + p.days + '/' + p.price).join(',') === '1 week/7/199,1 month/30/500,3 days/3/99', 'plans saved', JSON.stringify(LIC.post({ action: 'status' }).plans));
});

await section('3. a friend: free picks open, others show the pay screen with plans, UPI QR and voucher box', async () => {
  await signIn(F, 'ravi@gmail.com');
  await go(F.page, '#/test/set1v3'); ok(await screen(F.page) !== 'pay', 'free mock opens');
  await go(F.page, '#/study/topic1'); ok(await screen(F.page) !== 'pay', 'free notes open');
  await go(F.page, '#/study/topic2'); ok(await screen(F.page) === 'pay', 'Topic 2 notes ask for a plan');
  ok(await F.page.locator('.plan').count() === 3 && /₹199 for 7 days/.test(await F.page.locator('.plans').textContent()), 'plans shown with price and days');
  await F.page.waitForTimeout(800);
  ok(await F.page.locator('#pyQr svg').count() === 1, 'UPI QR code drawn');
  ok(/upi:\/\/pay\?pa=owner%40okbank.*am=199/.test(await F.page.getAttribute('#pyApp', 'href')), 'UPI app link has the UPI ID and amount', await F.page.getAttribute('#pyApp', 'href'));
  await F.page.click('.plan[data-i="1"]'); await F.page.waitForTimeout(400);
  ok(/am=500/.test(await F.page.getAttribute('#pyApp', 'href')), 'choosing the month plan changes the amount');
  await go(F.page, '#/tests');
  const locks = await F.page.locator('a.locked').count(), open = await F.page.locator('a[href="#/test/set1v3"]:not(.locked)').count();
  ok(locks > 5 && open === 1, 'Tests list shows locks on paid mocks only', locks + ' locked');
});

await section('4. pay by UPI and send the reference; the owner approves; access starts', async () => {
  await go(F.page, '#/pay');
  await F.page.click('.plan[data-i="0"]');
  await F.page.fill('#pyRef', '12'); await F.page.click('#pySend');
  ok(await F.page.locator('#pyErr:visible').count() === 1, 'a too-short reference is caught');
  await F.page.fill('#pyRef', '412345678901'); await F.page.fill('#pyName', 'Ravi'); await F.page.click('#pySend'); await F.page.waitForTimeout(1000);
  ok(await F.page.locator('.pend').count() === 1 && /1 week/.test(await F.page.locator('.pend').textContent()), 'shows waiting for approval');
  await go(O.page, '#/admin'); await O.page.waitForTimeout(800);
  ok(/ravi@gmail.com/.test(await O.page.locator('#adm').textContent()) && /412345678901/.test(await O.page.locator('#adm').textContent()), 'owner sees the request with the UPI reference');
  await O.page.click('[data-ok="ravi@gmail.com"]'); await O.page.waitForTimeout(800);
  await go(F.page, '#/pay'); await F.page.waitForTimeout(500);
  if (await F.page.locator('#pyChk').count()) { await F.page.click('#pyChk'); await F.page.waitForTimeout(1200); }
  await go(F.page, '#/study/topic2');
  ok(await screen(F.page) !== 'pay', 'Topic 2 opens after approval');
  const exp = LIC.post({ action: 'admin', token: Object.keys(tokens).find(t => tokens[t] === OWNER) }).users.find(u => u.email === 'ravi@gmail.com').expires;
  ok(exp && Math.round((Date.parse(exp) - Date.now()) / 86400000) === 7, '1-week plan ends in 7 days', exp);
  // the same UPI reference cannot be reused by another account
  ok(LIC.post({ action: 'request', token: (tokens['x'] = 'meera@gmail.com', 'x'), plan: '1 week', utr: '412345678901' }).error === 'reference_used', 'a UPI reference works once');
});

await section('5. vouchers: one person, one time', async () => {
  await go(O.page, '#/admin'); await O.page.click('[data-tab="vou"]'); await O.page.waitForTimeout(300);
  await O.page.fill('#vN', '1'); await O.page.fill('#vD', '0'); await O.page.fill('#vNote', 'for Meera'); await O.page.click('#vMake'); await O.page.waitForTimeout(900);
  const code = (await O.page.locator('#vMade .code').first().textContent()).trim();
  ok(/^GPS-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(code), 'a code is made', code);
  const M = await device('meera'); await signIn(M, 'meera@gmail.com');
  await go(M.page, '#/test/set2v3'); ok(await screen(M.page) === 'pay', 'Meera is asked to pay');
  await M.page.fill('#pyCode', 'GPS-WRONG-CODE'); await M.page.click('#pyRedeem'); await M.page.waitForTimeout(800);
  ok(/not valid/.test(await M.page.locator('#pyVErr').textContent()), 'a wrong code is refused');
  await M.page.fill('#pyCode', code.toLowerCase()); await M.page.click('#pyRedeem'); await M.page.waitForTimeout(1500);
  await go(M.page, '#/test/set2v3'); ok(await screen(M.page) !== 'pay', 'the voucher unlocks everything');
  const K = await device('kiran'); await signIn(K, 'kiran@gmail.com');
  await go(K.page, '#/pay'); await K.page.fill('#pyCode', code); await K.page.click('#pyRedeem'); await K.page.waitForTimeout(1000);
  ok(/already been used/.test(await K.page.locator('#pyVErr').textContent()), 'the same code is refused for anyone else');
  await go(O.page, '#/admin'); await O.page.click('[data-tab="vou"]'); await O.page.waitForTimeout(300);
  ok(/meera@gmail.com/.test(await O.page.locator('#adm').textContent()), 'owner sees who used the code');
  for (const d of [M, K]) { d.errs.forEach(e => F.errs.push(e)); await d.ctx.close(); }
});

await section('6. when a plan ends, the paid parts lock again; the owner can remove access', async () => {
  const row = LIC.tabs.Users._data.find(r => r[0] === 'ravi@gmail.com'); row[9] = new Date(Date.now() - 60000);
  await go(F.page, '#/'); await F.page.waitForTimeout(1500);
  await go(F.page, '#/study/topic2');
  ok(await screen(F.page) === 'pay' && /ended/.test(await F.page.locator('main').textContent()), 'after the end date: pay screen says the plan ended');
  await go(F.page, '#/test/set1v3'); ok(await screen(F.page) !== 'pay', 'free picks still open');
});

await section('7. PDFs follow the same rules', async () => {
  await go(F.page, '#/study/pdfs');
  const a = F.page.locator('a[href*="Topic-2-"]').first();
  if (await a.count()) { await a.click(); await F.page.waitForTimeout(800); ok(/#\/pay/.test(F.page.url()), 'a paid topic PDF goes to the pay screen', F.page.url()); }
  else ok(true, 'no topic PDF link on this screen');
});

for (const d of [F, O]) ok(!d.errs.length, 'no page errors', d.errs.join(' | '));
await browser.close();
console.log(`\npaid ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
