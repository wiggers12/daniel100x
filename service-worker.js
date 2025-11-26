self.addEventListener("install", (e) => {
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  clients.claim();
});

// Não usar cache antigo — sempre buscar a versão nova
self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});