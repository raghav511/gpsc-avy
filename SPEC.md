# GPSCavy: build spec

GPSCavy is a phone-first study and test app for the **Goa Public Service Commission (GPSC) CBRT for Homoeopathic Physician** (exam on Sunday 1 November 2026).

It replaces several separate artifacts with one app:
- the mock exam;
- the GK and English drills;
- the Topic 5–10 study notes;
- the GK and English playbooks;
- the printable PDFs.

It is hosted on GitHub Pages from this repo and must work offline after the first load.

The design in `design/` was approved by the owner. Build to it: `design/screenshots/*.png` show each screen at 390×844, and `design/screens/*.dc.html` hold the full markup, copy and behaviour of each screen.

## 1. Hard rules

- **Static site only**: HTML + CSS + vanilla JS (or a small build that outputs static files into `docs/` or the repo root). No server and no login.
- **Phone first**: everything must work at 360–430 px width with thumb-reachable controls and tap targets of at least 44 px. It must also work on tablet and desktop.
- **Colourful, not black and white**:
  - Primary is indigo `#4338ca` / `#4f46e5`, with a saffron/amber accent `#f59e0b`.
  - Each section has its own colour, used everywhere that section appears:

    | Section | Colour |
    |---|---|
    | Comprehension | blue `#2563eb` |
    | Grammar | violet `#7c3aed` |
    | GK | amber `#d97706` |
    | Reasoning | teal `#0d9488` |
    | Core | pink `#db2777` |

  - Levels are green (Easy), amber (Intermediate) and red (Hard).
  - Light and dark themes both follow `prefers-color-scheme`.
- **Every screen has a way back**: a back button or bottom nav. The only exception is the test runner, which shows a back arrow that asks "Leave test? Your answers are saved".
- **Submitting a test needs a confirmation step**:
  1. Show the counts of answered, unanswered and flagged questions.
  2. After submitting, show a short **Undo** (about 10 s) that reopens the test exactly where it was.
- **Content must match the button**: a button labelled X opens X.
  - "English drills" opens English drills, not Practice Set 14.
  - A custom test with only English contains no GK questions.
  - A subject chip in Study opens that subject.
  - Write an automated test for this (see §9).
- **Never change question ids or set ids.** Saved progress refers to them.
- **Installable PWA**:
  - `manifest.webmanifest`, icons and a service worker that caches the app shell plus `content/`.
  - Add an "Add to Home screen" hint on first visit, on mobile only.
- **Shareable links**: hash routes such as `#/tests`, `#/test/set14`, `#/study/topic9`, `#/progress`. These deep-link correctly when sent over WhatsApp.

## 2. Content (all in `content/`)

| Path | What it is |
|---|---|
| `content/data/sets.json` | `{sets:[…], papers:[…]}`: every test (see §3) |
| `content/notes/topic5.html` … `topic10.html` | Study notes (HTML fragments, no `<html>`). Diagrams are inline SVG in `<figure class="diagram">`. Colours use `var(--cds-*, fallback)`, so the app should define the `--cds-*` tokens for light and dark (fallbacks are light theme). |
| `content/playbooks/gk-playbook.html`, `english-playbook.html` | Full-page GK and English playbooks. Extract the `<body>` content and restyle it to the app theme. Keep all text. |
| `content/pdfs/*.pdf` | Printable sets: 1–25 individually and combined, level tests, GK drills, English drills, Topic 8 notes. Listed in Study → PDFs, opened in a new tab and shareable. |
| `reference/mock-exam-standalone.html` | **The working reference implementation** of the exam engine (timer, palette, flagging, save/resume, results, review, level breakdown, progress download and upload). Port its logic; don't reinvent it. |

The notes contain no allopathic pharmacology, apart from vaccines, which are kept. Do not add any.

## 3. Data model (`sets.json`)

### 3.1 Test sets

Each set has these fields:

```
{ id, set (display name), minutes, sections:[{id,name,short,marks}], passages:{pid:{title,paras:[…]}},
  questions:[{n, sec, q, opts:[4], ans:'A'..'D', why, passage?, lvl:'E'|'I'|'H'}],
  core?, level?, levelIndex?, lvlset?, mix?, drill?, group?, short?, hidden? }
```

| Kind | How to recognise it | Count | Details |
|---|---|---|---|
| Practice sets | `set1v3`, `set2v3` … (no `drill`/`hidden`/`lvlset`) | 25 | 60 questions, 75 min. Sections: comp 10, gram 5, gk 10, lr 10, core 25. `core` names the core subject. `level` is one of easy, intermediate or hard. |
| Level tests | `lvlset` | 9 | `lvl-easy-1..3`, `lvl-intermediate-1..3`, `lvl-hard-1..3`. `mix` shows the E/I/H counts. |
| GK drills | `gkd1..6` | 6 | `drill:true`, single section `gk`, 15 min |
| English drills | `end1..4` | 4 | `drill:true, group:'en'`. These are **Grammar drills** and go under English → Grammar. |
| Legacy sets | `hidden:true` | — | Old versions of sets. Never list them, but keep them so that old attempts can be re-graded and reviewed. |

