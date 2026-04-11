<template>
  <div class="settings-view">
    <div class="settings-header">
      <div class="settings-header-content">
        <div class="settings-header-icon">
          <span class="material-icons">settings</span>
        </div>
        <div class="settings-header-text">
          <h1>App Settings</h1>
          <p>Customize your experience</p>
        </div>
      </div>
    </div>

    <div class="settings-content">
      <!-- Account -->
      <div class="settings-section">
        <h3 class="settings-section-title">Account</h3>
        <div class="settings-card">
          <div class="settings-item" @click="goToProfile">
            <!-- FIX: icon-blue class instead of inline style="background:#E3F2FD; color:#2196F3" -->
            <div class="settings-item-icon icon-blue">
              <span class="material-icons">person</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Profile</div>
              <div class="settings-item-subtitle">View and edit your profile</div>
            </div>
            <span class="material-icons settings-chevron">chevron_right</span>
          </div>
          <div class="settings-divider"></div>
          <div class="settings-item" @click="goToAdminLogin">
            <div class="settings-item-icon icon-orange">
              <span class="material-icons">admin_panel_settings</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Admin Login</div>
              <div class="settings-item-subtitle">Access admin dashboard</div>
            </div>
            <span class="material-icons settings-chevron">chevron_right</span>
          </div>
        </div>
      </div>

      <!-- Appearance -->
      <div class="settings-section">
        <h3 class="settings-section-title">Appearance</h3>
        <div class="settings-card">
          <div class="settings-item">
            <div class="settings-item-icon icon-purple">
              <span class="material-icons">dark_mode</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Dark Mode</div>
              <div class="settings-item-subtitle">Toggle dark theme</div>
            </div>
            <label class="settings-switch">
              <input type="checkbox" v-model="isDarkMode" @change="toggleTheme">
              <span class="settings-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Info -->
      <div class="settings-section">
        <h3 class="settings-section-title">Info</h3>
        <div class="settings-card">
          <div class="settings-item" @click="showFacilitiesRoomsPanel = true">
            <div class="settings-item-icon icon-orange">
              <span class="material-icons">business</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Facilities & Rooms</div>
              <div class="settings-item-subtitle">Browse campus facilities</div>
            </div>
            <span class="material-icons settings-chevron">chevron_right</span>
          </div>
        </div>
      </div>

      <!-- About -->
      <div class="settings-section">
        <h3 class="settings-section-title">About</h3>
        <div class="settings-card">
          <div class="settings-item">
            <div class="settings-item-icon icon-blue">
              <span class="material-icons">info_outline</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">About TechnoPath</div>
              <div class="settings-item-subtitle">SEAIT Campus Guide & Navigation</div>
            </div>
          </div>
          <div class="settings-divider"></div>
          <div class="settings-item">
            <div class="settings-item-icon icon-green">
              <span class="material-icons">verified</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Version</div>
              <div class="settings-item-subtitle">1.0.0</div>
            </div>
          </div>
          <div class="settings-divider"></div>
          <div class="settings-item" @click="checkForUpdates">
            <div class="settings-item-icon icon-deep-orange">
              <span class="material-icons">system_update</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Check for Updates</div>
              <div class="settings-item-subtitle">{{ updateStatusText }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-spacer"></div>
    </div>

    <!-- Facilities & Rooms Panel Modal -->
    <Transition name="fade">
      <div v-if="showFacilitiesRoomsPanel" class="modal-overlay" @click="showFacilitiesRoomsPanel = false">
        <div class="dialog fr-dialog" @click.stop
             style="padding: 0; width: 95vw; max-width: 600px; overflow: hidden; border-radius: 16px;">
          <FacilitiesRoomsPanel @close="showFacilitiesRoomsPanel = false" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/themeStore.js'
import { showToast } from '../services/toast.js'
import FacilitiesRoomsPanel from '../components/FacilitiesRoomsPanel.vue'

const router    = useRouter()
const themeStore = useThemeStore()

const isDarkMode = computed({
  get: () => themeStore.isDarkMode,
  set: (val) => themeStore.setTheme(val),
})

const showFacilitiesRoomsPanel = ref(false)
const updateStatusText         = ref('Verify you have the latest version')

const goToAdminLogin = () => router.push('/admin/login')
const goToProfile    = () => router.push('/profile')

const toggleTheme = () => {
  themeStore.toggleTheme()
  showToast(themeStore.isDarkMode ? 'Dark mode enabled' : 'Light mode enabled', 'info')
}

// FIX: Real service-worker update check instead of always saying "up to date"
const checkForUpdates = async () => {
  updateStatusText.value = 'Checking...'
  try {
    if (!('serviceWorker' in navigator)) {
      showToast('Service worker not supported in this browser', 'warning')
      updateStatusText.value = 'Not supported'
      return
    }
    const reg = await navigator.serviceWorker.getRegistration()
    if (!reg) {
      showToast('App is up to date', 'success')
      updateStatusText.value = 'Already up to date'
      return
    }

    await reg.update()

    if (reg.waiting) {
      // A new SW is waiting — prompt user
      showToast('Update available! Restart the app to apply.', 'info', 5000)
      updateStatusText.value = 'Update available — restart to apply'
    } else {
      showToast('You are on the latest version.', 'success')
      updateStatusText.value = 'Already up to date'
    }
  } catch {
    showToast('Could not check for updates', 'error')
    updateStatusText.value = 'Check failed — try again'
  }
}

onMounted(() => {
  themeStore.initTheme()
})
</script>

<style>
@import '../assets/settings.css';
</style>
