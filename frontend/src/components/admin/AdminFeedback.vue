<template>
  <div class="adminfeedback-section">
    <!-- Header -->
    <div class="section-header">
      <div>
        <h1>Feedback & Ratings</h1>
        <p class="subtitle">View and manage user feedback and ratings</p>
      </div>
      <div class="header-actions">
        <button class="btn-export" @click="exportFeedback">
          <span class="material-icons">download</span>
          Export
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-box">
        <span class="stat-number">{{ stats.total }}</span>
        <span class="stat-label">Total Feedback</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ stats.averageRating }}</span>
        <span class="stat-label">Avg Rating</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ stats.thisWeek }}</span>
        <span class="stat-label">This Week</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ stats.unread }}</span>
        <span class="stat-label">Unread</span>
      </div>
    </div>

    <!-- Rating Distribution -->
    <div class="rating-distribution">
      <h3>Rating Distribution</h3>
      <div class="rating-bars">
        <div v-for="i in 5" :key="i" class="rating-bar-row">
          <span class="star-label">{{ 6 - i }} <span class="material-icons">star</span></span>
          <div class="bar-container">
            <div class="bar" :style="{ width: getRatingPercentage(6 - i) + '%' }"></div>
          </div>
          <span class="count">{{ getRatingCount(6 - i) }}</span>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <span class="material-icons">search</span>
        <input v-model="searchQuery" type="text" placeholder="Search feedback..." />
      </div>
      <select v-model="filterRating" class="filter-select">
        <option value="">All Ratings</option>
        <option value="5">5 Stars</option>
        <option value="4">4 Stars</option>
        <option value="3">3 Stars</option>
        <option value="2">2 Stars</option>
        <option value="1">1 Star</option>
      </select>
      <select v-model="filterStatus" class="filter-select">
        <option value="">All Status</option>
        <option value="unread">Unread</option>
        <option value="read">Read</option>
        <option value="responded">Responded</option>
      </select>
    </div>

    <!-- Feedback List -->
    <div class="feedback-list">
      <div v-for="item in filteredFeedback" :key="item.id" :class="['feedback-card', { 'unread': !item.is_read }]">
        <div class="feedback-header">
          <div class="user-info">
            <span class="material-icons user-avatar">account_circle</span>
            <div class="user-details">
              <span class="user-name">{{ item.user_name || 'Anonymous' }}</span>
              <span class="user-email">{{ item.user_email || 'No email provided' }}</span>
            </div>
          </div>
          <div class="feedback-meta">
            <div class="rating">
              <span v-for="i in 5" :key="i" class="material-icons" :class="{ 'filled': i <= item.rating }">
                {{ i <= item.rating ? 'star' : 'star_border' }}
              </span>
            </div>
            <span class="date">{{ formatDate(item.created_at) }}</span>
          </div>
        </div>
        <div class="feedback-content">
          <p>{{ item.comment }}</p>
        </div>
        <div class="feedback-footer">
          <div class="tags">
            <span v-if="item.category" class="tag">{{ item.category }}</span>
            <span :class="['status-tag', 'status-' + (item.is_responded ? 'responded' : item.is_read ? 'read' : 'unread')]">
              {{ item.is_responded ? 'Responded' : item.is_read ? 'Read' : 'Unread' }}
            </span>
          </div>
          <div class="actions">
            <button v-if="!item.is_read" class="btn-action" @click="markAsRead(item)">
              <span class="material-icons">mark_email_read</span>
              Mark Read
            </button>
            <button class="btn-action" @click="showResponseModal(item)">
              <span class="material-icons">reply</span>
              Respond
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredFeedback.length === 0" class="empty-state">
      <span class="material-icons">rate_review</span>
      <p>No feedback found</p>
    </div>

    <!-- Response Modal -->
    <div v-if="showResponseModalFlag" class="modal-overlay" @click.self="closeResponseModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>Respond to Feedback</h2>
          <button class="btn-close" @click="closeResponseModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="original-feedback">
            <div class="rating-display">
              <span v-for="i in 5" :key="i" class="material-icons" :class="{ 'filled': i <= currentFeedback.rating }">
                {{ i <= currentFeedback.rating ? 'star' : 'star_border' }}
              </span>
            </div>
            <p class="feedback-text">{{ currentFeedback.comment }}</p>
            <p class="feedback-author">— {{ currentFeedback.user_name || 'Anonymous' }}</p>
          </div>
          <div class="form-group">
            <label>Your Response</label>
            <textarea v-model="responseText" rows="4" placeholder="Type your response..."></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeResponseModal">Cancel</button>
          <button class="btn-primary" @click="sendResponse">Send Response</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'
