<template>
  <div class="qrscanner-view">
    <header class="qrscanner-top-bar">
      <button class="qrscanner-back-btn" @click="goBack">
          <span class="material-icons">arrow_back</span>
        </button>
      <h1>QR Scanner</h1>
      <div class="qrscanner-spacer"></div>
    </header>

    <div class="qrscanner-scanner-container">
      <div v-if="!hasCamera" class="qrscanner-no-camera">
        <span class="material-icons" style="font-size: 64px; color: #FF9800;">photo_camera</span>
        <p style="margin-top: 16px;">Camera access required</p>
        <p class="qrscanner-subtitle">Please allow camera access to scan QR codes</p>
      </div>
      
      <div v-else-if="isScanning" class="qrscanner-scanning-area">
        <video ref="videoRef" class="qrscanner-camera-feed" autoplay playsinline></video>
        <canvas ref="canvasRef" class="qrscanner-hidden-canvas"></canvas>
        
        <!-- Scan overlay -->
        <div class="qrscanner-scan-overlay">
          <div class="qrscanner-scan-frame">
            <div class="qrscanner-corner qrscanner-top-left"></div>
            <div class="qrscanner-corner qrscanner-top-right"></div>
            <div class="qrscanner-corner qrscanner-bottom-left"></div>
            <div class="qrscanner-corner qrscanner-bottom-right"></div>
            <div class="qrscanner-scan-line"></div>
          </div>
          <p class="qrscanner-scan-text">Point camera at QR code</p>
        </div>
      </div>

      <div v-else-if="scanResult" class="qrscanner-result-panel">
        <div class="qrscanner-result-icon">
          <span class="material-icons" style="font-size: 40px;">check</span>
        </div>
        <h3>QR Code Detected!</h3>
        <p class="qrscanner-result-data">{{ scanResult }}</p>
        <div class="qrscanner-result-actions">
          <button class="qrscanner-action-btn qrscanner-secondary" @click="resetScan">Scan Again</button>
          <button class="qrscanner-action-btn qrscanner-primary" @click="processResult">Continue</button>
        </div>
      </div>
    </div>

    <!-- Manual entry fallback -->
    <div class="qrscanner-manual-entry">
      <p class="qrscanner-divider">or</p>
      <div class="qrscanner-input-group">
        <input
          v-model="manualCode"
          type="text"
          placeholder="Enter location code manually"
          @keyup.enter="processManualCode"
        />
        <button @click="processManualCode" :disabled="!manualCode">Go</button>
      </div>
      <p class="qrscanner-hint">Try codes like: RST-CL1, JST-CR2, MST-LIB</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import jsQR from 'jsqr'

const router = useRouter()
const videoRef = ref(null)
const canvasRef = ref(null)
const hasCamera = ref(false)
const isScanning = ref(false)
const scanResult = ref('')
const manualCode = ref('')
let stream = null
let scanInterval = null

const goBack = () => router.back()

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' }
    })
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      hasCamera.value = true
      isScanning.value = true
      startScanning()
    }
  } catch (error) {
    console.error('Camera access denied:', error)
    hasCamera.value = false
  }
}

const startScanning = () => {
  scanInterval = setInterval(() => {
    if (!videoRef.value || !canvasRef.value) return
    
    const video = videoRef.value
    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const code = jsQR(imageData.data, imageData.width, imageData.height)
    
    if (code) {
      scanResult.value = code.data
      isScanning.value = false
      stopCamera()
    }
  }, 200)
}

const stopCamera = () => {
  if (scanInterval) {
    clearInterval(scanInterval)
    scanInterval = null
  }
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
}

const resetScan = () => {
  scanResult.value = ''
  isScanning.value = true
  startCamera()
}

const processResult = () => {
  // Parse QR code and navigate
  const code = scanResult.value.trim()
  
  if (code.startsWith('SEAIT:')) {
    const location = code.replace('SEAIT:', '')
    router.push({
      path: '/navigate',
      query: { destination: location }
    })
  } else {
    // Try to parse as facility/room code
    processLocationCode(code)
  }
}

const processManualCode = () => {
  if (!manualCode.value) return
  processLocationCode(manualCode.value)
}

const processLocationCode = (code) => {
  // Map common codes to locations
  const locationMap = {
    'RST-CL1': 'RST Building - Computer Lab 1',
    'RST-CL2': 'RST Building - Computer Lab 2',
    'JST-CL4': 'JST Building - Computer Lab 4',
    'JST-CR4': 'JST Building - Classroom 4',
    'MST-CL6': 'MST Building - Computer Lab 6',
    'MST-CICT': 'MST Building - CICT Office',
    'MST-DEAN': 'MST Building - Dean Office',
    'LIB': 'Library',
    'REG': 'Registrar Office',
    'CAF': 'Cafeteria',
  }
  
  const location = locationMap[code.toUpperCase()] || code
  
  router.push({
    path: '/navigate',
    query: { destination: location }
  })
}

onMounted(() => {
  startCamera()
})

onUnmounted(() => {
  stopCamera()
})
</script>

<style>
/* Styles moved to external file: src/assets/qrscanner.css */
@import '../assets/qrscanner.css';
</style>
