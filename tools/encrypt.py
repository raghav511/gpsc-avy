#!/usr/bin/env python3
"""Scramble the content of a built copy of GPSCavy, in place, for the public website.

  python3 tools/encrypt.py DIST_DIR KEY_FILE

Each content file is AES-256-GCM encrypted with its own key, HMAC-SHA256(master key, item name); the item names match
js/vault.js and the free list in the owner's access script (tools/licence/Code.gs), which hands the keys out.
File layout: b'GPSCAVY1' + 12-byte nonce + ciphertext with tag. index/meta/answer-key JSON, pictures and the app stay plain.
"""
import base64, hmac, hashlib, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b'GPSCAVY1'


def item_for(path):
    p = path.replace(os.sep, '/')
    m = re.match(r'^data/sets/(.+)\.json$', p)
    if m: return 'set:' + m.group(1)
    m = re.match(r'^data/notes/topic(\d+)\.html$', p)
    if m: return 'notes:' + m.group(1)
    m = re.match(r'^data/playbooks/(gk|english)-playbook\.html$', p)
    if m: return 'playbook:' + m.group(1)
    if p == 'data/search.json': return 'search'
    if p.startswith('data/pool/'): return 'custom'
    m = re.match(r'^content/pdfs/Topic-(\d+)-.*\.pdf$', p)
    if m: return 'notes:' + m.group(1)
    if p.startswith('content/pdfs/') and p.endswith('.pdf'): return 'pdfs'
    return None


def item_key(master, item):
    return hmac.new(master, item.encode(), hashlib.sha256).digest()


def main(dist, key_file):
    master = base64.b64decode(open(key_file).read().strip())
    assert len(master) == 32, 'the master key must be 32 bytes'
    n = 0
    for root, _, files in os.walk(dist):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, dist)
            item = item_for(rel)
            if not item: continue
            data = open(full, 'rb').read()
            if data.startswith(MAGIC): continue
            nonce = os.urandom(12)
            open(full, 'wb').write(MAGIC + nonce + AESGCM(item_key(master, item)).encrypt(nonce, data, None))
            n += 1
    print('encrypted', n, 'files')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
