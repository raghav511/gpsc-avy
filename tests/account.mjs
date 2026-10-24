// Sign in with Google + sync through the student's own Google Drive. Google is mocked: a fake sign-in page that
// sends the browser straight back with a pass, and a fake Drive shared by two "devices" (two browser contexts).
//   node tests/account.mjs --base http://localhost:8765/gpsc-avy/ --profile ipad|pixel
import fs from 'node:fs';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const prof = args.profile || 'pixel';
const PROFILES = {
  pixel: { engine: 'chromium', viewport: { width: 412, height: 923 }, isMobile: true, hasTouch: true },
  ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true }
};
const { engine, ...opts } = PROFILES[prof];
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const CID = '1234567890-testclient.apps.googleusercontent.com';

// ---- the fake Google: one Drive per email
const drives = {}; const tokens = {}; const log = [];
let deny = false, silentNeedsLogin = false;
async function device(name) {
  const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block' }, opts));
  await ctx.route(/\/js\/config\.js/, r => r.fulfill({ status: 200, contentType: 'text/javascript', body: "export const GOOGLE_CLIENT_ID = '" + CID + "';" }));
  await ctx.route('https://accounts.google.com/**', async r => {
    const u = new URL(r.request().url()); const p = u.searchParams; log.push({ name, auth: Object.fromEntries(p) });
    const back = p.get('redirect_uri') + '#';
    const go = to => r.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><title>Google</title><script>location.replace(' + JSON.stringify(to) + ')</script>' });
    if (deny) return go(back + 'error=access_denied&state=' + p.get('state'));
    if (p.get('prompt') === 'none' && silentNeedsLogin) return go(back + 'error=interaction_required&state=' + p.get('state'));
    const email = p.get('login_hint') || 'friend@gmail.com';
    const t = 'tok-' + Math.random().toString(36).slice(2); tokens[t] = email;
    return go(back + 'access_token=' + t + '&token_type=Bearer&expires_in=3599&scope=' + encodeURIComponent('email openid https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/userinfo.email') + '&state=' + p.get('state'));
  });
  const H = { 'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*' };
  const who = r => tokens[(r.request().headers().authorization || '').replace('Bearer ', '')];
  await ctx.route('https://www.googleapis.com/**', async r => {
    const q = r.request(); if (q.method() === 'OPTIONS') return r.fulfill({ status: 204, headers: H });
    const email = who(r); if (!email) return r.fulfill({ status: 401, headers: H, contentType: 'application/json', body: '{"error":{"code":401}}' });
    const d = drives[email] = drives[email] || { files: {} };
    const u = new URL(q.url());
    log.push({ name, api: q.method() + ' ' + u.pathname, email });
    if (u.pathname === '/oauth2/v3/userinfo') return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: JSON.stringify({ email, sub: 'x' }) });
    if (u.pathname === '/drive/v3/files' && q.method() === 'GET') {
      ok(u.searchParams.get('spaces') === 'appDataFolder', 'Drive listing only looks in the private app folder');
      return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: JSON.stringify({ files: Object.keys(d.files).map(id => ({ id, modifiedTime: '2026-10-24T00:00:00Z' })) }) });
    }
    let m;
    if ((m = /^\/drive\/v3\/files\/([^/]+)$/.exec(u.pathname)) && u.searchParams.get('alt') === 'media') return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: d.files[m[1]] || '{}' });
    if (u.pathname === '/upload/drive/v3/files' && q.method() === 'POST') {
      const body = q.postData(); const meta = JSON.parse(body.split('\r\n\r\n')[1].split('\r\n--')[0]);
      ok(meta.parents && meta.parents[0] === 'appDataFolder' && meta.name === 'gpscavy-progress.json', 'new file goes in the private app folder');
      const id = 'f' + Object.keys(d.files).length; d.files[id] = body.split('\r\n\r\n')[2].split('\r\n--')[0];
      return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: JSON.stringify({ id }) });
    }
    if ((m = /^\/upload\/drive\/v3\/files\/([^/]+)$/.exec(u.pathname)) && q.method() === 'PATCH') { d.files[m[1]] = q.postData(); return r.fulfill({ status: 200, headers: H, contentType: 'application/json', body: '{}' }); }
    return r.fulfill({ status: 404, headers: H, body: '{}' });
  });
  await ctx.route('https://oauth2.googleapis.com/**', r => r.fulfill({ status: 200, headers: H, body: '{}' }));
  const page = await ctx.newPage(); const errs = [];
  page.on('pageerror', e => errs.push(e.message));
  return { ctx, page, errs };
}
const ATT = (id, score) => ({ id, set: 'set3', setName: 'Practice Set 3', score, total: 60, wrong: 60 - score, skipped: 0, usedMs: 1000, auto: false, submittedAt: '2026-10-2' + id.slice(-1) + 'T01:00:00Z', answers: { 1: 'A' } });
const hist = p => p.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1') || '[]').map(a => a.id).sort().join(','));
const waitIdle = p => p.waitForFunction(() => window.__gpsBooted && !document.querySelector('.tbn.syncb.busy'), null, { timeout: 20000 }).then(() => p.waitForTimeout(600));
async function section(name, fn) { console.log('▸', name); try { await fn(); } catch (e) { fail++; failures.push(name + ' threw ' + e.message.split('\n')[0]); console.log('  THREW', e.message.split('\n').slice(0, 2).join(' / ')); } }

