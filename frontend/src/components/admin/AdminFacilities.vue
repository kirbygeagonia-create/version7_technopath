<template>
  <div class="adminfacilities-section">
    <!-- Header -->
    <div class="section-header">
      <div class="header-title">
        <h1>Facilities Management</h1>
        <p class="subtitle">Manage campus buildings and facilities</p>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-box">
        <span class="stat-number">{{ facilities.length }}</span>
        <span class="stat-label">Total Facilities</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ facilities.filter(f => f.facility_type === 'academic').length }}</span>
        <span class="stat-label">Academic</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ facilities.filter(f => f.facility_type === 'administrative').length }}</span>
        <span class="stat-label">Administrative</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ facilities.filter(f => f.facility_type === 'service' || f.facility_type === 'sports' || f.facility_type === 'dining' || f.facility_type === 'library').length }}</span>
        <span class="stat-label">Facilities</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <span class="material-icons">search</span>
        <input v-model="searchQuery" type="text" placeholder="Search facilities..." />
      </div>
      <select v-model="filterType" class="filter-select">
        <option value="">All Types</option>
        <option value="academic">Academic Building</option>
        <option value="administrative">Administrative</option>
        <option value="library">Library</option>
        <option value="sports">Sports & Recreation</option>
        <option value="dining">Dining</option>
        <option value="service">Service Facility</option>
      </select>
    </div>

    <!-- Add Facility Button -->
    <button class="btn-primary btn-add-inline" @click="showCreateModal = true">
      <span class="material-icons">add_business</span>
      Add Facility
    </button>

    <!-- Facilities Grid -->
    <div class="facilities-grid">
      <div v-for="facility in filteredFacilities" :key="facility.id" class="facility-card">
        <div class="facility-image">
          <span class="material-icons">business</span>
        </div>
        <div class="facility-content">
          <div class="facility-header">
            <h3>{{ facility.name }}</h3>
            <span :class="['type-badge', 'type-' + facility.facility_type]">{{ formatType(facility.facility_type) }}</span>
          </div>
          <p class="facility-code">Code: {{ facility.code }}</p>
          <p class="facility-description">{{ facility.description }}</p>
          <div class="facility-stats">
            <span class="stat">
              <span class="material-icons">meeting_room</span>
              {{ facility.room_count || 0 }} Rooms
            </span>
            <span class="stat">
              <span class="material-icons">layers</span>
              {{ facility.floors || 1 }} Floors
            </span>
          </div>
          <div class="facility-actions">
            <button class="btn-icon" @click="editFacility(facility)" title="Edit">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon" @click="viewRooms(facility)" title="View Rooms">
              <span class="material-icons">meeting_room</span>
            </button>
            <button class="btn-icon btn-danger" @click="confirmDelete(facility)" title="Delete">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredFacilities.length === 0" class="empty-state">
      <span class="material-icons">business</span>
      <p>No facilities found</p>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit Facility' : 'Add New Facility' }}</h2>
          <button class="btn-close" @click="closeModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Facility Name</label>
            <input v-model="form.name" type="text" placeholder="Enter facility name" />
          </div>
          <div class="form-group">
            <label>Room</label>
            <input v-model="form.room" type="text" placeholder="e.g., CL6, Room 101" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Code</label>
              <input v-model="form.code" type="text" placeholder="e.g., BUILD-A" />
            </div>
            <div class="form-group">
              <label>Type</label>
              <select v-model="form.facility_type">
                <option value="academic">Academic Building</option>
                <option value="administrative">Administrative</option>
                <option value="library">Library</option>
                <option value="sports">Sports & Recreation</option>
                <option value="dining">Dining</option>
                <option value="service">Service Facility</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Enter facility description"></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Number of Floors</label>
              <input v-model="form.floors" type="number" min="1" />
            </div>
            <div class="form-group">
              <label>Room Count</label>
              <input v-model="form.room_count" type="number" min="0" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn-primary" @click="saveFacility">
            {{ showEditModal ? 'Save Changes' : 'Create Facility' }}
          </button>
          <button 
            v-if="showEditModal || showCreateModal" 
            class="btn-announce" 
            @click="announceFacilityChange"
            title="Announce this change to users"
          >
            <span class="material-icons">campaign</span>
            Announce
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-dialog modal-sm">
        <div class="modal-header">
          <span class="material-icons modal-icon">warning</span>
          <h2>Delete Facility</h2>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ facilityToDelete?.name }}</strong>?</p>
          <p class="text-muted">This will also delete all associated rooms. This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn-danger" @click="deleteFacility">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'

