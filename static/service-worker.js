// Version deiner App - erhöhe diese bei Updates
const VERSION = 'v1';
const CACHE_NAME = `expense-tracker-${VERSION}`;

// Alle Dateien die offline verfügbar sein sollen
const STATIC_FILES = [
  '/',
  '/index.html',
  '/dashboard.js',
  '/dashboard.html',
  '/upload.js',
  '/indexeddb.js', 
  '/sync.js',
  '/offline-indicator.js',
  '/icons/android/android-launchericon-192-192.png'  // → static/icons/android/...  '/icons/icon-512x512.png'
  // Füge hier alle deine CSS/JS Dateien hinzu
];

// ========================================
// 1. INSTALLATION - Läuft beim ersten Mal
// ========================================
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installation gestartet');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Dateien werden gecacht');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('[Service Worker] Installation erfolgreich');
        // Aktiviere sofort, warte nicht
        return self.skipWaiting();
      })
  );
});

// ========================================
// 2. AKTIVIERUNG - Läuft nach Installation
// ========================================
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Aktivierung gestartet');
  
  event.waitUntil(
    // Lösche alte Caches
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[Service Worker] Alter Cache gelöscht:', name);
            return caches.delete(name);
          })
      );
    })
    .then(() => {
      console.log('[Service Worker] Aktivierung erfolgreich');
      // Übernimm Kontrolle über alle Tabs sofort
      return self.clients.claim();
    })
  );
});

// ========================================
// 3. FETCH - Läuft bei jeder Anfrage
// ========================================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // API-Anfragen (deine Backend-Calls)
  if (url.pathname === '/api' && request.method === 'POST') {
    console.log('[SW] POST /api erkannt');
    event.respondWith(handleApiRequest(request));
  } 
  else if (url.pathname === '/api/dashboard' && request.method === 'GET') {
    console.log('[SW] GET /api/dashboard erkannt');
    event.respondWith(handleApiRequest(request));
  }
  else if (url.pathname.startsWith('/api/')) {
    console.log('[SW] Andere API-Route:', url.pathname);
    event.respondWith(handleApiRequest(request));
  } 
  // Statische Dateien (HTML, CSS, JS, Bilder)
  else {
    event.respondWith(handleStaticRequest(request));
  }
});

// ========================================
// Statische Dateien: Cache First
// ========================================
async function handleStaticRequest(request) {
  // 1. Schaue zuerst im Cache
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    console.log('[Service Worker] Aus Cache geladen:', request.url);
    return cachedResponse;
  }
  
  // 2. Nicht im Cache? Hole vom Netzwerk
  try {
    const networkResponse = await fetch(request);
    
    // Speichere im Cache für nächstes Mal
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, networkResponse.clone());
    
    console.log('[Service Worker] Vom Netzwerk geladen:', request.url);
    return networkResponse;
  } catch (error) {
    console.error('[Service Worker] Fehler beim Laden:', error);
    
    // Offline-Fallback (optional)
    return new Response('Offline - Datei nicht verfügbar', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// ========================================
// API-Anfragen: Network First
// (Für Expense Tracker wichtig!)
// ========================================
async function handleApiRequest(request) {
  const requestClone = request.clone();
  try {
    console.log('[SW] API Request - leite durch:', request.url);
    console.log('[SW] Headers:', [...request.headers.entries()]);
    // 1. Versuche vom Netzwerk zu laden (frische Daten!)
    const networkResponse = await fetch(request);
    
    // 2. Speichere Antwort im Cache
    // 2. Speichere NUR GET-Requests im Cache
    if (request.method === 'GET') {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      console.log('[Service Worker] API (GET) im Cache gespeichert:', request.url);
    } else {
      console.log('[Service Worker] API (POST/PUT/DELETE) nicht gecacht:', request.url);
    }
    return networkResponse;
    
  } catch (error) {
    // 3. Offline? Schaue im Cache
    console.log('[Service Worker] Offline - Request-Methode:', requestClone.method);
    
    if (requestClone.method === 'GET') {
      // GET: Versuche aus Cache zu laden
      const cachedResponse = await caches.match(requestClone);
      
      if (cachedResponse) {
        console.log('[Service Worker] API aus Cache geladen:', requestClone.url);
        return cachedResponse;
      }
      
      // Nicht im Cache
      return new Response(
        JSON.stringify({
          error: 'offline',
          message: 'Keine Internetverbindung und keine gecachten Daten verfügbar.'
        }),
        {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        }
      );
      
    } else if (requestClone.method === 'POST') {
      // POST: Lese die Daten und sende sie an die Hauptseite
      try {
        const requestData = await requestClone.clone().json();
        
        // Sende Message an alle offenen Tabs/Windows
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
          client.postMessage({
            type: 'SAVE_OFFLINE_EXPENSE',
            data: requestData
          });
        });
        
        console.log('[Service Worker] POST-Daten an Client gesendet für IndexedDB');
        
        // Gib erfolgreiche Response zurück (simuliert)
        return new Response(
          JSON.stringify({
            status: 'offline_saved',
            message: 'Offline gespeichert. Wird synchronisiert sobald online.'
          }),
          {
            status: 202, // 202 = Accepted (wird später verarbeitet)
            headers: { 'Content-Type': 'application/json' }
          }
        );
        
      } catch (parseError) {
        console.error('[Service Worker] Fehler beim Parsen der POST-Daten:', parseError);
        return new Response(
          JSON.stringify({
            error: 'offline',
            message: 'Fehler beim Speichern der Offline-Daten.'
          }),
          {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      }
    }
    
    // 4. Auch nicht im Cache? Gib Offline-Nachricht
    return new Response(
      JSON.stringify({
        error: 'offline',
        message: 'Keine Internetverbindung. Daten werden lokal gespeichert.'
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}
