<template>
  <div class="offline-sync-panel">
    <!-- Offline Status Card -->
    <div class="sync-card" :class="{ 'offline-ready': isOfflineReady }">
      <div class="sync-header">
        <div class="sync-icon">
          <span class="material-icons">{{ isOfflineReady ? 'cloud_done' : 'cloud_off' }}</span>
        </div>
        <div class="sync-info">
          <h4>{{ isOfflineReady ? 'Ready for Offline' : 'Offline Mode Setup' }}</h4>
          <p class="sync-status-text">
            {{ statusText }}
          </p>
        </div>
      </div>
      
      <!-- Sync Stats -->
      <div class="sync-stats" v-if="syncStats">
        <div class="stat-item">
          <span class="stat-value">{{ syncStats.buildings }}</span>
          <span class="stat-label">Buildings</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ syncStats.rooms }}</span>
          <span class="stat-label">Rooms</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ syncStats.paths }}</span>
          <span class="stat-label">Paths</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ syncStats.faqs }}</span>
          <span class="stat-label">FAQs</span>
        </div>
      </div>
      
      <!-- Last Sync Time -->
      <div class="last-sync" v-if="syncStats?.lastSync">
        <span class="material-icons">schedule</span>
        <span>Last sync: {{ formatLastSync(syncStats.lastSync) }}</span>
      </div>
      
      <!-- Action Buttons -->
      <div class="sync-actions">
        <button 
          class="btn-scan-qr" 
          @click="openQRScanner"
          :disabled="isSyncing"
        >
          <span class="material-icons">qr_code_scanner</span>
          {{ isOfflineReady ? 'Re-scan for Updates' : 'Scan QR to Setup' }}
        </button>
        
        <button 
          class="btn-refresh" 
          @click="refreshSync"
          :disabled="isSyncing || !isOnline"
          v-if="isOfflineReady"
        >
          <span class="material-icons">refresh</span>
          Refresh Data
        </button>
      </div>
      
      <!-- Sync Progress -->
      <div class="sync-progress" v-if="isSyncing">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: syncProgress + '%' }"></div>
        </div>
        <span class="progress-text">{{ syncMessage }}</span>
      </div>
      
      <!-- Network Status -->
      <div class="network-status" :class="{ 'online': isOnline, 'offline': !isOnline }">
        <span class="material-icons">{{ isOnline ? 'wifi' : 'wifi_off' }}</span>
        <span>{{ isOnline ? 'Online' : 'Offline' }}</span>
      </div>
    </div>
    
    <!-- QR Scanner Modal -->
    <QRCodeScanner 
      :is-open="showQRScanner" 
      @close="closeQRScanner"
      @sync-complete="onSyncComplete"
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import QRCodeScanner from './QRCodeScanner.vue'
import { getSyncStatus, performFullSync, isOnline, setupAutoSync } from '../services/syncService.js'