const facilities = ref([])
const rooms = ref([])
const searchQuery = ref('')
const filterType = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const facilityToDelete = ref(null)

// Room Management
const selectedFacility = ref('')
const newRoomName = ref('')
const newRoomFloor = ref('')

// Announcement
const announcementText = ref('')

const form = ref({
  id: null,
  name: '',
  room: '',
  code: '',
  facility_type: 'academic',
  description: '',
  total_floors: 1,
  room_count: 0
})

const filteredFacilities = computed(() => {
  return facilities.value.filter(f => {
    const matchesSearch = !searchQuery.value || 
      f.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      f.code.toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesType = !filterType.value || f.facility_type === filterType.value
    
    return matchesSearch && matchesType
  })
})

// Rooms filtered by selected facility for management
const facilityRooms = computed(() => {
  if (!selectedFacility.value) return []
  const id = parseInt(selectedFacility.value)
  return rooms.value.filter(r => r.facility === id || r.facility_id === id)
})

// Available floors for selected facility
const availableFloors = computed(() => {
  if (!selectedFacility.value) return []
  return [1, 2, 3, 4]
})

// Handle facility selection - reset room inputs
function onFacilitySelect() {
  newRoomName.value = ''
  newRoomFloor.value = ''
}

// Add a room to facility
async function addRoom() {
  if (!selectedFacility.value || !newRoomName.value.trim()) return
  
  try {
    const roomData = {
      name: newRoomName.value.trim(),
      facility: parseInt(selectedFacility.value),
      floor: parseInt(newRoomFloor.value) || 1,
      is_active: true
    }
    
    await api.post('/rooms/', roomData)
    showToast(`Room "${roomData.name}" added successfully`, 'success')
    
    // Reload rooms
    const roomsRes = await api.get('/rooms/')
    rooms.value = roomsRes.data || []
    
    // Reset inputs
    newRoomName.value = ''
    newRoomFloor.value = ''
  } catch (error) {
    console.error('Failed to add room:', error)
    showToast('Failed to add room', 'error')
  }
}

// Edit a room
async function editRoom(room) {
  const newName = prompt('Enter new room name:', room.name)
  if (!newName || newName === room.name) return
  
  try {
    await api.patch(`/rooms/${room.id}/`, { name: newName })
    showToast(`Room updated to "${newName}"`, 'success')
    
    // Reload rooms
    const roomsRes = await api.get('/rooms/')
    rooms.value = roomsRes.data || []
  } catch (error) {
    console.error('Failed to update room:', error)
    showToast('Failed to update room', 'error')
  }
}

// Delete a room
async function deleteRoom(room) {
  if (!confirm(`Are you sure you want to delete room "${room.name}"?`)) return
  
  try {
    await api.delete(`/rooms/${room.id}/`)
    showToast(`Room "${room.name}" deleted`, 'success')
    
    // Reload rooms
    const roomsRes = await api.get('/rooms/')
    rooms.value = roomsRes.data || []
  } catch (error) {
    console.error('Failed to delete room:', error)
    showToast('Failed to delete room', 'error')
  }
}

