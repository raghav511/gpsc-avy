// Ask Gemini: a study assistant on every screen. Text, voice, or a photo / video, about anything or about the page you are on.
// The key is the user's own Gemini API key, kept only on this device (never exported or synced). Calls go straight to Google.
import { $, esc, sheet, closeSheet, sheetOpen, toast, lsGet, lsSet, lsDel } from './core.js';

const AKEY = 'gpscavy-ai-v1';
const API = 'https://generativelanguage.googleapis.com/v1beta/models/';
// tried in turn: a busy (503), retired (404) or rate-limited (429) model falls through to the next one
const MODELS = ['gemini-3.5-flash', 'gemini-flash-latest', 'gemini-3.8-flash', 'gemini-flash-lite-latest', 'gemini-3.5-flash-lite'];
const WAIT = 12000; // a model that has not started answering by then is overloaded: move on to the next
const MAX_MEDIA = 14 * 1024 * 1024; // inline request limit is 20 MB; base64 adds a third
const conf = () => lsGet(AKEY, {}) || {};
let goodModel = ''; // the model that last answered: tried first next time (also remembered on this device)
const chat = []; // this session's conversation: {role:'user'|'model', parts:[...], view:{text, media, voice}}
let busy = null; // AbortController of the running request

export const ICONS = {
  spark: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><defs><linearGradient id="aig" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4f8cff"/><stop offset=".55" stop-color="#9b6bff"/><stop offset="1" stop-color="#ff6fae"/></linearGradient></defs><path d="M12 2c.6 4.9 3.4 7.6 8.3 8.3v1.4C15.4 12.4 12.6 15.1 12 20h-1.4c-.6-4.9-3.4-7.6-8.3-8.3v-1.4C7.2 9.6 10 6.9 10.6 2z" fill="url(#aig)" transform="translate(.7 1)"/></svg>',
  text: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="6" width="19" height="12" rx="3"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/></svg>',
  mic: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/></svg>',
  cam: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8h3l2-3h6l2 3h3a1 1 0 011 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V9a1 1 0 011-1z"/><circle cx="12" cy="13" r="3.5"/></svg>',
  send: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12l16-8-6 16-2.5-6.5z"/></svg>',
  stop: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/></svg>',
  x: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
  gear: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 01-4 0v-.1a1.7 1.7 0 00-1.1-1.5 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 010-4h.1a1.7 1.7 0 001.5-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 014 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 010 4h-.1a1.7 1.7 0 00-1.5 1z"/></svg>'
};

// ---------- the page the user is looking at ----------
export function pageContext() {
  const app = $('#app'); if (!app) return null;
  const screen = document.body.dataset.screen || 'home';
  let label = '', text = '';
  const h1 = app.querySelector('h1');
  const nb = $('#nb');
  if (nb && nb.querySelector('.ns')) {
    // notes: the sections on screen and the one after, so "this" means what you are reading
    const secs = Array.from(nb.querySelectorAll('.ns'));
    const mid = innerHeight * 0.4;
    let i = secs.findIndex(s => { const r = s.getBoundingClientRect(); return r.top <= mid && r.bottom > mid; });
    if (i < 0) i = Math.max(0, secs.findIndex(s => s.getBoundingClientRect().bottom > 0));
    const pick = secs.slice(i, i + 2);
    const h2 = pick[0].querySelector('h2');
    const hn = h2 && h2.querySelector('.nnum');
    const ht = h2 ? (hn ? hn.textContent.trim() + ' ' + h2.textContent.trim().slice(hn.textContent.trim().length).trim() : h2.textContent.trim()) : '';
    label = (h1 ? h1.textContent.trim() : 'Notes') + (ht ? ' · ' + ht : '');
    text = pick.map(s => s.innerText).join('\n\n');
  } else if (screen === 'runner' || app.querySelector('#rq')) {
    const qn = app.querySelector('.qn');
    label = qn ? qn.textContent.trim() : 'This question';
    text = app.innerText; // the passage, the question and its options
  } else {
    const main = app.querySelector('main') || app;
    label = (h1 && h1.textContent.trim()) || document.title;
    text = main.innerText;
  }
  text = text.replace(/\n{3,}/g, '\n\n').trim().slice(0, 14000);
  return text.length > 40 ? { label: label.slice(0, 80), text } : null;
}

