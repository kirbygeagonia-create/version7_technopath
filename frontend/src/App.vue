<template>
  <div id="app-root" :class="{ 'app-desktop': isDesktop, 'app-mobile': !isDesktop }">
    <!-- Desktop Layout -->
    <template v-if="isDesktop">
      <!-- Side Navigation for Desktop -->
      <aside class="app-side-nav" v-if="showSideNav">
        <div class="app-side-nav-header">
          <span class="app-logo-fallback">
            <span class="material-icons">school</span>
          </span>
          <div class="app-logo-text">TechnoPath</div>
        </div>
        
        <nav class="app-side-nav-menu">
          <router-link 
            v-for="item in menuItems" 
            :key="item.path"
            :to="item.path"
            class="app-side-nav-item"
            :class="{ 'app-active': currentRoute === item.path }"
          >
            <span class="material-icons">{{ item.icon }}</span>
            <span class="app-nav-text">{{ item.label }}</span>
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
            <router-link to="/instructor-info" class="app-info-item">
              <span class="material-icons">school</span>
              <span>Instructor Info</span>
            </router-link>
            <router-link to="/employees" class="app-info-item">
              <span class="material-icons">people</span>
              <span>Employees</span>
            </router-link>
          </div>
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
          <router-view v-slot="{ Component }">
            <keep-alive :include="['HomeView', 'SettingsView']">
              <component :is="Component" />
            </keep-alive>
          </router-view>
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
        <router-view v-slot="{ Component }">
          <keep-alive :include="['HomeView', 'SettingsView']">
            <component :is="Component" />
          </keep-alive>
        </router-view>
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
          <span class="material-icons">{{ item.icon }}</span>
          <span class="app-nav-label">{{ item.label }}</span>
        </router-link>
      </nav>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSyncStore } from './stores/syncStore.js'
import { useAuthStore } from './stores/authStore.js'

const router = useRouter()
const route = useRoute()
const syncStore = useSyncStore()
const authStore = useAuthStore()

const windowWidth = ref(window.innerWidth)

const isDesktop = computed(() => windowWidth.value >= 1024)
const currentRoute = computed(() => route.path)

const isActiveRoute = (path) => {
  if (path === '/navigate') {
    return route.path === '/navigate' || route.path === '/map'
  }
  return route.path === path
}

// Full menu for desktop side nav
const menuItems = [
  { path: '/', label: 'Home', icon: 'home' },
  { path: '/navigate', label: 'Navigate', icon: 'map' },
  { path: '/qr-scanner', label: 'QR Scanner', icon: 'qr_code_scanner' },
  { path: '/chatbot', label: 'Chatbot', icon: 'smart_toy' },
  { path: '/notifications', label: 'Notifications', icon: 'notifications' },
  { path: '/feedback', label: 'Ratings & Feedback', icon: 'star' },
  { path: '/settings', label: 'Settings', icon: 'settings' },
]

// Simplified menu for mobile bottom nav
const mobileMenuItems = [
  { path: '/', label: 'Home', icon: 'home' },
  { path: '/navigate', label: 'Navigate', icon: 'explore' },
  { path: '/settings', label: 'Settings', icon: 'settings' },
]

// Hide side nav on admin routes
const showSideNav = computed(() => {
  return !route.path.startsWith('/admin')
})

// Hide bottom nav on certain routes
const showBottomNav = computed(() => {
  const hiddenRoutes = ['/admin', '/qr-scanner', '/chatbot', '/notifications', '/feedback']
  return !hiddenRoutes.some(path => route.path.startsWith(path))
})

// Info dropdown state
const isInfoDropdownOpen = ref(false)

function updateWindowWidth() {
  windowWidth.value = window.innerWidth
}

function updateStatus() {
  syncStore.updateOnlineStatus()
}

onMounted(() => {
  window.addEventListener('resize', updateWindowWidth)
  window.addEventListener('online', updateStatus)
  window.addEventListener('offline', updateStatus)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateWindowWidth)
  window.removeEventListener('online', updateStatus)
  window.removeEventListener('offline', updateStatus)
})
</script>

<style>
/* Global styles only - component styles moved to external file */
@import './assets/app.css';
</style>
