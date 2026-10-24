#!/bin/sh
# Build the public website copy of GPSCavy: only the app and the content it needs, with the content scrambled.
#   sh tools/publish.sh OUT_DIR KEY_FILE
# OUT_DIR is replaced. The readable sources (content/data, notes, playbooks), tools, tests and design never go in it.
set -e
SRC=$(cd "$(dirname "$0")/.." && pwd)
OUT=$1; KEY=$2
[ -n "$OUT" ] && [ -f "$KEY" ] || { echo "usage: sh tools/publish.sh OUT_DIR KEY_FILE"; exit 1; }
find "$OUT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} + 2>/dev/null || mkdir -p "$OUT"
mkdir -p "$OUT/content"
cd "$SRC"
cp index.html privacy.html manifest.webmanifest sw.js version.json "$OUT/"
cp -R js icons fonts data "$OUT/"
cp -R content/pdfs "$OUT/content/"
rm -f "$OUT/content/pdfs/notes-pdf.json"
find "$OUT" -name '__pycache__' -prune -exec rm -rf {} +
cat > "$OUT/README.md" <<'MD'
# GPSCavy

Practice and study app for the Goa PSC CBRT: Homoeopathic Physician. **Open it:** https://raghav511.github.io/gpsc-avy/

This repository holds only the published app. Its questions, notes and PDFs are stored encrypted and unlock in the app for signed-in users.
MD
touch "$OUT/.nojekyll"
python3 "$SRC/tools/encrypt.py" "$OUT" "$KEY"
echo "published copy in $OUT"
