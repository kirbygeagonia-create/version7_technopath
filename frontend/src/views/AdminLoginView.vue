<template>
  <div class="adminlogin-view">
    <div class="adminlogin-card">
      <h1>TechnoPath Admin</h1>
      <p class="adminlogin-subtitle">SEAIT Campus Guide Administration</p>

      <form @submit.prevent="handleLogin">
        <div class="adminlogin-input-group">
          <label>Username</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="Enter username"
            required
          />
        </div>

        <div class="adminlogin-input-group">
          <label>Password</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="Enter password"
            required
          />
        </div>

        <div v-if="error" class="adminlogin-error-message">
          {{ error }}
        </div>

        <button type="submit" class="adminlogin-btn-primary" :disabled="isLoading">
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <p class="adminlogin-back-link">
        <button class="adminlogin-btn-back-link" @click="goBack">
          <span class="material-icons" style="font-size: 16px; vertical-align: middle;">arrow_back</span>
          Back to app
        </button>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore.js'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

async function handleLogin() {
  error.value = ''
  isLoading.value = true

  try {
    await authStore.login(username.value, password.value)
    router.push('/admin')
  } catch (err) {
    console.error('Login error:', err)
    
    // Fallback: Allow mock login for development/demo when backend is unavailable
    if (err.response?.status === 500 || !err.response) {
      // Check for default admin credentials
      if (username.value === 'admin' && password.value === 'admin123') {
        console.log('Using fallback mock login (backend unavailable)')
        // Set mock user data
        authStore.user = { id: 1, username: 'admin', user_type: 'super_admin' }
        authStore.token = 'mock_token_for_development'
        localStorage.setItem('technopath_token', 'mock_token_for_development')
        localStorage.setItem('technopath_user', JSON.stringify(authStore.user))
        router.push('/admin')
        return
      }
      error.value = 'Server error. Backend may be unavailable. Using default credentials: admin/admin123'
    } else {
      error.value = err.response?.data?.detail || 'Login failed. Please check your credentials.'
    }
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.push('/')
}
</script>

<style>
/* Styles moved to external file: src/assets/adminlogin.css */
@import '../assets/adminlogin.css';
</style>
