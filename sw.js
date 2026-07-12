// sw_template.js - source template for the generated sw.js.
//
// build.py copies this file to sw.js at the repo root, replacing:
//   26    -> integer version number from version.json (drives the shell cache name)
//   ["./", "index.html", "manifest.json", "icons/gg-192.png", "icons/gg-512.png", "icons/gg-maskable-512.png", "fonts/cormorant-garamond-cyrillic-400-italic.woff2", "fonts/cormorant-garamond-cyrillic-700.woff2", "fonts/cormorant-garamond-cyrillic-ext-400-italic.woff2", "fonts/cormorant-garamond-cyrillic-ext-700.woff2", "fonts/cormorant-garamond-latin-400-italic.woff2", "fonts/cormorant-garamond-latin-700.woff2", "fonts/cormorant-garamond-latin-ext-400-italic.woff2", "fonts/cormorant-garamond-latin-ext-700.woff2", "fonts/cormorant-garamond-vietnamese-400-italic.woff2", "fonts/cormorant-garamond-vietnamese-700.woff2", "fonts/crimson-text-latin-400-italic.woff2", "fonts/crimson-text-latin-400.woff2", "fonts/crimson-text-latin-600.woff2", "fonts/crimson-text-latin-700.woff2", "fonts/crimson-text-latin-ext-400-italic.woff2", "fonts/crimson-text-latin-ext-400.woff2", "fonts/crimson-text-latin-ext-600.woff2", "fonts/crimson-text-latin-ext-700.woff2", "fonts/crimson-text-vietnamese-400-italic.woff2", "fonts/crimson-text-vietnamese-400.woff2", "fonts/crimson-text-vietnamese-600.woff2", "fonts/crimson-text-vietnamese-700.woff2", "fonts/noto-serif-cyrillic-400-italic.woff2", "fonts/noto-serif-cyrillic-700.woff2", "fonts/noto-serif-cyrillic-ext-400-italic.woff2", "fonts/noto-serif-cyrillic-ext-700.woff2", "fonts/noto-serif-greek-400-italic.woff2", "fonts/noto-serif-greek-700.woff2", "fonts/noto-serif-greek-ext-400-italic.woff2", "fonts/noto-serif-greek-ext-700.woff2", "fonts/noto-serif-latin-400-italic.woff2", "fonts/noto-serif-latin-700.woff2", "fonts/noto-serif-latin-ext-400-italic.woff2", "fonts/noto-serif-latin-ext-700.woff2", "fonts/noto-serif-math-400-italic.woff2", "fonts/noto-serif-math-700.woff2", "fonts/noto-serif-vietnamese-400-italic.woff2", "fonts/noto-serif-vietnamese-700.woff2", "fonts/playfair-display-cyrillic-700.woff2", "fonts/playfair-display-latin-700.woff2", "fonts/playfair-display-latin-ext-700.woff2", "fonts/playfair-display-vietnamese-700.woff2"]  -> JSON array of shell asset URLs (./  index.html  manifest.json
//                         icons/*  fonts/*.woff2)
//
// Two-tier cache architecture (see plan doc, architecture decision (c)):
//   - shell-v{N}  : the app shell (HTML/manifest/icons/fonts). Small, rotates every
//                    build, updates silently (skipWaiting) since it's cheap to refetch.
//   - media-v1    : the offline audio library. Never rotates with the shell version;
//                    only ever grows/shrinks via explicit DOWNLOAD_ASSETS / PRUNE
//                    messages from the page, or lazily on first play while online.

