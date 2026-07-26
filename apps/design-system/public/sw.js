const CACHE_NAME = "digifax-offline-cache-v1";
const OFFLINE_URLS = [
  "/",
  "/design-system",
  "/shell",
  "/intake",
  "/review",
  "/patient",
  "/fhir",
  "/workflow",
  "/analytics",
  "/admin",
  "/settings",
  "/notifications"
];

// Install service worker
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[Service Worker] Caching offline workspace routes");
      return cache.addAll(OFFLINE_URLS);
    })
  );
  self.skipWaiting();
});

// Activate service worker
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log("[Service Worker] Clearing old cache storage");
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch events interceptor
self.addEventListener("fetch", (event) => {
  // Only handle GET requests
  if (event.request.method !== "GET") return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      return fetch(event.request).catch(() => {
        console.warn("[Service Worker] Network request failed. Falling back to cache.");
      });
    })
  );
});
