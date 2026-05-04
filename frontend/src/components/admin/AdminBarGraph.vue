<template>
  <div class="admin-bar-graph">
    <div class="bar-graph-header">
      <h2>Database Analytics</h2>
      <div class="data-type-selector">
        <select v-model="selectedDataType" class="admin-select">
          <option value="overview">Overview Dashboard</option>
          <option value="announcements">Announcements</option>
          <option value="users">Users</option>
          <option value="feedback">Feedback</option>
          <option value="rooms">Rooms</option>
          <option value="facilities">Facilities</option>
          <option value="paths">Navigation Paths</option>
        </select>
        <button class="admin-btn admin-btn-primary" @click="refreshData">
          <span class="material-icons">refresh</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Overview Cards -->
    <div class="stats-overview">
      <div 
        v-for="stat in currentStats" 
        :key="stat.key"
        class="stat-card"
        :class="{ clickable: stat.clickable }"
        @click="stat.clickable && openCRUDModal(stat)"
      >
        <div class="stat-icon" :style="{ background: stat.color }">
          <span class="material-icons">{{ stat.icon }}</span>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div v-if="stat.clickable" class="edit-hint">
          <span class="material-icons">edit</span>
        </div>
      </div>
    </div>

    <!-- Bar Chart Section -->
    <div class="chart-section">
      <h3>{{ chartTitle }}</h3>
      <div class="bar-chart-container">
        <div 
          v-for="item in chartData" 
          :key="item.label"
          class="bar-item"
          :class="{ clickable: item.clickable }"
          @click="item.clickable && openItemDetail(item)"
        >
          <div class="bar-label">{{ item.label }}</div>
          <div class="bar-wrapper">
            <div 
              class="bar-fill"
              :style="{ 
                width: item.percentage + '%',
                background: item.color || '#2196F3'
              }"
            >
              <span class="bar-value">{{ item.value }}</span>
            </div>
          </div>
          <div v-if="item.clickable" class="bar-actions">
            <button class="icon-btn" @click.stop="editItem(item)" title="Edit">
              <span class="material-icons">edit</span>
            </button>
            <button class="icon-btn" @click.stop="deleteItem(item)" title="Delete">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add New Button -->
    <div class="actions-bar">
      <button class="admin-btn admin-btn-success" @click="openCreateModal">
        <span class="material-icons">add</span>
        Add New {{ singularDataType }}
      </button>
      <button class="admin-btn" @click="exportData">
        <span class="material-icons">download</span>
        Export Data
      </button>
    </div>

    <!-- CRUD Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ modalTitle }}</h3>
          <button class="close-btn" @click="closeModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveItem">
            <div v-for="field in formFields" :key="field.name" class="form-group">
              <label>{{ field.label }}</label>
              <input 
                v-if="field.type === 'text' || field.type === 'number'"
                v-model="formData[field.name]"
                :type="field.type"
                :placeholder="field.placeholder"
                class="admin-input"
                :required="field.required"
              />
              <textarea 
                v-else-if="field.type === 'textarea'"
                v-model="formData[field.name]"
                :placeholder="field.placeholder"
                class="admin-input admin-textarea"
                :required="field.required"
                rows="3"
              ></textarea>
              <select 
                v-else-if="field.type === 'select'"
                v-model="formData[field.name]"
                class="admin-input"
                :required="field.required"
              >
                <option v-for="opt in field.options" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button class="admin-btn" @click="closeModal">Cancel</button>
          <button class="admin-btn admin-btn-primary" @click="saveItem">
            <span class="material-icons">save</span>
            {{ editingId ? 'Update' : 'Create' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content confirm-modal">
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button class="close-btn" @click="cancelDelete">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ deleteItemName }}</strong>?</p>
          <p class="warning-text">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="admin-btn" @click="cancelDelete">Cancel</button>
          <button class="admin-btn admin-btn-danger" @click="confirmDelete">
            <span class="material-icons">delete</span>
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'
import { useAuthStore } from '../../stores/authStore.js'