const SW_VERSION = '26';
const SHELL_CACHE = 'shell-v' + SW_VERSION;
const MEDIA_CACHE = 'media-v1';
const SHELL_ASSETS = ["./", "index.html", "manifest.json", "icons/gg-192.png", "icons/gg-512.png", "icons/gg-maskable-512.png", "fonts/cormorant-garamond-cyrillic-400-italic.woff2", "fonts/cormorant-garamond-cyrillic-700.woff2", "fonts/cormorant-garamond-cyrillic-ext-400-italic.woff2", "fonts/cormorant-garamond-cyrillic-ext-700.woff2", "fonts/cormorant-garamond-latin-400-italic.woff2", "fonts/cormorant-garamond-latin-700.woff2", "fonts/cormorant-garamond-latin-ext-400-italic.woff2", "fonts/cormorant-garamond-latin-ext-700.woff2", "fonts/cormorant-garamond-vietnamese-400-italic.woff2", "fonts/cormorant-garamond-vietnamese-700.woff2", "fonts/crimson-text-latin-400-italic.woff2", "fonts/crimson-text-latin-400.woff2", "fonts/crimson-text-latin-600.woff2", "fonts/crimson-text-latin-700.woff2", "fonts/crimson-text-latin-ext-400-italic.woff2", "fonts/crimson-text-latin-ext-400.woff2", "fonts/crimson-text-latin-ext-600.woff2", "fonts/crimson-text-latin-ext-700.woff2", "fonts/crimson-text-vietnamese-400-italic.woff2", "fonts/crimson-text-vietnamese-400.woff2", "fonts/crimson-text-vietnamese-600.woff2", "fonts/crimson-text-vietnamese-700.woff2", "fonts/noto-serif-cyrillic-400-italic.woff2", "fonts/noto-serif-cyrillic-700.woff2", "fonts/noto-serif-cyrillic-ext-400-italic.woff2", "fonts/noto-serif-cyrillic-ext-700.woff2", "fonts/noto-serif-greek-400-italic.woff2", "fonts/noto-serif-greek-700.woff2", "fonts/noto-serif-greek-ext-400-italic.woff2", "fonts/noto-serif-greek-ext-700.woff2", "fonts/noto-serif-latin-400-italic.woff2", "fonts/noto-serif-latin-700.woff2", "fonts/noto-serif-latin-ext-400-italic.woff2", "fonts/noto-serif-latin-ext-700.woff2", "fonts/noto-serif-math-400-italic.woff2", "fonts/noto-serif-math-700.woff2", "fonts/noto-serif-vietnamese-400-italic.woff2", "fonts/noto-serif-vietnamese-700.woff2", "fonts/playfair-display-cyrillic-700.woff2", "fonts/playfair-display-latin-700.woff2", "fonts/playfair-display-latin-ext-700.woff2", "fonts/playfair-display-vietnamese-700.woff2"];

// ---------------------------------------------------------------------------
// install / activate
// ---------------------------------------------------------------------------

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then((cache) => cache.addAll(SHELL_ASSETS))
      .then(() => self.skipWaiting())
      .catch((err) => {
        // Precache failure shouldn't brick installation; the fetch handler's
        // network-first / cache-first fallbacks still work without a full
        // precache, and the next successful install/activate will retry.
        console.error('[sw] shell precache failed', err);
      })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((names) => Promise.all(
        names
          .filter((name) => name.startsWith('shell-v') && name !== SHELL_CACHE)
          .map((name) => caches.delete(name))
        // media-v1 is never touched here - it rotates only via explicit PRUNE.
      ))
      .then(() => self.clients.claim())
  );
});

// ---------------------------------------------------------------------------
// fetch
// ---------------------------------------------------------------------------

function isNavigationRequest(request) {
  return request.mode === 'navigate' ||
    (request.method === 'GET' &&
      request.headers.get('accept') &&
      request.headers.get('accept').indexOf('text/html') !== -1);
}

function isAudioRequest(url) {
  return /\/audio\/[^/]+\.ogg$/.test(url.pathname);
}

function isShellStaticAsset(url) {
  return /\/(fonts\/[^/]+\.woff2|icons\/[^/]+\.(png|svg)|manifest\.json)$/.test(url.pathname);
}

async function networkFirst(request) {
  const cache = await caches.open(SHELL_CACHE);
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      cache.put(request, response.clone()).catch(() => {});
    }
    return response;
  } catch (err) {
    const cached = (await cache.match(request)) ||
      (await cache.match('index.html')) ||
      (await cache.match('./'));
    if (cached) return cached;
    throw err;
  }
}

async function cacheFirst(request, cacheName, storeOnMiss) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (storeOnMiss && response && response.ok) {
    try {
      await cache.put(request, response.clone());
    } catch (err) {
      // Storage quota exceeded or similar - the caller still gets the
      // network response; the page's explicit DOWNLOAD_ASSETS flow is the
      // authoritative path for building the offline library and reports
      // quota errors back to the page.
    }
  }
  return response;
}

