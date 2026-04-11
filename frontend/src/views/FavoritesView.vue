<template>
  <div class="favorites-view">
    <div class="favorites-header">
      <button class="favorites-back-btn" @click="goBack">
        <span class="material-icons">arrow_back</span>
      </button>
      <h1>My Favorites</h1>
      <div class="favorites-spacer"></div>
    </div>

    <div class="favorites-content">
      <div v-if="favorites.length === 0" class="favorites-empty">
        <span class="material-icons favorites-empty-icon">favorite_border</span>
        <h3>No Favorites Yet</h3>
        <p>Save your frequently visited locations for quick access</p>
        <button class="favorites-explore-btn" @click="goToHome">
          <span class="material-icons">explore</span>
          Explore Map
        </button>
      </div>

      <div v-else class="favorites-list">
        <div class="favorites-count">{{ favorites.length }} saved location{{ favorites.length !== 1 ? 's' : '' }}</div>
        <div v-for="favorite in favorites" :key="favorite.id" class="favorites-item">
          <div class="favorites-item-content" @click="goToLocation(favorite)">
            <div class="favorites-item-icon" :class="favorite.type">
              <span class="material-icons">{{ favorite.type === 'facility' ? 'business' : 'meeting_room' }}</span>
            </div>
            <div class="favorites-item-text">
              <div class="favorites-item-title">{{ favorite.name }}</div>
              <div class="favorites-item-subtitle">{{ favorite.description || favorite.type }}</div>
              <div class="favorites-item-date">Added {{ formatDate(favorite.addedAt) }}</div>
            </div>
          </div>
          <button class="favorites-delete-btn" @click.stop="askRemove(favorite.id)" title="Remove from favorites">
            <span class="material-icons">delete_outline</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Proper confirm dialog - no browser confirm() -->
    <ConfirmDialog
      :visible="confirmVisible"
      title="Remove Favorite"
      message="Remove this location from your favorites?"
      type="danger"
      confirm-text="Remove"
      cancel-text="Cancel"
      @confirm="confirmRemove"
      @cancel="confirmVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { showToast } from '../services/toast.js'

const router = useRouter()
const favorites = ref([])
const confirmVisible = ref(false)
const pendingDeleteId = ref(null)

const loadFavorites = () => {
  const saved = localStorage.getItem('tp_favorites')
  favorites.value = saved ? JSON.parse(saved) : []
}

const saveFavorites = () => {
  localStorage.setItem('tp_favorites', JSON.stringify(favorites.value))
}

const askRemove = (id) => {
  pendingDeleteId.value = id
  confirmVisible.value = true
}

const confirmRemove = () => {
  if (pendingDeleteId.value !== null) {
    favorites.value = favorites.value.filter(f => f.id !== pendingDeleteId.value)
    saveFavorites()
    showToast('Location removed from favorites', 'info')
  }
  confirmVisible.value = false
  pendingDeleteId.value = null
}

const goToLocation = (favorite) => {
  sessionStorage.setItem('tp_selected_location', JSON.stringify({ type: favorite.type, name: favorite.name }))
  router.push('/')
}

const formatDate = (dateString) => {
  if (!dateString) return 'recently'
  const date = new Date(dateString)
  const diff = Date.now() - date
  if (diff < 86400000) {
    const h = Math.floor(diff / 3600000)
    return h < 1 ? 'just now' : `${h}h ago`
  }
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}d ago`
  return date.toLocaleDateString()
}

const goBack = () => router.back()
const goToHome = () => router.push('/')

onMounted(loadFavorites)
</script>

<style>
@import '../assets/favorites.css';
</style>
