import db from './db.js'
import api from './api.js'

// Key stored in IndexedDB sync_meta table to track last sync time
const LAST_SYNC_KEY = 'last_sync_timestamp'

// Flag to prevent multiple simultaneous syncs
let isSyncing = false

// Check if device is online
export function isOnline() {
  return navigator.onLine
}

// Get the last time this device synced with the server
async function getLastSync() {
  try {
    const meta = await db.sync_meta.get(LAST_SYNC_KEY)
    return meta ? meta.value : null
  } catch {
    return null
  }
}

// Save the current time as last sync timestamp
async function setLastSync(timestamp) {
  await db.sync_meta.put({ key: LAST_SYNC_KEY, value: timestamp })
}

// Main sync function — call this on app startup when online
export async function syncAllData() {
  // Prevent multiple simultaneous syncs
  if (isSyncing) {
    console.log('[Sync] Sync already in progress — skipping')
    return { success: false, reason: 'already_syncing' }
  }

  if (!isOnline()) {
    console.log('[Sync] Device is offline — skipping sync, using cached data')
    return { success: false, reason: 'offline' }
  }

  isSyncing = true

  try {
    console.log('[Sync] Online — starting data sync from server...')
    const lastSync = await getLastSync()
    const syncStart = new Date().toISOString()

    // Fetch all data from Django API in parallel
    // Uses Promise.allSettled so one failing endpoint doesn't kill the entire cache
    // NOTE: Now uses page_size=1000 to get all data in one request (with pagination)
    const endpoints = [
      { key: 'facilities',       url: '/facilities/?page_size=1000',       table: 'facilities' },
      { key: 'rooms',            url: '/rooms/?page_size=1000',           table: 'rooms' },
      { key: 'departments',      url: '/core/departments/?page_size=1000', table: 'departments' },
      { key: 'nodes',            url: '/navigation/nodes/?page_size=1000', table: 'navigation_nodes' },
      { key: 'edges',            url: '/navigation/edges/?page_size=1000', table: 'navigation_edges' },
      { key: 'mapMarkers',       url: '/core/map-markers/?page_size=1000', table: 'map_markers' },
      { key: 'mapLabels',        url: '/core/map-labels/?page_size=1000',  table: 'map_labels' },
      { key: 'faq',              url: '/chatbot/faq/?page_size=1000',      table: 'faq_entries' },
      // notification_types table was removed in db.js v5 — do NOT fetch or write
      { key: 'notifications',    url: '/notifications/?page_size=1000',   table: 'notifications' },
      { key: 'appConfig',        url: '/core/app-config/',                table: 'app_config' },
    ]

    const results = await Promise.allSettled(
      endpoints.map(ep => api.get(ep.url))
    )

    // Build a map of successfully-fetched data
    // Handle both paginated (results array) and non-paginated (direct array) responses
    const fetched = {}
    results.forEach((result, i) => {
      if (result.status === 'fulfilled') {
        const responseData = result.value.data
        // Check if paginated response (has 'results' key with array)
        if (responseData && Array.isArray(responseData.results)) {
          fetched[endpoints[i].key] = responseData.results
          console.log(`[Sync] Fetched ${responseData.results.length} items from ${endpoints[i].url} (paginated, total: ${responseData.count})`)
        } else if (Array.isArray(responseData)) {
          // Non-paginated response (direct array)
          fetched[endpoints[i].key] = responseData
          console.log(`[Sync] Fetched ${responseData.length} items from ${endpoints[i].url}`)
        } else {
          console.warn(`[Sync] Unexpected response format from ${endpoints[i].url}:`, responseData)
          fetched[endpoints[i].key] = responseData
        }
      } else {
        console.warn(`[Sync] Failed to fetch ${endpoints[i].url}:`, result.reason?.message)
      }
    })

    // Determine which tables to include in the transaction
    const tablesToWrite = endpoints
      .filter(ep => fetched[ep.key] !== undefined)
      .map(ep => db[ep.table])
      .filter(Boolean)

    if (tablesToWrite.length === 0) {
      console.warn('[Sync] All endpoints failed — keeping existing cached data')
      return { success: false, reason: 'all_endpoints_failed' }
    }

    // Write all successfully-fetched data into IndexedDB
    await db.transaction('rw', ...tablesToWrite, async () => {
      // Simple tables: clear and replace
      const simpleTables = [
        'facilities', 'rooms', 'departments', 'nodes', 'edges',
        'mapMarkers', 'mapLabels', 'faq', 'appConfig'
      ]
      const tableMap = {
        facilities: 'facilities', rooms: 'rooms', departments: 'departments',
        nodes: 'navigation_nodes', edges: 'navigation_edges',
        mapMarkers: 'map_markers', mapLabels: 'map_labels',
        faq: 'faq_entries', appConfig: 'app_config'
      }

      for (const key of simpleTables) {
        if (fetched[key] !== undefined) {
          await db[tableMap[key]].clear()
          await db[tableMap[key]].bulkPut(fetched[key])
        }
      }

      // Notifications: preserve read state across sync
      if (fetched.notifications !== undefined) {
        const notifList = Array.isArray(fetched.notifications) ? fetched.notifications : []
        if (notifList.length > 0) {
          const existingNotifs = await db.notifications.toArray()
          const readStates = {}
          for (const n of existingNotifs) {
            readStates[n.id] = !!n.is_read
          }

          const newNotifs = notifList.map((n) => {
            if (readStates[n.id]) n.is_read = true
            return n
          })

          await db.notifications.clear()
          await db.notifications.bulkPut(newNotifs)
        }
      }
    })

    // Save sync timestamp
    await setLastSync(syncStart)

    const successCount = Object.keys(fetched).length
    const totalCount = endpoints.length
    console.log(`[Sync] Sync complete — ${successCount}/${totalCount} endpoints cached for offline use`)
    return { success: true, syncedAt: syncStart, synced: successCount, total: totalCount }

  } catch (error) {
    console.error('[Sync] Sync failed:', error.message)
    return { success: false, reason: error.message }
  } finally {
    isSyncing = false
  }
}

