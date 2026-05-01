<template>
  <div class="adminannouncements-section">
    <h1>Announcements</h1>
    
    <div class="adminannouncements-form" v-if="auth.canPostAnnouncement">
      <h2>{{ willPublishDirectly ? 'Publish Announcement' : 'Submit for Approval' }}</h2>
      <input v-model="newTitle" placeholder="Title" class="tp-input" />
      <textarea v-model="newContent" placeholder="Content" class="tp-textarea" rows="4"></textarea>
      <select v-model="newScope" class="tp-select">
        <option value="campus_wide">Entire Campus</option>
        <option value="all_college">All College Students</option>
        <option value="basic_ed_only">Basic Education Only</option>
        <option value="department">My Department Only</option>
        <option value="specific_users">Specific Users (by name/ID)</option>
      </select>
      <!-- User Picker for Specific Users -->
      <div v-if="newScope === 'specific_users'" class="tp-users-picker">
        <label>Select Recipients:</label>
        
        <!-- Search Input -->
        <div class="tp-search-wrapper">
          <input 
            v-model="userSearchQuery" 
            @input="searchUsers"
            placeholder="Search users by name or username..." 
            class="tp-input tp-search-input"
            autocomplete="off"
          />
          <span class="tp-search-icon material-icons">search</span>
        </div>
        
        <!-- Search Results Dropdown -->
        <div v-if="searchResults.length > 0 && showSearchResults" class="tp-search-results">
          <div 
            v-for="user in searchResults" 
            :key="user.id"
            @click="selectUser(user)"
            class="tp-user-option"
          >
            <div class="tp-user-info">
              <strong>{{ user.display_name || user.username }}</strong>
              <small>({{ user.username }}) - {{ getRoleLabel(user.role) }}</small>
            </div>
            <span class="material-icons tp-add-icon">add_circle</span>
          </div>
        </div>
        
        <!-- Selected Users Chips -->
        <div v-if="selectedUsers.length > 0" class="tp-selected-users">
          <span class="tp-selected-label">Selected ({{ selectedUsers.length }}):</span>
          <div class="tp-chips-container">
            <div 
              v-for="user in selectedUsers" 
              :key="user.id"
              class="tp-user-chip"
            >
              <span class="tp-chip-name">{{ user.display_name || user.username }}</span>
              <button @click="removeUser(user)" class="tp-chip-remove" title="Remove">
                <span class="material-icons">close</span>
              </button>
            </div>
          </div>
        </div>
        
        <small v-else class="tp-hint">Click on users from search results to add them</small>
      </div>
      <button @click="submitAnnouncement" class="adminannouncements-btn-primary">
        {{ willPublishDirectly ? 'Publish Now' : 'Submit for Approval' }}
      </button>
      <p v-if="!willPublishDirectly" class="tp-info">
        This will be submitted to the {{ auth.user?.role === 'dean' ? 'Super Admin' : (auth.user?.role === 'program_head' ? 'Dean or Super Admin' : 'Super Admin') }} for approval before it goes live.
      </p>
    </div>

    <h2>My Announcements</h2>
    <div v-if="myAnnouncements.length === 0" class="tp-empty">No announcements yet.</div>
    <div v-for="a in myAnnouncements" :key="a.id" class="adminannouncements-card">
      <span :class="['adminannouncements-status-badge', 'adminannouncements-status-' + a.status]">{{ formatStatus(a.status) }}</span>
      
      <!-- Edit Mode -->
      <div v-if="editingId === a.id">
        <input v-model="editTitle" class="tp-input" placeholder="Title" />
        <textarea v-model="editContent" class="tp-textarea" rows="3" placeholder="Content"></textarea>
        <select v-model="editScope" class="tp-select">
          <option value="campus_wide">Entire Campus</option>
          <option value="all_college">All College Students</option>
          <option value="basic_ed_only">Basic Education Only</option>
          <option value="department">My Department Only</option>
          <option value="specific_users">Specific Users (by name/ID)</option>
        </select>
        <div class="adminannouncements-actions">
          <button @click="saveEdit(a.id)" class="adminannouncements-btn-primary">Save</button>
          <button @click="cancelEdit" class="adminannouncements-btn-secondary">Cancel</button>
        </div>
      </div>
      
      <!-- View Mode -->
      <div v-else>
        <h3>{{ a.title }}</h3>
        <p>{{ a.content }}</p>
        <p v-if="a.rejection_note" class="adminannouncements-rejection-note">Rejected: {{ a.rejection_note }}</p>
        <p v-if="a.scope === 'specific_users'" class="tp-target-users">
          <strong>To:</strong> {{ Array.isArray(a.target_users) ? a.target_users.join(', ') : a.target_users }}
        </p>
        <small>{{ formatTime(a.created_at) }}</small>
        
        <!-- Edit and Delete actions -->
        <div class="adminannouncements-card-actions">
          <button @click="startEdit(a)" class="adminannouncements-btn-icon" title="Edit">
            <span class="material-icons">edit</span>
          </button>
          <button @click="deleteAnnouncement(a.id)" class="adminannouncements-btn-icon delete" title="Delete">
            <span class="material-icons">delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/authStore.js'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'

