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
- `SPEC.md`: the full build spec

## Develop

```sh
python3 tools/build.py            # regenerate data/ and stamp the service-worker version
python3 -m http.server 8765       # from the folder above the repo, then open http://localhost:8765/gpsc-avy/
node tests/acceptance.mjs --profile pixel   # also: --profile iphone, --profile desktop
```

Run `tools/build.py` after any change to `content/`, `js/` or `index.html`, so the service worker picks up the new version.
