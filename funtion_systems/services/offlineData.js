import db from './db.js'
import api from './api.js'
import { isOnline } from './sync.js'

/**
 * Offline-aware data service
 * Fetches from API when online, falls back to IndexedDB when offline
 */

const CACHE_DURATION_MS = 5 * 60 * 1000 // 5 minutes

// Helper to check if cache is stale
function isCacheStale(lastSync) {
  if (!lastSync) return true
  const lastSyncTime = new Date(lastSync).getTime()
  return Date.now() - lastSyncTime > CACHE_DURATION_MS
}

// Get cached data with metadata
async function getCachedData(tableName) {
  try {
    const data = await db[tableName].toArray()
    const meta = await db.sync_meta.get('last_sync_timestamp')
    return {
      data,
      cached: true,
      lastSync: meta?.value || null,
      count: data.length
    }
  } catch (err) {
    console.error(`[OfflineDB] Error reading ${tableName}:`, err)
    return { data: [], cached: false, lastSync: null, count: 0, error: err.message }
  }
}

/**
 * Facilities - offline aware
 */
export async function getFacilities() {
  if (isOnline()) {
    try {
      const res = await api.get('/facilities/')
      // Update cache in background
      db.transaction('rw', db.facilities, db.sync_meta, async () => {
        await db.facilities.clear()
        await db.facilities.bulkPut(res.data)
      }).catch(() => {}) // Silent fail for cache update
      return { data: res.data, source: 'api', cached: false }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const cached = await getCachedData('facilities')
  return { 
    data: cached.data, 
    source: 'cache', 
    cached: true,
    lastSync: cached.lastSync,
    stale: isCacheStale(cached.lastSync)
  }
}

/**
 * Rooms - offline aware
 */
export async function getRooms(facilityId = null) {
  if (isOnline()) {
    try {
      const params = facilityId ? { params: { facility: facilityId } } : {}
      const res = await api.get('/rooms/', params)
      // Update cache
      db.transaction('rw', db.rooms, async () => {
        if (facilityId) {
          // Only update rooms for this facility
          const existing = await db.rooms.toArray()
          const others = existing.filter(r => r.facility_id !== facilityId)
          await db.rooms.clear()
          await db.rooms.bulkPut([...others, ...res.data])
        } else {
          await db.rooms.clear()
          await db.rooms.bulkPut(res.data)
        }
      }).catch(() => {})
      return { data: res.data, source: 'api', cached: false }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const cached = await getCachedData('rooms')
  let data = cached.data
  if (facilityId) {
    data = data.filter(r => r.facility_id === facilityId)
  }
  return { 
    data, 
    source: 'cache', 
    cached: true,
    lastSync: cached.lastSync,
    stale: isCacheStale(cached.lastSync)
  }
}

/**
 * Map Markers - offline aware
 */
export async function getMapMarkers() {
  if (isOnline()) {
    try {
      const res = await api.get('/core/map-markers/')
      db.transaction('rw', db.map_markers, async () => {
        await db.map_markers.clear()
        await db.map_markers.bulkPut(res.data)
      }).catch(() => {})
      return { data: res.data, source: 'api', cached: false }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const cached = await getCachedData('map_markers')
  return { 
    data: cached.data, 
    source: 'cache', 
    cached: true,
    lastSync: cached.lastSync,
    stale: isCacheStale(cached.lastSync)
  }
}

/**
 * Navigation Nodes & Edges - offline aware (for pathfinding)
 */
export async function getNavigationData() {
  if (isOnline()) {
    try {
      const [nodesRes, edgesRes] = await Promise.all([
        api.get('/navigation/nodes/'),
        api.get('/navigation/edges/')
      ])
      db.transaction('rw', db.navigation_nodes, db.navigation_edges, async () => {
        await db.navigation_nodes.clear()
        await db.navigation_nodes.bulkPut(nodesRes.data)
        await db.navigation_edges.clear()
        await db.navigation_edges.bulkPut(edgesRes.data)
      }).catch(() => {})
      return { 
        nodes: nodesRes.data, 
        edges: edgesRes.data, 
        source: 'api', 
        cached: false 
      }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const [nodesCached, edgesCached] = await Promise.all([
    getCachedData('navigation_nodes'),
    getCachedData('navigation_edges')
  ])
  
  return { 
    nodes: nodesCached.data, 
    edges: edgesCached.data, 
    source: 'cache', 
    cached: true,
    lastSync: nodesCached.lastSync,
    stale: isCacheStale(nodesCached.lastSync)
  }
}

/**
 * FAQ Entries - offline aware
 */
export async function getFAQEntries() {
  if (isOnline()) {
    try {
      const res = await api.get('/chatbot/faq/')
      db.transaction('rw', db.faq_entries, async () => {
        await db.faq_entries.clear()
        await db.faq_entries.bulkPut(res.data)
      }).catch(() => {})
      return { data: res.data, source: 'api', cached: false }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const cached = await getCachedData('faq_entries')
  return { 
    data: cached.data, 
    source: 'cache', 
    cached: true,
    lastSync: cached.lastSync,
    stale: isCacheStale(cached.lastSync)
  }
}

/**
 * Notifications - offline aware
 */
export async function getNotifications() {
  if (isOnline()) {
    try {
      const res = await api.get('/notifications/')
      // Preserve read states
      const existing = await db.notifications.toArray()
      const readStates = {}
      for (const n of existing) {
        readStates[n.id] = !!n.is_read
      }
      const newNotifs = res.data.map(n => {
        if (readStates[n.id]) n.is_read = true
        return n
      })
      db.transaction('rw', db.notifications, async () => {
        await db.notifications.clear()
        await db.notifications.bulkPut(newNotifs)
      }).catch(() => {})
      return { data: newNotifs, source: 'api', cached: false }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const cached = await getCachedData('notifications')
  return { 
    data: cached.data, 
    source: 'cache', 
    cached: true,
    lastSync: cached.lastSync,
    stale: isCacheStale(cached.lastSync)
  }
}

/**
 * App Config - offline aware
 */
export async function getAppConfig() {
  if (isOnline()) {
    try {
      const res = await api.get('/core/app-config/')
      db.transaction('rw', db.app_config, async () => {
        await db.app_config.clear()
        await db.app_config.bulkPut(res.data)
      }).catch(() => {})
      return { data: res.data, source: 'api', cached: false }
    } catch (err) {
      console.log('[OfflineDB] API failed, using cache:', err.message)
    }
  }
  
  const cached = await getCachedData('app_config')
  return { 
    data: cached.data, 
    source: 'cache', 
    cached: true,
    lastSync: cached.lastSync,
    stale: isCacheStale(cached.lastSync)
  }
}

/**
 * Get offline status summary
 */
export async function getOfflineStatus() {
  const meta = await db.sync_meta.get('last_sync_timestamp')
  const lastSync = meta?.value || null
  
  const tableCounts = await Promise.all([
    db.facilities.count(),
    db.rooms.count(),
    db.map_markers.count(),
    db.navigation_nodes.count(),
    db.faq_entries.count()
  ])
  
  return {
    isOnline: isOnline(),
    lastSync,
    stale: isCacheStale(lastSync),
    cachedRecords: {
      facilities: tableCounts[0],
      rooms: tableCounts[1],
      mapMarkers: tableCounts[2],
      navigationNodes: tableCounts[3],
      faqEntries: tableCounts[4]
    }
  }
}

export default {
  getFacilities,
  getRooms,
  getMapMarkers,
  getNavigationData,
  getFAQEntries,
  getNotifications,
  getAppConfig,
  getOfflineStatus
}
