// Reset that sticks. The bug: Practice Set 1/2 showed Resume again after "Reset and exit", because the sync folder
// still had the unfinished test and the next sync brought it back. Here the sync link is a stubborn fake that always
// returns what it has ever been sent (an old server without tombstones), the worst case.
//   node tests/reset.mjs --base http://localhost:8765/gpsc-avy/ --profile pixel|ipad
import fs from 'node:fs';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const prof = args.profile || 'pixel';
const PROFILES = { pixel: { engine: 'chromium', viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true }, ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true } };
const { engine, ...opts } = PROFILES[prof];
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const HUB = 'https://script.google.com/macros/s/HUBTEST/exec';
const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block' }, opts));
const T0 = Date.now() - 3600000;
const st = (set, n) => ({ set, phase: 'exam', startedAt: T0, savedAt: T0 + 1000, endAt: Date.now() + 3000000, paused: true, remainMs: 3000000, cur: 3, answers: Object.fromEntries(Array.from({ length: n }, (_, i) => [i + 1, 'A'])), flags: {}, mode: 'exam' });
// the stubborn hub: remembers everything it is sent, forgets nothing
const hub = { format: 'gpsc-cbrt-progress', version: 1, attempts: [], inProgress: [st('set1v3', 7), st('set2v3', 4)], customTests: [] };
await ctx.route(HUB + '*', async r => {
  const b = JSON.parse(r.request().postData() || '{}').progress;
  if (b) { b.attempts.forEach(a => { if (!hub.attempts.some(x => x.id === a.id)) hub.attempts.push(a); }); (b.inProgress || []).forEach(s => { if (!hub.inProgress.some(x => x.set === s.set && x.startedAt === s.startedAt)) hub.inProgress.push(s); }); }
  r.fulfill({ status: 200, headers: { 'access-control-allow-origin': '*' }, contentType: 'application/json', body: JSON.stringify({ ok: true, progress: hub }) });
});
await ctx.addInitScript(([h, a]) => { if (location.protocol === 'about:') return; if (!localStorage.getItem('gpscavy-settings-v1')) localStorage.setItem('gpscavy-settings-v1', JSON.stringify({ a2hs: 1, welcomed: 1, syncUrl: h })); if (!localStorage.getItem('gpsc-cbrt-history-v1')) localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify([a])); },
  [HUB, { id: 'set3-' + T0, set: 'set3', setName: 'Practice Set 3', score: 41, total: 60, wrong: 19, skipped: 0, usedMs: 1, auto: false, submittedAt: new Date(T0).toISOString(), answers: { 1: 'A' } }]);
const page = await ctx.newPage(); const errs = [];
page.on('pageerror', e => errs.push(e.message));
const go = async h => { await page.goto('about:blank'); await page.goto(BASE + h); await page.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }); await page.waitForTimeout(900); };
const sync = async () => { await page.click('.tbn.syncb'); await page.waitForFunction(() => !document.querySelector('.tbn.syncb.busy'), null, { timeout: 15000 }); await page.waitForTimeout(800); };
const live = id => page.evaluate(i => { const s = JSON.parse(localStorage.getItem('gpsc-cbrt-' + i + '-v1') || 'null'); return !!(s && s.phase === 'exam'); }, id);
async function section(name, fn) { console.log('▸', name); try { await fn(); } catch (e) { fail++; failures.push(name + ' threw ' + e.message.split('\n')[0]); console.log('  THREW', e.message.split('\n').slice(0, 2).join(' / ')); } }

await section('1. the sync link hands back Practice Sets 1 and 2 in progress', async () => {
  await go('#/tests'); await sync();
  ok(await live('set1v3') && await live('set2v3'), 'both show as in progress after a sync');
  ok(await page.locator('.rwrap:has(a[href="#/test/set1v3"]) .rstb').count() === 1, 'a Reset button sits next to Resume');
});

await section('2. Reset and exit inside the test stays reset after syncing (the reported bug)', async () => {
  await go('#/test/set1v3'); await page.waitForTimeout(500);
  // open the test (resume) then leave with Reset and exit
  const res = page.locator('#rGo, .wide.pri:has-text("Resume"), a:has-text("Resume")').first(); if (await res.count()) { await res.click(); await page.waitForTimeout(800); }
  await page.click('#rBack'); await page.waitForTimeout(400);
  await page.click('#lReset'); await page.waitForTimeout(300); await page.click('#rDo'); await page.waitForTimeout(1200);
  ok(!(await live('set1v3')), 'cleared on this device');
  await go('#/tests'); await sync(); await sync();
  ok(!(await live('set1v3')), 'still reset after two syncs with the stubborn sync link');
  ok(await page.locator('a[href="#/test/set1v3"] .pill-res').count() === 0, 'no Resume on Practice Set 1');
});

await section('3. Reset from the Tests list: in progress, and a scored test', async () => {
  await go('#/tests');
  await page.click('.rwrap:has(a[href="#/test/set2v3"]) .rstb'); await page.waitForTimeout(400);
  ok(await page.locator('#sheet #rsProg').count() === 1, 'reset sheet offers to clear the unfinished attempt');
  await page.click('#rsGo'); await page.waitForTimeout(800);
  ok(!(await live('set2v3')), 'Practice Set 2 cleared');
  await sync();
  ok(!(await live('set2v3')) && await page.locator('a[href="#/test/set2v3"] .pill-res').count() === 0, 'and stays cleared after sync');
  // a scored test
  const row = page.locator('.rwrap:has(a[href="#/test/set3"]) .rstb');
  ok(await row.count() === 1, 'a scored test also has a Reset button');
  await row.click(); await page.waitForTimeout(400);
  ok(await page.locator('#sheet #rsAtt:checked').count() === 1 && /41\/60/.test(await page.locator('#sheet').textContent()), 'offers to remove the scored attempt (41/60)');
  await page.click('#rsGo'); await page.waitForTimeout(800);
  ok(await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length) === 0, 'attempt removed');
  ok(await page.locator('a[href="#/test/set3"] .pill-go').count() === 1, 'Practice Set 3 shows Start again');
  // undo brings it back
  await page.click('#toast button'); await page.waitForTimeout(800);
  ok(await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length) === 1, 'Undo brings the score back');
  await page.locator('.rwrap:has(a[href="#/test/set3"]) .rstb').click(); await page.waitForTimeout(300); await page.click('#rsGo'); await page.waitForTimeout(800);
  await sync(); await sync();
  ok(await page.evaluate(() => JSON.parse(localStorage.getItem('gpsc-cbrt-history-v1')).length) === 0, 'a removed score stays removed after syncing');
});

await section('4. Home: Resume card has Reset too', async () => {
  await page.evaluate(s => localStorage.setItem('gpsc-cbrt-set5-v1', JSON.stringify(s)), st('set5', 2));
  await go('#/');
  ok(await page.locator('.home-rw .rstb').count() === 1, 'Reset next to the Resume card');
  await page.click('.home-rw .rstb'); await page.waitForTimeout(300); await page.click('#rsGo'); await page.waitForTimeout(800);
  ok(await page.locator('.resume').count() === 0, 'Resume card gone after reset');
});

ok(!errs.length, 'no page errors', errs.join(' | '));
await browser.close();
console.log(`\nreset ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
