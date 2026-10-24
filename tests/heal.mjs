// Self-repair tests: the app must start, or repair itself, whatever state the device's copy is in.
// Progress (localStorage) must survive every repair.
//   node tests/heal.mjs --base http://localhost:8765/gpsc-avy/ --profile ipad|pixel
// Needs the service worker, so the base must be served over http://localhost (a secure context).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const prof = args.profile || 'ipad';
const PROFILES = {
  pixel: { engine: 'chromium', viewport: { width: 412, height: 923 }, isMobile: true, hasTouch: true },
  ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, hasTouch: true }
};
const { engine, ...opts } = PROFILES[prof];
const V = JSON.parse(fs.readFileSync(path.join(ROOT, 'version.json'), 'utf8')).v;
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };
const browser = await PW[engine].launch(engine === 'chromium' && fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const ATT = JSON.stringify([{ id: 'set3-1', set: 'set3', setName: 'Practice Set 3', score: 41, total: 60, wrong: 19, skipped: 0, usedMs: 1, auto: false, submittedAt: '2026-10-23T01:00:00Z', answers: { 1: 'A' } }]);
const state = p => p.evaluate(() => ({ booted: !!window.__gpsBooted, v: (document.querySelector('meta[name="gps-v"]') || {}).content, screen: document.body.dataset.screen, repair: !!document.querySelector('#fixGo'),
  kept: (localStorage.getItem('gpsc-cbrt-history-v1') || '').includes('set3-1') && (localStorage.getItem('gpscavy-ai-v1') || '').includes('AIzaKEEP') })).catch(e => ({ err: e.message }));
async function fresh() {
  const ctx = await browser.newContext(opts); await ctx.addInitScript(() => { window.__gpscTest = 1; }); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.goto(BASE + '#/');
  await p.evaluate(a => { localStorage.setItem('gpsc-cbrt-history-v1', a); localStorage.setItem('gpscavy-ai-v1', JSON.stringify({ key: 'AIzaKEEP0123456789abcdefghijklmn' })); localStorage.setItem('gpscavy-settings-v1', '{"a2hs":1,"welcomed":1}'); }, ATT);
  await p.waitForFunction(() => navigator.serviceWorker && navigator.serviceWorker.controller, null, { timeout: 30000 }).catch(() => { });
  await p.reload(); await p.waitForFunction(() => window.__gpsBooted, null, { timeout: 30000 });
  return { ctx, p, errs };
}
async function waitFor(p, cond, ms) { const t0 = Date.now(); let s; while (Date.now() - t0 < ms) { s = await state(p); if (cond(s)) return [s, (Date.now() - t0) / 1000]; await p.waitForTimeout(500); } return [s, ms / 1000]; }
async function section(name, fn) { console.log('▸', name); try { await fn(); } catch (e) { fail++; failures.push(name + ' threw ' + e.message.split('\n')[0]); console.log('  THREW', e.message.split('\n').slice(0, 2).join(' / ')); } }

await section('1. normal start: current version, controlled by the service worker', async () => {
  const { ctx, p, errs } = await fresh();
  const s = await state(p);
  ok(s.booted && s.v === V && s.screen === 'home', 'starts on Home with version ' + V, JSON.stringify(s));
  const mods = await p.evaluate(() => performance.getEntriesByType('resource').map(e => e.name).filter(n => /\/js\/[a-z]+\.js/.test(n)));
  ok(mods.length && mods.every(n => n.includes('?v=' + V)), 'every module is loaded with this version in its URL', mods.join(' '));
  ok(!errs.length, 'no page errors', errs.join(' | '));
  await ctx.close();
});

await section('2. a cached module from another version: repairs itself, progress kept', async () => {
  const { ctx, p } = await fresh();
  await p.evaluate(async v => { const c = await caches.open(v); const ks = await c.keys(); const k = ks.find(r => /js\/core\.js/.test(r.url)); await c.put(k, new Response('export const nope = 1;', { headers: { 'content-type': 'text/javascript' } })); }, V);
  await p.reload();
  const [s, t] = await waitFor(p, s => s.booted, 30000);
  ok(s.booted && s.screen === 'home', 'the app starts again by itself', JSON.stringify(s) + ' after ' + t + ' s');
  ok(s.kept, 'attempts and AI key kept');
  await ctx.close();
});

await section('3. app files cannot load: two automatic tries, then the Repair screen; Repair works once files load', async () => {
  const { ctx, p } = await fresh();
  let block = true;
  await ctx.route(/\/js\/app\.js/, r => block ? r.abort() : r.continue());
  await p.evaluate(async () => { for (const k of await caches.keys()) await caches.delete(k); for (const r of await navigator.serviceWorker.getRegistrations()) await r.unregister(); });
  await p.reload();
  const [s, t] = await waitFor(p, s => s.repair, 45000);
  ok(s.repair, 'Repair screen shown after the automatic tries', t + ' s ' + JSON.stringify(s));
  ok(s.kept, 'progress kept on the Repair screen');
  ok(/progress is safe/i.test(await p.locator('#app').textContent()), 'says the progress is safe');
  block = false;
  await p.click('#fixGo');
  const [s2, t2] = await waitFor(p, s => s.booted, 30000);
  ok(s2.booted && s2.kept, 'Repair opens the app, progress kept', t2 + ' s');
  await ctx.close();
});

await section('4. offline launch uses the saved copy and never wipes it', async () => {
  const { ctx, p } = await fresh();
  await p.waitForTimeout(1500);
  await ctx.setOffline(true);
  await p.reload().catch(() => { });
  const [s] = await waitFor(p, s => s.booted, 20000);
  ok(s.booted && s.screen === 'home', 'opens offline', JSON.stringify(s));
  const n = await p.evaluate(async () => (await caches.keys()).filter(k => k.startsWith('gpscavy-')).length);
  ok(n >= 1, 'offline copy still there');
  await ctx.setOffline(false); await ctx.close();
});

await section('5. the website has a newer version but this copy does not get it: it fetches it by itself', async () => {
  const { ctx, p } = await fresh();
  // the website (this folder) now says a newer version exists, but its files are unchanged
  const VJ = path.join(ROOT, 'version.json'), keep = fs.readFileSync(VJ, 'utf8');
  fs.writeFileSync(VJ, JSON.stringify({ v: 'gpscavy-newer00001' }));
  try {
  await p.reload();
  const [s, t] = await waitFor(p, s => false, 32000);
  const forced = await p.evaluate(() => localStorage.getItem('gpscavy-forced'));
  ok(forced && forced.includes('gpscavy-newer00001'), 'a fresh copy was fetched', String(forced));
  const [s2] = await waitFor(p, s => s.booted, 20000);
  ok(s2.booted && s2.kept, 'the app is running afterwards, progress kept', JSON.stringify(s2));
  // only once per half hour for the same version: no loop
  await p.reload(); await p.waitForTimeout(30000);
  const f2 = await p.evaluate(() => JSON.parse(localStorage.getItem('gpscavy-forced')));
  ok(JSON.parse(forced).at === f2.at, 'does not keep re-fetching in a loop');
  } finally { fs.writeFileSync(VJ, keep); }
  await ctx.close();
});

await section('6. Settings, Repair app: a fresh copy, progress kept', async () => {
  const { ctx, p } = await fresh();
  await p.click('.tbn.gear'); await p.waitForTimeout(600);
  await p.click('#stFix'); await p.click('#stFixGo');
  await p.waitForTimeout(1500);
  const [s] = await waitFor(p, s => s.booted, 30000);
  ok(s.booted && s.kept && /fresh=/.test(p.url()), 'repaired and back on Home, progress kept', p.url());
  await ctx.close();
});

await browser.close();
console.log(`\nheal ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
