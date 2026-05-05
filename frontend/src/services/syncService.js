/**
 * Offline Sync Service
 * Handles downloading data from API and storing in IndexedDB
 */

import api from './api.js'
import offlineDB, { STORES, setLastSync, getOfflineStats } from './offlineDB.js'

const SYNC_ENDPOINT = '/navigation/offline-sync/'

/**
 * Perform full offline sync - download all data from server
 */
export async function performFullSync() {
  console.log('[Sync] Starting full offline sync...')
  
  try {
    // Call the offline sync API
    const response = await api.get(SYNC_ENDPOINT)
    
    if (response.data.status !== 'ok') {
      throw new Error(response.data.message || 'Sync failed')
    }
    
    const { data, stats, timestamp } = response.data
    
    console.log('[Sync] Downloaded data:', stats)
    
    // Store all data in IndexedDB
    await Promise.all([
      offlineDB.storeData(STORES.BUILDINGS, data.buildings || []),
      offlineDB.storeData(STORES.ROOMS, data.rooms || []),
      offlineDB.storeData(STORES.PATHS, data.paths || []),
      offlineDB.storeData(STORES.FAQS, data.faqs || [])
    ])
    
    // Update last sync timestamp
    await setLastSync(timestamp)
    
    console.log('[Sync] Full sync completed successfully')
    
    return {
      success: true,
      stats,
      timestamp,
      message: `Synced ${stats.buildings} buildings, ${stats.rooms} rooms, ${stats.paths} paths, ${stats.faqs} FAQs`
    }
    
  } catch (error) {
    console.error('[Sync] Full sync failed:', error)
    throw error
  }
}

/**
 * Check if we're online
 */
export function isOnline() {
  return navigator.onLine
}

/**
 * Get current sync status
 */
export async function getSyncStatus() {
  const [online, stats] = await Promise.all([
    isOnline(),
    getOfflineStats()
  ])
  
  return {
    online,
    ...stats,
    needsSync: online && (!stats.lastSync || isSyncStale(stats.lastSync, 24))
  }
}

/**
 * Check if sync is stale (older than hours specified)
 */
function isSyncStale(lastSyncTimestamp, hours = 24) {
  if (!lastSyncTimestamp) return true
  
  const lastSync = new Date(lastSyncTimestamp)
  const now = new Date()
  const diffHours = (now - lastSync) / (1000 * 60 * 60)
  
  return diffHours > hours
}

/**
 * Sync only pending queue items (when coming back online)
 */
export async function syncPendingQueue() {
  if (!isOnline()) {
    console.log('[Sync] Cannot sync queue - offline')
    return { synced: 0 }
  }
  
  try {
    const pendingItems = await offlineDB.getPendingQueue()
    
    if (pendingItems.length === 0) {
      return { synced: 0 }
    }
    
    console.log(`[Sync] Syncing ${pendingItems.length} pending items...`)
    
    let synced = 0
    
    for (const item of pendingItems) {
      try {
        // Send to server based on type
        switch (item.type) {
          case 'feedback':
            await api.post('/chatbot/feedback/', item.data)
            break
          case 'chat_rating':
            await api.post('/chatbot/rate/', item.data)
            break
          case 'path_usage':
            // Could track path usage analytics
            break
          default:
            console.log('[Sync] Unknown queue type:', item.type)
        }
        
        // Mark as synced
        await offlineDB.markQueueItemSynced(item.id)
        synced++
        
      } catch (error) {
        console.error(`[Sync] Failed to sync item ${item.id}:`, error)
        // Continue with next item
      }
    }
    
    console.log(`[Sync] Queue sync completed: ${synced}/${pendingItems.length} items synced`)
    
    return { synced, total: pendingItems.length }
    
  } catch (error) {
    console.error('[Sync] Queue sync failed:', error)
    throw error
  }
}

/**
 * Auto-sync when coming back online
 */
export function setupAutoSync() {
  window.addEventListener('online', async () => {
    console.log('[Sync] Back online - checking for pending sync...')
    
    try {
      // Sync any pending queue items
      await syncPendingQueue()
      
      // Check if data is stale
      const status = await getSyncStatus()
      if (status.needsSync) {
        console.log('[Sync] Data is stale, performing full sync...')
        await performFullSync()
      }
    } catch (error) {
      console.error('[Sync] Auto-sync failed:', error)
    }
  })
  
  console.log('[Sync] Auto-sync listener registered')
}

/**
 * Clear all offline data
 */
export async function clearOfflineData() {
  await offlineDB.clearAllData()
  console.log('[Sync] All offline data cleared')
}

/**
 * Get data from IndexedDB (for offline use)
 */
export async function getOfflineData(storeName) {
  return offlineDB.getAllData(storeName)
}

/**
 * Get building by ID (offline-capable)
 */
export async function getBuildingById(id) {
  return offlineDB.getDataById(STORES.BUILDINGS, id)
}

/**
 * Get room by ID (offline-capable)
 */
export async function getRoomById(id) {
  return offlineDB.getDataById(STORES.ROOMS, id)
}

/**
 * Get path by ID (offline-capable)
 */
export async function getPathById(id) {
  return offlineDB.getDataById(STORES.PATHS, id)
}

export default {
  performFullSync,
  syncPendingQueue,
  getSyncStatus,
  isOnline,
  setupAutoSync,
  clearOfflineData,
  getOfflineData,
  getBuildingById,
  getRoomById,
  getPathById
}