// Upload any queued offline feedback/ratings when back online
export async function syncOfflineQueue() {
  if (!isOnline()) return

  try {
    const pendingFeedback = await db.feedback
      .where('synced')
      .equals(0)
      .toArray()

    for (const item of pendingFeedback) {
      try {
        await api.post('/feedback/', item)
        await db.feedback.update(item.id, { synced: 1 })
      } catch (err) {
        console.warn('[Sync] Could not upload feedback item:', err.message)
      }
    }
  } catch (err) {
    console.warn('[Sync] Offline queue sync failed:', err.message)
  }
}

// Listen for connectivity changes and auto-sync when coming back online
export function registerConnectivityListener(onSyncComplete) {
  window.addEventListener('online', async () => {
    console.log('[Sync] Connection restored — syncing data...')
    const result = await syncAllData()
    await syncOfflineQueue()
    if (onSyncComplete) onSyncComplete(result)
  })

  window.addEventListener('offline', () => {
    console.log('[Sync] Connection lost — app will continue working offline')
  })
}

// Polling interval tracker
let pollInterval = null

// Start polling for lightweight data updates (notifications/announcements)
export function startPolling() {
  if (pollInterval) return
  
  // Poll every 30 seconds
  pollInterval = setInterval(async () => {
    if (!isOnline()) return
    
    try {
      const notificationsRes = await api.get('/notifications/?page_size=200')
      const raw = notificationsRes.data
      const list = Array.isArray(raw) ? raw : (raw?.results || [])
      if (!Array.isArray(list) || list.length === 0) {
        return
      }

      const existingNotifs = await db.notifications.toArray()
      const readStates = {}
      for (const n of existingNotifs) {
        readStates[n.id] = !!n.is_read
      }

      const newNotifs = list.map((n) => {
        if (readStates[n.id]) n.is_read = true
        return n
      })

      await db.transaction('rw', db.notifications, async () => {
        await db.notifications.bulkPut(newNotifs)
      })
      
      // Also opportunistically upload offline queue if device is online
      await syncOfflineQueue()
    } catch (e) {
      console.warn('[Sync] Polling failed:', e.message)
    }
  }, 30000)
}

export function stopPolling() {
  if (pollInterval) {
    clearInterval(pollInterval)
    pollInterval = null
  }
}
