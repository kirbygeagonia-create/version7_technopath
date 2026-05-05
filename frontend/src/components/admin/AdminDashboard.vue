<template>
  <div class="admindashboard-section">
    <!-- Header -->
    <div class="dashboard-header">
      <div>
        <h1>Dashboard</h1>
        <p class="dashboard-subtitle">Welcome back, {{ auth.displayName }}</p>
      </div>
      <div class="dashboard-actions">
        <button class="btn-refresh" @click="loadDashboardData">
          <span class="material-icons">refresh</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card stat-primary">
        <div class="stat-icon">
          <span class="material-icons">campaign</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalAnnouncements }}</div>
          <div class="stat-label">Total Announcements</div>
        </div>
      </div>

      <div class="stat-card stat-success">
        <div class="stat-icon">
          <span class="material-icons">people</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-label">Active Users</div>
        </div>
      </div>

      <div class="stat-card stat-info">
        <div class="stat-icon">
          <span class="material-icons">star</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.newFeedback }}</div>
          <div class="stat-label">New Feedback</div>
        </div>
      </div>

      <div class="stat-card stat-warning">
        <div class="stat-icon">
          <span class="material-icons">business</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalBuildings }}</div>
          <div class="stat-label">Buildings</div>
        </div>
      </div>

      <div class="stat-card stat-purple">
        <div class="stat-icon">
          <span class="material-icons">meeting_room</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalRooms }}</div>
          <div class="stat-label">Rooms</div>
        </div>
      </div>

      <div class="stat-card stat-orange">
        <div class="stat-icon">
          <span class="material-icons">route</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalPaths }}</div>
          <div class="stat-label">Navigation Paths</div>
        </div>
      </div>

      <div class="stat-card stat-teal">
        <div class="stat-icon">
          <span class="material-icons">chat</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalChatLogs }}</div>
          <div class="stat-label">Chat Interactions</div>
        </div>
      </div>

      <div class="stat-card stat-pink">
        <div class="stat-icon">
          <span class="material-icons">help</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.totalFAQs }}</div>
          <div class="stat-label">FAQ Entries</div>
        </div>
      </div>
    </div>

    <!-- Data Visualization Chart -->
    <div class="panel-card data-chart">
      <h2>
        <span class="material-icons">analytics</span>
        System Data Overview
        <span class="chart-total-badge">Total: {{ totalDataCount }}</span>
      </h2>
      <div class="chart-container">
        <div class="bar-chart">
          <div v-for="(item, index) in chartData" :key="index" class="chart-bar-item">
            <div class="chart-label">{{ item.label }}</div>
            <div class="chart-bar-wrapper">
              <div class="chart-bar" :style="{ width: item.percentage + '%', background: item.color }">
                <span class="chart-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="chart-legend">
        <div v-for="(item, index) in chartData" :key="index" class="legend-item">
          <span class="legend-color" :style="{ background: item.color }"></span>
          <span class="legend-label">{{ item.label }}</span>
        </div>
        <div class="legend-item legend-total">
          <span class="legend-total-label">Total Records:</span>
          <span class="legend-total-value">{{ totalDataCount }}</span>
        </div>
      </div>
    </div>

    <!-- Unsynced Paths Warning -->
    <div v-if="localPathsCount > stats.totalPaths" class="panel-card unsynced-warning">
      <h2>
        <span class="material-icons" style="color: var(--color-warning);">warning</span>
        Unsynced Navigation Paths
      </h2>
      <p class="unsynced-message">
        You have <strong>{{ localPathsCount - stats.totalPaths }}</strong> path(s) saved locally that aren't synced to the database.
        Go to <strong>Map Management → SVG Paths</strong> and click "Save" on each path to sync them.
      </p>
      <button class="action-btn" @click="navigateTo('paths')">
        <span class="material-icons">route</span>
        <span>Go to Path Manager</span>
      </button>
    </div>

    <!-- Navigation Paths Detail -->
    <div v-if="pathsData.length > 0" class="panel-card paths-detail">
      <h2>
        <span class="material-icons">route</span>
        Navigation Paths
        <span class="chart-total-badge">{{ pathsData.length }} Paths</span>
      </h2>
      <div class="paths-list">
        <div v-for="path in pathsData" :key="path.id" class="path-item">
          <div class="path-from-to">
            <span class="path-from">{{ path.from_location || path.from || 'Unknown' }}</span>
            <span class="material-icons path-arrow">arrow_forward</span>
            <span class="path-to">{{ path.to_location || path.to || path.name || 'Unknown' }}</span>
          </div>
          <div class="path-meta">
            <span v-if="path.floor" class="path-floor">Floor {{ path.floor }}</span>
            <span v-if="path.element_ids || path.elementIds" class="path-stops">
              {{ (path.element_ids || path.elementIds || []).length }} stops
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- DATA RECORDS SECTION - Shows actual records from all models -->
    <div class="data-records-section">
      <h2 class="section-title">
        <span class="material-icons">storage</span>
        All Data Records
      </h2>

      <!-- Buildings List -->
      <div v-if="buildingsData.length > 0" class="panel-card data-card">
        <h3>
          <span class="material-icons">business</span>
          Buildings ({{ buildingsData.length }})
        </h3>
        <div class="data-list">
          <div v-for="building in buildingsData.slice(0, 5)" :key="building.id" class="data-item">
            <span class="data-name">{{ building.name }}</span>
            <span class="data-type">{{ building.facility_type }}</span>
          </div>
        </div>
        <button v-if="buildingsData.length > 5" class="view-all-btn" @click="navigateTo('facilities')">
          View all {{ buildingsData.length }} buildings →
        </button>
      </div>

      <!-- Rooms List -->
      <div v-if="roomsData.length > 0" class="panel-card data-card">
        <h3>
          <span class="material-icons">meeting_room</span>
          Rooms ({{ roomsData.length }})
        </h3>
        <div class="data-list">
          <div v-for="room in roomsData.slice(0, 5)" :key="room.id" class="data-item">
            <span class="data-name">{{ room.name }}</span>
            <span class="data-type">{{ room.room_type }}</span>
          </div>
        </div>
        <button v-if="roomsData.length > 5" class="view-all-btn" @click="navigateTo('rooms')">
          View all {{ roomsData.length }} rooms →
        </button>
      </div>

      <!-- Users List -->
      <div v-if="usersData.length > 0" class="panel-card data-card">
        <h3>
          <span class="material-icons">people</span>
          Active Users ({{ usersData.length }})
        </h3>
        <div class="data-list">
          <div v-for="user in usersData.slice(0, 5)" :key="user.id" class="data-item">
            <span class="data-name">{{ user.display_name || user.username }}</span>
            <span class="data-type">{{ user.role }}</span>
          </div>
        </div>
        <button v-if="usersData.length > 5" class="view-all-btn" @click="navigateTo('admins')">
          View all {{ usersData.length }} users →
        </button>
      </div>

      <!-- Feedback List -->
      <div v-if="feedbackData.length > 0" class="panel-card data-card">
        <h3>
          <span class="material-icons">feedback</span>
          Recent Feedback ({{ feedbackData.length }})
        </h3>
        <div class="data-list">
          <div v-for="item in feedbackData.slice(0, 5)" :key="item.id" class="data-item">
            <span class="data-name">{{ item.message?.substring(0, 40) || 'No message' }}...</span>
            <span class="data-rating">{{ '⭐'.repeat(item.rating || 0) }}</span>
          </div>
        </div>
        <button v-if="feedbackData.length > 5" class="view-all-btn" @click="navigateTo('feedback')">
          View all {{ feedbackData.length }} feedback →
        </button>
      </div>

      <!-- Chat Logs List -->
      <div v-if="chatLogsData.length > 0" class="panel-card data-card">
        <h3>
          <span class="material-icons">chat</span>
          Recent Chat Interactions ({{ chatLogsData.length }})
        </h3>
        <div class="data-list">
          <div v-for="log in chatLogsData.slice(0, 5)" :key="log.id" class="data-item">
            <span class="data-name">{{ log.user_query?.substring(0, 40) || 'No query' }}...</span>
            <span :class="['data-status', log.is_successful ? 'success' : 'error']">
              {{ log.is_successful ? '✓' : '✗' }} {{ log.mode }}
            </span>
          </div>
        </div>
        <button v-if="chatLogsData.length > 5" class="view-all-btn" @click="navigateTo('faq')">
          View all {{ chatLogsData.length }} chat logs →
        </button>
      </div>

      <!-- FAQs List -->
      <div v-if="faqsData.length > 0" class="panel-card data-card">
        <h3>
          <span class="material-icons">quiz</span>
          FAQ Entries ({{ faqsData.length }})
        </h3>
        <div class="data-list">
          <div v-for="faq in faqsData.slice(0, 5)" :key="faq.id" class="data-item">
            <span class="data-name">{{ faq.question?.substring(0, 50) || 'No question' }}...</span>
            <span class="data-type">{{ faq.category }}</span>
          </div>
        </div>
        <button v-if="faqsData.length > 5" class="view-all-btn" @click="navigateTo('faq')">
          View all {{ faqsData.length }} FAQs →
        </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="content-grid">
      <!-- Quick Actions -->
      <div class="panel-card quick-actions">
        <h2>
          <span class="material-icons">bolt</span>
          Quick Actions
        </h2>
        <div class="actions-list">
          <button v-if="auth.canPostAnnouncement" class="action-btn" @click="navigateTo('announcements')">
            <span class="material-icons">add_circle</span>
            <span>Create Announcement</span>
          </button>
          <button v-if="auth.canSendCampusNotification" class="action-btn" @click="navigateTo('notifications')">
            <span class="material-icons">notifications_active</span>
            <span>Send Notification</span>
          </button>
          <button v-if="auth.canManageFacilities" class="action-btn" @click="navigateTo('facilities')">
            <span class="material-icons">business</span>
            <span>Manage Facilities</span>
          </button>
          <button v-if="auth.canManageAllRooms || auth.canManageOwnRooms" class="action-btn" @click="navigateTo('rooms')">
            <span class="material-icons">meeting_room</span>
            <span>Manage Rooms</span>
          </button>
          <button v-if="auth.canManageFAQ" class="action-btn" @click="navigateTo('faq')">
            <span class="material-icons">smart_toy</span>
            <span>Update FAQ</span>
          </button>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="panel-card recent-activity">
        <h2>
          <span class="material-icons">history</span>
          Recent Activity
        </h2>
        <div v-if="recentActivity.length === 0" class="empty-state">
          <span class="material-icons">inbox</span>
          <p>No recent activity</p>
        </div>
        <div v-else class="activity-list">
          <div v-for="activity in displayedActivities" :key="activity.id" class="activity-item">
            <div class="activity-icon" :class="'activity-' + activity.type">
              <span class="material-icons">{{ activity.icon }}</span>
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.title }}</div>
              <div class="activity-meta">{{ activity.user }} • {{ activity.time }}</div>
            </div>
          </div>
        </div>
        <button 
          v-if="recentActivity.length > 3" 
          class="view-all-btn" 
          @click="showAllActivities = !showAllActivities"
        >
          {{ showAllActivities ? 'Show Less' : `See More (${recentActivity.length - 3})` }}
        </button>
      </div>

      <!-- My Announcements -->
      <div class="panel-card my-announcements" v-if="auth.canPostAnnouncement">
        <h2>
          <span class="material-icons">campaign</span>
          My Announcements
        </h2>
        <div v-if="myAnnouncements.length === 0" class="empty-state">
          <span class="material-icons">campaign</span>
          <p>No announcements yet</p>
        </div>
        <div v-else class="announcement-list">
          <div v-for="ann in myAnnouncements.slice(0, 5)" :key="ann.id" class="announcement-item">
            <span :class="['status-badge', 'status-' + ann.status]">{{ formatStatus(ann.status) }}</span>
            <div class="announcement-title">{{ ann.title }}</div>
            <div class="announcement-date">{{ formatDate(ann.created_at) }}</div>
          </div>
        </div>
        <button v-if="myAnnouncements.length > 5" class="view-all-btn" @click="navigateTo('announcements')">
          View All ({{ myAnnouncements.length }})
        </button>
      </div>

      <!-- System Status -->
      <div class="panel-card system-status">
        <h2>
          <span class="material-icons">monitor_heart</span>
          System Status
        </h2>
        <div class="status-list">
          <div class="status-item">
            <div class="status-label">
              <span class="material-icons">wifi</span>
              API Connection
            </div>
            <div class="status-value">
              <span class="status-dot status-online"></span>
              Online
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">
              <span class="material-icons">storage</span>
              Database
            </div>
            <div class="status-value">
              <span class="status-dot status-online"></span>
              Operational
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">
              <span class="material-icons">cloud_sync</span>
              Sync Status
            </div>
            <div class="status-value">
              <span class="status-dot status-online"></span>
              Synced
            </div>
          </div>
          <div class="status-item">
            <div class="status-label">
              <span class="material-icons">update</span>
              Last Updated
            </div>
            <div class="status-value text-secondary">{{ lastUpdated }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- User Info Card -->
    <div class="user-info-panel">
      <div class="user-avatar">
        <span class="material-icons">account_circle</span>
      </div>
      <div class="user-details">
        <div class="user-name">{{ auth.displayName }}</div>
        <div class="user-role">{{ auth.roleLabel }}</div>
        <div class="user-dept">{{ auth.departmentLabel }}</div>
      </div>
      <div class="user-permissions">
        <div class="permission-tag" v-if="auth.canManageFacilities">Facilities</div>
        <div class="permission-tag" v-if="auth.canManageAllRooms || auth.canManageOwnRooms">Rooms</div>
        <div class="permission-tag" v-if="auth.canManageNavigation">Navigation</div>
        <div class="permission-tag" v-if="auth.canManageFAQ">FAQ</div>
        <div class="permission-tag" v-if="auth.canPostAnnouncement">Announcements</div>
        <div class="permission-tag" v-if="auth.canApproveAnnouncements">Approvals</div>
        <div class="permission-tag" v-if="auth.canManageAdminAccounts">Admin Accounts</div>
        <div class="permission-tag" v-if="auth.canViewAuditLog || auth.canViewDeptAuditLog">Audit Log</div>
        <div class="permission-tag" v-if="auth.canViewAllFeedback || auth.canViewDeptFeedback">Feedback</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/authStore.js'
import api from '../../services/api.js'

const auth = useAuthStore()

const stats = ref({
  totalAnnouncements: 0,
  totalUsers: 0,
  newFeedback: 0,
  totalBuildings: 0,
  totalRooms: 0,
  totalPaths: 0,
  totalChatLogs: 0,
  totalFAQs: 0
})

const myAnnouncements = ref([])
const recentActivity = ref([])
const lastUpdated = ref('Just now')
const showAllActivities = ref(false)
const pathsData = ref([]) // Store paths with destinations for chart
const localPathsCount = ref(0) // Count of localStorage paths

// Data records for detailed view
const buildingsData = ref([])
const roomsData = ref([])
const usersData = ref([])
const feedbackData = ref([])
const chatLogsData = ref([])
const faqsData = ref([])

// Computed property to limit displayed activities
const displayedActivities = computed(() => {
  if (showAllActivities.value) {
    return recentActivity.value
  }
  return recentActivity.value.slice(0, 3)
})

function navigateTo(section) {
  // Emit event or use a global state to navigate
  window.dispatchEvent(new CustomEvent('admin-navigate', { detail: section }))
}

function formatStatus(status) {
  const labels = {
    'pending_approval': 'Pending',
    'published': 'Published',
    'rejected': 'Rejected',
    'archived': 'Archived'
  }
  return labels[status] || status
}

function formatDate(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

async function loadDashboardData() {
  lastUpdated.value = new Date().toLocaleTimeString()
  
  try {
    // Fetch multiple stats in parallel
    const promises = []
    
    // Fetch buildings count and data
    promises.push(
      api.get('/facilities/')
        .then(r => { 
          const data = r.data || []
          stats.value.totalBuildings = data.length
          buildingsData.value = data.slice(0, 10) // Store first 10 for display
        })
        .catch(() => { stats.value.totalBuildings = 0 })
    )
    
    // Fetch rooms count and data
    promises.push(
      api.get('/rooms/')
        .then(r => { 
          const data = r.data || []
          stats.value.totalRooms = data.length
          roomsData.value = data.slice(0, 10)
        })
        .catch(() => { stats.value.totalRooms = 0 })
    )
    
    // Fetch chat logs count and data
    promises.push(
      api.get('/chatbot/logs/')
        .then(r => { 
          const data = r.data || []
          stats.value.totalChatLogs = data.length
          chatLogsData.value = data.slice(0, 10)
        })
        .catch(() => { stats.value.totalChatLogs = 0 })
    )
    
    // Fetch FAQ count and data
    promises.push(
      api.get('/chatbot/faq/')
        .then(r => { 
          const data = r.data || []
          stats.value.totalFAQs = data.length
          faqsData.value = data.slice(0, 10)
        })
        .catch(() => { stats.value.totalFAQs = 0 })
    )
    
    // Fetch navigation paths count and details
    promises.push(
      api.get('/navigation/paths/')
        .then(r => { 
          const paths = r.data || []
          stats.value.totalPaths = Array.isArray(paths) ? paths.length : 0
          pathsData.value = Array.isArray(paths) ? paths : []
          console.log('[Dashboard] API Paths loaded:', stats.value.totalPaths)
          
          // Also check localStorage for unsynced paths
          try {
            const localPaths = JSON.parse(localStorage.getItem('svg_navigation_paths_v2') || '{}')
            localPathsCount.value = Object.keys(localPaths).length
            if (localPathsCount.value > stats.value.totalPaths) {
              console.log('[Dashboard] Found', localPathsCount.value - stats.value.totalPaths, 'unsynced paths in localStorage')
            }
          } catch (e) {
            localPathsCount.value = 0
            console.log('[Dashboard] No localStorage paths found')
          }
        })
        .catch((e) => { 
          console.error('[Dashboard] Failed to load paths from API:', e)
          stats.value.totalPaths = 0 
          pathsData.value = []
        })
    )
    
    if (auth.canPostAnnouncement) {
      promises.push(
        api.get('/announcements/mine/')
          .then(r => { 
            myAnnouncements.value = r.data
            stats.value.totalAnnouncements = r.data.length 
          })
          .catch(() => { stats.value.totalAnnouncements = 0 })
      )
    }
    
    // Fetch real user count and data
    promises.push(
      api.get('/users/')
        .then(r => { 
          const data = r.data || []
          stats.value.totalUsers = data.length
          usersData.value = data.slice(0, 10)
        })
        .catch(() => { stats.value.totalUsers = 0 })
    )
    
    // Fetch real feedback count and data
    if (auth.canViewAllFeedback || auth.canViewDeptFeedback) {
      promises.push(
        api.get('/feedback/')
          .then(r => { 
            const data = r.data || []
            stats.value.newFeedback = data.length
            feedbackData.value = data.slice(0, 10)
          })
          .catch(() => { stats.value.newFeedback = 0 })
      )
    }
    
    // Fetch recent activity from audit log (Super Admin gets all, Dean gets dept only)
    if (auth.canViewAuditLog || auth.canViewDeptAuditLog) {
      promises.push(
        api.get('/users/audit-log/?limit=5')
          .then(r => {
            recentActivity.value = r.data.map(item => ({
              id: item.id,
              type: item.entity_type === 'announcement' ? 'announcement' : 
                    item.entity_type === 'user' ? 'user' : 'feedback',
              icon: item.entity_type === 'announcement' ? 'campaign' : 
                    item.entity_type === 'user' ? 'person_add' : 'star',
              title: `${item.action} ${item.entity_type}`,
              user: item.user || 'System',
              time: formatTimeAgo(new Date(item.created_at))
            }))
          })
          .catch(() => {
            // Fallback to empty activity if audit log fails
            recentActivity.value = []
          })
      )
    }
    
    await Promise.all(promises)
  } catch (e) {
    console.error('Failed to load dashboard data:', e)
  }
}

function formatTimeAgo(date) {
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins} min ago`
  if (diffHours < 24) return `${diffHours} hours ago`
  if (diffDays < 7) return `${diffDays} days ago`
  return date.toLocaleDateString()
}

// Chart data computed property
const chartData = computed(() => {
  const maxVal = Math.max(
    stats.value.totalUsers,
    stats.value.totalBuildings,
    stats.value.totalRooms,
    stats.value.totalPaths,
    stats.value.totalAnnouncements,
    stats.value.newFeedback,
    stats.value.totalChatLogs,
    stats.value.totalFAQs,
    1
  )
  
  const colors = [
    '#4CAF50', '#2196F3', '#FF9800', '#9C27B0', 
    '#F44336', '#00BCD4', '#795548', '#607D8B'
  ]
  
  return [
    { label: 'Users', value: stats.value.totalUsers, percentage: (stats.value.totalUsers / maxVal) * 100, color: colors[0] },
    { label: 'Buildings', value: stats.value.totalBuildings, percentage: (stats.value.totalBuildings / maxVal) * 100, color: colors[1] },
    { label: 'Rooms', value: stats.value.totalRooms, percentage: (stats.value.totalRooms / maxVal) * 100, color: colors[2] },
    { label: 'Paths', value: stats.value.totalPaths, percentage: (stats.value.totalPaths / maxVal) * 100, color: colors[3] },
    { label: 'Announcements', value: stats.value.totalAnnouncements, percentage: (stats.value.totalAnnouncements / maxVal) * 100, color: colors[4] },
    { label: 'Feedback', value: stats.value.newFeedback, percentage: (stats.value.newFeedback / maxVal) * 100, color: colors[5] },
    { label: 'Chat Logs', value: stats.value.totalChatLogs, percentage: (stats.value.totalChatLogs / maxVal) * 100, color: colors[6] },
    { label: 'FAQs', value: stats.value.totalFAQs, percentage: (stats.value.totalFAQs / maxVal) * 100, color: colors[7] }
  ]
})

// Total data count
const totalDataCount = computed(() => {
  return stats.value.totalUsers +
    stats.value.totalBuildings +
    stats.value.totalRooms +
    stats.value.totalPaths +
    stats.value.totalAnnouncements +
    stats.value.newFeedback +
    stats.value.totalChatLogs +
    stats.value.totalFAQs
})

onMounted(loadDashboardData)
</script>

<style scoped>
.admindashboard-section { 
  padding: 24px; 
  font-family: var(--font-primary);
  width: 100%;
  max-width: 100%;
  min-width: 1024px;
  margin: 0 auto;
  box-sizing: border-box;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.dashboard-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.dashboard-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh:hover {
  background: var(--color-surface-2);
  transform: translateY(-1px);
}

.btn-refresh .material-icons {
  font-size: 18px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
  width: 100%;
}

@media (max-width: 1400px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon .material-icons {
  font-size: 28px;
}

.stat-primary .stat-icon { background: var(--color-primary-light); }
.stat-primary .stat-icon .material-icons { color: var(--color-primary); }

.stat-warning .stat-icon { background: var(--color-warning-bg); }
.stat-warning .stat-icon .material-icons { color: var(--color-warning); }

.stat-success .stat-icon { background: var(--color-success-bg); }
.stat-success .stat-icon .material-icons { color: var(--color-success); }

.stat-info .stat-icon { background: var(--color-info-bg); }
.stat-info .stat-icon .material-icons { color: var(--color-info); }

.stat-purple .stat-icon { background: #F3E5F5; }
.stat-purple .stat-icon .material-icons { color: #9C27B0; }

.stat-orange .stat-icon { background: #FFF3E0; }
.stat-orange .stat-icon .material-icons { color: #FF9800; }

.stat-teal .stat-icon { background: #E0F2F1; }
.stat-teal .stat-icon .material-icons { color: #009688; }

.stat-pink .stat-icon { background: #FCE4EC; }
.stat-pink .stat-icon .material-icons { color: #E91E63; }

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-top: 2px;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
  width: 100%;
}

@media (max-width: 1200px) {
  .content-grid {
    grid-template-columns: 1.5fr 1fr;
  }
}

.panel-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.panel-card h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-border);
}

.panel-card h2 .material-icons {
  font-size: 22px;
  color: var(--color-primary);
}

.chart-total-badge {
  margin-left: auto;
  padding: 6px 14px;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 600;
}

.quick-actions {
  grid-column: span 1;
}

.actions-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

@media (max-width: 1200px) {
  .actions-list {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  }
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  white-space: nowrap;
  min-height: 48px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
  width: 100%;
}

.action-btn:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn .material-icons {
  font-size: 20px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
}

.activity-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon .material-icons {
  font-size: 18px;
}

.activity-announcement { background: var(--color-primary-light); }
.activity-announcement .material-icons { color: var(--color-primary); }

.activity-user { background: var(--color-success-bg); }
.activity-user .material-icons { color: var(--color-success); }

.activity-feedback { background: var(--color-info-bg); }
.activity-feedback .material-icons { color: var(--color-info); }

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.activity-meta {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
}

.announcement-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.announcement-item {
  padding: 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--color-border);
}

.announcement-item:hover {
  background: var(--color-surface-2);
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  margin-bottom: 6px;
}

.status-pending_approval { background: var(--color-warning-bg); color: var(--color-warning); }
.status-published { background: var(--color-success-bg); color: var(--color-success); }
.status-rejected { background: var(--color-danger-bg); color: var(--color-danger); }
.status-archived { background: var(--color-surface-2); color: var(--color-text-hint); }

.announcement-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 4px;
  line-height: 1.4;
}

.announcement-date {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
}

.view-all-btn {
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  background: transparent;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: var(--color-primary-light);
  border-style: solid;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
}

.status-item:last-child {
  border-bottom: none;
}

.status-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.status-label .material-icons {
  font-size: 18px;
  color: var(--color-text-hint);
}

.status-value {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
}

.status-online { background: var(--color-success); }
.status-offline { background: var(--color-danger); }

.text-secondary {
  color: var(--color-text-hint);
  font-weight: 400;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: var(--color-text-hint);
}

.empty-state .material-icons {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-state p {
  font-size: var(--text-sm);
  margin: 0;
}

.user-info-panel {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-bg) 100%);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
}

.user-avatar {
  width: 56px;
  height: 56px;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar .material-icons {
  font-size: 32px;
  color: white;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.user-role {
  font-size: var(--text-sm);
  color: var(--color-primary);
  font-weight: 500;
}

.user-dept {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.user-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-width: 300px;
}

.permission-tag {
  padding: 4px 10px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

/* Data Chart */
.data-chart {
  margin-bottom: 24px;
}

.chart-container {
  padding: 20px 0;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-label {
  width: 100px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  text-align: right;
  flex-shrink: 0;
}

.chart-bar-wrapper {
  flex: 1;
  height: 32px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.chart-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  border-radius: var(--radius-md);
  transition: width 0.5s ease;
  min-width: 40px;
}

.chart-value {
  font-size: var(--text-sm);
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0,0,0,0.2);
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
}

.legend-label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.legend-total {
  margin-left: auto;
  padding: 4px 12px;
  background: var(--color-surface);
  border: 2px solid var(--color-primary);
  border-radius: var(--radius-md);
  font-weight: 600;
}

.legend-total-label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.legend-total-value {
  font-size: var(--text-sm);
  color: var(--color-primary);
  font-weight: 700;
  margin-left: 4px;
}

/* Unsynced Warning */
.unsynced-warning {
  margin-bottom: 24px;
  background: linear-gradient(135deg, #FFF8E1 0%, #FFF3E0 100%);
  border-color: var(--color-warning);
}

.unsynced-warning h2 {
  color: var(--color-warning-dark);
}

.unsynced-message {
  padding: 16px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.unsynced-message strong {
  color: var(--color-warning-dark);
}

/* Paths Detail Section */
.paths-detail {
  margin-bottom: 24px;
}

.paths-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.path-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 16px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}

.path-item:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.path-from-to {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-sm);
  font-weight: 600;
}

.path-from {
  color: var(--color-text-primary);
}

.path-arrow {
  font-size: 18px;
  color: var(--color-primary);
}

.path-to {
  color: var(--color-primary);
  font-weight: 700;
}

.path-meta {
  display: flex;
  gap: 12px;
  font-size: var(--text-xs);
  color: var(--color-text-hint);
}

.path-floor {
  background: var(--color-secondary-light);
  color: var(--color-secondary);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.path-stops {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Data Records Section */
.data-records-section {
  margin-bottom: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: var(--text-lg);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  padding: 0 4px;
}

.section-title .material-icons {
  color: var(--color-primary);
  font-size: 24px;
}

.data-card {
  margin-bottom: 16px;
}

.data-card h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  padding: 0 0 12px 0;
  border-bottom: 1px solid var(--color-border);
}

.data-card h3 .material-icons {
  color: var(--color-primary);
  font-size: 20px;
}

.data-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px 0;
}

.data-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}

.data-item:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
}

.data-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-type {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
  background: var(--color-bg);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  text-transform: capitalize;
}

.data-rating {
  font-size: var(--text-sm);
}

.data-status {
  font-size: var(--text-xs);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.data-status.success {
  background: var(--color-success-light);
  color: var(--color-success);
}

.data-status.error {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.view-all-btn {
  width: 100%;
  padding: 12px;
  margin-top: 8px;
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: var(--color-primary);
  color: white;
}

@media (max-width: 768px) {
  .admindashboard-section {
    padding: 12px;
    min-width: auto;
  }
  
  .admin-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding-bottom: 16px;
  }
  
  .admin-header h1 {
    font-size: var(--text-xl);
  }
  
  .header-actions {
    width: 100%;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .btn-refresh {
    width: 40px;
    height: 40px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .stat-card {
    padding: 14px;
    gap: 10px;
  }
  
  .stat-icon {
    width: 36px;
    height: 36px;
  }
  
  .stat-icon .material-icons {
    font-size: 18px;
  }
  
  .stat-value {
    font-size: 20px;
  }
  
  .stat-label {
    font-size: 10px;
  }
  
  .panel-card {
    padding: 16px;
  }
  
  .panel-card h2 {
    font-size: var(--text-base);
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .chart-total-badge {
    margin-left: 0;
    font-size: var(--text-xs);
    padding: 4px 10px;
  }
  
  .chart-container {
    padding: 12px 0;
  }
  
  .chart-label {
    width: 60px;
    font-size: 11px;
  }
  
  .chart-bar-wrapper {
    height: 28px;
  }
  
  .chart-value {
    font-size: 11px;
    padding-right: 8px;
  }
  
  .chart-legend {
    gap: 8px;
  }
  
  .legend-item {
    font-size: 10px;
  }
  
  .legend-color {
    width: 10px;
    height: 10px;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .quick-actions {
    grid-column: span 1;
  }
  
  .actions-list {
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }
  
  .action-btn {
    padding: 14px 10px;
    font-size: var(--text-xs);
  }
  
  .action-btn .material-icons {
    font-size: 20px;
  }
  
  .recent-activity,
  .my-announcements,
  .system-status,
  .user-info-panel {
    grid-column: span 1;
  }
  
  .user-header h3 {
    font-size: var(--text-base);
  }
  
  .permission-tag {
    font-size: 9px;
    padding: 3px 8px;
  }
  
  .announcement-item,
  .activity-item {
    padding: 12px;
  }
  
  .announcement-title,
  .activity-title {
    font-size: var(--text-sm);
  }
  
  .announcement-meta,
  .activity-time {
    font-size: 10px;
  }
  
  .legend-total {
    width: 100%;
    margin-top: 8px;
    justify-content: center;
  }
  
  .paths-list {
    max-height: 250px;
  }
  
  .path-item {
    padding: 10px 12px;
  }
  
  .path-from-to {
    font-size: var(--text-xs);
    flex-wrap: wrap;
  }
  
  .path-arrow {
    font-size: 16px;
  }
  
  .path-meta {
    gap: 8px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-value {
    font-size: 18px;
  }
  
  .stat-label {
    font-size: 9px;
  }
  
  .actions-list {
    grid-template-columns: 1fr;
  }
  
  .chart-label {
    width: 50px;
    font-size: 10px;
  }
}
</style>
