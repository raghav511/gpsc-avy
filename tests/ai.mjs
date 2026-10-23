// Ask Gemini tests. The Gemini API is mocked: no key or network needed.
//   node tests/ai.mjs --base http://localhost:8765/gpsc-avy/ --profile pixel|ipad
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const PROFILES = {
  pixel: { viewport: { width: 412, height: 923 }, deviceScaleFactor: 2.625, isMobile: true, hasTouch: true, userAgent: 'Mozilla/5.0 (Linux; Android 16; Pixel 10a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36' },
  ipad: { engine: 'webkit', viewport: { width: 810, height: 1080 }, deviceScaleFactor: 2, isMobile: false, hasTouch: true, userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15' },
  ipadland: { engine: 'webkit', viewport: { width: 1080, height: 810 }, deviceScaleFactor: 2, isMobile: false, hasTouch: true },
  iphone: { viewport: { width: 375, height: 667 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true }
};
const prof = args.profile || 'pixel';
const { engine = 'chromium', ...opts } = PROFILES[prof];
let pass = 0, fail = 0; const failures = [];
const ok = (c, name, extra) => { if (c) pass++; else { fail++; failures.push(name + (extra ? ' :: ' + extra : '')); console.log('  FAIL', name, extra || ''); } };

const browser = await PW[engine].launch();
const ctx = await browser.newContext(Object.assign({ serviceWorkers: 'block' }, opts));
// fakes: speech recognition (switchable), and a microphone recorder that yields a short real WAV
await ctx.addInitScript(() => {
  window.__gpscTest = 1;
  window.__srMode = 'none';
  const realSR = window.SpeechRecognition || window.webkitSpeechRecognition;
  class FakeSR { constructor() { this.lang = ''; } start() { setTimeout(() => {
    if (window.__srMode === 'fail') { this.onerror && this.onerror({ error: 'service-not-allowed' }); this.onend && this.onend(); return; }
    const r = [{ 0: { transcript: 'what is the keynote of ledum' }, isFinal: true, length: 1 }];
    this.onresult && this.onresult({ results: r }); this.onend && this.onend(); }, 120); } stop() { } }
  Object.defineProperty(window, 'webkitSpeechRecognition', { get: () => window.__srMode === 'none' ? undefined : FakeSR, configurable: true });
  Object.defineProperty(window, 'SpeechRecognition', { get: () => window.__srMode === 'none' ? undefined : FakeSR, configurable: true });
  const wav = () => { const n = 8000, b = new ArrayBuffer(44 + n * 2), v = new DataView(b); const w = (o, s) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
    w(0, 'RIFF'); v.setUint32(4, 36 + n * 2, true); w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true); v.setUint32(24, 8000, true); v.setUint32(28, 16000, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, n * 2, true);
    for (let i = 0; i < n; i++) v.setInt16(44 + i * 2, Math.sin(i / 3) * 8000, true); return new Blob([b], { type: 'audio/wav' }); };
  const gum = async () => ({ getTracks: () => [{ stop() { } }] });
  try { Object.defineProperty(navigator, 'mediaDevices', { value: { getUserMedia: gum }, configurable: true }); } catch (e) { navigator.mediaDevices.getUserMedia = gum; }
  window.MediaRecorder = class { constructor() { this.state = 'inactive'; this.mimeType = 'audio/wav'; } static isTypeSupported() { return false; }
    start() { this.state = 'recording'; } stop() { this.state = 'inactive'; this.ondataavailable && this.ondataavailable({ data: wav() }); setTimeout(() => this.onstop && this.onstop(), 10); } };
});
const reqs = [];
let reply = { status: 200, text: '**Ledum** keynote: punctured wounds that are *cold to touch*, better by cold.\n\n- Insect stings\n- Black eye' };
await ctx.route('https://generativelanguage.googleapis.com/**', async r => {
  const body = JSON.parse(r.request().postData() || '{}');
  reqs.push({ url: r.request().url(), key: r.request().headers()['x-goog-api-key'], body });
  if (reply.status !== 200) return r.fulfill({ status: reply.status, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ error: { message: reply.msg || 'error' } }) });
  const chunks = reply.text.match(/[\s\S]{1,25}/g).map(t => 'data: ' + JSON.stringify({ candidates: [{ content: { role: 'model', parts: [{ text: t }] } }] }) + '\r\n\r\n').join('');
  return r.fulfill({ status: 200, headers: { 'content-type': 'text/event-stream', 'access-control-allow-origin': '*' }, body: chunks });
});
const page = await ctx.newPage();
const errors = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
const open = async h => { await page.goto('about:blank'); await page.goto(BASE + h); await page.waitForLoadState('networkidle'); await page.waitForTimeout(450); };
const settle = (ms = 350) => page.waitForTimeout(ms);
const lastReq = () => reqs[reqs.length - 1];
const userParts = r => r.body.contents.filter(c => c.role === 'user').pop().parts;
async function section(name, fn) { console.log('▸', name); try { await fn(); } catch (e) { fail++; failures.push(name + ' threw ' + e.message.split('\n')[0]); console.log('  THREW', e.message.split('\n').slice(0, 3).join(' / ')); try { await page.screenshot({ path: '/tmp/claude-0/aifail.png' }); console.log('  at', page.url()); } catch (x) { } } }