// ---------- the floating tab and its menu ----------
export function menu(tab) {
  const old = $('#aimenu'); if (old) { old.remove(); return; }
  const r = tab.getBoundingClientRect();
  const m = document.createElement('div');
  m.id = 'aimenu'; m.setAttribute('role', 'menu'); m.setAttribute('aria-label', 'Ask Gemini');
  m.innerHTML = '<span class="aim-t">' + ICONS.spark + 'Ask Gemini</span>' +
    [['text', 'Type'], ['voice', 'Speak'], ['camera', 'Camera']].map(([k, l]) => '<button type="button" role="menuitem" data-mode="' + k + '"><span class="aim-i">' + ICONS[k === 'voice' ? 'mic' : k === 'camera' ? 'cam' : 'text'] + '</span>' + l + '</button>').join('');
  document.body.appendChild(m);
  const top = Math.min(Math.max(r.top + r.height / 2 - m.offsetHeight / 2, 8), innerHeight - m.offsetHeight - 8);
  m.style.top = top + 'px';
  const off = e => { if (!m.contains(e.target) && e.target !== tab && !tab.contains(e.target)) close(); };
  const key = e => { if (e.key === 'Escape') { close(); tab.focus(); } };
  const close = () => { m.remove(); document.removeEventListener('pointerdown', off, true); document.removeEventListener('keydown', key); window.removeEventListener('hashchange', close); };
  m.addEventListener('click', e => { const b = e.target.closest('[data-mode]'); if (!b) return; close(); open(b.dataset.mode); });
  setTimeout(() => { document.addEventListener('pointerdown', off, true); document.addEventListener('keydown', key); window.addEventListener('hashchange', close); }, 0);
  m.querySelector('button').focus();
}

// ---------- the panel ----------
let ctx = null, useCtx = true, media = null;
export function open(mode) {
  if (!conf().key) return keySheet(() => open(mode));
  ctx = pageContext(); useCtx = !!ctx; media = null;
  const el = sheet(
    '<div class="aih"><span class="aih-t">' + ICONS.spark + 'Ask Gemini</span><span class="sp"></span>' +
    (chat.length ? '<button type="button" class="ib aih-b" id="aiNew">New chat</button>' : '') +
    '<button type="button" class="ib aih-b" id="aiSet" aria-label="Gemini settings">' + ICONS.gear + '</button><button type="button" class="ib aih-b" data-close aria-label="Close">' + ICONS.x + '</button></div>' +
    (ctx ? '<button type="button" class="aictx on" id="aiCtx" aria-pressed="true"><span class="aictx-d"></span><span>Ask about this page: <b>' + esc(ctx.label) + '</b></span></button>' : '') +
    '<div class="aimsgs" id="aiMsgs" aria-live="polite"></div>' +
    '<div class="aiatt" id="aiAtt" hidden></div>' +
    '<div class="aibar"><button type="button" class="aiic" id="aiCam" aria-label="Photo or video">' + ICONS.cam + '</button>' +
    '<textarea id="aiIn" rows="1"' + (mode === 'text' ? ' data-focus' : '') + ' placeholder="' + (ctx ? 'Ask about this page…' : 'Ask anything…') + '" aria-label="Your question" enterkeyhint="send"></textarea>' +
    '<button type="button" class="aiic" id="aiMic" aria-label="Speak your question">' + ICONS.mic + '</button>' +
    '<button type="button" class="aiic aisend" id="aiSend" aria-label="Send">' + ICONS.send + '</button></div>' +
    '<input type="file" id="aiShot" accept="image/*,video/*" capture="environment" hidden><input type="file" id="aiPick" accept="image/*,video/*" hidden>',
    { label: 'Ask Gemini', onClose: () => { stopVoice(); if (busy) busy.abort(); } });
  el.classList.add('aisheet');
  renderMsgs();
  const inp = $('#aiIn');
  inp.addEventListener('input', () => { inp.style.height = 'auto'; inp.style.height = Math.min(inp.scrollHeight, 140) + 'px'; });
  inp.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); send(); } });
  $('#aiSend').onclick = () => busy ? busy.abort() : send();
  $('#aiMic').onclick = () => voice();
  $('#aiCam').onclick = () => cameraChoice();
  $('#aiSet').onclick = () => keySheet(() => open('text'));
  const nw = $('#aiNew'); if (nw) nw.onclick = () => { chat.length = 0; open('text'); };
  const cb = $('#aiCtx'); if (cb) cb.onclick = () => { useCtx = !useCtx; cb.classList.toggle('on', useCtx); cb.setAttribute('aria-pressed', useCtx); };
  for (const id of ['aiShot', 'aiPick']) $('#' + id).onchange = e => { const f = e.target.files[0]; e.target.value = ''; if (f) attach(f); };
  if (mode === 'voice') voice();
  else if (mode === 'camera') cameraChoice();
  else inp.focus({ preventScroll: true });
}

