self.addEventListener("install", (e) => {
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  clients.claim();
});

// ❌ REMOVIDO: fetch intercept — NÃO pode existir para Jitsi
// (deixe SEM NENHUM fetch-event)