const auth = useAuthStore()
const selectedDataType = ref('overview')
const loading = ref(false)
const rawData = ref([])

// Modal state
const showModal = ref(false)
const showDeleteConfirm = ref(false)
const editingId = ref(null)
const deleteItemId = ref(null)
const deleteItemName = ref('')
const formData = ref({})

// Data type configurations
const dataConfigs = {
  overview: {
    title: 'Dashboard Overview',
    icon: 'dashboard',
    apiEndpoint: null,
    stats: [
      { key: 'announcements', label: 'Total Announcements', icon: 'campaign', color: '#2196F3', clickable: true },
      { key: 'pending', label: 'Pending Approvals', icon: 'pending_actions', color: '#FF9800', clickable: true },
      { key: 'users', label: 'Active Users', icon: 'people', color: '#4CAF50', clickable: true },
      { key: 'feedback', label: 'New Feedback', icon: 'star', color: '#9C27B0', clickable: true }
    ]
  },
  announcements: {
    title: 'Announcements',
    icon: 'campaign',
    apiEndpoint: '/announcements/',
    stats: [
      { key: 'total', label: 'Total', icon: 'campaign', color: '#2196F3' },
      { key: 'published', label: 'Published', icon: 'check_circle', color: '#4CAF50' },
      { key: 'pending', label: 'Pending', icon: 'schedule', color: '#FF9800' },
      { key: 'rejected', label: 'Rejected', icon: 'cancel', color: '#f44336' }
    ],
    formFields: [
      { name: 'title', label: 'Title', type: 'text', required: true, placeholder: 'Enter title' },
      { name: 'content', label: 'Content', type: 'textarea', required: true, placeholder: 'Enter content' },
      { name: 'status', label: 'Status', type: 'select', required: true, options: [
        { value: 'published', label: 'Published' },
        { value: 'pending', label: 'Pending' },
        { value: 'draft', label: 'Draft' }
      ]}
    ]
  },
  users: {
    title: 'Users',
    icon: 'people',
    apiEndpoint: '/users/',
    stats: [
      { key: 'total', label: 'Total Users', icon: 'people', color: '#2196F3' },
      { key: 'active', label: 'Active', icon: 'check_circle', color: '#4CAF50' },
      { key: 'inactive', label: 'Inactive', icon: 'cancel', color: '#f44336' }
    ],
    formFields: [
      { name: 'email', label: 'Email', type: 'text', required: true, placeholder: 'user@example.com' },
      { name: 'first_name', label: 'First Name', type: 'text', required: true },
      { name: 'last_name', label: 'Last Name', type: 'text', required: true },
      { name: 'is_active', label: 'Active', type: 'select', required: true, options: [
        { value: true, label: 'Yes' },
        { value: false, label: 'No' }
      ]}
    ]
  },
  feedback: {
    title: 'Feedback',
    icon: 'star',
    apiEndpoint: '/feedback/',
    stats: [
      { key: 'total', label: 'Total', icon: 'star', color: '#2196F3' },
      { key: 'unread', label: 'Unread', icon: 'mark_email_unread', color: '#FF9800' },
      { key: 'responded', label: 'Responded', icon: 'reply', color: '#4CAF50' }
    ],
    formFields: [
      { name: 'user_name', label: 'User Name', type: 'text', required: true },
      { name: 'rating', label: 'Rating (1-5)', type: 'number', required: true, placeholder: '5' },
      { name: 'comment', label: 'Comment', type: 'textarea', required: true }
    ]
  },
  rooms: {
    title: 'Rooms',
    icon: 'meeting_room',
    apiEndpoint: '/rooms/',
    stats: [
      { key: 'total', label: 'Total', icon: 'meeting_room', color: '#2196F3' },
      { key: 'classroom', label: 'Classrooms', icon: 'school', color: '#4CAF50' },
      { key: 'lab', label: 'Labs', icon: 'science', color: '#9C27B0' },
      { key: 'active', label: 'Active', icon: 'check_circle', color: '#2196F3' }
    ],
    formFields: [
      { name: 'name', label: 'Room Name', type: 'text', required: true },
      { name: 'type', label: 'Type', type: 'select', required: true, options: [
        { value: 'classroom', label: 'Classroom' },
        { value: 'lab', label: 'Lab' },
        { value: 'office', label: 'Office' },
        { value: 'hall', label: 'Hall' }
      ]},
      { name: 'floor', label: 'Floor', type: 'number', required: true, placeholder: '1' },
      { name: 'is_active', label: 'Active', type: 'select', required: true, options: [
        { value: true, label: 'Yes' },
        { value: false, label: 'No' }
      ]}
    ]
  },
  facilities: {
    title: 'Facilities',
    icon: 'business',
    apiEndpoint: '/facilities/',
    stats: [
      { key: 'total', label: 'Total', icon: 'business', color: '#2196F3' },
      { key: 'active', label: 'Active', icon: 'check_circle', color: '#4CAF50' }
    ],
    formFields: [
      { name: 'name', label: 'Facility Name', type: 'text', required: true },
      { name: 'type', label: 'Type', type: 'select', required: true, options: [
        { value: 'building', label: 'Building' },
        { value: 'amenity', label: 'Amenity' },
        { value: 'service', label: 'Service' }
      ]},
      { name: 'description', label: 'Description', type: 'textarea', required: false }
    ]
  },
  paths: {
    title: 'Navigation Paths',
    icon: 'map',
    apiEndpoint: '/navigation/paths/',
    stats: [
      { key: 'total', label: 'Total Paths', icon: 'map', color: '#2196F3' },
      { key: 'floor1', label: 'Floor 1', icon: 'looks_one', color: '#4CAF50' },
      { key: 'floor2', label: 'Floor 2', icon: 'looks_two', color: '#FF9800' },
      { key: 'other', label: 'Other Floors', icon: 'more', color: '#9C27B0' }
    ],
    formFields: [
      { name: 'name', label: 'Path Name', type: 'text', required: true },
      { name: 'floor', label: 'Floor', type: 'number', required: true, placeholder: '1' },
      { name: 'from', label: 'From Location', type: 'text', required: true },
      { name: 'to', label: 'To Location', type: 'text', required: true }
    ]
  }
}

