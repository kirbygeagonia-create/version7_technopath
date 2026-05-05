<template>
  <div class="qr-scanner-overlay" v-if="isOpen">
    <div class="qr-scanner-modal">
      <div class="scanner-header">
        <h3>
          <span class="material-icons">qr_code_scanner</span>
          Scan QR Code for Offline Access
        </h3>
        <button class="close-btn" @click="closeScanner">
          <span class="material-icons">close</span>
        </button>
      </div>
      
      <div class="scanner-content">
        <!-- QR Scanner Video Feed -->
        <div id="qr-reader" ref="qrReader" class="qr-reader-container"></div>
        
        <!-- Manual Sync Button (fallback) -->
        <div class="manual-sync-fallback" v-if="showFallback">
          <p>Camera not available?</p>
          <button class="manual-sync-btn" @click="triggerManualSync">
            <span class="material-icons">sync</span>
            Sync Manually
          </button>
        </div>
        
        <!-- Sync Status -->
        <div class="sync-status" v-if="syncStatus">
          <div class="status-message" :class="syncStatus.type">
            <span class="material-icons">{{ syncStatus.icon }}</span>
            <span>{{ syncStatus.message }}</span>
          </div>
          <div class="sync-progress" v-if="syncStatus.progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: syncStatus.progress + '%' }"></div>
            </div>
            <span class="progress-text">{{ syncStatus.progress }}%</span>
          </div>
        </div>
      </div>
      
      <div class="scanner-footer">
        <p class="scanner-hint">Point your camera at the campus QR code to download offline data</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { performFullSync, getSyncStatus } from '../services/syncService.js'

export default {
  name: 'QRCodeScanner',
  
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['close', 'sync-complete'],
  
  setup(props, { emit }) {
    const qrReader = ref(null)
    const html5QrCode = ref(null)
    const showFallback = ref(false)
    const syncStatus = ref(null)
    
    const closeScanner = () => {
      stopScanner()
      emit('close')
    }
    
    const startScanner = async () => {
      try {
        // Dynamically import the QR scanner library
        const { Html5Qrcode } = await import('html5-qrcode')
        
        html5QrCode.value = new Html5Qrcode('qr-reader')
        
        const config = {
          fps: 10,
          qrbox: { width: 250, height: 250 }
        }
        
        await html5QrCode.value.start(
          { facingMode: 'environment' },
          config,
          onScanSuccess,
          onScanFailure
        )
        
        showFallback.value = false
        
      } catch (error) {
        console.error('[QR Scanner] Failed to start:', error)
        showFallback.value = true
      }
    }
    
    const stopScanner = () => {
      if (html5QrCode.value) {
        html5QrCode.value.stop().catch(err => {
          console.error('[QR Scanner] Stop error:', err)
        })
        html5QrCode.value = null
      }
    }
    
    const onScanSuccess = async (decodedText) => {
      console.log('[QR Scanner] QR Code detected:', decodedText)
      
      try {
        // Parse QR code data
        let qrData
        try {
          qrData = JSON.parse(decodedText)
        } catch {
          qrData = { action: 'offline-sync', url: decodedText }
        }
        
        // Only process if it's an offline sync QR
        if (qrData.action === 'offline-sync' || qrData.url?.includes('offline-sync')) {
          // Stop scanner
          stopScanner()
          
          // Show syncing status
          syncStatus.value = {
            type: 'syncing',
            icon: 'sync',
            message: 'Syncing campus data...',
            progress: 0
          }
          
          // Start sync animation
          const progressInterval = setInterval(() => {
            if (syncStatus.value && syncStatus.value.progress < 90) {
              syncStatus.value.progress += 10
            }
          }, 300)
          
          // Perform the actual sync
          const result = await performFullSync()
          
          clearInterval(progressInterval)
          
          // Show success
          syncStatus.value = {
            type: 'success',
            icon: 'check_circle',
            message: result.message,
            progress: 100
          }
          
          // Emit sync complete
          setTimeout(() => {
            emit('sync-complete', result)
            closeScanner()
          }, 1500)
          
        } else {
          syncStatus.value = {
            type: 'error',
            icon: 'error',
            message: 'Invalid QR code. Please scan the campus offline sync code.'
          }
        }
        
      } catch (error) {
        console.error('[QR Scanner] Sync failed:', error)
        syncStatus.value = {
          type: 'error',
          icon: 'error',
          message: 'Sync failed. Please try again.'
        }
      }
    }
    
    const onScanFailure = (error) => {
      // This is called frequently when no QR is detected - ignore
      // console.debug('[QR Scanner] Scan failed:', error)
    }
    
    const triggerManualSync = async () => {
      syncStatus.value = {
        type: 'syncing',
        icon: 'sync',
        message: 'Syncing campus data...',
        progress: 0
      }
      
      try {
        const result = await performFullSync()
        
        syncStatus.value = {
          type: 'success',
          icon: 'check_circle',
          message: result.message,
          progress: 100
        }
        
        setTimeout(() => {
          emit('sync-complete', result)
          closeScanner()
        }, 1500)
        
      } catch (error) {
        syncStatus.value = {
          type: 'error',
          icon: 'error',
          message: 'Sync failed. Please check your connection.'
        }
      }
    }
    
    onMounted(() => {
      if (props.isOpen) {
        startScanner()
      }
    })
    
    onUnmounted(() => {
      stopScanner()
    })
    
    return {
      qrReader,
      showFallback,
      syncStatus,
      closeScanner,
      triggerManualSync
    }
  }
}
</script>

<style scoped>
.qr-scanner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.qr-scanner-modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.scanner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.scanner-header h3 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.scanner-header h3 .material-icons {
  color: #FF6B00;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-btn:hover {
  background: #f0f0f0;
}

.scanner-content {
  padding: 20px;
}

.qr-reader-container {
  width: 100%;
  min-height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f5;
}

.manual-sync-fallback {
  text-align: center;
  padding: 20px;
}

.manual-sync-fallback p {
  color: #666;
  margin-bottom: 12px;
}

.manual-sync-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #FF6B00;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  margin: 0 auto;
  transition: background 0.2s;
}

.manual-sync-btn:hover {
  background: #e56000;
}

.sync-status {
  margin-top: 20px;
  padding: 16px;
  border-radius: 8px;
  background: #f8f9fa;
}

.status-message {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.status-message.syncing {
  color: #FF6B00;
}

.status-message.success {
  color: #28a745;
}

.status-message.error {
  color: #dc3545;
}

.sync-progress {
  margin-top: 12px;
}

.progress-bar {
  height: 6px;
  background: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #FF6B00;
  transition: width 0.3s ease;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.scanner-footer {
  padding: 16px 20px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
}

.scanner-hint {
  margin: 0;
  font-size: 13px;
  color: #666;
  text-align: center;
}

@media (max-width: 480px) {
  .qr-scanner-overlay {
    padding: 0;
  }
  
  .qr-scanner-modal {
    max-width: 100%;
    height: 100vh;
    border-radius: 0;
    display: flex;
    flex-direction: column;
  }
  
  .scanner-content {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  
  .qr-reader-container {
    flex: 1;
    min-height: auto;
  }
}
</style>
