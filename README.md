# GPSCavy

Phone-first practice and study app for the **Goa PSC CBRT: Homoeopathic Physician** (1 Nov 2026).

**Open it:** https://raghav511.github.io/gpsc-avy/

On an Android phone, open the link in Chrome, then tap **⋮ → Add to Home screen** (or **Install app**). It then opens in one tap and works offline.

- 25 full mock sets, 9 Easy/Intermediate/Hard level tests, GK, English Grammar and Comprehension drills
- Custom tests by subject, core topic and difficulty, in exam or learn mode
- Topic 5–10 study notes with diagrams and quick-check quizzes, GK and English playbooks, printable PDFs
- Revise incorrect, progress tracking, and a progress file you can share on WhatsApp to sync with the mock-exam page

Shareable links: `#/tests`, `#/test/set14`, `#/study/topic9`, `#/progress`, `#/drills/gk`, `#/custom`.

## Repo layout

- `index.html`, `js/`, `sw.js`, `manifest.webmanifest`, `icons/`, `fonts/`: the app (vanilla JS, no framework, no build step needed to run)
- `data/`: generated from `content/` by `python3 tools/build.py` (small set index, one file per set, notes, playbooks, pools, search index)
- `content/`: question bank (`data/sets.json`), notes, playbooks, PDFs
- `design/`: approved screen designs and phone screenshots
- `reference/`: the working mock-exam page the engine is ported from
- `tests/acceptance.mjs`: SPEC §10 acceptance tests (Playwright)
- `tests/ai.mjs`: AI assistant tests (all four AI companies mocked)
- `tests/heal.mjs`: self-repair tests (broken cache, files that will not load, offline start, newer version on the site)
- `SPEC.md`: the full build spec

## Develop

```sh
python3 tools/build.py            # regenerate data/ and stamp the service-worker version
python3 -m http.server 8765       # from the folder above the repo, then open http://localhost:8765/gpsc-avy/
node tests/acceptance.mjs --profile pixel   # also: --profile iphone, --profile desktop, --profile ipad
node tests/ai.mjs --profile ipad
node tests/heal.mjs --profile ipad
```

Run `tools/build.py` after any change to `content/`, `js/` or `index.html`, so the service worker picks up the new version.

**Top right of every screen:** Update app, Sync progress and Settings (gear). Labels show on wide screens; icons on phones and iPad portrait. The sync button shows an orange dot when sync is not connected and a red dot when the last sync failed. Settings holds sync, the AI assistant, notes text size, backup files, the app version and Repair app.

**Sync progress**
- One button, top right of every screen. It combines this device, your other devices and the GPSC CBRT Mock Exam page in one file in your Google Drive (`GPSCavy sync/GPSCavy-progress.json`).
- Merging is a union: attempts are never removed; a later submission of the same attempt replaces the earlier one; a test in progress keeps its newest copy.
- The app also syncs by itself when it opens, 15 s after each test (after the Undo window) and when you leave it.
- The hub is a small Google Apps Script web app you own: `tools/sync-hub/Code.gs` (paste your Drive file and folder ids). Each device is connected once with the web app's `/exec` link.

**Updates** apply by themselves: a new version takes over the next time the app is opened or brought back, never in the middle of a test. To get it straight away, tap **Update app**. Progress is kept on the device and is never touched by an update.

**Self-repair.** The build stamps one version into `sw.js`, `version.json`, the page and every module URL (`js/core.js?v=…`), so a device can never run a mix of files from two versions. When online, each launch loads the newest page. Every launch also asks `version.json` which version is newest and fetches it if this copy is behind. If the app cannot start, the boot guard in `index.html` clears only the app's own files and service worker and starts again (twice), then shows a Repair screen that also retries by itself when back online. Attempts, tests in progress, the sync link and AI keys live in localStorage and are never touched.

**Google sign-in and sync for everyone.** Friends sign in with their own Google account; their progress (attempts, tests in progress, saved questions) is kept in a hidden app folder in *their own* Google Drive (`drive.appdata` scope), never with the owner. Set up once: a free Google Cloud project with the Drive API on, an OAuth consent screen (External, published, scopes `drive.appdata`, `openid`, `userinfo.email`, privacy page `privacy.html`), and a Web client with origin `https://raghav511.github.io` and redirect `https://raghav511.github.io/gpsc-avy/`. Put the client ID in `js/config.js`. Sign-in uses Google's redirect page (works in iPad/iPhone home-screen apps). Google gives browser apps a one-hour pass; after that a tap on Sync signs in again without a password. The owner's sync link (Apps Script hub) still works alongside.

**Paid access.** `tools/licence/Code.gs` runs in the owner's Google Sheet (setup steps at its top) and is the only judge of plans, prices, what is free, who has paid and voucher codes. Put its `/exec` link in `js/config.js` (`LICENCE_URL`). The owner signs in and opens Settings → Paid access to approve UPI payments, edit plans, tick free content and make single-use vouchers. With `LICENCE_URL` empty, everything is free. Tests run the real script in Node (`tests/licence-sim.mjs`).

**AI assistant.** Settings → AI assistant: choose Google Gemini, Anthropic Claude, OpenAI or OpenRouter, paste your own API key and pick a model (default: the company's recommended model, set in `PROVIDERS` in `js/ai.js`). Keys stay on the device. Videos and voice recordings need Gemini; photos and text work with all four.

When changing the app, run `python3 tools/build.py` before pushing: it stamps a new service-worker version, which is how phones and iPads notice the update.
