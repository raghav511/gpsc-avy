// GPSCavy sync hub. Keeps one combined progress file in your Google Drive.
// The GPSCavy app (phone, iPad) posts its progress here; the GPSC CBRT Mock Exam page drops its progress in the inbox folder.
// Every sync is a union: attempts are never removed, and a later submission of the same attempt replaces the earlier one.
var HUB_FILE = 'PASTE_HUB_FILE_ID';   // GPSCavy sync/GPSCavy-progress.json
var INBOX = 'PASTE_INBOX_FOLDER_ID';      // GPSCavy sync/inbox
var MERGED = 'merged';                                 // inbox files are moved here after merging (kept, never deleted)

function doGet(e) {
  if (e && e.parameter && e.parameter.ping) return out({ ok: true, hub: 'gpscavy', version: 1 });
  return out(run(null));
}
function doPost(e) {
  var body = {};
  try { body = JSON.parse(e.postData.contents); } catch (x) { return out({ ok: false, error: 'bad_json' }); }
  return out(run(body.progress || null));
}
function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

function run(incoming) {
  var lock = LockService.getScriptLock();
  lock.waitLock(28000);
  try {
    var file = DriveApp.getFileById(HUB_FILE);
    var hub = parse(file.getBlob().getDataAsString()) || empty();
    var inbox = DriveApp.getFolderById(INBOX), used = [];
    var it = inbox.getFiles();
    while (it.hasNext()) { var f = it.next(); var o = parse(f.getBlob().getDataAsString()); if (o) hub = merge(hub, o); used.push(f); }
    if (incoming) hub = merge(hub, incoming);
    hub.exportedAt = new Date().toISOString();
    file.setContent(JSON.stringify(hub));
    if (used.length) {
      var dest = inbox.getFoldersByName(MERGED); dest = dest.hasNext() ? dest.next() : inbox.createFolder(MERGED);
      used.forEach(function (f) { f.moveTo(dest); });
    }
    return { ok: true, progress: hub };
  } finally { lock.releaseLock(); }
}
function empty() { return { format: 'gpsc-cbrt-progress', version: 1, hub: true, exportedFrom: 'sync-hub', attempts: [], inProgress: [], customTests: [] }; }
function parse(t) {
  try { var o = JSON.parse(t); return o && o.format === 'gpsc-cbrt-progress' && Array.isArray(o.attempts) ? o : null; } catch (e) { return null; }
}
function merge(a, b) {
  var out = empty(), byId = {}, order = [];
  [a.attempts || [], b.attempts || []].forEach(function (list) {
    list.forEach(function (x) {
      if (!x || !x.id || !x.set || !x.answers) return;
      var k = String(x.id), cur = byId[k];
      if (!cur) { byId[k] = x; order.push(k); }
      else if (String(x.submittedAt || '') > String(cur.submittedAt || '')) byId[k] = x;
    });
  });
  out.attempts = order.map(function (k) { return byId[k]; })
    .sort(function (p, q) { return String(q.submittedAt).localeCompare(String(p.submittedAt)); });
  var prog = {};
  [a.inProgress || [], b.inProgress || []].forEach(function (list) {
    list.forEach(function (st) {
      if (!st || !st.set || st.phase !== 'exam') return;
      if (byId[st.set + '-' + st.startedAt]) return;            // already submitted
      var t = Number(st.savedAt || st.startedAt || 0), cur = prog[st.set];
      if (!cur || t > Number(cur.savedAt || cur.startedAt || 0)) prog[st.set] = st;
    });
  });
  out.inProgress = Object.keys(prog).map(function (k) { return prog[k]; });
  var cts = {};
  [a.customTests || [], b.customTests || []].forEach(function (list) { list.forEach(function (c) { if (c && c.id && !cts[c.id]) cts[c.id] = c; }); });
  out.customTests = Object.keys(cts).map(function (k) { return cts[k]; });
  out.summary = { attempts: out.attempts.length };
  return out;
}