// ---------------------------------------------------------------
await section('1. the tab is on every screen and never covers content', async () => {
  const screens = ['#/', '#/tests', '#/tests/level', '#/study', '#/study/core', '#/progress', '#/study/topic1', '#/study/topic6', '#/study/topic9', '#/study/playbook/gk', '#/study/papers', '#/search?q=ledum', '#/test/set14', '#/drills/gk', '#/custom'];
  for (const h of screens) {
    await open(h);
    if (h === '#/test/set14') { await page.click('#go'); await settle(900); }
    for (const y of [0, 600, 1800]) {
      await page.evaluate(y => document.getElementById('app').scrollTo(0, y), y); await settle(450);
      const r = await page.evaluate(() => {
        const t = document.getElementById('aitab'); if (!t) return { missing: true };
        const b = t.getBoundingClientRect(); const over = [];
        for (let x = b.left + 1; x < b.right; x += 3) for (let yy = b.top + 1; yy < b.bottom; yy += 5) {
          const e = document.elementsFromPoint(x, yy).find(e => e !== t && !t.contains(e));
          if (e && !e.matches('html,body,#app,main,.pad,.notes,#nb,.ns,.nb,.stack')) over.push(e.className || e.tagName);
        }
        return { vis: b.width > 5 && getComputedStyle(t).display !== 'none', w: b.width, right: Math.round(innerWidth - b.right), over: [...new Set(over)] };
      });
      ok(!r.missing && r.vis, 'tab visible ' + h + ' @' + y, JSON.stringify(r));
      ok(r.over && !r.over.length, 'tab covers nothing ' + h + ' @' + y, JSON.stringify(r.over));
      ok(r.right === 0 && r.w <= 22, 'tab sits in the margin ' + h, JSON.stringify(r));
    }
  }
});

await section('2. menu: three ways to ask; Escape closes; sheet hides the tab', async () => {
  await open('#/study/topic9');
  await page.click('#aitab'); await settle();
  const modes = await page.$$eval('#aimenu [data-mode]', bs => bs.map(b => b.dataset.mode + ':' + b.textContent.trim()));
  ok(modes.join() === 'text:Type,voice:Speak,camera:Camera', 'menu shows Type, Speak, Camera', modes.join());
  const sizes = await page.$$eval('#aimenu button', bs => bs.map(b => b.getBoundingClientRect().height));
  ok(sizes.every(h => h >= 44), 'menu buttons are big enough to tap', sizes.join());
  await page.keyboard.press('Escape'); await settle();
  ok(await page.locator('#aimenu').count() === 0, 'Escape closes the menu');
  await page.click('#aitab'); await settle();
  await page.mouse.click(40, 300); await settle();
  ok(await page.locator('#aimenu').count() === 0, 'tapping elsewhere closes the menu');
});

