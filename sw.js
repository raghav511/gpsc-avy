// GPSCavy service worker. The version is stamped by tools/build.py from a hash of the shell and data files.
const V = 'gpscavy-c427c7ec6d';
const SHELL = ['./', 'index.html', 'js/app.js', 'js/core.js', 'js/runner.js', 'js/study.js', 'manifest.webmanifest',
  'icons/icon-180.png', 'icons/icon-192.png', 'icons/icon-512.png', 'fonts/jakarta-latin.woff2', 'fonts/inter-latin.woff2',
  'data/index.json', 'data/meta.json', 'data/keys.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL.map(u => new Request(u, { cache: 'reload' })))));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('gpscavy-') && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('message', e => { if (e.data === 'skipWaiting') self.skipWaiting(); });

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method === 'POST' && new URL(req.url).pathname.endsWith('/share-target')) {
    // A progress file shared into the app from WhatsApp or Files: park it, then open the app on the upload preview.
    e.respondWith(req.formData().then(fd => {
      const f = fd.getAll('file').find(x => x && typeof x !== 'string');
      if (!f) return Response.redirect('./?shared=1#/', 303);
      return caches.open('inbox-gpscavy').then(c => c.put('inbox', new Response(f, { headers: { 'x-name': encodeURIComponent(f.name || 'shared-file.json') } })))
        .then(() => Response.redirect('./?shared=1#/', 303));
    }).catch(() => Response.redirect('./?shared=1#/', 303)));
    return;
  }
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  const path = url.pathname.slice(self.registration.scope.length - location.origin.length);
  if (path.startsWith('content/pdfs/')) return; // PDFs are never cached: fetched only when opened
  if (req.mode === 'navigate') {
    e.respondWith(caches.open(V).then(c => c.match('index.html').then(hit => hit || fetch(req))));
    return;
  }
  // shell files: cache first (versioned); data files: stale-while-revalidate
  e.respondWith(caches.open(V).then(c => c.match(req, { ignoreSearch: true }).then(hit => {
    const net = fetch(req).then(res => { if (res.ok && res.type === 'basic') c.put(req, res.clone()); return res; });
    if (hit) { if (path.startsWith('data/')) net.catch(() => { }); return hit; }
    return net;
  })));
});