Comprehension drills are passage-based questions (`sec:'comp'`) gathered from the practice sets, grouped by passage. See `design/screens/DrillComp.dc.html`.

Section ids are `comp`, `gram`, `gk`, `lr` and `core`. Always display the sections in that order.

The difficulty of a set is the mean of its questions' `lvl` values, with E=1, I=2 and H=3:

| Mean | Level |
|---|---|
| ≤ 1.75 | Easy |
| ≤ 1.95 | Intermediate |
| > 1.95 | Hard |

Show the level as a coloured chip on every set card.

### 3.2 `papers`

`papers` lists past GPSC question papers (`date`, `post`, `url`, `match`). List them in Study → Past papers as external links.

## 4. Screens (see `design/`)

Bottom navigation has four tabs: **Home · Tests · Study · Progress**.

### 4.1 Home (`Main`)

- Header: the GPSCavy logo and a search button. Search covers questions, notes and sets.
- **Exam countdown card**: days left until 1 Nov 2026, the exam format, and the last score as a badge.
- **Resume card**, shown when a test is in progress: set name, answered/total, current question, time left and a progress bar.
- Two big buttons:
  - **Full mock**: picks the next unattempted practice set, or the least recent one.
  - **Pick subjects**: opens the custom test builder.
- **Accuracy by section** bars, in section colours, with a "Weakest: X. Practise X drills" link that goes to the right drills.
- **Today's read**: rotates through Topics 5–10 and links to the notes and their quiz.
- **Sync card** (see §6): **Download progress** and **Upload progress**, plus "last synced" text.

### 4.2 Tests (`Tests`)

Four tabs: **Mock sets · By level · Drills · My tests**.

**Mock sets**
- Lists the 25 sets with a level chip, the core subject, and the best score with its date.
- A level filter: All, Easy, Intermediate, Hard.

**By level**
- The 9 level tests, grouped Easy, Intermediate, Hard.
- Each shows its E/I/H mix.

**Drills**
- Three groups. Each opens its own picker:
  - GK drills (`DrillGk`);
  - English Grammar drills (`DrillEn`);
  - English Comprehension drills (`DrillComp`).

**My tests**
- Saved custom tests and past attempts.
- Each opens its review: score, wrong answers and time used.

**Mode choice before a test starts**
- **Exam mode**: timer runs, no answers until submit.
- **Learn mode**: answer revealed with its explanation after each question (`Learn`).

### 4.3 Custom test builder (`Custom`)

- Pick subjects with multi-select chips: Comprehension, Grammar, GK, Reasoning, Core.
- Choose a question count for each subject. Core can be narrowed to core subjects (the `core` names of sets).
- Difficulty: Any, Easy, Medium (= Intermediate) or Hard. This filters questions by `lvl`.
- Time: auto (75 min × fraction of 60) or a custom value.
- Mode: Exam or Learn.
- **No repeats** toggle: excludes questions already answered correctly.
- **Save as my test**, or start now.
- Comprehension questions always come with their passage, keeping passage groups together.
- The test must contain **only** the chosen subjects.

### 4.4 Test runner (`Question`)

The behaviour comes from the reference implementation.

**Top bar**
- Back arrow, set name, countdown timer, and a palette button.

**Question view**
- The passage is collapsible on top for comp questions.
- Four large option buttons.
- Flag for review, Clear, Previous and Next.

**Palette sheet**
- Question grid coloured by state: answered, flagged, unanswered, current.
- Grouped by section, with section colours.

**Saving and timing**
- Autosave state on every change (`localStorage`), so a reload or app close resumes the test.
- The timer keeps counting from the saved remaining time.
- When the time is up, the test auto-submits, marked as auto.

**Submit**
- Use the confirm step and the Undo window described in §1.

### 4.5 Results and review

- Score out of total, accuracy, and time used.
- Score by section and by level (E/I/H), each shown as bars.
- Review list: filter by All, Wrong, Skipped or Flagged, and by section. Each item shows your answer, the correct answer and the explanation (`why`), with a level chip.
- Buttons: **Retake wrong only**, **Back to tests**, **Home**.

### 4.6 Study (`Study`, `Notes`, `Quiz9`)

**Subject chips**
- All, Core, GK, English Grammar, English Comprehension, PDFs, **Revise incorrect**.
- Every chip is tappable and opens its own list.