await section('3. first use asks for a key; the key stays on this device', async () => {
  await page.evaluate(() => localStorage.removeItem('gpscavy-ai-v1'));
  await open('#/study/topic9');
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle();
  ok(await page.locator('#sheet:has-text("Connect Gemini")').count() === 1, 'connect sheet shown without a key');
  ok(await page.locator('#sheet a[href="https://aistudio.google.com/apikey"]').count() === 1, 'links to Google AI Studio for a key');
  await page.fill('#aiKey', 'nope'); await page.click('#aiSave'); await settle();
  ok(await page.locator('#aiKeyErr:visible').count() === 1, 'rejects something that is not a key');
  await page.fill('#aiKey', 'AIzaSyTESTKEY0123456789abcdefghijkl'); await page.click('#aiSave'); await settle(600);
  ok(await page.locator('.aisheet').count() === 1, 'saving the key opens the assistant');
  const st = await page.evaluate(() => [localStorage.getItem('gpscavy-ai-v1'), localStorage.getItem('gpscavy-settings-v1') || '']);
  ok(st[0].includes('AIzaSyTESTKEY') && !st[1].includes('AIza'), 'key stored apart from settings (never exported or synced)');
  await page.keyboard.press('Escape'); await settle();
});

await section('4. text question about the page: page sent once, streamed answer, follow-up', async () => {
  reqs.length = 0;
  await open('#/study/topic9');
  await page.evaluate(() => { const s = document.querySelector('.ns[id^="92-"]'); document.getElementById('app').scrollTo(0, s.getBoundingClientRect().top + document.getElementById('app').scrollTop - 100); });
  await settle(500);
  await page.evaluate(() => { const s = document.querySelector('.ns[id^="92-"]'); document.getElementById('app').scrollTo(0, s.getBoundingClientRect().top + document.getElementById('app').scrollTop - 100); }); // again, once off-screen sections have laid out
  await settle(500);
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle(500);
  const chip = await page.locator('#aiCtx').textContent();
  ok(/Traumatology/.test(chip), 'context chip names the section on screen', chip);
  ok(await page.evaluate(() => document.activeElement && document.activeElement.id) === 'aiIn', 'Type mode focuses the box');
  ok(await page.locator('#aitab').isHidden(), 'tab hides while the panel is open');
  await page.fill('#aiIn', 'What is the keynote of Ledum?'); await page.keyboard.press('Enter');
  await page.waitForSelector('.aim.model .aimd b', { timeout: 8000 }); await settle(400);
  const r = lastReq();
  ok(r && /:streamGenerateContent\?alt=sse$/.test(r.url) && r.key === 'AIzaSyTESTKEY0123456789abcdefghijkl' && !r.url.includes('AIza'), 'calls Gemini with the key in a header, not the URL', r && r.url);
  const up = userParts(r).map(p => p.text || '').join('\n');
  ok(/Traumatology/.test(up) && /fracture/i.test(up) && /keynote of Ledum/.test(up), 'question carries the page text', up.slice(0, 120));
  ok(r.body.systemInstruction && /GPSC/.test(r.body.systemInstruction.parts[0].text), 'system instruction set for the exam');
  const ans = await page.locator('.aim.model').last().innerHTML();
  ok(/<b>Ledum<\/b>/.test(ans) && /<li>Insect stings<\/li>/.test(ans) && /<i>cold to touch<\/i>/.test(ans), 'answer rendered with bold, italics and a list', ans.slice(0, 160));
  await page.fill('#aiIn', 'And Hypericum?'); await page.click('#aiSend');
  await page.waitForFunction(() => document.querySelectorAll('.aim.model').length === 2, null, { timeout: 8000 }); await settle(300);
  const r2 = lastReq();
  ok(r2.body.contents.length === 3 && !/Traumatology/.test(userParts(r2).map(p => p.text || '').join('')), 'follow-up keeps the chat and does not resend the page', String(r2.body.contents.length));
  await page.click('#aiCtx'); ok(await page.locator('#aiCtx[aria-pressed="false"]').count() === 1, 'page context can be switched off');
  // Back closes the panel; reopening keeps the conversation
  await page.goBack(); await settle(500);
  ok(await page.locator('.aisheet').count() === 0 && /topic9/.test(await page.evaluate(() => location.hash)), 'Back closes the panel and stays on the page');
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle();
  ok(await page.locator('.aim.user').count() === 2, 'conversation kept for the session');
  await page.click('#aiNew'); await settle();
  ok(await page.locator('.aim').count() === 0 && await page.locator('.aisug .fchip').count() === 3, 'New chat clears it and offers starters');
  await page.click('.aisug .fchip >> nth=1'); await page.waitForSelector('.aim.model .aimd', { timeout: 8000 });
  ok(/MCQs/.test(userParts(lastReq()).map(p => p.text || '').join('')), 'a starter question sends at once');
  await page.keyboard.press('Escape'); await settle();
});

