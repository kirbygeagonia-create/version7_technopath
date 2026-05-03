<template>
  <div id="app-root" :class="{ 'app-desktop': isDesktop, 'app-mobile': !isDesktop }">
    <!-- Desktop Layout -->
    <template v-if="isDesktop">
      <!-- Side Navigation for Desktop -->
      <aside class="app-side-nav" v-if="showSideNav">
        <div class="app-side-nav-header">
          <img 
            src="./assets/SEAITlogo.png" 
            alt="SEAIT Logo" 
            class="app-logo-img"
            @error="$event.target.style.display='none'"
          />
          <div class="app-logo-text">TechnoPath</div>
        </div>
        
        <nav class="app-side-nav-menu">
          <router-link 
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="app-side-nav-item"
            :class="{ 'app-active': currentRoute === item.path }"
            :data-label="item.label"
          >
            <span class="material-icons">
              {{ item.icon }}
              <!-- Notification badge for desktop -->
              <span v-if="item.path === '/notifications' && unreadCount > 0" class="nav-badge desktop-badge">
                {{ unreadCount > 99 ? '99+' : unreadCount }}
              </span>
            </span>
            <span class="app-nav-text">{{ item.label }}</span>
            <!-- Notification badge alternative position -->
            <span v-if="item.path === '/notifications' && unreadCount > 0" class="nav-badge-alt">
              {{ unreadCount > 99 ? '99+' : unreadCount }}
            </span>
          </router-link>
        </nav>

        <!-- Info Dropdown Section for Desktop -->
        <div class="app-info-section">
          <div 
            class="app-info-dropdown-header"
            @click="isInfoDropdownOpen = !isInfoDropdownOpen"
          >
            <span class="material-icons">info</span>
            <span class="app-nav-text">Information</span>
            <span class="material-icons app-dropdown-chevron">
              {{ isInfoDropdownOpen ? 'expand_less' : 'expand_more' }}
            </span>
          </div>
          <div v-if="isInfoDropdownOpen" class="app-info-dropdown-content">
            <router-link to="/building-info" class="app-info-item">
              <span class="material-icons">business</span>
              <span>Building Info</span>
            </router-link>
            <router-link to="/rooms-info" class="app-info-item">
              <span class="material-icons">meeting_room</span>
              <span>Rooms Info</span>
            </router-link>
          </div>
        </div>

        <!-- Admin Panel Button (visible only for admins) -->
        <div v-if="authStore.isAdmin" class="app-admin-section">
          <router-link to="/admin" class="app-admin-link">
            <span class="material-icons">admin_panel_settings</span>
            <span class="app-nav-text">Admin Panel</span>
          </router-link>
        </div>

        <div class="app-side-nav-footer">
          <div class="app-user-info" v-if="authStore.isLoggedIn">
            <span class="material-icons">account_circle</span>
            <span class="app-username">{{ authStore.user?.username }}</span>
          </div>
        </div>
      </aside>

      <!-- Main Content Area -->
      <div class="app-main-area" :class="showSideNav ? 'app-with-sidebar' : 'app-full-width'">
        <!-- Offline/Sync Banners -->
        <div v-if="!syncStore.isOnline" class="app-status-banner app-offline">
          <span class="material-icons">wifi_off</span>
          You are offline — map and navigation still work using saved data
        </div>
        <div v-if="syncStore.isSyncing" class="app-status-banner app-syncing">
          <span class="material-icons">sync</span>
          Updating map data...
        </div>

        <!-- Router View -->
        <main class="app-main-content">
          <RouterView v-slot="{ Component, route }">
            <Transition :name="route.meta.transition || 'page-slide'" mode="out-in">
              <component :is="Component" :key="route.path" />
            </Transition>
          </RouterView>
        </main>
      </div>
    </template>

    <!-- Mobile Layout -->
    <template v-else>
      <!-- Status Banners -->
      <div v-if="!syncStore.isOnline" class="app-status-banner app-offline">
        <span class="material-icons">wifi_off</span>
        You are offline
      </div>
      <div v-if="syncStore.isSyncing" class="app-status-banner app-syncing">
        <span class="material-icons">sync</span>
        Updating...
      </div>

      <!-- Main Content -->
      <div class="app-content-area">
        <RouterView v-slot="{ Component, route }">
          <Transition :name="route.meta.transition || 'page-slide'" mode="out-in">
            <keep-alive :include="['HomeView', 'SettingsView']">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </Transition>
        </RouterView>
      </div>

      <!-- Bottom Navigation for Mobile -->
      <nav class="app-bottom-nav" v-if="showBottomNav">
        <router-link 
          v-for="item in mobileMenuItems" 
          :key="item.path"
          :to="item.path"
          class="app-nav-item"
          :class="{ 'app-active': isActiveRoute(item.path) }"
        >
          <span class="material-icons">
            {{ item.icon }}
            <!-- Notification dot for bell icon -->
            <span v-if="item.path === '/notifications' && unreadCount > 0" class="nav-dot"></span>
          </span>
          <span class="app-nav-label">{{ item.label }}</span>
          <!-- Notification badge on bell icon -->
          <span v-if="item.path === '/notifications' && unreadCount > 0" class="nav-badge">
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
          <!-- Notification badge for ratings/feedback -->
          <span v-if="item.path === '/feedback' && unreadFeedbackCount > 0" class="nav-badge feedback-badge">
            {{ unreadFeedbackCount > 9 ? '9+' : unreadFeedbackCount }}
          </span>
        </router-link>

      </nav>
    </template>
    <!-- Global Toast Component -->
    <AppToast />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSyncStore } from './stores/syncStore.js'
