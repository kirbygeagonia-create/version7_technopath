<template>
  <div class="adminrooms-section">
    <div class="section-header">
      <div>
        <h1>Room Management</h1>
        <p class="subtitle">{{ ownOnly ? `Managing rooms for: ${dept}` : 'Managing all rooms across campus' }}</p>
      </div>
      <button class="btn-primary" @click="showCreateModal = true">
        <span class="material-icons">add</span>
        Add Room
      </button>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-box">
        <span class="stat-number">{{ rooms.length }}</span>
        <span class="stat-label">Total Rooms</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ rooms.filter(r => r.type === 'classroom').length }}</span>
        <span class="stat-label">Classrooms</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ rooms.filter(r => r.type === 'lab').length }}</span>
        <span class="stat-label">Labs</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ rooms.filter(r => r.is_active).length }}</span>
        <span class="stat-label">Active</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-box">
        <span class="material-icons">search</span>
        <input v-model="searchQuery" type="text" placeholder="Search rooms..." />
      </div>
      <select v-model="filterBuilding" class="filter-select">
        <option value="">All Buildings</option>
        <option v-for="b in buildings" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model="filterType" class="filter-select">
        <option value="">All Types</option>
        <option value="classroom">Classroom</option>
        <option value="lab">Laboratory</option>
        <option value="office">Office</option>
        <option value="meeting">Meeting Room</option>
        <option value="other">Other</option>
      </select>
    </div>

    <!-- Rooms Grid -->
    <div class="rooms-grid">
      <div v-for="room in filteredRooms" :key="room.id" class="room-card">
        <div class="room-image">
          <span class="material-icons">meeting_room</span>
        </div>
        <div class="room-content">
          <div class="room-header">
            <h3>{{ room.name }}</h3>
            <span :class="['status-badge', room.is_active ? 'active' : 'inactive']">
              {{ room.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="room-details">
            <p><span class="label">Room Number:</span> {{ room.room_number }}</p>
            <p><span class="label">Building:</span> {{ getBuildingName(room.building_id) }}</p>
            <p><span class="label">Floor:</span> {{ room.floor }}</p>
            <p><span class="label">Type:</span> {{ formatType(room.type) }}</p>
            <p><span class="label">Capacity:</span> {{ room.capacity }} people</p>
          </div>
          <div class="room-actions">
            <button class="btn-icon" @click="editRoom(room)" title="Edit">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon" @click="toggleStatus(room)" :title="room.is_active ? 'Deactivate' : 'Activate'">
              <span class="material-icons">{{ room.is_active ? 'block' : 'check_circle' }}</span>
            </button>
            <button class="btn-icon btn-danger" @click="confirmDelete(room)" title="Delete">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredRooms.length === 0" class="empty-state">
      <span class="material-icons">meeting_room</span>
      <p>No rooms found</p>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>{{ showEditModal ? 'Edit Room' : 'Add New Room' }}</h2>
          <button class="btn-close" @click="closeModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>Room Number</label>
              <input v-model="form.room_number" type="text" placeholder="e.g., 101" />
            </div>
            <div class="form-group">
              <label>Room Name</label>
              <input v-model="form.name" type="text" placeholder="Display name" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Building</label>
              <select v-model="form.building_id">
                <option v-for="b in buildings" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Floor</label>
              <input v-model="form.floor" type="number" min="1" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Type</label>
              <select v-model="form.type">
                <option value="classroom">Classroom</option>
                <option value="lab">Laboratory</option>
                <option value="office">Office</option>
                <option value="meeting">Meeting Room</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="form-group">
              <label>Capacity</label>
              <input v-model="form.capacity" type="number" min="1" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Course / Program</label>
              <select v-model="form.course_code">
                <option value="">— Shared / No specific course —</option>
                <option value="BSIT">BSIT</option>
                <option value="BSCS">BSCS</option>
                <option value="BSECE">BSECE</option>
                <option value="BSEd">BSEd</option>
                <option value="Criminology">Criminology</option>
                <option value="BSHM">BSHM</option>
                <option value="BSA">BSA</option>
                <option value="BSBA">BSBA</option>
                <option value="STEM">STEM</option>
                <option value="ABM">ABM</option>
                <option value="HUMSS">HUMSS</option>
                <option value="GAS">GAS</option>
              </select>
            </div>
            <div class="form-group">
              <label>Highlight Color <span style="font-size:11px;color:var(--color-text-secondary)">(optional)</span></label>
              <input v-model="form.course_color" type="color" style="height:36px;width:100%;padding:2px 4px;cursor:pointer" />
            </div>
          </div>
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input v-model="form.is_active" type="checkbox" />
              <span>Active</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn-primary" @click="saveRoom">{{ showEditModal ? 'Save' : 'Create' }}</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-dialog modal-sm">
        <div class="modal-header">
          <span class="material-icons modal-icon">warning</span>
          <h2>Delete Room</h2>
        </div>
        <div class="modal-body">
          <p>Delete <strong>{{ roomToDelete?.name }}</strong>?</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancel</button>
          <button class="btn-danger" @click="deleteRoom">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../../services/api.js'

const props = defineProps({
  ownOnly: { type: Boolean, default: false },
  dept: { type: String, default: '' }
})

const rooms = ref([])
const buildings = ref([])
const searchQuery = ref('')
const filterBuilding = ref('')
const filterType = ref('')
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const roomToDelete = ref(null)

const form = ref({
  id: null,
  room_number: '',
  name: '',
  building_id: '',
  floor: 1,
  type: 'classroom',
  capacity: 30,
  is_active: true
})

const filteredRooms = computed(() => {
  return rooms.value.filter(r => {
    const matchesSearch = !searchQuery.value || 
      r.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      r.room_number.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesBuilding = !filterBuilding.value || r.building_id === parseInt(filterBuilding.value)
    const matchesType = !filterType.value || r.type === filterType.value
    return matchesSearch && matchesBuilding && matchesType
  })
})

function getBuildingName(id) {
  const b = buildings.value.find(b => b.id === id)
  return b?.name || 'Unknown'
}

function formatType(type) {
  const labels = { classroom: 'Classroom', lab: 'Laboratory', office: 'Office', meeting: 'Meeting Room', other: 'Other' }
  return labels[type] || type
}

function editRoom(room) {
  form.value = { ...room }
  showEditModal.value = true
}

function closeModal() {
  showCreateModal.value = false
  showEditModal.value = false
  form.value = { id: null, room_number: '', name: '', building_id: '', floor: 1, type: 'classroom', capacity: 30, is_active: true, course_code: '', course_color: '' }
}

function confirmDelete(room) {
  roomToDelete.value = room
  showDeleteModal.value = true
}

async function loadData() {
  try {
    const [roomsRes, buildingsRes] = await Promise.all([
      api.get(props.ownOnly ? `/rooms/?department=${props.dept}` : '/rooms/'),
      api.get('/facilities/')
    ])
    rooms.value = roomsRes.data
    buildings.value = buildingsRes.data
  } catch (e) {
    console.error('Failed to load rooms:', e)
    rooms.value = [
      { id: 1, room_number: '101', name: 'Computer Lab 1', building_id: 1, floor: 1, type: 'lab', capacity: 40, is_active: true },
      { id: 2, room_number: '102', name: 'Lecture Hall A', building_id: 1, floor: 1, type: 'classroom', capacity: 120, is_active: true },
      { id: 3, room_number: '201', name: 'Programming Lab', building_id: 1, floor: 2, type: 'lab', capacity: 35, is_active: true }
    ]
    buildings.value = [{ id: 1, name: 'Main Academic Building' }]
  }
}

async function saveRoom() {
  try {
    if (showEditModal.value) {
      await api.put(`/rooms/${form.value.id}/`, form.value)
    } else {
      await api.post('/rooms/', form.value)
    }
    closeModal()
    loadData()
  } catch (e) {
    console.error('Failed to save room:', e)
  }
}

async function toggleStatus(room) {
  try {
    await api.patch(`/rooms/${room.id}/`, { is_active: !room.is_active })
    room.is_active = !room.is_active
  } catch (e) {
    console.error('Failed to toggle status:', e)
  }
}

async function deleteRoom() {
  try {
    await api.delete(`/rooms/${roomToDelete.value.id}/`)
    showDeleteModal.value = false
    loadData()
  } catch (e) {
    console.error('Failed to delete room:', e)
  }
}

onMounted(loadData)
</script>

<style scoped>
.adminrooms-section { padding: 0; font-family: var(--font-primary); max-width: 1400px; }

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

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.room-card {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
  transition: all 0.2s ease;
}

.room-card:hover {
  box-shadow: var(--shadow-sm);
}

.room-image {
  height: 100px;
  background: linear-gradient(135deg, var(--color-info-bg) 0%, var(--color-surface) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.room-image .material-icons {
  font-size: 40px;
  color: var(--color-info);
}

.room-content {
  padding: 16px;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.room-header h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.status-badge {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
}

.status-badge.active { background: var(--color-success-bg); color: var(--color-success); }
.status-badge.inactive { background: var(--color-surface-2); color: var(--color-text-hint); }

.room-details {
  margin-bottom: 12px;
}

.room-details p {
  margin: 4px 0;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.room-details .label {
  font-weight: 500;
  color: var(--color-text-primary);
}

.room-actions {
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
.form-group select {
  width: 100%;
  padding: 10px 12px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  outline: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
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
</style>