function cameraChoice() {
  const att = $('#aiAtt');
  att.hidden = false;
  att.innerHTML = '<div class="aicam"><button type="button" class="btn vio" id="aiTake">' + ICONS.cam + 'Take photo or video</button><button type="button" class="btn sec" id="aiLib">Choose from gallery</button></div>';
  $('#aiTake').onclick = () => $('#aiShot').click();
  $('#aiLib').onclick = () => $('#aiPick').click();
}

async function attach(f) {
  const att = $('#aiAtt');
  const isVid = /^video\//.test(f.type) || /\.(mov|mp4|webm|3gp)$/i.test(f.name);
  try {
    if (isVid) {
      if (f.size > MAX_MEDIA) { toast('That video is too long to send. Keep it under about 20 seconds.', null, 4500); return; }
      media = { mime: vidMime(f), data: await b64(f), kind: 'video', url: URL.createObjectURL(f) };
    } else {
      const small = await shrink(f);
      media = { mime: 'image/jpeg', data: small.split(',')[1], kind: 'image', url: small };
    }
  } catch (e) { toast('Could not read that file. Try another photo or video.'); return; }
  att.hidden = false;
  att.innerHTML = '<div class="aithumb">' + (media.kind === 'image' ? '<img src="' + media.url + '" alt="Attached photo">' : '<video src="' + media.url + '" muted playsinline></video>') +
    '<span>' + (media.kind === 'image' ? 'Photo attached' : 'Video attached') + '</span><button type="button" class="ib" id="aiRm" aria-label="Remove attachment">' + ICONS.x + '</button></div>';
  $('#aiRm').onclick = () => { media = null; att.hidden = true; att.innerHTML = ''; };
  const inp = $('#aiIn'); inp.placeholder = media.kind === 'image' ? 'Ask about this photo…' : 'Ask about this video…'; inp.focus({ preventScroll: true });
}
const vidMime = f => { const t = (f.type || '').toLowerCase(); if (t === 'video/quicktime' || /\.mov$/i.test(f.name)) return 'video/mov'; return t || 'video/mp4'; };
const b64 = f => new Promise((ok, no) => { const r = new FileReader(); r.onload = () => ok(String(r.result).split(',')[1]); r.onerror = no; r.readAsDataURL(f); });
function shrink(f) {
  return new Promise((ok, no) => {
    const img = new Image(); const u = URL.createObjectURL(f);
    img.onload = () => {
      const s = Math.min(1, 1280 / Math.max(img.naturalWidth, img.naturalHeight));
      const c = document.createElement('canvas'); c.width = Math.round(img.naturalWidth * s); c.height = Math.round(img.naturalHeight * s);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height); URL.revokeObjectURL(u); ok(c.toDataURL('image/jpeg', .85));
    };
    img.onerror = () => { URL.revokeObjectURL(u); no(new Error('image')); };
    img.src = u;
  });
}