**Core**
- Topic 5–10 notes cards.
- The reader (`Notes`) has:
  - a sticky contents list;
  - collapsible sections;
  - tables that scroll sideways on their own;
  - diagrams that scale to fit.
- Each topic has a **Quick-check quiz**: the 20 MCQs at the end of each note, playable in Learn mode (`Quiz9`).

**GK**
- The GK playbook (Goa and India GK — **Goa, not Gujarat**) and the GK drills.

**English Grammar / Comprehension**
- The English playbook, split by its grammar and comprehension parts.
- The matching drills.

**PDFs**
- Every PDF, opened and shareable.

**Revise incorrect**
- Sub-chips: All, Core, GK, English Comprehension, English Grammar, PDFs.
- Shows every question answered wrong in any attempt, de-duplicated, latest first.
- From there:
  - practise them as a test;
  - for Core, jump to the related notes topic.
- The PDFs sub-chip lists the PDF sets those wrong questions came from.

### 4.7 Progress (`Progress`)

- Attempts timeline, with a score trend line.
- Best and average score per section.
- Level breakdown.
- A heatmap of practice days.
- Weak areas, each linking to drills.
- The full sync controls (§6).

## 5. Storage

- Use `localStorage` (or IndexedDB) for attempts, in-progress tests, custom tests and settings. Wrap every access in try/catch.
- Attempt shape:

  ```
  {id, set, setName, score, total, wrong, skipped, usedMs, auto, submittedAt, answers}
  ```

  - `answers` maps question `n` to `'A'..'D'`.
  - The flag list sits beside it in the in-progress state.
- Re-grade an attempt against `sets.json` by id. A legacy set id resolves to the hidden set.

## 6. Progress file (sync with the mock-exam artifact) — must stay compatible

The progress file is a single JSON file. It must be small enough to send on WhatsApp. Name it `GPSC-progress-YYYY-MM-DD.json`.

```
{ "format":"gpsc-cbrt-progress", "version":1, "exportedAt":ISO, "exportedFrom":"gpscavy-app",
  "note":"…", "summary":{"attempts":N,"best":{setId:score}},
  "attempts":[attempt…], "inProgress":[savedTestState…] }
```

**Download**
- Use the Web Share API with a file when it is available. This puts **WhatsApp** in the phone share sheet directly.
- Otherwise fall back to a normal file download.

**Upload**
- Use a file picker.
- Validate `format` and `version`.
- **Merge, never overwrite**:
  - add only attempt `id`s that are missing;
  - an in-progress test replaces the local one only when it is newer.
- Report the result, e.g. "Added 3 attempts, 10 already here".

**Compatibility**
- Files exported by the mock-exam artifact (`exportedFrom:"mock-exam"`) must import cleanly, and the app's files must import into the artifact.
- Set ids are shared, e.g. `set1v3`, `set12v2`, `lvl-easy-1`.

## 7. Visual system

- Fonts: Plus Jakarta Sans for UI and headings, Inter for body text (Google Fonts), with system fallbacks.
- Cards: radius 20–24 px, soft shadows, background `#f4f4fb` (light) or `#12121c` (dark).
- Section colours as in §1, with tinted "soft" variants for backgrounds.
- Motion: subtle 150–200 ms transitions. Respect `prefers-reduced-motion`.
- Accessibility:
  - contrast at least 4.5:1;
  - focus rings;
  - `aria-label`s on icon buttons;
  - options as `<button>`s with `aria-pressed`.

## 8. Hosting

- Serve with GitHub Pages from the `main` branch: root, or `/docs` if a build step is used.
- All asset paths must be relative, because the site lives at `/gpsc-avy/`.
- Show the public URL in the README.

## 9. Acceptance tests

Run with Playwright at 390×844, then at 1280×800.

1. Every tab and every button navigates, and every non-root screen has a working back control.
2. **Content matches labels**:
   - for every set, drill and level card, the opened test's title and question sections match the card;
   - a custom test with only Grammar contains only `gram` questions, and the same holds for every subject;
   - each Study chip shows the right list.
3. **Test runner**: answer, flag, the palette, a reload in the middle of a test, the timer resuming, submit with the confirm step and Undo, and auto-submit at 0.
4. **Results**: section and level breakdowns add up to the total. The review filters work.
5. **Revise incorrect** shows exactly the wrong answers from the stored attempts, per sub-chip.
6. **Sync**:
   - export, clear storage, import: the data is identical;
   - importing the same file twice adds nothing;
   - a file in the mock-exam format imports.
7. **Notes**: all 15 diagrams render, and wide tables don't cause horizontal page scroll.
8. No console errors. Lighthouse PWA installable, and performance at least 85 on mobile.