// Post announcement
function postAnnouncement() {
  if (!announcementText.value.trim()) return
  
  const message = announcementText.value.trim()
  
  // Emit announcement event
  window.dispatchEvent(new CustomEvent('facility-announcement', { 
    detail: { 
      type: 'announcement',
      message: message,
      timestamp: new Date().toISOString()
    }
  }))
  
  showToast(`Announcement posted: ${message}`, 'success')
  announcementText.value = ''
}

function formatType(type) {
  const labels = {
    'academic': 'Academic',
    'administrative': 'Administrative',
    'library': 'Library',
    'sports': 'Sports',
    'dining': 'Dining',
    'service': 'Service'
  }
  return labels[type] || type
}

function editFacility(facility) {
  form.value = { ...facility }
  showEditModal.value = true
}

function closeModal() {
  showCreateModal.value = false
  showEditModal.value = false
  form.value = { id: null, name: '', room: '', code: '', facility_type: 'academic', description: '', total_floors: 1, room_count: 0 }
}

function confirmDelete(facility) {
  facilityToDelete.value = facility
  showDeleteModal.value = true
}

function viewRooms(facility) {
  window.dispatchEvent(new CustomEvent('admin-navigate', { detail: 'rooms' }))
}

// Announce facility changes
function announceFacilityChange() {
  const action = showCreateModal.value ? 'added' : 'updated'
  const facilityName = form.value.name || 'Unknown Facility'
  const message = `Facility "${facilityName}" has been ${action}.`
  
  // Emit announcement event
  window.dispatchEvent(new CustomEvent('facility-announcement', { 
    detail: { 
      type: action,
      facility: form.value,
      message: message
    }
  }))
  
  showToast(message, 'success')
}

async function loadFacilities() {
  try {
    const [facilitiesRes, roomsRes] = await Promise.all([
      api.get('/facilities/'),
      api.get('/rooms/')
    ])
    facilities.value = facilitiesRes.data
    rooms.value = roomsRes.data || []
  } catch (e) {
    console.error('Failed to load facilities:', e)
    // Mock data
    facilities.value = [
      { id: 1, name: 'Main Academic Building', code: 'MAIN-ACAD', type: 'academic', description: 'Primary academic building with classrooms and lecture halls', floors: 4, room_count: 45 },
      { id: 2, name: 'Science and Technology Center', code: 'SCI-TECH', type: 'academic', description: 'Laboratories and research facilities', floors: 3, room_count: 28 },
      { id: 3, name: 'Administration Building', code: 'ADMIN-BLDG', type: 'admin', description: 'Administrative offices and registrar', floors: 2, room_count: 15 },
      { id: 4, name: 'University Library', code: 'LIB-MAIN', type: 'library', description: 'Main campus library with study areas', floors: 3, room_count: 12 },
      { id: 5, name: 'Student Canteen', code: 'CANTEEN-01', type: 'canteen', description: 'Main dining facility for students', floors: 1, room_count: 3 },
      { id: 6, name: 'Gymnasium', code: 'GYM-01', type: 'facility', description: 'Sports and recreational facility', floors: 1, room_count: 5 }
    ]
  }
}

async function saveFacility() {
  try {
    if (showEditModal.value) {
      await api.put(`/facilities/${form.value.id}/`, form.value)
    } else {
      await api.post('/facilities/', form.value)
    }
    closeModal()
    loadFacilities()
  } catch (e) {
    console.error('Failed to save facility:', e)
    showToast('Failed to save facility', 'error')
  }
}

async function deleteFacility() {
  try {
    await api.delete(`/facilities/${facilityToDelete.value.id}/`)
    showDeleteModal.value = false
    loadFacilities()
  } catch (e) {
    console.error('Failed to delete facility:', e)
  }
}

onMounted(loadFacilities)
</script>

<style scoped>
.adminfacilities-section { padding: 0; font-family: var(--font-primary); max-width: 1400px; }

.section-header {
  margin-bottom: 24px;
}

.header-title {
  flex: 1;
}

.section-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.btn-add-inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  margin-bottom: 24px;
  font-size: var(--text-base);
  font-weight: 600;
  width: auto;
}

.subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0 0 8px 0;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.btn-primary .material-icons {
  font-size: 20px;
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
  min-width: 160px;
  cursor: pointer;
}

/* Room Management Section */
.room-management-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 20px;
}

.room-management-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 12px;
}

.room-management-section h3 .material-icons {
  color: var(--color-primary);
}

.room-management-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.room-management-row .admin-input {
  flex: 1;
  min-width: 150px;
  padding: 10px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  cursor: pointer;
}

.room-management-row .admin-input:disabled {
  background: var(--color-surface);
  color: var(--color-text-hint);
  cursor: not-allowed;
}

.rooms-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.room-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.room-name {
  flex: 1;
  font-weight: 500;
  color: var(--color-text-primary);
}

.room-floor {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  background: var(--color-surface);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

.no-rooms {
  margin-top: 16px;
  padding: 16px;
  text-align: center;
  color: var(--color-text-hint);
  background: var(--color-bg);
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
}

/* Announcement Section */
.announcement-section {
  background: var(--color-primary-light);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-lg);
  padding: 16px;
  margin-bottom: 20px;
}

.announcement-section h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 12px;
}

.announcement-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.announcement-row .announcement-input {
  flex: 1;
  padding: 10px 14px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
}

.facilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.facility-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: all 0.2s ease;
}

.facility-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.facility-image {
  height: 120px;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-surface) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.facility-image .material-icons {
  font-size: 48px;
  color: var(--color-primary);
}

.facility-content {
  padding: 16px;
}

.facility-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.facility-header h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  flex: 1;
}

.type-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
}

.type-academic { background: var(--color-info-bg); color: var(--color-info); }
.type-admin { background: var(--color-warning-bg); color: var(--color-warning); }
.type-facility { background: var(--color-success-bg); color: var(--color-success); }
.type-library { background: #F3E5F5; color: #7B1FA2; }
.type-canteen { background: #FFF3E0; color: #E65100; }

.facility-code {
  font-size: var(--text-xs);
  color: var(--color-text-hint);
  margin-bottom: 8px;
}

.facility-description {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.facility-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.facility-stats .stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.facility-stats .stat .material-icons {
  font-size: 16px;
  color: var(--color-text-hint);
}

.facility-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-icon.btn-danger:hover {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.btn-icon .material-icons {
  font-size: 18px;
}

.btn-announce {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: var(--color-success);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-announce:hover {
  background: var(--color-success-dark);
  transform: translateY(-1px);
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
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-dialog.modal-sm {
  max-width: 400px;
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

.modal-icon {
  font-size: 32px;
  color: var(--color-warning);
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

.form-group input,
.form-group select,
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
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: var(--color-primary);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
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

.btn-danger {
  padding: 10px 20px;
  background: var(--color-danger);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: #B71C1C;
}

.text-muted {
  font-size: var(--text-sm);
  color: var(--color-text-hint);
  margin-top: 8px;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .adminfacilities-section {
    padding: 12px;
    min-width: auto;
  }
  
  .section-header h1 {
    font-size: var(--text-lg);
  }
  
  .stats-row {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .stat-box {
    flex: 1;
    min-width: calc(50% - 8px);
    padding: 12px;
  }
  
  .stat-number {
    font-size: var(--text-xl);
  }
  
  .filters-bar {
    flex-direction: column;
    gap: 12px;
  }
  
  .search-box {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .btn-add-inline {
    width: 100%;
    justify-content: center;
  }
  
  .facility-grid {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .facility-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .facility-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .modal-overlay {
    padding: 16px;
  }
  
  .modal-content {
    max-height: 90vh;
    width: 100%;
    max-width: 100%;
    margin: 0;
  }
  
  .form-group input,
  .form-group select,
  .form-group textarea {
    font-size: 16px; /* Prevent iOS zoom */
  }
  
  .search-box input {
    font-size: 16px; /* Prevent iOS zoom */
  }
}
</style>
