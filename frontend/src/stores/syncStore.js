import { defineStore } from 'pinia'
import { syncAllData, isOnline } from '../services/sync.js'

export const useSyncStore = defineStore('sync', {
  state: () => ({
    isOnline: navigator.onLine,
    isSyncing: false,
    lastSyncedAt: null,
    syncError: null
  }),

  actions: {
    async sync() {
      this.isSyncing = true
      this.syncError = null
      const result = await syncAllData()
      this.isSyncing = false
      if (result.success) {
        this.lastSyncedAt = result.syncedAt
      } else {
        this.syncError = result.reason
      }
    },

    updateOnlineStatus() {
      this.isOnline = navigator.onLine
    }
  }
})