import { useAuthStore } from '../../stores/authStore.js'

const auth = useAuthStore()
const feedback = ref([])
const searchQuery = ref('')
const filterRating = ref('')
const filterStatus = ref('')
const showResponseModalFlag = ref(false)
const currentFeedback = ref(null)
const responseText = ref('')

const stats = computed(() => {
  const total = feedback.value.length
  const sum = feedback.value.reduce((acc, f) => acc + f.rating, 0)
  const averageRating = total > 0 ? (sum / total).toFixed(1) : '0.0'
  
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  const thisWeek = feedback.value.filter(f => new Date(f.created_at) > oneWeekAgo).length
  
  const unread = feedback.value.filter(f => !f.is_read).length
  
  return { total, averageRating, thisWeek, unread }
})

const filteredFeedback = computed(() => {
  return feedback.value.filter(f => {
    const matchesSearch = !searchQuery.value || 
      (f.comment?.toLowerCase().includes(searchQuery.value.toLowerCase())) ||
      (f.user_name?.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    const matchesRating = !filterRating.value || f.rating === parseInt(filterRating.value)
    
    const matchesStatus = !filterStatus.value || 
      (filterStatus.value === 'unread' ? !f.is_read :
       filterStatus.value === 'read' ? (f.is_read && !f.is_responded) :
       filterStatus.value === 'responded' ? f.is_responded : true)
    
    return matchesSearch && matchesRating && matchesStatus
  })
})

function getRatingCount(rating) {
  return feedback.value.filter(f => f.rating === rating).length
}

function getRatingPercentage(rating) {
  const count = getRatingCount(rating)
  return feedback.value.length > 0 ? (count / feedback.value.length * 100) : 0
}

function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

function showResponseModal(item) {
  currentFeedback.value = item
  responseText.value = ''
  showResponseModalFlag.value = true
}

function closeResponseModal() {
  showResponseModalFlag.value = false
  currentFeedback.value = null
  responseText.value = ''
}

// Check permissions - allow if user can view all OR department-level feedback
const canViewFeedback = computed(() => auth.canViewAllFeedback || auth.canViewDeptFeedback)

async function loadFeedback() {
  if (!canViewFeedback.value) {
    console.warn('[AdminFeedback] User lacks permission to view feedback')
    feedback.value = []
    return
  }

  try {
    // Use department filter if user only has dept-level permission
    const endpoint = auth.canViewAllFeedback
      ? '/feedback/'
      : `/feedback/?department=${auth.department}`
    const response = await api.get(endpoint)
    feedback.value = response.data
  } catch (e) {
    console.error('Failed to load feedback:', e)
    // Mock data
    feedback.value = [
      { id: 1, user_name: 'John Doe', user_email: 'john@student.edu', rating: 5, comment: 'The app is really helpful for finding my way around campus! Love the map feature.', category: 'App Experience', is_read: true, is_responded: true, created_at: new Date(Date.now() - 86400000).toISOString() },
      { id: 2, user_name: 'Jane Smith', user_email: 'jane@student.edu', rating: 4, comment: 'Great app, but would love to see more detailed room information.', category: 'Feature Request', is_read: true, is_responded: false, created_at: new Date(Date.now() - 172800000).toISOString() },
      { id: 3, user_name: 'Mike Johnson', user_email: null, rating: 5, comment: 'The navigation feature is brilliant! Makes finding rooms so much easier.', category: 'App Experience', is_read: false, is_responded: false, created_at: new Date(Date.now() - 200000).toISOString() },
      { id: 4, user_name: 'Sarah Lee', user_email: 'sarah@student.edu', rating: 3, comment: 'Good concept but the map can be slow to load sometimes.', category: 'Performance', is_read: true, is_responded: false, created_at: new Date(Date.now() - 259200000).toISOString() },
      { id: 5, rating: 2, comment: 'Had trouble finding the library. Needs better navigation.', category: 'Navigation', is_read: false, is_responded: false, created_at: new Date(Date.now() - 345600000).toISOString() }
    ]
  }
}

async function markAsRead(item) {
  try {
    await api.patch(`/feedback/${item.id}/`, { is_read: true })
    item.is_read = true
  } catch (e) {
    console.error('Failed to mark as read:', e)
    item.is_read = true
  }
}

async function sendResponse() {
  try {
    await api.post(`/feedback/${currentFeedback.value.id}/respond/`, { response: responseText.value })
    currentFeedback.value.is_responded = true
    currentFeedback.value.is_read = true
    closeResponseModal()
  } catch (e) {
    console.error('Failed to send response:', e)
    showToast('Failed to send response', 'error')
  }
}

function exportFeedback() {
  const csv = [
    ['Date', 'User', 'Email', 'Rating', 'Category', 'Comment', 'Status'],
    ...feedback.value.map(f => [
      new Date(f.created_at).toISOString(),
      f.user_name || 'Anonymous',
      f.user_email || '',
      f.rating,
      f.category || '',
      f.comment,
      f.is_responded ? 'Responded' : f.is_read ? 'Read' : 'Unread'
    ])
  ].map(row => row.join(',')).join('\n')

  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `feedback-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(loadFeedback)
</script>

<style scoped>
.adminfeedback-section { padding: 0; font-family: var(--font-primary); max-width: 1400px; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-export {
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

.btn-export:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  padding: 14px 20px;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  min-width: 100px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.rating-distribution {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 20px;
  margin-bottom: 20px;
}

.rating-distribution h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 16px 0;
}

.rating-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rating-bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.star-label {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  min-width: 50px;
}

.star-label .material-icons {
  font-size: 16px;
  color: var(--color-primary);
}

.bar-container {
  flex: 1;
  height: 8px;
  background: var(--color-surface);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.bar {
  height: 100%;
  background: var(--color-primary);
  border-radius: var(--radius-full);
  transition: width 0.3s ease;
}

.count {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  min-width: 30px;
  text-align: right;
}

.filters-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  max-width: 400px;
  padding: 10px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.search-box .material-icons {
  font-size: 20px;
  color: var(--color-text-hint);
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  outline: none;
}

.filter-select {
  padding: 10px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  min-width: 140px;
  cursor: pointer;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feedback-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  padding: 20px;
  transition: all 0.2s ease;
}

.feedback-card.unread {
  border-left: 3px solid var(--color-primary);
  background: linear-gradient(90deg, var(--color-primary-light) 0%, var(--color-bg) 100%);
}

.feedback-card:hover {
  box-shadow: var(--shadow-sm);
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  font-size: 40px;
  color: var(--color-text-hint);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: var(--color-text-primary);
}

.user-email {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.feedback-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.rating {
  display: flex;
  gap: 2px;
}

.rating .material-icons {
  font-size: 18px;
  color: var(--color-border);
}

.rating .material-icons.filled {
  color: var(--color-primary);
}

.date {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
}

.feedback-content {
  margin-bottom: 16px;
}

.feedback-content p {
  font-size: var(--text-base);
  color: var(--color-text-primary);
  line-height: 1.5;
  margin: 0;
}

.feedback-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.tags {
  display: flex;
  gap: 8px;
}

.tag {
  padding: 4px 10px;
  background: var(--color-surface);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.status-tag {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
}

.status-unread { background: var(--color-primary-light); color: var(--color-primary); }
.status-read { background: var(--color-surface-2); color: var(--color-text-secondary); }
.status-responded { background: var(--color-success-bg); color: var(--color-success); }

.actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-family: var(--font-primary);
  font-size: var(--text-xs);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-action .material-icons {
  font-size: 16px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  color: var(--color-text-hint);
}

.empty-state .material-icons {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-dialog {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.btn-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-hint);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.modal-body {
  padding: 24px;
}

.original-feedback {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-bottom: 20px;
}

.rating-display {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
}

.rating-display .material-icons {
  font-size: 20px;
  color: var(--color-border);
}

.rating-display .material-icons.filled {
  color: var(--color-primary);
}

.feedback-text {
  font-size: var(--text-base);
  color: var(--color-text-primary);
  line-height: 1.5;
  margin: 0 0 8px 0;
  font-style: italic;
}

.feedback-author {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin: 0;
  text-align: right;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.form-group textarea {
  width: 100%;
  padding: 12px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  outline: none;
  resize: vertical;
  min-height: 100px;
}

.form-group textarea:focus {
  border-color: var(--color-primary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.btn-secondary {
  padding: 10px 20px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--color-surface);
}

.btn-primary {
  padding: 10px 20px;
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}
</style>