const auth = useAuthStore()
const emit = defineEmits(['my-pending'])

const newTitle = ref('')
const newContent = ref('')
const newScope = ref('campus_wide')
const newTargetUsers = ref('')
const myAnnouncements = ref([])

// User picker state
const userSearchQuery = ref('')
const searchResults = ref([])
const showSearchResults = ref(false)
const selectedUsers = ref([])
let searchTimeout = null

// Edit mode state
const editingId = ref(null)
const editTitle = ref('')
const editContent = ref('')
const editScope = ref('campus_wide')

const willPublishDirectly = computed(() => {
  if (auth.user?.role === 'super_admin') return true
  if (auth.user?.role === 'dean' && newScope.value === 'department') return true
  return false
})

function formatStatus(status) {
  const labels = {
    'pending_approval': 'Awaiting Approval',
    'published': 'Published',
    'rejected': 'Rejected',
    'archived': 'Archived'
  }
  return labels[status] || status
}

function formatTime(ts) {
  if (!ts) return ''
  return new Date(ts).toLocaleString()
}

async function loadMyAnnouncements() {
  try {
    const r = await api.get('/announcements/mine/')
    myAnnouncements.value = r.data
    const pending = r.data.filter(a => a.status === 'pending_approval').length
    emit('my-pending', pending)
  } catch (e) {
    console.error('Failed to load announcements:', e)
  }
}

async function searchUsers() {
  if (!userSearchQuery.value.trim()) {
    searchResults.value = []
    showSearchResults.value = false
    return
  }
  
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(async () => {
    try {
      const r = await api.get(`/users/?search=${encodeURIComponent(userSearchQuery.value)}&limit=10`)
      // Filter out already selected users
      const selectedIds = selectedUsers.value.map(u => u.id)
      searchResults.value = r.data.filter(u => !selectedIds.includes(u.id))
      showSearchResults.value = searchResults.value.length > 0
    } catch (e) {
      console.error('Failed to search users:', e)
    }
  }, 300)
}

function selectUser(user) {
  if (!selectedUsers.value.find(u => u.id === user.id)) {
    selectedUsers.value.push(user)
  }
  userSearchQuery.value = ''
  searchResults.value = []
  showSearchResults.value = false
}

function removeUser(user) {
  selectedUsers.value = selectedUsers.value.filter(u => u.id !== user.id)
}

function getRoleLabel(role) {
  const labels = {
    'super_admin': 'Super Admin',
    'dean': 'Dean',
    'program_head': 'Program Head',
    'basic_ed_head': 'Basic Ed Head',
    'student': 'Student',
    'college_student': 'College Student',
    'basic_ed_student': 'Basic Ed Student',
    'faculty': 'Faculty',
    'staff': 'Staff'
  }
  return labels[role] || role
}

async function submitAnnouncement() {
  if (!newTitle.value || !newContent.value) return
  
  // Get target users for specific_users scope
  let targetUsers = []
  if (newScope.value === 'specific_users') {
    targetUsers = selectedUsers.value.map(u => u.username)
    if (targetUsers.length === 0) {
      showToast('Please select at least one recipient', 'error')
      return
    }
  }
  
  try {
    await api.post('/announcements/create/', {
      title: newTitle.value,
      content: newContent.value,
      scope: newScope.value,
      target_users: targetUsers
    })
    newTitle.value = ''
    newContent.value = ''
    newScope.value = 'campus_wide'
    newTargetUsers.value = ''
    selectedUsers.value = []
    userSearchQuery.value = ''
    await loadMyAnnouncements()
    showToast('Announcement submitted successfully!', 'success')
  } catch (e) {
    console.error('Failed to submit:', e)
    showToast('Failed to submit announcement', 'error')
  }
}

function startEdit(announcement) {
  editingId.value = announcement.id
  editTitle.value = announcement.title
  editContent.value = announcement.content
  editScope.value = announcement.scope || 'campus_wide'
}

function cancelEdit() {
  editingId.value = null
  editTitle.value = ''
  editContent.value = ''
  editScope.value = 'campus_wide'
}

async function saveEdit(id) {
  if (!editTitle.value || !editContent.value) return
  try {
    await api.put(`/announcements/${id}/`, {
      title: editTitle.value,
      content: editContent.value,
      scope: editScope.value
    })
    showToast('Announcement updated successfully', 'success')
    cancelEdit()
    await loadMyAnnouncements()
  } catch (e) {
    console.error('Failed to update:', e)
    showToast('Failed to update announcement', 'error')
  }
}

