// TechnoPath Service Worker - Enhanced for Offline Support
const CACHE_NAME = 'technopath-v3'
const OFFLINE_PAGE = '/offline.html'

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/SEAITMAP.svg',
  '/Map_labeled.svg'
]

self.addEventListener('install', (event) => {
  console.log('[SW] Installing...')
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching assets')
      return cache.addAll(PRECACHE_ASSETS)
    })
  )
  
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  console.log('[SW] Activating...')
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
  
  self.clients.claim()
})

// Network-first strategy with IndexedDB fallback
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return
  
  // Skip dev server resources
  if (event.request.url.includes('/@') || 
      event.request.url.includes('?t=') ||
      event.request.url.includes('__vite') ||
      event.request.url.includes('localhost')) {
    return
  }
  
  const url = new URL(event.request.url)
  
  // API requests - network first, no cache
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/navigation/')) {
    event.respondWith(
      fetch(event.request).catch((error) => {
        console.log('[SW] API request failed, no cache available:', url.pathname)
        // Return a custom offline response for API requests
        return new Response(
          JSON.stringify({ 
            status: 'offline', 
            message: 'You are offline. Please connect to the internet.' 
          }),
          { 
            headers: { 'Content-Type': 'application/json' },
            status: 503
          }
        )
      })
    )
    return
  }
  
  // Static assets - stale-while-revalidate strategy
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      // Return cached version immediately if available
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        // Update cache with fresh version
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone()
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache)
          })
        }
        return networkResponse
      }).catch((error) => {
        console.log('[SW] Network fetch failed, using cache:', url.pathname)
        // Return cached version if network fails
        return cachedResponse
      })
      
      // Return cached version or wait for network
      return cachedResponse || fetchPromise
    })
  )
})

// Background sync for pending operations
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-queue') {
    console.log('[SW] Background sync triggered')
    event.waitUntil(syncPendingQueue())
  }
})

// Handle messages from main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
})

async function syncPendingQueue() {
  // This will be handled by the main app using IndexedDB
  // Service worker just notifies all clients
  const clients = await self.clients.matchAll()
  clients.forEach(client => {
    client.postMessage({ type: 'SYNC_REQUIRED' })
  })
}