// ---------- voice: live speech-to-text where the browser has it, otherwise record and let Gemini listen ----------
let rec = null, recorder = null;
function stopVoice() { try { if (rec) rec.stop(); } catch (e) { } try { if (recorder && recorder.state === 'recording') recorder.stop(); } catch (e) { } }
function voice() {
  const mic = $('#aiMic'); if (!mic) return;
  if (rec || (recorder && recorder.state === 'recording')) { stopVoice(); return; }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const inp = $('#aiIn');
  if (SR) {
    try {
      rec = new SR(); rec.lang = 'en-IN'; rec.interimResults = true; rec.continuous = false;
      const before = inp.value ? inp.value.trim() + ' ' : '';
      let final = '', failed = false;
      rec.onresult = e => { let t = ''; final = ''; for (const r of e.results) { if (r.isFinal) final += r[0].transcript; else t += r[0].transcript; } inp.value = before + final + t; inp.dispatchEvent(new Event('input')); };
      rec.onerror = e => { failed = e.error; };
      rec.onend = () => {
        rec = null; mic.classList.remove('rec'); setHint('');
        // the browser's speech service is missing or blocked (common in installed iOS apps): record instead and let Gemini listen
        if (failed && failed !== 'no-speech' && failed !== 'aborted') { recordAudio(); return; }
        if (final.trim()) send();
      };
      rec.start(); mic.classList.add('rec'); setHint('Listening… speak your question. Tap the mic to stop.');
      return;
    } catch (e) { rec = null; }
  }
  recordAudio();
}
async function recordAudio() {
  const mic = $('#aiMic');
  if (!navigator.mediaDevices || !window.MediaRecorder) { toast('Voice is not available in this browser. Type your question instead.', null, 4000); return; }
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }); }
  catch (e) { toast('Allow the microphone to ask by voice.', null, 4000); return; }
  const type = ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4', 'audio/ogg'].find(t => MediaRecorder.isTypeSupported && MediaRecorder.isTypeSupported(t)) || '';
  recorder = type ? new MediaRecorder(stream, { mimeType: type }) : new MediaRecorder(stream);
  const chunks = []; const t0 = Date.now();
  recorder.ondataavailable = e => { if (e.data.size) chunks.push(e.data); };
  recorder.onstop = async () => {
    stream.getTracks().forEach(t => t.stop()); mic.classList.remove('rec'); setHint('');
    const blob = new Blob(chunks, { type: recorder.mimeType || type || 'audio/webm' });
    if (Date.now() - t0 < 700 || !blob.size) return;
    setHint('Preparing your voice question…');
    // Gemini reads WAV everywhere; Safari records MP4/AAC and Chrome WebM, so convert to 16 kHz mono WAV first
    let audio;
    try { audio = { mime: 'audio/wav', data: await b64(await toWav(blob)) }; }
    catch (e) { audio = { mime: (blob.type || 'audio/webm').split(';')[0], data: await b64(blob) }; }
    setHint('');
    audio.secs = Math.max(1, Math.round((Date.now() - t0) / 1000));
    send({ audio });
  };
  recorder.start(); mic.classList.add('rec'); setHint('Recording… tap the mic again when you have asked.');
  setTimeout(() => { if (recorder && recorder.state === 'recording') recorder.stop(); }, 60000);
}
async function toWav(blob) {
  const AC = window.AudioContext || window.webkitAudioContext;
  const ac = new AC();
  try {
    const ab = await blob.arrayBuffer();
    const src = await new Promise((ok, no) => { const p = ac.decodeAudioData(ab, ok, no); if (p && p.then) p.then(ok, no); });
    const rate = 16000, len = Math.ceil(src.duration * rate);
    const off = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(1, len, rate);
    const n = off.createBufferSource(); n.buffer = src; n.connect(off.destination); n.start(0);
    const out = await off.startRendering();
    const pcm = out.getChannelData(0), buf = new ArrayBuffer(44 + pcm.length * 2), v = new DataView(buf);
    const w = (o, str) => { for (let i = 0; i < str.length; i++) v.setUint8(o + i, str.charCodeAt(i)); };
    w(0, 'RIFF'); v.setUint32(4, 36 + pcm.length * 2, true); w(8, 'WAVE'); w(12, 'fmt '); v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
    v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true); w(36, 'data'); v.setUint32(40, pcm.length * 2, true);
    for (let i = 0; i < pcm.length; i++) { const x = Math.max(-1, Math.min(1, pcm[i])); v.setInt16(44 + i * 2, x < 0 ? x * 0x8000 : x * 0x7fff, true); }
    return new Blob([buf], { type: 'audio/wav' });
  } finally { try { ac.close(); } catch (e) { } }
}
function setHint(t) { const att = $('#aiAtt'); if (!att) return; if (t) { att.hidden = false; att.dataset.hint = '1'; att.innerHTML = '<p class="aihint"><span class="aipulse"></span>' + esc(t) + '</p>'; } else if (att.dataset.hint) { delete att.dataset.hint; att.innerHTML = ''; att.hidden = !media; } }