async function deleteAnnouncement(id) {
  if (!confirm('Are you sure you want to delete this announcement?')) return
  try {
    await api.delete(`/announcements/${id}/`)
    showToast('Announcement deleted', 'success')
    await loadMyAnnouncements()
  } catch (e) {
    console.error('Failed to delete:', e)
    showToast('Failed to delete announcement', 'error')
  }
}

onMounted(loadMyAnnouncements)
</script>

<style scoped>
.adminannouncements-section { padding: 20px; font-family: var(--font-primary); }
.adminannouncements-form { background: var(--color-surface); padding: 20px; border-radius: var(--radius-md); margin-bottom: 24px; }
.adminannouncements-form h2 { margin-bottom: 16px; }
.tp-input, .tp-textarea, .tp-select { 
  display: block; width: 100%; margin-bottom: 12px; padding: 10px; 
  border: 1px solid var(--color-border); border-radius: var(--radius-sm);
  font-family: var(--font-primary); font-size: var(--text-base);
}
/* User Picker Styles */
.tp-users-picker {
  background: var(--color-bg);
  padding: 16px;
  border-radius: var(--radius-md);
  margin-bottom: 12px;
  border: 1px solid var(--color-border);
}

.tp-users-picker label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 10px;
}

.tp-search-wrapper {
  position: relative;
  margin-bottom: 12px;
}

.tp-search-input {
  padding-right: 40px !important;
  margin-bottom: 0 !important;
}

.tp-search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-hint);
  font-size: 20px;
}

.tp-search-results {
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.tp-user-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border-light);
  transition: background 0.2s;
}

.tp-user-option:hover {
  background: var(--color-primary-light);
}

.tp-user-option:last-child {
  border-bottom: none;
}

.tp-user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tp-user-info strong {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.tp-user-info small {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.tp-add-icon {
  color: var(--color-success);
  font-size: 24px;
}

.tp-selected-users {
  margin-top: 12px;
}

.tp-selected-label {
  display: block;
  font-size: var(--text-xs);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.tp-chips-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tp-user-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--color-primary-light);
  color: var(--color-primary);
  padding: 6px 12px;
  border-radius: 20px;
  font-size: var(--text-sm);
  font-weight: 500;
}

.tp-chip-name {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tp-chip-remove {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.tp-chip-remove:hover {
  background: rgba(0,0,0,0.1);
}

.tp-chip-remove .material-icons {
  font-size: 16px;
}

.tp-hint {
  color: var(--color-text-hint);
  font-size: var(--text-xs);
  display: block;
  margin-top: 8px;
}

/* Display target users in card */
.tp-target-users {
  margin: 8px 0;
  padding: 8px 12px;
  background: var(--color-primary-light);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}
.adminannouncements-btn-primary { 
  background: var(--color-primary); color: white; border: none; 
  padding: 12px 24px; border-radius: var(--radius-md); cursor: pointer;
  font-family: var(--font-primary); font-size: var(--text-base); min-height: 44px;
}
.adminannouncements-btn-primary:hover { background: var(--color-primary-dark); }
.tp-info { color: var(--color-text-secondary); font-size: var(--text-sm); margin-top: 8px; }
.tp-empty { color: var(--color-text-hint); padding: 20px; text-align: center; }
.adminannouncements-card { 
  background: var(--color-bg); border: 1px solid var(--color-border); 
  padding: 16px; border-radius: var(--radius-md); margin-bottom: 12px; 
}
.adminannouncements-card h3 { margin-bottom: 8px; }
.adminannouncements-status-badge { 
  display: inline-block; padding: 2px 8px; border-radius: var(--radius-full); 
  font-size: var(--text-xs); font-weight: 600; margin-bottom: 8px;
}
.adminannouncements-status-pending_approval { background: #FFF8E1; color: #E65100; }
.adminannouncements-status-published { background: #E8F5E9; color: #1B5E20; }
.adminannouncements-status-rejected { background: #FFEBEE; color: #B71C1C; }
.adminannouncements-status-archived { background: #ECEFF1; color: #263238; }
.adminannouncements-rejection-note { background: #FFEBEE; padding: 8px; border-radius: var(--radius-sm); color: #B71C1C; margin-top: 8px; }

.adminannouncements-card-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.adminannouncements-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.adminannouncements-btn-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: none;
  background: var(--color-surface);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.adminannouncements-btn-icon:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.adminannouncements-btn-icon.delete:hover {
  background: #FFEBEE;
  color: #C62828;
}

.adminannouncements-btn-secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: var(--font-primary);
  font-size: var(--text-base);
  min-height: 44px;
}

.adminannouncements-btn-secondary:hover {
  background: var(--color-bg);
}
</style>