const config = computed(() => dataConfigs[selectedDataType.value])
const chartTitle = computed(() => config.value.title + ' Statistics')
const singularDataType = computed(() => {
  const type = selectedDataType.value
  if (type === 'overview') return 'Item'
  return type.charAt(0).toUpperCase() + type.slice(1, -1) // Remove 's' from end
})
const modalTitle = computed(() => 
  editingId.value ? `Edit ${singularDataType.value}` : `Create ${singularDataType.value}`
)
const formFields = computed(() => config.value.formFields || [])

const currentStats = computed(() => {
  if (selectedDataType.value === 'overview') {
    return [
      { key: 'announcements', label: 'Total Announcements', value: stats.value.announcements || 0, icon: 'campaign', color: '#2196F3', clickable: true },
      { key: 'pending', label: 'Pending Approvals', value: stats.value.pending || 0, icon: 'pending_actions', color: '#FF9800', clickable: true },
      { key: 'users', label: 'Active Users', value: stats.value.users || 0, icon: 'people', color: '#4CAF50', clickable: true },
      { key: 'feedback', label: 'New Feedback', value: stats.value.feedback || 0, icon: 'star', color: '#9C27B0', clickable: true }
    ]
  }
  
  const typeStats = []
  const statConfig = config.value.stats || []
  
  statConfig.forEach(stat => {
    let value = 0
    if (rawData.value && Array.isArray(rawData.value)) {
      switch(stat.key) {
        case 'total':
          value = rawData.value.length
          break
        case 'published':
          value = rawData.value.filter(i => i.status === 'published').length
          break
        case 'pending':
        case 'unread':
          value = rawData.value.filter(i => i.status === 'pending' || !i.is_read).length
          break
        case 'active':
          value = rawData.value.filter(i => i.is_active !== false).length
          break
        case 'inactive':
          value = rawData.value.filter(i => i.is_active === false).length
          break
        case 'classroom':
          value = rawData.value.filter(i => i.type === 'classroom').length
          break
        case 'lab':
          value = rawData.value.filter(i => i.type === 'lab').length
          break
        case 'responded':
          value = rawData.value.filter(i => i.is_responded).length
          break
        case 'floor1':
          value = rawData.value.filter(i => i.floor === 1).length
          break
        case 'floor2':
          value = rawData.value.filter(i => i.floor === 2).length
          break
        case 'other':
          value = rawData.value.filter(i => i.floor > 2).length
          break
        case 'rejected':
          value = rawData.value.filter(i => i.status === 'rejected').length
          break
      }
    }
    typeStats.push({
      ...stat,
      value,
      clickable: selectedDataType.value !== 'overview'
    })
  })
  
  return typeStats
})