// Media elements issue Range requests (Range: bytes=start-end). The Cache API
// stores a full 200 response; returning that 200 to a Range request works in
// desktop Chrome but is rejected by several mobile browsers, so offline
// playback silently fails. This serves audio from cache with proper 206
// Partial Content slicing when a Range header is present.
async function serveAudio(request) {
  const cache = await caches.open(MEDIA_CACHE);
  let cached = await cache.match(request);

  if (!cached) {
    // Cache miss: fetch from network, store the full response for next time,
    // and let the network response (which supports Range) satisfy this request.
    try {
      const response = await fetch(request);
      if (response && (response.ok || response.status === 206)) {
        // Re-fetch a full copy to cache (the network 206 can't be cached whole).
        fetch(request.url, { cache: 'no-store' })
          .then((full) => { if (full && full.ok) cache.put(request.url, full.clone()); })
          .catch(() => {});
      }
      return response;
    } catch (err) {
      return new Response('', { status: 504, statusText: 'Offline and not cached' });
    }
  }

  const rangeHeader = request.headers.get('range');
  if (!rangeHeader) return cached;

  // Slice the cached full body to satisfy the Range request with a 206.
  const buf = await cached.arrayBuffer();
  const total = buf.byteLength;
  const m = /bytes=(\d+)-(\d*)/.exec(rangeHeader);
  let start = m ? parseInt(m[1], 10) : 0;
  let end = m && m[2] ? parseInt(m[2], 10) : total - 1;
  if (isNaN(start) || start >= total) start = 0;
  if (isNaN(end) || end >= total) end = total - 1;
  const chunk = buf.slice(start, end + 1);
  const headers = new Headers(cached.headers);
  headers.set('Content-Range', 'bytes ' + start + '-' + end + '/' + total);
  headers.set('Content-Length', String(chunk.byteLength));
  headers.set('Accept-Ranges', 'bytes');
  return new Response(chunk, { status: 206, statusText: 'Partial Content', headers: headers });
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  let url;
  try {
    url = new URL(request.url);
  } catch (err) {
    return;
  }

  // Cross-origin (YouTube iframes, etc.) - network only, no interception.
  if (url.origin !== self.location.origin) return;

  if (isNavigationRequest(request) || url.pathname.endsWith('/index.html')) {
    event.respondWith(networkFirst(request));
    return;
  }
  if (isAudioRequest(url)) {
    // Serve audio with proper Range (206) support from cache; falls back to
    // network + lazy caching on a miss. See serveAudio for why 206 matters.
    event.respondWith(serveAudio(request));
    return;
  }
  if (isShellStaticAsset(url)) {
    event.respondWith(cacheFirst(request, SHELL_CACHE, true));
    return;
  }
  // Anything else same-origin (e.g. asset-list.json, version.json) is left
  // to the network so the page always sees fresh manifests.
});

// ---------------------------------------------------------------------------
// message: DOWNLOAD_ASSETS / PRUNE
// ---------------------------------------------------------------------------

function postToClient(client, msg) {
  if (client && typeof client.postMessage === 'function') {
    client.postMessage(msg);
  }
}

function toPathKey(u) {
  try {
    const parsed = new URL(u, self.location.href);
    return parsed.pathname + parsed.search;
  } catch (err) {
    return u;
  }
}

async function downloadAssets(assets, client, keepUrls) {
  const cache = await caches.open(MEDIA_CACHE);
  // Self-cleaning: remove any stale entries (old versions, interrupted
  // downloads, superseded ?v= hashes) BEFORE downloading, so the offline
  // library never accumulates beyond the current asset set.
  if (keepUrls && keepUrls.length) {
    try { await pruneMedia(keepUrls); } catch (e) { /* best-effort */ }
  }
  const total = assets.length;
  let done = 0;
  let bytesDone = 0;

  // Download with a small concurrency pool instead of strictly sequentially.
  // Each file is a separate HTTPS request to GitHub Pages; running several in
  // parallel hides per-request latency and is dramatically faster on mobile.
  const CONCURRENCY = 6;
  let index = 0;

  async function worker() {
    while (index < assets.length) {
      const asset = assets[index++];
      try {
        const existing = await cache.match(asset.url);
        if (existing) {
          done++;
          bytesDone += asset.size || 0;
          postToClient(client, { type: 'PROGRESS', done, total, bytesDone });
          continue;
        }
        const response = await fetch(asset.url);
        if (!response || !response.ok) {
          throw new Error('HTTP ' + (response && response.status));
        }
        try {
          await cache.put(asset.url, response.clone());
        } catch (quotaErr) {
          postToClient(client, {
            type: 'DOWNLOAD_ERROR',
            url: asset.url,
            reason: 'quota',
            remaining: total - done,
          });
          continue;
        }
        done++;
        bytesDone += asset.size || 0;
        postToClient(client, { type: 'PROGRESS', done, total, bytesDone });
      } catch (err) {
        postToClient(client, {
          type: 'DOWNLOAD_ERROR',
          url: asset.url,
          reason: 'network',
          remaining: total - done,
        });
        // Keep going with the rest of the batch.
      }
    }
  }

  const workers = [];
  for (let i = 0; i < Math.min(CONCURRENCY, assets.length); i++) {
    workers.push(worker());
  }
  await Promise.all(workers);

  postToClient(client, { type: 'DOWNLOAD_COMPLETE', done, total });
}

async function pruneMedia(keepUrls) {
  const cache = await caches.open(MEDIA_CACHE);
  const keepSet = new Set(keepUrls.map(toPathKey));
  const requests = await cache.keys();
  await Promise.all(
    requests
      .filter((req) => !keepSet.has(toPathKey(req.url)))
      .map((req) => cache.delete(req))
  );
}

self.addEventListener('message', (event) => {
  const data = event.data;
  if (!data || !data.type) return;
  if (data.type === 'DOWNLOAD_ASSETS') {
    event.waitUntil(downloadAssets(data.assets || [], event.source, data.keepUrls || []));
  } else if (data.type === 'PRUNE') {
    event.waitUntil(pruneMedia(data.keepUrls || []));
  }
});
