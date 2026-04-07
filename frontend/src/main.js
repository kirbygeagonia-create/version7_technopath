import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router/index.js'
import './assets/main.css'
import 'material-icons/iconfont/material-icons.css'
import { syncAllData, registerConnectivityListener } from './services/sync.js'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// On app load: sync data from Django to IndexedDB if online
syncAllData().then(result => {
  if (result.success) {
    console.log('TechnoPath: Data synced at', result.syncedAt)
  } else {
    console.log('TechnoPath: Running offline with cached data')
  }
})

// Auto-sync whenever the device reconnects to the internet
registerConnectivityListener((result) => {
  console.log('TechnoPath: Reconnected and synced:', result)
})
