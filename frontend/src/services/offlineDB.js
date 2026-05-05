/**
 * Offline Database Service using IndexedDB
 * Stores campus data locally for offline navigation
 */

const DB_NAME = 'TechnoPathOffline'
const DB_VERSION = 1

// Store names
const STORES = {
  BUILDINGS: 'buildings',
  ROOMS: 'rooms',
  PATHS: 'paths',
  FAQS: 'faqs',
  USERS: 'users',
  METADATA: 'metadata',
  QUEUE: 'syncQueue'
}

let db = null

/**
 * Initialize IndexedDB connection
 */
export async function initOfflineDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    
    request.onerror = () => reject(request.error)
    request.onsuccess = () => {
      db = request.result
      resolve(db)
    }
    
    request.onupgradeneeded = (event) => {
      const database = event.target.result
      
      // Create object stores
      if (!database.objectStoreNames.contains(STORES.BUILDINGS)) {
        database.createObjectStore(STORES.BUILDINGS, { keyPath: 'id' })
      }
      if (!database.objectStoreNames.contains(STORES.ROOMS)) {
        database.createObjectStore(STORES.ROOMS, { keyPath: 'id' })
      }
      if (!database.objectStoreNames.contains(STORES.PATHS)) {
        database.createObjectStore(STORES.PATHS, { keyPath: 'id' })
      }
      if (!database.objectStoreNames.contains(STORES.FAQS)) {
        database.createObjectStore(STORES.FAQS, { keyPath: 'id' })
      }
      if (!database.objectStoreNames.contains(STORES.USERS)) {
        database.createObjectStore(STORES.USERS, { keyPath: 'id' })
      }
      if (!database.objectStoreNames.contains(STORES.METADATA)) {
        database.createObjectStore(STORES.METADATA, { keyPath: 'key' })
      }
      if (!database.objectStoreNames.contains(STORES.QUEUE)) {
        const queueStore = database.createObjectStore(STORES.QUEUE, { keyPath: 'id', autoIncrement: true })
        queueStore.createIndex('type', 'type', { unique: false })
        queueStore.createIndex('synced', 'synced', { unique: false })
      }
    }
  })
}

/**
 * Store multiple items in a store
 */
export async function storeData(storeName, items) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readwrite')
    const store = transaction.objectStore(storeName)
    
    // Clear existing data
    const clearRequest = store.clear()
    
    clearRequest.onsuccess = () => {
      // Add all new items
      let completed = 0
      const total = items.length
      
      if (total === 0) {
        resolve()
        return
      }
      
      items.forEach(item => {
        const addRequest = store.put(item)
        addRequest.onsuccess = () => {
          completed++
          if (completed === total) resolve()
        }
        addRequest.onerror = () => reject(addRequest.error)
      })
    }
    
    clearRequest.onerror = () => reject(clearRequest.error)
  })
}

/**
 * Get all items from a store
 */
export async function getAllData(storeName) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly')
    const store = transaction.objectStore(storeName)
    const request = store.getAll()
    
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

/**
 * Get single item by ID
 */
export async function getDataById(storeName, id) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([storeName], 'readonly')
    const store = transaction.objectStore(storeName)
    const request = store.get(id)
    
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

/**
 * Store metadata (sync timestamp, etc.)
 */
export async function setMetadata(key, value) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.METADATA], 'readwrite')
    const store = transaction.objectStore(STORES.METADATA)
    const request = store.put({ key, value, updatedAt: new Date().toISOString() })
    
    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

/**
 * Get metadata
 */
export async function getMetadata(key) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.METADATA], 'readonly')
    const store = transaction.objectStore(STORES.METADATA)
    const request = store.get(key)
    
    request.onsuccess = () => resolve(request.result?.value)
    request.onerror = () => reject(request.error)
  })
}

/**
 * Get last sync timestamp
 */
export async function getLastSync() {
  const metadata = await getMetadata('lastSync')
  return metadata || null
}

/**
 * Set last sync timestamp
 */
export async function setLastSync(timestamp) {
  return setMetadata('lastSync', timestamp)
}

/**
 * Add item to sync queue (for offline changes)
 */
export async function addToQueue(type, data) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.QUEUE], 'readwrite')
    const store = transaction.objectStore(STORES.QUEUE)
    const request = store.add({
      type,
      data,
      synced: false,
      createdAt: new Date().toISOString()
    })
    
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

/**
 * Get all pending items in queue
 */
export async function getPendingQueue() {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.QUEUE], 'readonly')
    const store = transaction.objectStore(STORES.QUEUE)
    const index = store.index('synced')
    const request = index.getAll(false)
    
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

/**
 * Mark queue item as synced
 */
export async function markQueueItemSynced(id) {
  if (!db) await initOfflineDB()
  
  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORES.QUEUE], 'readwrite')
    const store = transaction.objectStore(STORES.QUEUE)
    
    const getRequest = store.get(id)
    getRequest.onsuccess = () => {
      const item = getRequest.result
      if (item) {
        item.synced = true
        item.syncedAt = new Date().toISOString()
        const putRequest = store.put(item)
        putRequest.onsuccess = () => resolve()
        putRequest.onerror = () => reject(putRequest.error)
      } else {
        resolve()
      }
    }
    getRequest.onerror = () => reject(getRequest.error)
  })
}

/**
 * Clear all data (logout/reset)
 */
export async function clearAllData() {
  if (!db) await initOfflineDB()
  
  const stores = Object.values(STORES)
  
  return Promise.all(stores.map(storeName => {
    return new Promise((resolve, reject) => {
      const transaction = db.transaction([storeName], 'readwrite')
      const store = transaction.objectStore(storeName)
      const request = store.clear()
      
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }))
}

/**
 * Get database statistics
 */
export async function getOfflineStats() {
  const [buildings, rooms, paths, faqs, lastSync] = await Promise.all([
    getAllData(STORES.BUILDINGS),
    getAllData(STORES.ROOMS),
    getAllData(STORES.PATHS),
    getAllData(STORES.FAQS),
    getLastSync()
  ])
  
  return {
    buildings: buildings.length,
    rooms: rooms.length,
    paths: paths.length,
    faqs: faqs.length,
    lastSync,
    isOfflineReady: buildings.length > 0 && rooms.length > 0
  }
}

/**
 * Check if data is available offline
 */
export async function isOfflineReady() {
  const stats = await getOfflineStats()
  return stats.isOfflineReady
}

export { STORES }
export default {
  initOfflineDB,
  storeData,
  getAllData,
  getDataById,
  setMetadata,
  getMetadata,
  getLastSync,
  setLastSync,
  addToQueue,
  getPendingQueue,
  markQueueItemSynced,
  clearAllData,
  getOfflineStats,
  isOfflineReady,
  STORES
}