const chartData = computed(() => {
  if (!rawData.value || !Array.isArray(rawData.value)) return []
  
  const maxValue = Math.max(...rawData.value.map(i => 1), 1)
  const colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#f44336', '#00BCD4', '#795548', '#607D8B']
  
  return rawData.value.slice(0, 10).map((item, index) => {
    const value = item.stops || item.elementIds?.length || item.rating || 1
    return {
      label: item.name || item.title || `${singularDataType.value} ${item.id}`,
      value: value,
      percentage: Math.max((value / maxValue) * 100, 5),
      color: colors[index % colors.length],
      id: item.id,
      clickable: true,
      raw: item
    }
  })
})

const stats = ref({
  announcements: 0,
  pending: 0,
  users: 0,
  feedback: 0
})

async function refreshData() {
  loading.value = true
  
  try {
    // Load overview stats
    if (auth.canPostAnnouncement) {
      try {
        const ann = await api.get('/announcements/mine/')
        stats.value.announcements = ann.data.length
      } catch(e) { stats.value.announcements = 0 }
    }
    
    if (auth.canApproveAnnouncements) {
      try {
        const pending = await api.get('/announcements/pending/')
        stats.value.pending = pending.data.length
      } catch(e) { stats.value.pending = 0 }
    }
    
    try {
      const users = await api.get('/users/')
      stats.value.users = users.data.length
    } catch(e) { stats.value.users = 0 }
    
    if (auth.canViewAllFeedback || auth.canViewDeptFeedback) {
      try {
        const feedback = await api.get('/feedback/')
        stats.value.feedback = feedback.data.length
      } catch(e) { stats.value.feedback = 0 }
    }
    
    // Load specific data type
    if (config.value.apiEndpoint) {
      const response = await api.get(config.value.apiEndpoint)
      rawData.value = response.data || []
    }
    
    showToast('Data refreshed successfully', 'success')
  } catch (e) {
    console.error('Failed to refresh data:', e)
    showToast('Failed to refresh data', 'error')
  } finally {
    loading.value = false
  }
}

function openCRUDModal(stat) {
  selectedDataType.value = stat.key === 'pending' ? 'announcements' : stat.key
  refreshData()
}

function openCreateModal() {
  if (selectedDataType.value === 'overview') {
    showToast('Please select a specific data type first', 'warning')
    return
  }
  editingId.value = null
  formData.value = {}
  showModal.value = true
}

function editItem(item) {
  editingId.value = item.id
  formData.value = { ...item.raw }
  showModal.value = true
}

function openItemDetail(item) {
  editItem(item)
}

function closeModal() {
  showModal.value = false
  editingId.value = null
  formData.value = {}
}