const A = await device('phone'), B = await device('ipad');

await section('1. first start: a welcome page with sign-in, or carry on without', async () => {
  await A.page.goto(BASE + '#/'); await A.page.waitForFunction(() => window.__gpsBooted);
  ok(await A.page.locator('.welcome #gwGo').count() === 1 && await A.page.locator('#gwSkip').count() === 1, 'welcome page with Continue with Google and Use without signing in');
  ok(/own Google Drive/.test(await A.page.locator('.welcome').textContent()), 'explains where progress is kept');
  ok(await A.page.locator('#aitab:visible').count() === 0, 'no AI tab on the welcome page');
  const sw = await A.page.evaluate(() => document.getElementById('app').scrollWidth <= document.getElementById('app').clientWidth);
  ok(sw, 'no sideways scroll');
  await A.page.click('#gwSkip'); await A.page.waitForTimeout(500);
  ok(await A.page.locator('.hhead').count() === 1, 'Use without signing in opens Home');
  await A.page.reload(); await A.page.waitForFunction(() => window.__gpsBooted);
  ok(await A.page.locator('.welcome').count() === 0, 'the welcome page does not come back');
  ok(await A.page.getAttribute('.tbn.syncb', 'data-st') === 'off', 'Sync shows not signed in');
});

await section('2. sign in from the Sync button: Google page, back to the same screen, file made in Drive', async () => {
  await A.page.evaluate(a => localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify(a)), [ATT('a1', 40), ATT('a2', 44)]);
  await A.page.goto(BASE + '#/progress'); await A.page.reload(); await A.page.waitForFunction(() => window.__gpsBooted);
  await A.page.click('.tbn.syncb'); await A.page.waitForTimeout(400);
  ok(await A.page.locator('#sheet #gsGo').count() === 1, 'Sync without an account offers sign-in');
  await A.page.fill('#gsE', 'not-an-email'); await A.page.click('#gsGo');
  ok(await A.page.locator('#gsErr:visible').count() === 1, 'a mistyped email is caught');
  await A.page.fill('#gsE', 'ravi@gmail.com');
  await Promise.all([A.page.waitForURL(/#\/progress$/, { timeout: 15000 }), A.page.click('#gsGo')]);
  await waitIdle(A.page);
  const auth = log.filter(l => l.auth).pop().auth;
  ok(auth.client_id === CID && auth.response_type === 'token' && /drive\.appdata/.test(auth.scope) && !/auth\/drive( |$)/.test(auth.scope) && auth.login_hint === 'ravi@gmail.com' && auth.redirect_uri === BASE, 'asks Google only for the private app folder, with the email as a hint', JSON.stringify(auth).slice(0, 300));
  ok(!/access_token/.test(A.page.url()), 'the pass is removed from the address bar', A.page.url());
  const st = await A.page.evaluate(() => [JSON.parse(localStorage.getItem('gpscavy-settings-v1')).account, localStorage.getItem('gpscavy-gtoken') ? 1 : 0]);
  ok(st[0] && st[0].email === 'ravi@gmail.com' && st[1] === 1, 'signed in as ravi@gmail.com');
  const f = drives['ravi@gmail.com'] && Object.values(drives['ravi@gmail.com'].files)[0];
  ok(f && JSON.parse(f).attempts.length === 2, 'progress saved to Ravi\'s Drive', String(f).slice(0, 80));
  ok(f && !/gpscavy-gtoken|AIza|syncUrl/.test(f), 'no pass, keys or sync link in the Drive file');
  ok(await A.page.getAttribute('.tbn.syncb', 'data-st') === 'ok', 'Sync shows synced');
});

await section('3. a second device signs in with the same Gmail and gets everything; both stay in step', async () => {
  await B.page.goto(BASE + '#/'); await B.page.waitForFunction(() => window.__gpsBooted);
  await B.page.evaluate(a => localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify(a)), [ATT('b3', 50)]);
  await B.page.reload(); await B.page.waitForFunction(() => window.__gpsBooted);
  ok(await B.page.locator('.welcome').count() === 0, 'a device that already has attempts skips the welcome page');
  await B.page.click('.tbn.gear'); await B.page.waitForTimeout(500);
  await B.page.click('#sheet [data-act="signin"]'); await B.page.waitForTimeout(400);
  await B.page.fill('#gsE', 'ravi@gmail.com');
  await Promise.all([B.page.waitForURL(/#\/$/, { timeout: 15000 }), B.page.click('#gsGo')]);
  await waitIdle(B.page);
  ok(await hist(B.page) === 'a1,a2,b3', 'iPad has the phone\'s attempts plus its own', await hist(B.page));
  await A.page.click('.tbn.syncb'); await waitIdle(A.page);
  ok(await hist(A.page) === 'a1,a2,b3', 'phone gets the iPad\'s attempt', await hist(A.page));
  ok(JSON.parse(Object.values(drives['ravi@gmail.com'].files)[0]).attempts.length === 3 && Object.keys(drives['ravi@gmail.com'].files).length === 1, 'one file in Drive with all three');
});

await section('3b. saved questions follow the student across devices, and removing one sticks', async () => {
  await B.page.goto(BASE + '#/review/b3'); await B.page.waitForTimeout(1500);
  await B.page.locator('.savb').first().click(); await B.page.waitForTimeout(300);
  const ref = await B.page.locator('.savb').first().getAttribute('data-save');
  await B.page.click('.tbn.syncb'); await waitIdle(B.page);
  await A.page.click('.tbn.syncb'); await waitIdle(A.page);
  const onA = await A.page.evaluate(r => { const m = JSON.parse(localStorage.getItem('gpscavy-saved-v1') || '{}'); return m[r] && !m[r].off; }, ref);
  ok(onA, 'a question saved on the iPad is saved on the phone after sync', ref);
  await A.page.goto(BASE + '#/study/saved'); await A.page.waitForTimeout(1500);
  ok(await A.page.locator('.rev').count() === 1, 'it is listed in Study, Saved');
  await A.page.locator('.savb').first().click(); await A.page.waitForTimeout(300);
  await A.page.click('.tbn.syncb'); await waitIdle(A.page);
  await B.page.click('.tbn.syncb'); await waitIdle(B.page);
  const onB = await B.page.evaluate(r => { const m = JSON.parse(localStorage.getItem('gpscavy-saved-v1') || '{}'); return m[r] && !m[r].off; }, ref);
  ok(!onB, 'removing it on the phone removes it on the iPad too');
});

await section('4. another friend has a separate Drive: nothing mixes', async () => {
  const C = await device('friend');
  await C.page.goto(BASE + '#/'); await C.page.waitForFunction(() => window.__gpsBooted);
  await C.page.fill('#gwE', 'meera@gmail.com');
  await Promise.all([C.page.waitForURL(/#\/$/, { timeout: 15000 }), C.page.click('#gwGo')]);
  await waitIdle(C.page);
  ok(await hist(C.page) === '' && await C.page.locator('.hhead').count() === 1, 'Meera starts empty, on Home');
  ok(drives['meera@gmail.com'] && JSON.parse(Object.values(drives['meera@gmail.com'].files)[0]).attempts.length === 0 && JSON.parse(Object.values(drives['ravi@gmail.com'].files)[0]).attempts.length === 3, 'Ravi\'s and Meera\'s files are separate');
  await C.ctx.close();
});

await section('5. after Google\'s one-hour pass runs out: Sync signs in again by itself, no password', async () => {
  await A.page.evaluate(() => { const t = JSON.parse(localStorage.getItem('gpscavy-gtoken')); t.exp = Date.now() - 1000; localStorage.setItem('gpscavy-gtoken', JSON.stringify(t)); });
  await A.page.evaluate(a => { const h = JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')); h.push(a); localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify(h)); }, ATT('a4', 55));
  await A.page.goto(BASE + '#/tests'); await A.page.reload(); await A.page.waitForFunction(() => window.__gpsBooted); await A.page.waitForTimeout(1500);
  const n0 = log.filter(l => l.auth).length;
  ok(n0 === log.filter(l => l.auth).length, 'opening the app does not jump to Google by itself');
  await Promise.all([A.page.waitForURL(/#\/tests$/, { timeout: 15000 }), A.page.click('.tbn.syncb')]);
  await waitIdle(A.page);
  const auth = log.filter(l => l.auth).pop().auth;
  ok(auth.prompt === 'none' && auth.login_hint === 'ravi@gmail.com', 'quick sign-in (prompt=none) with the saved email', JSON.stringify(auth).slice(0, 200));
  ok(JSON.parse(Object.values(drives['ravi@gmail.com'].files)[0]).attempts.length === 4, 'then synced: the new attempt is in Drive');
  // Google needs the student after all (signed out of Google): its page is shown
  silentNeedsLogin = true;
  await A.page.evaluate(() => { const t = JSON.parse(localStorage.getItem('gpscavy-gtoken')); t.exp = Date.now() - 1000; localStorage.setItem('gpscavy-gtoken', JSON.stringify(t)); });
  const n1 = log.filter(l => l.auth).length;
  await A.page.click('.tbn.syncb'); await A.page.waitForTimeout(4000); await waitIdle(A.page);
  const two = log.filter(l => l.auth).slice(n1).map(l => l.auth.prompt || 'normal');
  ok(two.join(',') === 'none,normal', 'when the quick sign-in needs the student, Google\'s page is shown', two.join(','));
  silentNeedsLogin = false;
});

await section('6. cancelled sign-in, sign out, and progress is never lost', async () => {
  await A.page.click('.tbn.gear'); await A.page.waitForTimeout(500);
  ok(/Signed in as ravi@gmail.com/.test(await A.page.locator('#sheet').textContent()), 'Settings shows who is signed in');
  await A.page.click('#stOut'); await A.page.click('#stOutGo'); await A.page.waitForTimeout(600);
  const st = await A.page.evaluate(() => [JSON.parse(localStorage.getItem('gpscavy-settings-v1')).account, localStorage.getItem('gpscavy-gtoken'), JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length]);
  ok(!st[0] && !st[1] && st[2] === 4, 'signed out, attempts kept on the device', JSON.stringify(st));
  await A.page.keyboard.press('Escape');
  deny = true;
  await A.page.click('.tbn.syncb'); await A.page.waitForTimeout(300); await A.page.fill('#gsE', 'ravi@gmail.com');
  await Promise.all([A.page.waitForURL(/#\//, { timeout: 15000 }), A.page.click('#gsGo')]); await A.page.waitForTimeout(1500);
  ok(/cancelled/i.test(await A.page.locator('#toast').textContent()) && await hist(A.page) === 'a1,a2,a4,b3', 'a cancelled sign-in is explained; nothing lost', await A.page.locator('#toast').textContent());
  deny = false;
});

for (const d of [A, B]) ok(!d.errs.length, 'no page errors', d.errs.join(' | '));
await browser.close();
console.log(`\naccount ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
