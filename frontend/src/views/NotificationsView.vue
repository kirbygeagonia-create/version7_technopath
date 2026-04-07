<template>
  <div class="notifications-view">
    <header class="notifications-top-bar">
      <button class="notifications-back-btn" @click="goBack">
        <span class="material-icons">arrow_back</span>
      </button>
      <h1>Notifications</h1>
      <div class="notifications-spacer"></div>
    </header>

    <div class="notifications-main-content">
      <div class="notifications-list">
        <div v-if="notifications.length === 0" class="notifications-empty-state">
          <p>No notifications</p>
        </div>
        
        <div v-for="notif in notifications" :key="notif.id" 
             :class="['notifications-card', notif.type, { 'notifications-unread': !notif.is_read }]">
          <div class="notifications-card-header">
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import db from '../services/db.js'

const router = useRouter()
const notifications = ref([])

const goBack = () => router.back()

onMounted(async () => {
  notifications.value = await db.notifications
    .orderBy('created_at')
    .reverse()
    .toArray()
})

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
</script>

<style>
/* Styles moved to external file: src/assets/notifications.css */
@import '../assets/notifications.css';
</style>
