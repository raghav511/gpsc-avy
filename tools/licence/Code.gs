// GPSCavy paid access. Keeps your plans, what is free, who has paid and which voucher codes are used, in YOUR Google Sheet.
// It never sees anyone's progress: only their Gmail address, the plan they chose, the UPI reference they typed, and vouchers.
//
// Set up once (about 5 minutes):
//  1. Create a Google Sheet named "GPSCavy access". Extensions → Apps Script. Paste this whole file. Fill in the 4 values below.
//  2. Run setup() once (Run ▶, allow access). It makes the Users, Vouchers, Plans and Settings tabs.
//  3. Deploy → New deployment → Web app. Execute as: Me. Who has access: Anyone. Send the /exec link to Claude (it goes in js/config.js).
//
// Everything else (plans, prices, what is free, approving people, vouchers) is done in the app: sign in as OWNER_EMAIL,
// then Settings → Paid access. You can also edit the tabs by hand.
var OWNER_EMAIL = 'PASTE_YOUR_GMAIL';                          // you: always has access, and sees the admin screen
var CLIENT_ID = 'PASTE_GOOGLE_CLIENT_ID';                      // the app's Google sign-in client ID (…apps.googleusercontent.com)
var UPI_ID = 'PASTE_YOUR_UPI_ID';                               // for example yourname@okhdfcbank
var UPI_NAME = 'PASTE_NAME_SHOWN_IN_UPI';                       // the payee name people see in their UPI app

var T = { users: 'Users', vouchers: 'Vouchers', plans: 'Plans', settings: 'Settings' };
var COLS = {
  Users: ['Email', 'Status', 'How', 'UPI reference or voucher', 'Name', 'Requested', 'Approved', 'Plan', 'Days', 'Expires', 'Note'],
  Vouchers: ['Code', 'Used by', 'Used on', 'Made on', 'Days (0 = no end)', 'Note'],
  Plans: ['Plan', 'Days', 'Price (₹)', 'Active'],
  Settings: ['Setting', 'Value']
};
var U = { email: 0, status: 1, how: 2, ref: 3, name: 4, requested: 5, approved: 6, plan: 7, days: 8, expires: 9, note: 10 };

function setup() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  Object.keys(COLS).forEach(function (n) {
    var sh = ss.getSheetByName(n) || ss.insertSheet(n);
    if (sh.getLastRow() === 0) { sh.appendRow(COLS[n]); sh.setFrozenRows(1); sh.getRange(1, 1, 1, COLS[n].length).setFontWeight('bold'); }
  });
  var plans = ss.getSheetByName(T.plans);
  if (plans.getLastRow() === 1) { plans.appendRow(['1 week', 7, 199, 'yes']); plans.appendRow(['1 month', 30, 500, 'yes']); }
  var st = ss.getSheetByName(T.settings);
  if (st.getLastRow() === 1) st.appendRow(['free', JSON.stringify(['set:set1v3', 'notes:1'])]);
}

