// Basic service worker for cache control
const CACHE_NAME = 'technopath-v2'

self.addEventListener('install', (event) => {
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName)
          }
        })
      )
    })
  )
  self.clients.claim()
})

self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return
  
  // Skip dev server resources
  if (event.request.url.includes('/@') || 
      event.request.url.includes('?t=') ||
      event.request.url.includes('__vite')) {
    return
  }
  
  // Network-first strategy
  event.respondWith(
    fetch(event.request).then((response) => {
      // Don't cache if response is not ok
      if (!response || response.status !== 200) {
        return response
      }
      
      // Clone response and cache it
      const responseToCache = response.clone()
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, responseToCache)
      })
      
      return response
    }).catch(() => {
      return caches.match(event.request)
    })
  )
})
