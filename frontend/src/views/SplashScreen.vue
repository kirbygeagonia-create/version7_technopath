<template>
  <div class="splash-screen" :class="{ 'splash-exit': isExiting }">
    <div class="splash-logo-container">
      <img
        src="../assets/SEAITlogo.png"
        alt="SEAIT Logo"
        class="splash-logo-img"
        @error="logoFailed = true"
        v-if="!logoFailed"
      />
      <span v-else class="material-icons splash-logo-fallback">school</span>
    </div>

    <h1 class="splash-title">SEAIT Campus Guide</h1>
    <p class="splash-subtitle">TechnoPath Navigation System</p>

    <div class="splash-spinner-wrap">
      <div class="splash-spinner"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { syncAllData } from '../services/sync.js'

const router    = ref(useRouter())
const logoFailed = ref(false)
const isExiting  = ref(false)

onMounted(async () => {
  // FIX: Run minimum-display timer and sync in parallel.
  // Splash stays until BOTH the min timer AND the sync are done.
  // This is the correct data-driven approach — startTime/elapsed
  // in the previous version didn't work because module load and
  // onMounted fire within ~1ms of each other.
  const MIN_MS = 1500

  const [syncResult] = await Promise.all([
    syncAllData(),
    new Promise(resolve => setTimeout(resolve, MIN_MS)),
  ])

  if (!syncResult.success) {
    // Offline or sync failed — still proceed, app works with cache
    console.log('[Splash] Running offline or sync failed, using cached data')
  }

  isExiting.value = true

  // Wait for CSS exit animation (450ms fade-out in splash.css)
  setTimeout(() => {
    sessionStorage.setItem('tp_splash_shown', 'true')
    router.value.replace('/')
  }, 450)
})
</script>

<style>
@import '../assets/splash.css';
</style>