// ---------- conversation ----------
const SYSTEM = 'You are the study assistant inside GPSCavy, an app for the GPSC (Goa) CBRT exam for the post of Homoeopathic Physician. ' +
  'Answer clearly and briefly for exam revision: lead with the direct answer, then the key points. Use standard homoeopathy and medical textbooks ' +
  '(Hahnemann\'s Organon, Kent, Boericke, Allen\'s Keynotes, Mandal and Mandal, Park, Harrison, Dutta, Das). When the page text is given, base the answer on it and say if the page does not cover the question. ' +
  'If you are not sure, say so. Use short paragraphs and bullet lists; no tables.';

function renderMsgs() {
  const box = $('#aiMsgs'); if (!box) return;
  if (!chat.length) {
    box.innerHTML = '<div class="aiempty"><p><b>Ask a question</b> by typing, speaking or showing a photo or video.</p>' +
      (ctx ? '<div class="aisug">' + ['Explain this page simply', 'Give me 3 MCQs from this page', 'What is most likely to be asked here?'].map(s => '<button type="button" class="fchip" data-q="' + esc(s) + '">' + esc(s) + '</button>').join('') + '</div>' : '') + '</div>';
    box.querySelectorAll('[data-q]').forEach(b => b.onclick = () => { $('#aiIn').value = b.dataset.q; send(); });
    return;
  }
  box.innerHTML = chat.map(m => '<div class="aim ' + m.role + '">' + (m.role === 'user' ? userView(m.view) : '<div class="aimd">' + md(m.view.text || '') + (m.view.err ? '<p class="aierr">' + esc(m.view.err) + '</p>' : '') + '</div>') + '</div>').join('') + (busy && chat[chat.length - 1].role === 'user' ? '<div class="aim model"><span class="aidots"><i></i><i></i><i></i></span></div>' : '');
  box.scrollTop = box.scrollHeight;
}
function userView(v) {
  return (v.media ? (v.media.kind === 'image' ? '<img class="aimedia" src="' + v.media.url + '" alt="Photo you sent">' : '<video class="aimedia" src="' + v.media.url + '" muted playsinline controls></video>') : '') +
    (v.voice ? '<p class="aivoice">' + ICONS.mic + 'Voice question · ' + v.voice + ' s</p>' : '') + (v.text ? '<p>' + esc(v.text) + '</p>' : '') +
    (v.page ? '<p class="aipg">About: ' + esc(v.page) + '</p>' : '');
}

async function send(extra) {
  const inp = $('#aiIn'); if (!inp || busy) return;
  const text = inp.value.trim();
  const audio = extra && extra.audio;
  if (!text && !media && !audio) { inp.focus(); return; }
  const parts = [];
  // send the page once per conversation (and again only if the student has moved to a different part of it)
  const pkey = ctx ? ctx.label + '|' + ctx.text.length : '';
  const pageOn = !!(useCtx && ctx && !chat.some(m => m.view && m.view.pkey === pkey));
  if (pageOn) parts.push({ text: 'The page the student is looking at in the app ("' + ctx.label + '"):\n"""\n' + ctx.text + '\n"""' });
  if (media) parts.push({ inlineData: { mimeType: media.mime, data: media.data } });
  if (audio) parts.push({ inlineData: { mimeType: audio.mime, data: audio.data } }, { text: 'The student asked the question above by voice. Answer it; begin with one line in italics restating the question you heard.' });
  if (text) parts.push({ text });
  chat.push({ role: 'user', parts, view: { text, media, voice: audio ? audio.secs : 0, page: pageOn ? ctx.label : '', pkey: pageOn ? pkey : '' } });
  inp.value = ''; inp.style.height = 'auto'; media = null; const att = $('#aiAtt'); att.hidden = true; att.innerHTML = '';
  inp.placeholder = 'Ask a follow-up…';
  await ask();
}

