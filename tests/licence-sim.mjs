// Runs tools/licence/Code.gs (the real script) in Node with an in-memory Google Sheet, so the app's tests talk to the
// same logic the owner deploys. tokens: { token: email } stands in for Google's tokeninfo.
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
export function licenceSim(conf) {
  const tabs = {};
  const mkSheet = name => {
    const data = [];
    const sh = {
      getLastRow: () => data.length,
      appendRow: r => { data.push(r.slice()); },
      setFrozenRows: () => { }, getRange: (row, col, nr, nc) => ({
        setFontWeight: () => { },
        setValues: v => { for (let i = 0; i < (nr || 1); i++) for (let j = 0; j < (nc || 1); j++) { while (data.length < row + i) data.push([]); data[row - 1 + i][col - 1 + j] = v[i][j]; } },
        setValue: v => { while (data.length < row) data.push([]); data[row - 1][col - 1] = v; }
      }),
      getDataRange: () => ({ getValues: () => data.map(r => r.slice()) }), _data: data
    };
    return sh;
  };
  const ss = { getSheetByName: n => tabs[n] || null, insertSheet: n => (tabs[n] = mkSheet(n)) };
  const tokens = conf.tokens || {};
  const ctx = {
    SpreadsheetApp: { getActiveSpreadsheet: () => ss },
    LockService: { getScriptLock: () => ({ waitLock() { }, releaseLock() { } }) },
    UrlFetchApp: { fetch: u => { const t = decodeURIComponent(u.split('access_token=')[1]); const e = tokens[t]; return { getResponseCode: () => e ? 200 : 400, getContentText: () => JSON.stringify(e ? { aud: conf.clientId, email: e, email_verified: 'true' } : { error: 'invalid' }) }; } },
    ContentService: { createTextOutput: t => ({ setMimeType() { return t; } }), MimeType: { JSON: 1 } },
    Date, Math, JSON, String
  };
  let src = fs.readFileSync(path.join(ROOT, 'tools/licence/Code.gs'), 'utf8')
    .replace("var OWNER_EMAIL = 'PASTE_YOUR_GMAIL';", "var OWNER_EMAIL = " + JSON.stringify(conf.owner) + ";")
    .replace(/var CLIENT_ID = '[^']*';/, "var CLIENT_ID = " + JSON.stringify(conf.clientId) + ";")
    .replace("var UPI_ID = 'PASTE_YOUR_UPI_ID';", "var UPI_ID = 'owner@okbank';").replace("var UPI_NAME = 'PASTE_NAME_SHOWN_IN_UPI';", "var UPI_NAME = 'GPSCavy Owner';");
  vm.createContext(ctx); vm.runInContext(src, ctx);
  ctx.setup();
  return { post: body => JSON.parse(ctx.doPost({ postData: { contents: typeof body === 'string' ? body : JSON.stringify(body) } })), tabs, tokens };
}