async function saveItem() {
  try {
    if (editingId.value) {
      await api.put(`${config.value.apiEndpoint}${editingId.value}/`, formData.value)
      showToast(`${singularDataType.value} updated successfully`, 'success')
    } else {
      await api.post(config.value.apiEndpoint, formData.value)
      showToast(`${singularDataType.value} created successfully`, 'success')
    }
    closeModal()
    refreshData()
  } catch (e) {
    console.error('Failed to save:', e)
    showToast('Failed to save: ' + (e.response?.data?.detail || e.message), 'error')
  }
}

function deleteItem(item) {
  deleteItemId.value = item.id
  deleteItemName.value = item.label
  showDeleteConfirm.value = true
}

function cancelDelete() {
  showDeleteConfirm.value = false
  deleteItemId.value = null
  deleteItemName.value = ''
}

async function confirmDelete() {
  try {
    await api.delete(`${config.value.apiEndpoint}${deleteItemId.value}/`)
    showToast(`${singularDataType.value} deleted successfully`, 'success')
    cancelDelete()
    refreshData()
  } catch (e) {
    console.error('Failed to delete:', e)
    showToast('Failed to delete', 'error')
  }
}

function exportData() {
  const data = rawData.value || []
  const csv = convertToCSV(data)
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${selectedDataType.value}_data.csv`
  a.click()
  window.URL.revokeObjectURL(url)
  showToast('Data exported successfully', 'success')
}

function convertToCSV(data) {
  if (!data.length) return ''
  const headers = Object.keys(data[0]).join(',')
  const rows = data.map(row => 
    Object.values(row).map(v => 
      typeof v === 'string' ? `"${v.replace(/"/g, '""')}"` : v
    ).join(',')
  )
  return [headers, ...rows].join('\n')
}

watch(selectedDataType, () => {
  if (config.value.apiEndpoint) {
    refreshData()
  }
})

onMounted(refreshData)
</script>

<style scoped>
.admin-bar-graph {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100%;
}

.bar-graph-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.bar-graph-header h2 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.data-type-selector {
  display: flex;
  gap: 12px;
  align-items: center;
}

.admin-select {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  min-width: 200px;
}

/* Stats Overview */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

.stat-card.clickable {
  cursor: pointer;
}

.stat-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon .material-icons {
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  line-height: 1;
}

.stat-label {
  font-size: 13px;
  color: #666;
  margin-top: 4px;
}

.edit-hint {
  color: #999;
}

.edit-hint .material-icons {
  font-size: 20px;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.chart-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.bar-chart-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.bar-item.clickable {
  cursor: pointer;
}

.bar-label {
  width: 120px;
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar-wrapper {
  flex: 1;
  height: 36px;
  background: #f0f0f0;
  border-radius: 18px;
  overflow: hidden;
  position: relative;
}

.bar-fill {
  height: 100%;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  transition: width 0.5s ease;
  min-width: 40px;
}

.bar-value {
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.bar-actions {
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s;
}

.bar-item:hover .bar-actions {
  opacity: 1;
}

.icon-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f0f0f0;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: #e0e0e0;
}

.icon-btn .material-icons {
  font-size: 18px;
  color: #666;
}

/* Actions Bar */
.actions-bar {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.confirm-modal {
  max-width: 400px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.close-btn:hover {
  background: #f0f0f0;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.admin-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.admin-input:focus {
  outline: none;
  border-color: #2196F3;
}

.admin-textarea {
  resize: vertical;
  min-height: 80px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #eee;
}

.admin-btn {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.admin-btn:hover {
  background: #f5f5f5;
}

.admin-btn-primary {
  background: #2196F3;
  color: white;
  border-color: #2196F3;
}

.admin-btn-primary:hover {
  background: #1976D2;
}

.admin-btn-success {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.admin-btn-success:hover {
  background: #45a049;
}

.admin-btn-danger {
  background: #f44336;
  color: white;
  border-color: #f44336;
}

.admin-btn-danger:hover {
  background: #d32f2f;
}

.warning-text {
  color: #f44336;
  font-size: 13px;
  margin-top: 8px;
}
</style>