function doGet() { return out({ ok: true, service: 'gpscavy-licence', version: 2 }); }
function doPost(e) {
  var body = {};
  try { body = JSON.parse(e.postData.contents); } catch (x) { return out({ ok: false, error: 'bad_json' }); }
  try { return out(handle(body, whoIs(body.token))); }
  catch (x) { return out({ ok: false, error: String(x && x.message || x) }); }
}
function out(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

// The app sends the Google sign-in pass it already has; Google tells us whose it is, and that it was made for this app.
function whoIs(token) {
  if (!token) return '';
  var r = UrlFetchApp.fetch('https://oauth2.googleapis.com/tokeninfo?access_token=' + encodeURIComponent(token), { muteHttpExceptions: true });
  if (r.getResponseCode() !== 200) return '';
  var t = JSON.parse(r.getContentText());
  if ((t.aud || t.azp) !== CLIENT_ID || !t.email || String(t.email_verified) !== 'true') return '';
  return String(t.email).toLowerCase();
}

function handle(b, email) {
  if (!email && b.action === 'status') return { ok: true, email: '', status: 'none', owner: false, plans: plans(), free: free(), upi: UPI_ID, upiName: UPI_NAME }; // what anyone may see before signing in
  if (!email) return { ok: false, error: 'signin' };
  var owner = email === OWNER_EMAIL.toLowerCase();
  var a = b.action;
  if (a === 'status') return status(email, owner);
  if (a === 'request') return withLock(function () { return request(email, b); });
  if (a === 'voucher') return withLock(function () { return voucher(email, b.code); });
  if (!owner) return { ok: false, error: 'not_owner' };
  if (a === 'admin') return admin();
  if (a === 'approve' || a === 'reject' || a === 'revoke') return withLock(function () { return decide(String(b.email || '').toLowerCase(), a, b.days); });
  if (a === 'vouchers') return withLock(function () { return makeVouchers(Math.max(1, Math.min(50, +b.count || 1)), Math.max(0, +b.days || 0), String(b.note || '')); });
  if (a === 'plans') return withLock(function () { return savePlans(b.plans); });
  if (a === 'free') return withLock(function () { return saveFree(b.free); });
  return { ok: false, error: 'unknown_action' };
}
function withLock(f) { var l = LockService.getScriptLock(); l.waitLock(20000); try { return f(); } finally { l.releaseLock(); } }
function sheet(n) { return SpreadsheetApp.getActiveSpreadsheet().getSheetByName(n); }
function rows(n) { var v = sheet(n).getDataRange().getValues(); return v.slice(1).map(function (r, i) { return { r: r, row: i + 2 }; }); }
function findUser(email) { var all = rows(T.users); for (var i = 0; i < all.length; i++) if (String(all[i].r[U.email]).toLowerCase() === email) return all[i]; return null; }
function now() { return new Date(); }
function iso(d) { return d instanceof Date ? d.toISOString() : d ? String(d) : ''; }
function addDays(d, n) { return n > 0 ? new Date(d.getTime() + n * 86400000) : ''; }
function setUser(email, vals) {
  var u = findUser(email), sh = sheet(T.users), row = u ? u.r.slice() : [email];
  while (row.length < COLS.Users.length) row.push('');
  Object.keys(vals).forEach(function (k) { row[U[k]] = vals[k]; });
  if (u) sh.getRange(u.row, 1, 1, row.length).setValues([row]); else sh.appendRow(row);
}
function plans() { return rows(T.plans).filter(function (x) { return String(x.r[3] || 'yes').toLowerCase() !== 'no' && x.r[0]; }).map(function (x) { return { name: String(x.r[0]), days: +x.r[1] || 0, price: +x.r[2] || 0 }; }); }
function setting(k) { var s = rows(T.settings); for (var i = 0; i < s.length; i++) if (s[i].r[0] === k) return s[i]; return null; }
function free() { var s = setting('free'); try { var v = JSON.parse(s ? s.r[1] : '[]'); return Array.isArray(v) ? v : []; } catch (e) { return []; } }

function state(u) {
  if (!u) return { status: 'none' };
  var st = String(u.r[U.status] || 'pending').toLowerCase(), exp = u.r[U.expires];
  if (st === 'paid' && exp && new Date(exp).getTime() < Date.now()) st = 'expired';
  if (['paid', 'pending', 'rejected', 'expired', 'revoked'].indexOf(st) < 0) st = 'pending'; // anything else typed in the Sheet counts as waiting
  return { status: st, how: String(u.r[U.how] || ''), plan: String(u.r[U.plan] || ''), expires: iso(exp), requested: iso(u.r[U.requested]) };
}
function status(email, owner) {
  var s = owner ? { status: 'paid', how: 'owner', plan: '', expires: '' } : state(findUser(email));
  s.ok = true; s.email = email; s.owner = owner; s.plans = plans(); s.free = free(); s.upi = UPI_ID; s.upiName = UPI_NAME;
  return s;
}
function request(email, b) {
  var utr = String(b.utr || '').replace(/\s+/g, '');
  if (!/^[A-Za-z0-9]{8,30}$/.test(utr)) return { ok: false, error: 'bad_reference' };
  var p = plans().filter(function (x) { return x.name === b.plan; })[0];
  if (!p) return { ok: false, error: 'bad_plan' };
  if (state(findUser(email)).status === 'paid') return status(email, false);
  // one UPI reference can only be claimed once
  var taken = rows(T.users).some(function (x) { return String(x.r[U.ref]).toUpperCase() === utr.toUpperCase() && String(x.r[U.email]).toLowerCase() !== email; });
  if (taken) return { ok: false, error: 'reference_used' };
  setUser(email, { status: 'pending', how: 'UPI ₹' + p.price, ref: utr, name: String(b.name || '').slice(0, 60), requested: now(), approved: '', plan: p.name, days: p.days, expires: '' });
  return status(email, false);
}
function voucher(email, code) {
  code = String(code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
  if (code.length < 6) return { ok: false, error: 'bad_code' };
  var vs = rows(T.vouchers), v = null;
  for (var i = 0; i < vs.length; i++) if (String(vs[i].r[0]).toUpperCase().replace(/[^A-Z0-9]/g, '') === code) { v = vs[i]; break; }
  if (!v) return { ok: false, error: 'bad_code' };
  var usedBy = String(v.r[1] || '').toLowerCase();
  if (usedBy && usedBy !== email) return { ok: false, error: 'code_used' };   // single use: already claimed by someone else
  if (usedBy === email) return status(email, false);
  if (state(findUser(email)).status === 'paid') return { ok: false, error: 'already_paid' }; // keep the code for someone else
  var days = +v.r[4] || 0, t = now();
  sheet(T.vouchers).getRange(v.row, 2, 1, 2).setValues([[email, t]]);
  setUser(email, { status: 'paid', how: 'Voucher', ref: String(v.r[0]), requested: t, approved: t, plan: days ? days + ' days (voucher)' : 'Voucher, no end', days: days, expires: addDays(t, days) });
  return status(email, false);
}
function decide(email, action, days) {
  var u = findUser(email); if (!u) return { ok: false, error: 'no_such_user' };
  if (action === 'approve') { var d = days !== undefined && days !== '' && !isNaN(+days) ? +days : +u.r[U.days] || 0, t = now(); setUser(email, { status: 'paid', approved: t, days: d, expires: addDays(t, d) }); }
  else setUser(email, { status: action === 'reject' ? 'rejected' : 'revoked' });
  return admin();
}
function makeVouchers(n, days, note) {
  var sh = sheet(T.vouchers), made = [], have = {};
  rows(T.vouchers).forEach(function (v) { have[String(v.r[0])] = 1; });
  var A = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // no 0/O or 1/I to misread
  while (made.length < n) {
    var c = 'GPS-'; for (var i = 0; i < 8; i++) { c += A.charAt(Math.floor(Math.random() * A.length)); if (i === 3) c += '-'; }
    if (have[c]) continue; have[c] = 1; made.push(c);
    sh.appendRow([c, '', '', now(), days, note]);
  }
  var res = admin(); res.made = made; return res;
}
function savePlans(ps) {
  if (!Array.isArray(ps)) return { ok: false, error: 'bad_plans' };
  ps = ps.filter(function (p) { return p && String(p.name || '').trim() && +p.price > 0 && +p.days >= 0; }).slice(0, 8);
  var sh = sheet(T.plans), last = sh.getLastRow();
  for (var r = 2; r <= last; r++) sh.getRange(r, 1, 1, 4).setValues([['', '', '', '']]);
  ps.forEach(function (p, i) { sh.getRange(i + 2, 1, 1, 4).setValues([[String(p.name).trim().slice(0, 40), Math.round(+p.days), Math.round(+p.price), 'yes']]); });
  return admin();
}
function saveFree(list) {
  if (!Array.isArray(list)) return { ok: false, error: 'bad_free' };
  list = list.filter(function (x) { return typeof x === 'string' && /^[a-z]+(:[A-Za-z0-9_-]+)?$/.test(x); }).slice(0, 300);
  var s = setting('free');
  if (s) sheet(T.settings).getRange(s.row, 2).setValue(JSON.stringify(list)); else sheet(T.settings).appendRow(['free', JSON.stringify(list)]);
  return admin();
}
function admin() {
  var us = rows(T.users).filter(function (x) { return x.r[0]; }).map(function (x) { var s = state(x); return { email: String(x.r[U.email]), status: s.status, how: s.how, ref: String(x.r[U.ref] || ''), name: String(x.r[U.name] || ''), plan: s.plan, days: +x.r[U.days] || 0, requested: s.requested, approved: iso(x.r[U.approved]), expires: s.expires }; });
  var vs = rows(T.vouchers).filter(function (x) { return x.r[0]; }).map(function (x) { return { code: String(x.r[0]), usedBy: String(x.r[1] || ''), usedOn: iso(x.r[2]), made: iso(x.r[3]), days: +x.r[4] || 0, note: String(x.r[5] || '') }; });
  return { ok: true, owner: true, users: us, vouchers: vs, plans: plans(), free: free(), upi: UPI_ID, upiName: UPI_NAME };
}
