import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import './assets/main.css'
import 'material-icons/iconfont/material-icons.css'
import { registerConnectivityListener } from './services/sync.js'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// FIX: Global Vue error boundary — prevents white-screen on uncaught errors
app.config.errorHandler = (err, instance, info) => {
  console.error('[TechnoPath] Uncaught Vue error:', err, '\nInfo:', info)

  // Show friendly error UI instead of blank white screen
  const appEl = document.getElementById('app')
  if (appEl && !appEl.querySelector('.tp-error-boundary')) {
    appEl.innerHTML = `
      <div class="tp-error-boundary">
        <span class="material-icons">error_outline</span>
        <h2>Something went wrong</h2>
        <p>The app encountered an unexpected error. Please refresh to continue.</p>
        <button onclick="location.reload()">Refresh App</button>
      </div>
    `
  }
}

app.mount('#app')

// Register connectivity listener — auto-syncs when device reconnects
registerConnectivityListener((result) => {
  if (result.success) {
    console.log('[TechnoPath] Reconnected and synced at', result.syncedAt)
  }
})

// NOTE: syncAllData() is now called inside SplashScreen.vue so the
// splash screen can wait for it before dismissing.
// We do NOT call it here anymore to avoid double-syncing on startup.
