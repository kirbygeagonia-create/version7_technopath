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
              <input type="checkbox" v-model="isDarkMode">
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

      <!-- Share App -->
      <div class="settings-section">
        <h3 class="settings-section-title">Share</h3>
        <div class="settings-card">
          <div class="settings-item qr-item">
            <div class="settings-item-icon icon-purple">
              <span class="material-icons">qr_code</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Scan to Access</div>
              <div class="settings-item-subtitle">QR code to open the app</div>
            </div>
          </div>
          <div class="qr-code-container">
            <qrcode-vue :value="appUrl" :size="180" level="M" />
            <p class="qr-url">{{ appUrl }}</p>
            <button class="qr-copy-btn" @click="copyUrl">
              <span class="material-icons">content_copy</span>
              Copy Link
            </button>
          </div>
        </div>
      </div>

      <!-- About -->
      <div class="settings-section">
        <h3 class="settings-section-title">About</h3>
        <div class="settings-card">
          <div class="settings-item" @click="showAboutModal = true">
            <div class="settings-item-icon icon-blue">
              <span class="material-icons">info_outline</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">About TechnoPath</div>
              <div class="settings-item-subtitle">SEAIT Campus Guide & Navigation</div>
            </div>
            <span class="material-icons" style="color: var(--text-secondary); margin-left: auto;">chevron_right</span>
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

    <!-- About Modal -->
    <Transition name="fade">
      <div v-if="showAboutModal" class="modal-overlay" @click="showAboutModal = false">
        <div class="dialog" @click.stop style="max-width: 500px;">
          <div class="dialog-header">
            <h2 style="margin: 0; font-size: 1.25rem;">About TechnoPath</h2>
            <button class="close-btn" @click="showAboutModal = false">×</button>
          </div>
          <div style="padding: 24px;">
            <div style="text-align: center; margin-bottom: 20px;">
              <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #FF9800, #F57C00); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px;">
                <span class="material-icons" style="font-size: 40px; color: white;">school</span>
              </div>
              <h3 style="margin: 0; color: var(--text-primary);">TechnoPath SEAIT Guide</h3>
              <p style="margin: 4px 0 0; color: var(--text-secondary); font-size: 14px;">Version 1.0.0</p>
            </div>
            
            <p style="color: var(--text-primary); line-height: 1.6; margin-bottom: 16px;">
              <strong>TechnoPath</strong> is a comprehensive campus guide and navigation system designed specifically for <strong>SEAIT (Southeast Asian Institute of Technology)</strong> students, faculty, and visitors.
            </p>
            
            <h4 style="margin: 20px 0 12px; color: var(--text-primary);">Key Features:</h4>
            <ul style="color: var(--text-primary); line-height: 1.8; margin: 0; padding-left: 20px;">
              <li>Interactive campus map with building navigation</li>
              <li>Room and facility locator</li>
              <li>AI-powered chatbot assistant</li>
              <li>Real-time announcements and notifications</li>
              <li>Offline-capable PWA support</li>
            </ul>
            
            <h4 style="margin: 20px 0 12px; color: var(--text-primary);">Contact & Support:</h4>
            <p style="color: var(--text-secondary); line-height: 1.6; margin: 0;">
              For support or feedback, please contact the SEAIT IT Department or submit feedback through the app.
            </p>
            
            <p style="text-align: center; color: var(--text-secondary); font-size: 12px; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border);">
              © 2024 SEAIT. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../stores/themeStore.js'
import { showToast } from '../services/toast.js'
import FacilitiesRoomsPanel from '../components/FacilitiesRoomsPanel.vue'
import QrcodeVue from 'qrcode.vue'

const router    = useRouter()
const themeStore = useThemeStore()

const isDarkMode = computed({
  get: () => themeStore.isDarkMode,
  set: (val) => themeStore.setTheme(val),
})

const showFacilitiesRoomsPanel = ref(false)
const showAboutModal           = ref(false)
const updateStatusText         = ref('Verify you have the latest version')
const appUrl                   = ref(window.location.origin)

const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(appUrl.value)
    showToast('Link copied to clipboard', 'success')
  } catch {
    showToast('Failed to copy link', 'error')
  }
}

const goToAdminLogin = () => router.push('/admin/login')

// Watch for dark mode changes and show toast
watch(() => themeStore.isDarkMode, (newVal, oldVal) => {
  if (oldVal !== undefined && newVal !== oldVal) {
    showToast(newVal ? 'Dark mode enabled' : 'Light mode enabled', 'info')
  }
})

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
  // Update URL if it changes
  appUrl.value = window.location.origin
})
</script>

<style>
@import '../assets/settings.css';
</style>
