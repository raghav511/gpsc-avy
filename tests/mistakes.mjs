// Practise your mistakes: the Home box, the Progress list, Study → Revise incorrect, and the practise screen.
//   node tests/mistakes.mjs --base http://localhost:8765/gpsc-avy/ --profile pixel|ipad
import fs from 'node:fs';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base, prof = args.profile || 'pixel';
const PROFILES = { pixel: { engine: 'chromium', viewport: { width: 412, height: 915 }, isMobile: true, hasTouch: true }, ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true } };
const { engine, ...opts } = PROFILES[prof];
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block' }, opts));
await ctx.addInitScript(() => { if (location.protocol === 'about:') return; window.__gpscTest = 1; if (localStorage.getItem('seeded')) return;
  localStorage.setItem('gpscavy-settings-v1', JSON.stringify({ a2hs: 1, welcomed: 1 }));
  const ans = {}; for (let i = 1; i <= 60; i++) ans[i] = 'A';
  localStorage.setItem('gpsc-cbrt-history-v1', JSON.stringify([{ id: 'a1', set: 'set2', answers: ans, submittedAt: new Date(Date.now() - 864e5).toISOString(), score: 15, total: 60 }, { id: 'a2', set: 'set3', answers: ans, submittedAt: new Date().toISOString(), score: 15, total: 60 }]));
  localStorage.setItem('seeded', 1); });
const page = await ctx.newPage(); const errs = []; page.on('pageerror', e => errs.push(e.message));
const go = async h => { await page.goto('about:blank'); await page.goto(BASE + h); await page.waitForFunction(() => window.__gpsBooted, null, { timeout: 20000 }); await page.waitForTimeout(1500); };
const def = () => page.evaluate(() => { const id = location.hash.split('?')[0].slice(7); return (JSON.parse(localStorage.getItem('gpscavy-custom-v1') || '{}'))[id]; });
const wrongN = await (async () => { await go('#/study/wrong'); return +(await page.locator('.fchip.wrongc').textContent()).replace(/\D+/g, ''); })();
ok(wrongN > 0, 'there are wrong answers to practise', String(wrongN));

// Home: a small closed box; tapping opens the subjects and the button
await go('#/');
ok(await page.locator('details.mfix').count() === 1 && !(await page.locator('details.mfix').getAttribute('open') !== null), 'Home box starts closed');
ok(!(await page.locator('.mfix [data-mf="all"]').isVisible()), 'practise button hidden while closed');
await page.click('.mfix summary'); await page.waitForTimeout(300);
ok(await page.locator('.mfix [data-mf="all"]').isVisible(), 'tapping the box shows the practise button');
const chips = await page.$$eval('.mfix .mfc', cs => cs.map(c => +c.textContent.replace(/.*· /, '')));
ok(chips.reduce((a, b) => a + b, 0) === wrongN, 'subject counts add up to the total', chips.join('+') + ' vs ' + wrongN);
ok((await page.locator('.mfix summary').textContent()).includes(String(wrongN)), 'box shows the total');

// a subject: only that subject, learn mode by default, 10 picked
await page.click('.mfix [data-mf="gk"]'); await page.waitForTimeout(300);
ok(await page.locator('#sheet [data-mode="learn"].on').count() === 1, 'learn mode is the default');
await page.click('#mfHow [data-how="10"]'); await page.click('#mfGo'); await page.waitForTimeout(1500);
let d = await def();
ok(d && d.refs.length === 10 && d.refs.every(r => r[1] === 'gk') && d.mode === 'learn', 'GK practice: 10 GK questions in learn mode', d && JSON.stringify([d.refs.length, d.mode]));

// Progress: a core topic row starts a timed test of that topic only
await go('#/progress');
const tbtn = page.locator('#pm [data-mf="core"][data-t]').first(); const t = +(await tbtn.getAttribute('data-t'));
await tbtn.click(); await page.waitForTimeout(300);
ok(await page.locator('#sheet input:checked').count() === 1, 'a topic row ticks just that topic');
await page.click('[data-mode="exam"]'); await page.click('#mfGo'); await page.waitForTimeout(1500);
d = await def();
ok(d && d.mode === 'exam' && d.refs.every(r => r[1] === 'core'), 'timed core-topic test', d && d.mode);

// "Practise all" with one subject unticked
await go('#/progress');
await page.click('#pm [data-mf="all"]'); await page.waitForTimeout(300);
await page.uncheck('#sheet input[data-k="gk"]'); await page.click('#mfGo'); await page.waitForTimeout(1500);
d = await def();
ok(d && d.refs.length > 0 && !d.refs.some(r => r[1] === 'gk'), 'unticked subject left out');

// Study → Revise incorrect opens the same screen; core shows topic buttons
await go('#/study/wrong/core');
ok(await page.locator('[data-wt]').count() > 0, 'core topic buttons in Revise incorrect');
await page.click('#wtest'); await page.waitForTimeout(300);
ok(await page.locator('#sheet #mfGo').count() === 1, 'Revise incorrect opens the practise screen');
await go('#/study/wrong');
ok(await page.locator('.schip2[href="#/study/wrong/lr"]').count() === 1, 'Reasoning filter in Revise incorrect');
ok(!errs.length, 'no page errors', errs.join(' | '));
await browser.close();
console.log(`\nmistakes ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