import { useAuthStore } from './stores/authStore.js'
import { useThemeStore } from './stores/themeStore.js'
import AppToast from './components/AppToast.vue'
import { startPolling, stopPolling } from './services/sync.js'

const router = useRouter()
const route = useRoute()
const syncStore = useSyncStore()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const windowWidth = ref(window.innerWidth)

const isDesktop = computed(() => windowWidth.value >= 768)
const currentRoute = computed(() => route.path)

const isActiveRoute = (path) => {
  if (path === '/navigate') {
    return route.path === '/navigate' || route.path === '/map'
  }
  if (path === '/feedback') {
    return route.path === '/feedback'
  }
  return route.path === path
}

// Full menu for desktop side nav
const menuItems = [
  { path: '/', label: 'Home', icon: 'home' },
  { path: '/navigate', label: 'Navigate', icon: 'directions' },
  { path: '/chatbot', label: 'Chatbot', icon: 'smart_toy' },
  { path: '/notifications', label: 'Notifications', icon: 'notifications' },
  { path: '/feedback', label: 'Ratings & Feedback', icon: 'star' },
  { path: '/settings', label: 'Settings', icon: 'settings' },
]

// Simplified menu for mobile bottom nav — 3 items only
const mobileMenuItems = [
  { path: '/', label: 'Home', icon: 'home' },
  { path: '/navigate', label: 'Navigate', icon: 'directions' },
  { path: '/settings', label: 'Settings', icon: 'settings' },
]

// Unread notifications count
const unreadCount = ref(0)
const unreadFeedbackCount = ref(0)

async function loadUnreadCount() {
  // Check if user is authenticated first
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  if (!token) {
    unreadCount.value = 0
    unreadFeedbackCount.value = 0
    return
  }
  
  try {
    // Load notification count
    const res = await fetch('/api/notifications/unread-count/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (res.ok) {
      const data = await res.json()
      unreadCount.value = data.count || 0
    } else {
      unreadCount.value = 0
    }
    
    // Load feedback count (for admin users)
    const feedbackRes = await fetch('/api/feedback/pending-count/', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (feedbackRes.ok) {
      const feedbackData = await feedbackRes.json()
      unreadFeedbackCount.value = feedbackData.count || 0
    } else {
      unreadFeedbackCount.value = 0
    }
  } catch {
    // Silent fail - offline or error
    unreadCount.value = 0
    unreadFeedbackCount.value = 0
  }
}

// Hide side nav on admin routes
const showSideNav = computed(() => {
  return !route.path.startsWith('/admin') && route.path !== '/splash'
})

// Hide bottom nav on certain routes
const showBottomNav = computed(() => {
  const hiddenRoutes = ['/admin', '/splash']
  return !hiddenRoutes.some(path => route.path.startsWith(path))
})

// Info dropdown state
const isInfoDropdownOpen = ref(false)

let resizeTimer = null
function updateWindowWidth() {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    windowWidth.value = window.innerWidth
  }, 150)
}

function updateStatus() {
  syncStore.updateOnlineStatus()
}

onMounted(() => {
  themeStore.initTheme()
  window.addEventListener('resize', updateWindowWidth)
  window.addEventListener('online', updateStatus)
  window.addEventListener('offline', updateStatus)
  startPolling()
  loadUnreadCount()
  // Poll for unread notifications every 30 seconds
  setInterval(loadUnreadCount, 30000)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWindowWidth)
  window.removeEventListener('online', updateStatus)
  window.removeEventListener('offline', updateStatus)
  stopPolling()
})
</script>

<style>
/* Global styles only - component styles moved to external file */
@import './assets/app.css';
</style>
