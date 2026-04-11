<template>
  <div class="notifications-view">
    <header class="notifications-top-bar">
      <button class="notifications-back-btn" @click="goBack">
        <span class="material-icons">arrow_back</span>
      </button>
      <div class="notifications-header-title">
        <h1>Notifications</h1>
      </div>
      <button
        class="notifications-read-btn"
        @click="markAllAsRead"
        v-if="unreadCount > 0"
        title="Mark all as read"
      >
        <span class="material-icons">done_all</span>
      </button>
      <div v-else class="notifications-spacer"></div>
    </header>

    <div class="notifications-main-content">
      <div class="notifications-list">
        <div v-if="notifications.length === 0" class="notifications-empty-state">
          <div class="notifications-empty-icon">
            <span class="material-icons">notifications_off</span>
          </div>
          <h2>All caught up!</h2>
          <p>You have no notifications.</p>
        </div>

        <div
          v-for="notif in notifications"
          :key="notif.id"
          :class="['notifications-card', notif.type, { 'notifications-unread': !notif.is_read }]"
          @click="markAsRead(notif)"
        >
          <div class="notifications-card-header">
            <span
              v-if="notif.source_label"
              :class="['source-chip', 'chip-' + (notif.source_color || 'orange')]"
            >
              {{ notif.source_label }}
            </span>
            <span class="notifications-badge" :class="notif.type">{{ notif.type }}</span>
            <span class="notifications-time">{{ formatTime(notif.created_at) }}</span>
          </div>
          <h3>{{ notif.title }}</h3>
          <p>{{ notif.message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import db from '../services/db.js'
import api from '../services/api.js'
import { isOnline } from '../services/sync.js'
import { showToast } from '../services/toast.js'

const router        = useRouter()
const notifications = ref([])

const unreadCount = computed(() =>
  notifications.value.filter(n => !n.is_read).length
)

const goBack = () => router.back()

onMounted(async () => {
  try {
    if (isOnline()) {
      try {
        const res = await api.get('/notifications/')
        notifications.value = res.data
        await db.notifications.clear()
        await db.notifications.bulkPut(res.data)
      } catch {
        notifications.value = await db.notifications
          .orderBy('created_at').reverse().toArray()
      }
    } else {
      notifications.value = await db.notifications
        .orderBy('created_at').reverse().toArray()
    }
  } catch (err) {
    console.error('[Notifications] Failed to load:', err)
    showToast('Unable to load notifications', 'error')
  }
})

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return (
    date.toLocaleDateString() + ' ' +
    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  )
}

// FIX: Per-click read sync — also calls backend per-notification endpoint
async function markAsRead(notif) {
  if (notif.is_read) return
  notif.is_read = true
  await db.notifications.update(notif.id, { is_read: true })

  if (isOnline()) {
    try {
      await api.post(`/notifications/${notif.id}/read/`)
    } catch {
      // Store pending sync for when reconnected
      await storePendingRead(notif.id)
    }
  } else {
    await storePendingRead(notif.id)
  }
}

async function markAllAsRead() {
  const unread = notifications.value.filter(n => !n.is_read)
  if (unread.length === 0) return

  for (const notif of unread) {
    notif.is_read = true
    await db.notifications.update(notif.id, { is_read: true })
  }

  if (isOnline()) {
    try {
      await api.post('/notifications/read-all/')
    } catch {
      showToast('Offline: read status saved locally', 'info')
      for (const n of unread) await storePendingRead(n.id)
    }
  } else {
    showToast('Offline: read status saved locally', 'info')
    for (const n of unread) await storePendingRead(n.id)
  }
}

async function storePendingRead(id) {
  try {
    const meta    = await db.sync_meta.get('pending_reads')
    const pending = meta?.value || []
    if (!pending.includes(id)) {
      pending.push(id)
      await db.sync_meta.put({ key: 'pending_reads', value: pending })
    }
  } catch { /* silent */ }
}
</script>

<!-- FIX: All styles in external file — no more inline <style> block -->
<style>
@import '../assets/notifications.css';
</style>