await section('5. camera: photo and video are attached and sent', async () => {
  reqs.length = 0;
  await open('#/study/topic6');
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="camera"]'); await settle();
  ok(await page.locator('#aiTake').count() === 1 && await page.locator('#aiLib').count() === 1, 'camera mode offers camera and gallery');
  ok(await page.$eval('#aiShot', i => i.getAttribute('capture') === 'environment' && /image/.test(i.accept) && /video/.test(i.accept)), 'camera input opens the back camera for photo or video');
  const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAIAAADYYG7QAAAAQ0lEQVR42u3OMQ0AAAgDoGv/zkzCDmgMFoqWdkUbBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUF4wB3tAEBtq9TIwAAAABJRU5ErkJggg==', 'base64');
  await page.setInputFiles('#aiPick', { name: 'slide.png', mimeType: 'image/png', buffer: png }); await settle(600);
  ok(await page.locator('.aithumb img').count() === 1, 'photo thumbnail shown');
  await page.fill('#aiIn', 'Which organism is this?'); await page.click('#aiSend');
  await page.waitForSelector('.aim.model .aimd', { timeout: 8000 });
  const img = userParts(lastReq()).find(p => p.inlineData);
  ok(img && img.inlineData.mimeType === 'image/jpeg' && img.inlineData.data.length > 100, 'photo sent as an image', img && img.inlineData.mimeType);
  ok(await page.locator('.aim.user img.aimedia').count() === 1, 'photo shown in the chat');
  await page.click('#aiCam'); await settle();
  await page.setInputFiles('#aiPick', { name: 'clip.mov', mimeType: 'video/quicktime', buffer: Buffer.alloc(4096, 1) }); await settle(400);
  ok(await page.locator('.aithumb video').count() === 1, 'video attached');
  await page.click('#aiSend'); await page.waitForFunction(() => document.querySelectorAll('.aim.model').length === 2, null, { timeout: 8000 });
  const vid = userParts(lastReq()).find(p => p.inlineData);
  ok(vid && vid.inlineData.mimeType === 'video/mov', 'iPhone video sent as video/mov', vid && vid.inlineData.mimeType);
  await page.click('#aiCam'); await settle();
  await page.setInputFiles('#aiPick', { name: 'long.mp4', mimeType: 'video/mp4', buffer: Buffer.alloc(15 * 1024 * 1024, 1) }); await settle(400);
  ok(await page.locator('#toast:has-text("too long")').count() === 1 && await page.locator('.aithumb').count() === 0, 'over-long video refused with a message');
  await page.keyboard.press('Escape'); await settle();
});

