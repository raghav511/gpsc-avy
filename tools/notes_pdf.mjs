// Print the core-topic notes to PDF: one file per topic and one with all ten, in colour, with every picture and diagram.
//   node tools/notes_pdf.mjs [--base http://localhost:8765/gpsc-avy/]    (serve the repo first; needs Playwright Chromium)
// Writes content/pdfs/Topic-N-*.pdf, content/pdfs/GPSC-Core-Notes-All-Topics.pdf and content/pdfs/notes-pdf.json
// (the hash of the notes they were made from: tools/build.py refuses to build when the PDFs are out of date).
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
const PW = await import(process.env.PLAYWRIGHT || 'playwright').catch(() => import('/opt/npm-tools/node_modules/playwright/index.mjs'));
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => s.trim().split(/\s+/)));
const BASE = args.base || 'http://localhost:8765/gpsc-avy/';
const OUT = path.join(ROOT, 'content', 'pdfs');
const meta = JSON.parse(fs.readFileSync(path.join(ROOT, 'data/meta.json'), 'utf8'));
const TITLES = { 1: 'Organon of Medicine & Homoeopathic Philosophy', 2: 'Homoeopathic Materia Medica', 3: 'Homoeopathic Pharmacy', 4: 'Repertory & Repertorisation', 5: 'General & Applied Human Biology', 6: 'Pathology, Microbiology & Diagnostics', 7: 'Practice of Medicine & Homoeopathic Therapeutics', 8: 'Obstetrics, Gynaecology & Paediatrics', 9: 'Surgery, Allied Specialties & First-Aid', 10: 'Community Medicine, Forensic Medicine & Ethics' };
export const FILE = t => 'Topic-' + t + '-' + TITLES[t].replace(/&/g, '').replace(/[^A-Za-z0-9]+/g, '-').replace(/-+$/, '') + '.pdf';

// the app's variable web fonts become heavy Type 3 fonts in a PDF: print with the static system fonts instead
const css = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').match(/<style>([\s\S]*?)<\/style>/)[1].replace(/@font-face\{[^}]*\}/g, '');
const PRINT = `
:root{--ui:'Carlito','Liberation Sans',Arial,sans-serif!important;--body:'Carlito','Liberation Sans',Arial,sans-serif!important}
*{box-shadow:none!important;text-shadow:none!important;filter:none!important;backdrop-filter:none!important}
@page{size:A4;margin:14mm 12mm 16mm}
html,body{height:auto!important;overflow:visible!important;background:#fff!important}
#app{position:static!important;overflow:visible!important}
body{color:#1e1b4b}
.ns{content-visibility:visible!important;contain:none!important;break-before:auto}
.ns>h2{break-after:avoid}
.nh::after{display:none}
.nh{pointer-events:none}
figure,tr,.hook,.trap,.tip{break-inside:avoid}
.nc,table,blockquote,.ns{break-inside:auto!important;min-height:0!important}
figure.illus .zoom{cursor:default}
.notes{max-width:none!important;padding:0!important}
.cover{height:250mm;display:flex;flex-direction:column;justify-content:center;gap:10mm;break-after:page;padding:0 6mm}
.cover .k{font:800 13pt var(--ui);letter-spacing:.12em;text-transform:uppercase;color:#7c3aed}
.cover h1{font:800 34pt/1.1 var(--ui);margin:0;color:#1e1b4b}
.cover p{font:500 13pt/1.5 var(--body);color:#3f3d63;margin:0}
.cover .b{margin-top:16mm;font:600 11pt var(--body);color:#5b5a7a}
.cover .tc{columns:2;font:600 11pt/1.8 var(--body);color:#3f3d63}
.thead{font:800 22pt var(--ui);color:#1e1b4b;margin:0 0 6mm;padding-bottom:3mm;border-bottom:3px solid #7c3aed}
.topic{break-before:page}
`;
const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const notesOf = t => fs.readFileSync(path.join(ROOT, 'data/notes/topic' + t + '.html'), 'utf8');
const topics = meta.notes.map(n => n.t);
const hash = crypto.createHash('sha1');
for (const t of topics) hash.update(notesOf(t));
for (const f of fs.readdirSync(path.join(ROOT, 'data/figs')).sort()) hash.update(fs.readFileSync(path.join(ROOT, 'data/figs', f)));
const digest = hash.digest('hex').slice(0, 12);

function doc(ts, title, sub) {
  const toc = ts.length > 1 ? '<div class="tc">' + ts.map(t => '<div>Topic ' + t + ' · ' + esc(TITLES[t]) + '</div>').join('') + '</div>' : '';
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><base href="${BASE}"><title>${esc(title)}</title><style>${css}${PRINT}</style></head>
<body data-screen="print"><div id="app">
<section class="cover"><span class="k">GPSC CBRT · Homoeopathic Physician · Core</span><h1>${esc(title)}</h1><p>${esc(sub)}</p>${toc}</section>
${ts.map(t => `<section class="topic"><h1 class="thead">Topic ${t}: ${esc(TITLES[t])}</h1><main class="notes" style="--fs:1">${notesOf(t)}</main></section>`).join('\n')}
</div></body></html>`;
}

const browser = await PW.chromium.launch(fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const page = await browser.newPage();
await page.emulateMedia({ colorScheme: 'light', media: 'print' });
const out = { hash: digest, files: {} };
async function print(ts, file, title, sub) {
  await page.setContent(doc(ts, title, sub), { waitUntil: 'load' });
  await page.evaluate(async () => {
    document.querySelectorAll('img[loading]').forEach(i => i.loading = 'eager');
    await Promise.all(Array.from(document.images, i => i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; })));
    await document.fonts.ready;
  });
  const bad = await page.evaluate(() => Array.from(document.images).filter(i => !i.naturalWidth).map(i => i.src));
  if (bad.length) throw new Error('pictures did not load: ' + bad.join(', '));
  await page.pdf({ path: path.join(OUT, file), format: 'A4', printBackground: true, preferCSSPageSize: true, displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `<div style="font:8px sans-serif;color:#888;width:100%;padding:0 12mm;display:flex;justify-content:space-between"><span>${esc(title)}</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>` });
  // squeeze the file (about 15% smaller) when qpdf is installed
  try { const { execFileSync } = await import('node:child_process'); const f = path.join(OUT, file); execFileSync('qpdf', ['--object-streams=generate', '--recompress-flate', '--compression-level=9', f, f + '.tmp']); fs.renameSync(f + '.tmp', f); } catch (e) { }
  const kb = Math.round(fs.statSync(path.join(OUT, file)).size / 1024);
  out.files[file] = kb;
  console.log(file, kb, 'KB');
}
for (const t of topics) await print([t], FILE(t), 'Topic ' + t + ': ' + TITLES[t], 'Complete notes with pictures, memory hooks, rapid revision and practice MCQs.');
await print(topics, 'GPSC-Core-Notes-All-Topics.pdf', 'Core Notes: all 10 topics', 'The 25-mark core section in one file: every topic with its pictures, memory hooks, rapid revision and practice MCQs.');
await browser.close();
fs.writeFileSync(path.join(OUT, 'notes-pdf.json'), JSON.stringify(out, null, 1));
// no author, tool or date details in any downloadable file
try { (await import('node:child_process')).execFileSync('python3', [path.join(ROOT, 'tools', 'pdf_clean.py')], { stdio: 'inherit' }); } catch (e) { console.log('pdf_clean skipped:', e.message); }