export default {
  name: 'OfflineSyncPanel',
  
  components: {
    QRCodeScanner
  },
  
  setup() {
    const isOfflineReady = ref(false)
    const isOnline = ref(true)
    const syncStats = ref(null)
    const isSyncing = ref(false)
    const syncProgress = ref(0)
    const syncMessage = ref('')
    const showQRScanner = ref(false)
    
    const statusText = computed(() => {
      if (isSyncing.value) {
        return syncMessage.value
      }
      if (isOfflineReady.value) {
        return 'You can use the app without internet'
      }
      if (!isOnline.value) {
        return 'Connect to WiFi and scan QR to setup'
      }
      return 'Scan campus QR code to download data'
    })
    
    const loadSyncStatus = async () => {
      try {
        const status = await getSyncStatus()
        isOfflineReady.value = status.isOfflineReady
        isOnline.value = status.online
        syncStats.value = status
      } catch (error) {
        console.error('[OfflineSync] Failed to load status:', error)
      }
    }
    
    const openQRScanner = () => {
      showQRScanner.value = true
    }
    
    const closeQRScanner = () => {
      showQRScanner.value = false
    }
    
    const onSyncComplete = (result) => {
      console.log('[OfflineSync] Sync completed:', result)
      loadSyncStatus()
    }
    
    const refreshSync = async () => {
      if (isSyncing.value || !isOnline.value) return
      
      isSyncing.value = true
      syncProgress.value = 0
      syncMessage.value = 'Checking for updates...'
      
      const progressInterval = setInterval(() => {
        if (syncProgress.value < 90) {
          syncProgress.value += 5
          syncMessage.value = `Downloading data... ${syncProgress.value}%`
        }
      }, 200)
      
      try {
        const result = await performFullSync()
        clearInterval(progressInterval)
        syncProgress.value = 100
        syncMessage.value = 'Sync complete!'
        
        await loadSyncStatus()
        
        setTimeout(() => {
          isSyncing.value = false
          syncProgress.value = 0
        }, 1500)
        
      } catch (error) {
        clearInterval(progressInterval)
        syncProgress.value = 0
        syncMessage.value = 'Sync failed. Try again.'
        console.error('[OfflineSync] Refresh failed:', error)
        
        setTimeout(() => {
          isSyncing.value = false
        }, 2000)
      }
    }
    
    const formatLastSync = (timestamp) => {
      if (!timestamp) return 'Never'
      
      const date = new Date(timestamp)
      const now = new Date()
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)
      
      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins} min ago`
      if (diffHours < 24) return `${diffHours} hours ago`
      if (diffDays < 7) return `${diffDays} days ago`
      return date.toLocaleDateString()
    }
    
    onMounted(() => {
      loadSyncStatus()
      setupAutoSync()
      
      // Listen for online/offline events
      window.addEventListener('online', () => {
        isOnline.value = true
        loadSyncStatus()
      })
      window.addEventListener('offline', () => {
        isOnline.value = false
      })
    })
    
    return {
      isOfflineReady,
      isOnline,
      syncStats,
      isSyncing,
      syncProgress,
      syncMessage,
      showQRScanner,
      statusText,
      openQRScanner,
      closeQRScanner,
      onSyncComplete,
      refreshSync,
      formatLastSync
    }
  }
}
</script>

<style scoped>
.offline-sync-panel {
  width: 100%;
}

.sync-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid #e0e0e0;
  transition: all 0.3s ease;
}

.sync-card.offline-ready {
  border-color: #28a745;
  background: linear-gradient(135deg, #f8fff9 0%, #ffffff 100%);
}

.sync-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.sync-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #fff3e0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sync-icon .material-icons {
  font-size: 28px;
  color: #FF6B00;
}

.sync-card.offline-ready .sync-icon {
  background: #d4edda;
}

.sync-card.offline-ready .sync-icon .material-icons {
  color: #28a745;
}

.sync-info h4 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.sync-status-text {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.sync-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 12px 8px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #FF6B00;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}

.last-sync {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.last-sync .material-icons {
  font-size: 16px;
  color: #999;
}

.sync-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.btn-scan-qr,
.btn-refresh {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-scan-qr {
  background: #FF6B00;
  color: white;
}

.btn-scan-qr:hover:not(:disabled) {
  background: #e56000;
  transform: translateY(-1px);
}

.btn-refresh {
  background: #f8f9fa;
  color: #666;
  border: 2px solid #e0e0e0;
}

.btn-refresh:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #d0d0d0;
}

.btn-scan-qr:disabled,
.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sync-progress {
  margin-bottom: 16px;
}

.progress-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FF6B00, #ff8533);
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 13px;
  color: #666;
}

.network-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

.network-status.online {
  background: #d4edda;
  color: #155724;
}

.network-status.offline {
  background: #f8d7da;
  color: #721c24;
}

.network-status .material-icons {
  font-size: 18px;
}

@media (max-width: 480px) {
  .sync-card {
    padding: 16px;
  }
  
  .sync-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .sync-actions {
    flex-direction: column;
  }
  
  .btn-scan-qr,
  .btn-refresh {
    width: 100%;
  }
}
</style>
