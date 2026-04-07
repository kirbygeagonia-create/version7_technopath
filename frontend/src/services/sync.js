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
    const [
      facilitiesRes,
      roomsRes,
      departmentsRes,
      nodesRes,
      edgesRes,
      mapMarkersRes,
      mapLabelsRes,
      faqRes,
      notificationTypesRes,
      notificationsRes,
      appConfigRes
    ] = await Promise.all([
      api.get('/facilities/'),
      api.get('/rooms/'),
      api.get('/core/departments/'),
      api.get('/navigation/nodes/'),
      api.get('/navigation/edges/'),
      api.get('/core/map-markers/'),
      api.get('/core/map-labels/'),
      api.get('/chatbot/faq/'),
      api.get('/core/notification-types/'),
      api.get('/notifications/'),
      api.get('/core/app-config/')
    ])

    // Write all fetched data into IndexedDB (replaces existing data)
    await db.transaction('rw',
      db.facilities,
      db.rooms,
      db.departments,
      db.navigation_nodes,
      db.navigation_edges,
      db.map_markers,
      db.map_labels,
      db.faq_entries,
      db.notification_types,
      db.notifications,
      db.app_config,
      async () => {
        await db.facilities.clear()
        await db.facilities.bulkPut(facilitiesRes.data)

        await db.rooms.clear()
        await db.rooms.bulkPut(roomsRes.data)

        await db.departments.clear()
        await db.departments.bulkPut(departmentsRes.data)

        await db.navigation_nodes.clear()
        await db.navigation_nodes.bulkPut(nodesRes.data)

        await db.navigation_edges.clear()
        await db.navigation_edges.bulkPut(edgesRes.data)

        await db.map_markers.clear()
        await db.map_markers.bulkPut(mapMarkersRes.data)

        await db.map_labels.clear()
        await db.map_labels.bulkPut(mapLabelsRes.data)

        await db.faq_entries.clear()
        await db.faq_entries.bulkPut(faqRes.data)

        await db.notification_types.clear()
        await db.notification_types.bulkPut(notificationTypesRes.data)

        await db.notifications.clear()
        await db.notifications.bulkPut(notificationsRes.data)

        await db.app_config.clear()
        await db.app_config.bulkPut(appConfigRes.data)
      }
    )

    // Save sync timestamp
    await setLastSync(syncStart)

    console.log('[Sync] Sync complete — all data saved to IndexedDB for offline use')
    return { success: true, syncedAt: syncStart }

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