async function ask() {
  const c = conf();
  busy = new AbortController();
  const sendBtn = $('#aiSend'); if (sendBtn) { sendBtn.innerHTML = ICONS.stop; sendBtn.setAttribute('aria-label', 'Stop'); }
  renderMsgs();
  const reply = { role: 'model', parts: [{ text: '' }], view: { text: '' } };
  const body = JSON.stringify({ systemInstruction: { parts: [{ text: SYSTEM }] }, contents: chat.map(m => ({ role: m.role, parts: m.parts })), generationConfig: { temperature: 0.4, maxOutputTokens: 8192 /* newer models think first; thinking counts towards this limit */ } });
  const first = c.model || goodModel || c.last;
  const models = first ? [first].concat(MODELS.filter(m => m !== first)) : MODELS;
  let err = '';
  try {
    for (let i = 0; i < models.length; i++) {
      // each try has its own timer; Stop still cancels everything
      const ac = new AbortController(), user = busy.signal;
      const stop = () => ac.abort(); user.addEventListener('abort', stop);
      let slow = false; const timer = setTimeout(() => { slow = true; ac.abort(); }, WAIT);
      let res;
      try { res = await fetch(API + encodeURIComponent(models[i]) + ':streamGenerateContent?alt=sse', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-goog-api-key': c.key }, body, signal: ac.signal }); }
      catch (e) { clearTimeout(timer); if (slow && !user.aborted && i < models.length - 1) { err = 'Gemini is very busy right now. Wait a moment and ask again.'; continue; } if (slow) { err = 'Gemini is very busy right now. Wait a moment and ask again.'; break; } throw e; }
      clearTimeout(timer);
      if ([404, 429, 500, 503].includes(res.status) && i < models.length - 1) { if (res.status !== 404) err = await apiError(res); continue; }
      err = '';
      if (!res.ok) { err = await apiError(res); break; }
      goodModel = models[i]; if (c.last !== goodModel) lsSet(AKEY, Object.assign(conf(), { last: goodModel }));
      chat.push(reply);
      const rd = res.body.getReader(), dec = new TextDecoder(); let buf = '';
      for (;;) {
        const { value, done } = await rd.read(); if (done) break;
        buf += dec.decode(value, { stream: true });
        let k;
        while ((k = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, k).trim(); buf = buf.slice(k + 1);
          if (!line.startsWith('data:')) continue;
          try {
            const j = JSON.parse(line.slice(5));
            const cand = j.candidates && j.candidates[0];
            const t = ((cand && cand.content && cand.content.parts) || []).filter(p => !p.thought).map(p => p.text || '').join('');
            if (cand && cand.finishReason === 'MAX_TOKENS') reply.view.err = 'The answer was cut short. Ask for a shorter answer, or ask it to continue.';
            if (t) { reply.view.text += t; reply.parts[0].text = reply.view.text; paintLast(); }
            if (j.promptFeedback && j.promptFeedback.blockReason) reply.view.err = 'Gemini did not answer this one (' + j.promptFeedback.blockReason.toLowerCase() + ').';
          } catch (e) { }
        }
      }
      if (!reply.view.text && !reply.view.err) reply.view.err = 'No answer came back. Try asking again.';
      break;
    }
  } catch (e) {
    if (e.name === 'AbortError') { if (chat[chat.length - 1] === reply) reply.view.err = reply.view.text ? 'Stopped.' : 'Stopped.'; else err = 'Stopped.'; }
    else err = navigator.onLine === false ? 'You are offline. Gemini needs the internet.' : 'Could not reach Gemini. Check your connection and try again.';
  }
  if (err) chat.push({ role: 'model', parts: [{ text: '' }], view: { text: '', err } });
  if (!reply.parts[0].text && chat.includes(reply)) reply.parts[0].text = reply.view.err || '…';
  busy = null;
  if (sendBtn && document.body.contains(sendBtn)) { sendBtn.innerHTML = ICONS.send; sendBtn.setAttribute('aria-label', 'Send'); }
  renderMsgs();
}
function paintLast() {
  const box = $('#aiMsgs'); if (!box) return;
  const last = box.lastElementChild;
  const html = '<div class="aimd">' + md(chat[chat.length - 1].view.text) + '</div>';
  if (last && last.classList.contains('model') && !last.querySelector('.aidots')) last.innerHTML = html;
  else { if (last && last.querySelector('.aidots')) last.remove(); box.insertAdjacentHTML('beforeend', '<div class="aim model">' + html + '</div>'); }
  box.scrollTop = box.scrollHeight;
}
async function apiError(res) {
  let msg = '';
  try { const j = await res.json(); msg = (j.error && j.error.message) || ''; } catch (e) { }
  if (res.status === 400 && /api key/i.test(msg) || res.status === 401 || res.status === 403) return 'Your Gemini API key was not accepted. Open settings (the gear) and check it.';
  if (res.status === 429) return 'Gemini\'s free limit is used up for now. Wait a minute and ask again.';
  if (res.status === 503) return 'Gemini is very busy right now. Wait a moment and ask again.';
  if (res.status === 400 && /mime|unsupported|inline/i.test(msg)) return 'Gemini could not read that file type. Try a photo, or a shorter video.';
  return 'Gemini could not answer (' + res.status + (msg ? ': ' + msg.slice(0, 140) : '') + ').';
}

// ---------- minimal, safe markdown ----------
export function md(s) {
  const lines = esc(s).split('\n'); let out = '', list = '';
  const inl = t => t.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<i>$2</i>').replace(/`([^`]+)`/g, '<code>$1</code>');
  const end = () => { if (list) { out += '</' + list + '>'; list = ''; } };
  for (const l of lines) {
    let m;
    if ((m = /^\s*[-*•]\s+(.*)/.exec(l))) { if (list !== 'ul') { end(); out += '<ul>'; list = 'ul'; } out += '<li>' + inl(m[1]) + '</li>'; }
    else if ((m = /^\s*\d+[.)]\s+(.*)/.exec(l))) { if (list !== 'ol') { end(); out += '<ol>'; list = 'ol'; } out += '<li>' + inl(m[1]) + '</li>'; }
    else if (/^\s*([-*_])(\s*\1){2,}\s*$/.test(l)) { end(); out += '<hr>'; }
    else if ((m = /^#{1,4}\s+(.*)/.exec(l))) { end(); out += '<p class="aihd">' + inl(m[1]) + '</p>'; }
    else if (l.trim()) { end(); out += '<p>' + inl(l) + '</p>'; }
    else end();
  }
  end();
  return out;
}

// ---------- the key ----------
export function keySheet(then) {
  const c = conf();
  sheet('<h2>Connect Gemini</h2>' +
    '<p class="sub">Gemini answers with your own free Google AI key. It is saved only on this device: never in your progress file, never synced.</p>' +
    '<ol class="aisteps"><li>Open <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">aistudio.google.com/apikey</a> and sign in with Google.</li><li>Tap <b>Create API key</b> and copy it.</li><li>Paste it below.</li></ol>' +
    '<label class="ailab" for="aiKey">Gemini API key</label><input id="aiKey" class="aikey" type="password" autocomplete="off" spellcheck="false" placeholder="Paste your key" value="' + esc(c.key || '') + '" data-focus>' +
    '<details class="aiadv"><summary>Advanced</summary><label class="ailab" for="aiModel">Model</label><input id="aiModel" class="aikey" placeholder="gemini-flash-latest" value="' + esc(c.model || '') + '"></details>' +
    '<p class="aierr" id="aiKeyErr" hidden></p>' +
    '<div class="row2"><button type="button" class="btn sec" ' + (c.key ? 'id="aiDel">Remove key' : 'data-close>Not now') + '</button><button type="button" class="btn vio" id="aiSave">Save</button></div>',
    { label: 'Connect Gemini' });
  const del = $('#aiDel'); if (del) del.onclick = () => { lsDel(AKEY); closeSheet(); toast('Gemini key removed from this device.'); };
  $('#aiSave').onclick = () => {
    const k = $('#aiKey').value.trim(), m = $('#aiModel').value.trim();
    const e = $('#aiKeyErr');
    if (!/^[A-Za-z0-9_.\-]{20,}$/.test(k)) { e.hidden = false; e.textContent = 'That does not look like a Gemini API key. It is a long code with no spaces, starting with AIza or AQ.'; return; }
    lsSet(AKEY, { key: k, model: m || '' });
    closeSheet(true); toast('Gemini is connected.');
    if (then) then();
  };
}

export const ready = () => !!conf().key;
export const isBusy = () => !!busy || sheetOpen();