await section('6. voice: speech-to-text sends the question; recording fallback sends audio', async () => {
  reqs.length = 0;
  await open('#/study/topic2');
  await page.evaluate(() => { window.__srMode = 'ok'; });
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="voice"]');
  await page.waitForSelector('.aim.model .aimd', { timeout: 8000 });
  ok(/keynote of ledum/.test(userParts(lastReq()).map(p => p.text || '').join('')), 'spoken words become the question and are sent');
  await page.keyboard.press('Escape'); await settle();
  // no speech service (installed iOS app): record and send audio
  await page.evaluate(() => { window.__srMode = 'none'; });
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="voice"]'); await settle(1100);
  ok(await page.locator('#aiMic.rec').count() === 1 && await page.locator('.aihint').count() === 1, 'recording shows a clear listening state');
  await page.click('#aiMic');
  await page.waitForFunction(n => document.querySelectorAll('.aim.user').length > n, 1, { timeout: 8000 }).catch(() => { });
  await page.waitForSelector('.aim.model >> nth=1', { timeout: 8000 }).catch(() => { });
  const au = userParts(lastReq()).find(p => p.inlineData);
  ok(au && au.inlineData.mimeType === 'audio/wav' && au.inlineData.data.length > 1000, 'recorded question sent as WAV audio', au && au.inlineData.mimeType);
  ok(await page.locator('.aivoice').count() >= 1, 'voice question shown in the chat');
  // speech service blocked: falls back to recording
  await page.evaluate(() => { window.__srMode = 'fail'; });
  await page.click('#aiMic'); await settle(500);
  ok(await page.locator('#aiMic.rec').count() === 1, 'blocked speech service falls back to recording');
  await page.click('#aiMic'); await settle(600);
  await page.keyboard.press('Escape'); await settle();
});

await section('7. errors are explained in plain words', async () => {
  for (const [status, msg, want] of [[403, 'API key not valid', 'not accepted'], [429, 'quota', 'free limit'], [400, 'API key not valid. Please pass a valid API key.', 'not accepted'], [500, 'boom', 'could not answer']]) {
    reply = { status, msg };
    await open('#/');
    await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle();
    if (await page.locator('#aiNew').count()) { await page.click('#aiNew'); await settle(); }
    await page.fill('#aiIn', 'hello'); await page.click('#aiSend'); await page.waitForSelector('.aierr', { timeout: 8000 });
    const t = await page.locator('.aierr').last().textContent();
    ok(t.toLowerCase().includes(want), 'HTTP ' + status + ' explained', t);
    await page.keyboard.press('Escape'); await settle();
  }
  reply = { status: 200, text: 'ok' };
  await ctx.route('https://generativelanguage.googleapis.com/**', r => r.abort('internetdisconnected'));
  await open('#/');
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle();
  await page.fill('#aiIn', 'hello'); await page.click('#aiSend'); await page.waitForSelector('.aierr', { timeout: 8000 });
  ok(/connection|offline/i.test(await page.locator('.aierr').last().textContent()), 'network failure explained');
  await page.keyboard.press('Escape'); await settle();
});

