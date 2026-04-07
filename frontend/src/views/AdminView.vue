<template>
  <div class="admin-view">
    <!-- Desktop Admin Panel -->
    <div class="admin-panel">
      <!-- Sidebar -->
      <aside class="admin-sidebar">
        <div class="admin-logo">
          <span class="material-icons">admin_panel_settings</span>
          <span>TechnoPath Admin</span>
        </div>
        
        <nav class="admin-nav">
          <a
            v-for="item in allowedMenuItems"
            :key="item.key"
            :class="['admin-nav-item', { active: activeSection === item.key }]"
            @click="activeSection = item.key"
          >
            <span class="material-icons">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </a>
        </nav>

        <div class="admin-user-section">
          <div class="admin-user-info">
            <span class="material-icons">account_circle</span>
            <div class="admin-user-details">
              <span class="admin-username">{{ authStore.user?.username || 'Admin' }}</span>
              <span class="admin-role">{{ authStore.user?.user_type_display || 'Super Admin' }}</span>
            </div>
          </div>
          <button class="admin-logout-btn" @click="logout">
            <span class="material-icons">logout</span>
            Logout
          </button>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="admin-main">
        <!-- Dashboard Section -->
        <AdminDashboard v-if="activeSection === 'dashboard'" />

        <!-- Content Management Section -->
        <AdminContentManagement v-if="activeSection === 'content' && isSuperAdmin" />

        <!-- Reports Section -->
        <AdminReports v-if="activeSection === 'reports' && isSuperAdmin" />

        <!-- Settings Section -->
        <AdminSettings v-if="activeSection === 'settings'" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/authStore.js'
import { useRouter } from 'vue-router'
import AdminDashboard from '../components/AdminDashboard.vue'
import AdminContentManagement from '../components/AdminContentManagement.vue'
import AdminReports from '../components/AdminReports.vue'
import AdminSettings from '../components/AdminSettings.vue'

const authStore = useAuthStore()
const router = useRouter()
const activeSection = ref('dashboard')

const isSuperAdmin = computed(() => authStore.user?.user_type === 'super_admin')
const isDean = computed(() => authStore.user?.user_type === 'dean')
const canManageRooms = computed(() =>
  ['super_admin', 'program_head'].includes(authStore.user?.user_type)
)

// Menu items with icons
const menuItems = [
  { key: 'dashboard', label: 'Dashboard', icon: 'dashboard' },
  { key: 'content', label: 'Content', icon: 'edit_note' },
  { key: 'reports', label: 'Reports', icon: 'assessment' },
  { key: 'settings', label: 'Settings', icon: 'settings' },
]

// Build menu based on role
const allowedMenuItems = computed(() => {
  return menuItems.filter(item => {
    if (item.key === 'content' || item.key === 'reports') {
      return isSuperAdmin.value
    }
    return true
  })
})

function logout() {
  authStore.logout()
  router.push('/admin/login')
}

onMounted(() => {
  if (!authStore.isLoggedIn) {
    router.push('/admin/login')
  }
})
</script>

<style>
/* Styles moved to external file: src/assets/admin.css */
@import '../assets/admin.css';
</style>
