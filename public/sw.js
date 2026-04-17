/* ============================================================
 * FuelEcon · Service Worker
 *
 * Strategy:
 *   - Static HTML/CSS/JS/fonts → cache-first (instant loads offline)
 *   - API routes (/api/*)       → network-first (fresh data when online,
 *                                  cached fallback when offline)
 *   - Navigations               → network-first with offline fallback page
 *
 * Bump CACHE_VERSION on any deploy that changes static assets.
 * ============================================================ */

const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `fuelecon-${CACHE_VERSION}`;

const PRECACHE_URLS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.svg',
];

// Third-party assets we want cached after first visit
const RUNTIME_CACHE_ORIGINS = [
  'https://fonts.googleapis.com',
  'https://fonts.gstatic.com',
  'https://cdnjs.cloudflare.com',
];

// ---------- install: precache ----------
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

// ---------- activate: clean old caches ----------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k.startsWith('fuelecon-') && k !== CACHE_NAME)
            .map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ---------- fetch: strategy per request type ----------
self.addEventListener('fetch', (event) => {
  const request = event.request;

  // Only handle GETs
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Ignore chrome-extension:// and other non-http schemes
  if (!url.protocol.startsWith('http')) return;

  // ---- API: network-first with cache fallback ----
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // ---- Navigations: network-first, fall back to cached shell ----
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .catch(() => caches.match('/index.html').then((r) => r || caches.match('/')))
    );
    return;
  }

  // ---- Static + runtime cacheable origins: cache-first ----
  const isSameOrigin = url.origin === self.location.origin;
  const isRuntimeCacheable = RUNTIME_CACHE_ORIGINS.some((origin) => url.origin === origin);

  if (isSameOrigin || isRuntimeCacheable) {
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then((response) => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        });
      })
    );
  }
});

// ---------- message: manual cache updates from page ----------
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