await section('8. inside a test: asks about the current question; the timer keeps running', async () => {
  await ctx.unroute('https://generativelanguage.googleapis.com/**');
  await ctx.route('https://generativelanguage.googleapis.com/**', async r => { reqs.push({ body: JSON.parse(r.request().postData()) }); r.fulfill({ status: 200, headers: { 'content-type': 'text/event-stream', 'access-control-allow-origin': '*' }, body: 'data: ' + JSON.stringify({ candidates: [{ content: { parts: [{ text: 'Answer.' }] } }] }) + '\r\n\r\n' }); });
  await page.evaluate(() => localStorage.removeItem('gpsc-cbrt-set14-v1'));
  await open('#/test/set14'); await page.click('#go'); await settle(800);
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle();
  ok(/Question 1 of 60/.test(await page.locator('#aiCtx').textContent()), 'context is the current question');
  await page.fill('#aiIn', 'Explain'); await page.click('#aiSend'); await page.waitForSelector('.aim.model .aimd', { timeout: 8000 });
  const up = userParts(reqs[reqs.length - 1]).map(p => p.text || '').join('');
  ok(/Question 1 of 60/.test(up), 'question text sent');
  await page.keyboard.press('Escape'); await settle();
  ok(/#\/test\/set14/.test(await page.evaluate(() => location.hash)) && await page.locator('#rq .qt').count() === 1, 'still in the test after closing the panel');
});

await section('9. tab can be dragged and remembers its place', async () => {
  await open('#/progress');
  const b0 = await page.locator('#aitab').boundingBox();
  await page.mouse.move(b0.x + 8, b0.y + 26); await page.mouse.down(); await page.mouse.move(b0.x + 8, b0.y - 120, { steps: 6 }); await page.mouse.up(); await settle(500);
  const b1 = await page.locator('#aitab').boundingBox();
  ok(b1.y < b0.y - 60, 'drag moves the tab up', b0.y + ' -> ' + b1.y);
  ok(await page.locator('#aimenu').count() === 0, 'dragging does not open the menu');
  await open('#/progress'); const b2 = await page.locator('#aitab').boundingBox();
  ok(Math.abs(b2.y - b1.y) < 20, 'position remembered', b1.y + ' vs ' + b2.y);
  await page.evaluate(() => { const s = JSON.parse(localStorage.getItem('gpscavy-settings-v1')); delete s.aiY; localStorage.setItem('gpscavy-settings-v1', JSON.stringify(s)); });
});


await section('10. an overloaded model is skipped after a short wait', async () => {
  await ctx.unroute('https://generativelanguage.googleapis.com/**');
  const seen = [];
  await ctx.route('https://generativelanguage.googleapis.com/**', async r => {
    const m = r.request().url().split('/models/')[1].split(':')[0]; seen.push(m);
    if (seen.length === 1) { await new Promise(x => setTimeout(x, 16000)); return r.abort().catch(() => { }); } // first model never starts answering
    r.fulfill({ status: 200, headers: { 'content-type': 'text/event-stream', 'access-control-allow-origin': '*' }, body: 'data: ' + JSON.stringify({ candidates: [{ content: { parts: [{ text: 'Answered by the backup model.' }] } }] }) + '\r\n\r\n' });
  });
  await page.evaluate(() => { const c = JSON.parse(localStorage.getItem('gpscavy-ai-v1')); delete c.last; localStorage.setItem('gpscavy-ai-v1', JSON.stringify(c)); });
  await open('#/');
  await page.click('#aitab'); await settle(); await page.click('#aimenu [data-mode="text"]'); await settle();
  if (await page.locator('#aiNew').count()) { await page.click('#aiNew'); await settle(); }
  const t0 = Date.now();
  await page.fill('#aiIn', 'hello'); await page.click('#aiSend');
  await page.waitForSelector('.aim.model .aimd p', { timeout: 30000 });
  const secs = (Date.now() - t0) / 1000;
  ok(/backup model/.test(await page.locator('.aim.model').last().textContent()) && secs < 20 && seen.length === 2, 'moved to the next model after about 12 s', secs + ' s, tried ' + seen.join(' > '));
  const last = await page.evaluate(() => JSON.parse(localStorage.getItem('gpscavy-ai-v1')).last);
  ok(last === seen[1], 'the model that answered is remembered and tried first next time', String(last));
  await page.keyboard.press('Escape'); await settle();
});

ok(!errors.filter(e => !/Failed to load resource|internetdisconnected|ERR_INTERNET/.test(e)).length, 'no page errors', errors.slice(0, 4).join(' | '));
await browser.close();
console.log(`\nAI ${prof}: ${pass} passed, ${fail} failed`);
if (fail) { console.log(failures.map(f => ' - ' + f).join('\n')); process.exit(1); }
