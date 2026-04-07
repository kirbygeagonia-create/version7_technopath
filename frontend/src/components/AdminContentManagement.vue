<template>
  <div class="admin-content-management">
    <!-- Facilities Section -->
    <div class="content-section">
      <div class="section-header">
        <div class="section-title">
          <span class="material-icons" style="color: #2196F3;">business</span>
          <h3>Facilities</h3>
        </div>
        <button class="btn-add" @click="showFacilityDialog()">
          <span class="material-icons">add</span>
          Add
        </button>
      </div>
      <div class="items-list">
        <div v-if="facilities.length === 0" class="empty-state">No facilities yet</div>
        <div v-for="facility in facilities" :key="facility.id" class="item-card">
          <div class="item-icon blue">
            <span class="material-icons">business</span>
          </div>
          <div class="item-info">
            <div class="item-name">{{ facility.name }}</div>
            <div class="item-desc">{{ facility.description || 'No description' }}</div>
          </div>
          <div class="item-actions">
            <button class="btn-icon" @click="showFacilityDialog(facility)">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon delete" @click="deleteFacility(facility.id)">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Rooms Section -->
    <div class="content-section">
      <div class="section-header">
        <div class="section-title">
          <span class="material-icons" style="color: #FF9800;">meeting_room</span>
          <h3>Rooms</h3>
        </div>
        <button class="btn-add" @click="showRoomDialog()">
          <span class="material-icons">add</span>
          Add
        </button>
      </div>
      <div class="items-list">
        <div v-if="rooms.length === 0" class="empty-state">No rooms yet</div>
        <div v-for="room in rooms" :key="room.id" class="item-card">
          <div class="item-icon orange">
            <span class="material-icons">meeting_room</span>
          </div>
          <div class="item-info">
            <div class="item-name">{{ room.name }}</div>
            <div class="item-desc">{{ room.description || 'No description' }}</div>
          </div>
          <div class="item-actions">
            <button class="btn-icon" @click="showRoomDialog(room)">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon delete" @click="deleteRoom(room.id)">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Map Markers Section -->
    <div class="content-section">
      <div class="section-header">
        <div class="section-title">
          <span class="material-icons" style="color: #F44336;">location_on</span>
          <h3>Map Markers</h3>
        </div>
        <button class="btn-add" @click="showMarkerDialog()">
          <span class="material-icons">add</span>
          Add
        </button>
      </div>
      <div class="items-list">
        <div v-if="mapMarkers.length === 0" class="empty-state">No map markers yet</div>
        <div v-for="marker in mapMarkers" :key="marker.id" class="item-card">
          <div class="item-icon red">
            <span class="material-icons">location_on</span>
          </div>
          <div class="item-info">
            <div class="item-name">{{ marker.name }}</div>
            <div class="item-desc">Type: {{ marker.type }} | Position: ({{ marker.x_position?.toFixed(2) }}, {{ marker.y_position?.toFixed(2) }})</div>
          </div>
          <div class="item-actions">
            <button class="btn-icon" @click="showMarkerDialog(marker)">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon delete" @click="deleteMapMarker(marker.id)">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
      <!-- Map Editor Card -->
      <div class="map-editor-card">
        <div class="map-editor-info">
          <span class="material-icons">map</span>
          <div>
            <div class="editor-title">Map Editor</div>
            <div class="editor-desc">Edit campus map layout and markers visually</div>
          </div>
        </div>
        <div class="map-controls">
          <span class="control-chip"><span class="material-icons">add_location</span>Add Marker</span>
          <span class="control-chip"><span class="material-icons">edit_road</span>Edit Paths</span>
          <span class="control-chip"><span class="material-icons">layers</span>Floors</span>
          <span class="control-chip"><span class="material-icons">zoom_in</span>Zoom</span>
        </div>
        <button class="btn-edit-map" @click="openMapEditor">
          <span class="material-icons">edit</span>
          Edit Map
        </button>
      </div>
    </div>

    <!-- Admin Users Section -->
    <div class="content-section">
      <div class="section-header">
        <div class="section-title">
          <span class="material-icons" style="color: #9C27B0;">admin_panel_settings</span>
          <h3>Admin Users</h3>
        </div>
        <button class="btn-add" @click="showUserDialog()">
          <span class="material-icons">add</span>
          Add
        </button>
      </div>
      <div class="items-list">
        <div v-if="users.length === 0" class="empty-state">No users yet</div>
        <div v-for="user in users" :key="user.id" class="item-card">
          <div class="item-icon purple">
            <span class="material-icons">person</span>
          </div>
          <div class="item-info">
            <div class="item-name">{{ user.username }}</div>
            <div class="item-desc">Role: {{ user.role || user.user_type || 'user' }}</div>
          </div>
          <div class="item-actions">
            <button class="btn-icon" @click="showUserDialog(user)">
              <span class="material-icons">edit</span>
            </button>
            <button class="btn-icon delete" @click="deleteUser(user.id)">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialogs -->
    <!-- Facility Dialog -->
    <div v-if="dialogFacility.show" class="modal-overlay" @click.self="dialogFacility.show = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ dialogFacility.data.id ? 'Edit Facility' : 'Add Facility' }}</h3>
          <button class="btn-close" @click="dialogFacility.show = false">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Name</label>
            <input v-model="dialogFacility.data.name" type="text" placeholder="e.g., MST Building">
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="dialogFacility.data.description" rows="3" placeholder="Facility description"></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="dialogFacility.show = false">Cancel</button>
          <button class="btn-primary" @click="saveFacility">Save</button>
        </div>
      </div>
    </div>

    <!-- Room Dialog -->
    <div v-if="dialogRoom.show" class="modal-overlay" @click.self="dialogRoom.show = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ dialogRoom.data.id ? 'Edit Room' : 'Add Room' }}</h3>
          <button class="btn-close" @click="dialogRoom.show = false">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Name</label>
            <input v-model="dialogRoom.data.name" type="text" placeholder="e.g., CL1">
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="dialogRoom.data.description" rows="3" placeholder="Room description"></textarea>
          </div>
          <div class="form-group">
            <label>Facility</label>
            <select v-model="dialogRoom.data.facility_id">
              <option value="">Select facility</option>
              <option v-for="f in facilities" :key="f.id" :value="f.id">{{ f.name }}</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="dialogRoom.show = false">Cancel</button>
          <button class="btn-primary" @click="saveRoom">Save</button>
        </div>
      </div>
    </div>

    <!-- Map Marker Dialog -->
    <div v-if="dialogMarker.show" class="modal-overlay" @click.self="dialogMarker.show = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ dialogMarker.data.id ? 'Edit Map Marker' : 'Add Map Marker' }}</h3>
          <button class="btn-close" @click="dialogMarker.show = false">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Name</label>
            <input v-model="dialogMarker.data.name" type="text" placeholder="e.g., MST Building">
          </div>
          <div class="form-group">
            <label>Type</label>
            <select v-model="dialogMarker.data.type">
              <option value="facility">Facility</option>
              <option value="room">Room</option>
            </select>
          </div>
          <div class="form-row">
            <div class="form-group half">
              <label>X Position (0.0 - 1.0)</label>
              <input v-model="dialogMarker.data.x_position" type="number" step="0.01" min="0" max="1">
            </div>
            <div class="form-group half">
              <label>Y Position (0.0 - 1.0)</label>
              <input v-model="dialogMarker.data.y_position" type="number" step="0.01" min="0" max="1">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="dialogMarker.show = false">Cancel</button>
          <button class="btn-primary" @click="saveMapMarker">Save</button>
        </div>
      </div>
    </div>

    <!-- User Dialog -->
    <div v-if="dialogUser.show" class="modal-overlay" @click.self="dialogUser.show = false">
      <div class="modal-dialog">
        <div class="modal-header">
          <h3>{{ dialogUser.data.id ? 'Edit User' : 'Add User' }}</h3>
          <button class="btn-close" @click="dialogUser.show = false">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Username</label>
            <input v-model="dialogUser.data.username" type="text" placeholder="Enter username">
          </div>
          <div class="form-group">
            <label>Password {{ dialogUser.data.id ? '(leave blank to keep current)' : '' }}</label>
            <input v-model="dialogUser.data.password" type="password" placeholder="Enter password">
          </div>
          <div class="form-group">
            <label>Role</label>
            <select v-model="dialogUser.data.role">
              <option value="user">User</option>
              <option value="admin">Admin</option>
              <option value="super_admin">Super Admin</option>
              <option value="dean">Dean</option>
              <option value="program_head">Program Head</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="dialogUser.show = false">Cancel</button>
          <button class="btn-primary" @click="saveUser">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api.js'

const facilities = ref([])
const rooms = ref([])
const mapMarkers = ref([])
const users = ref([])

const dialogFacility = ref({ show: false, data: { name: '', description: '' } })
const dialogRoom = ref({ show: false, data: { name: '', description: '', facility_id: '' } })
const dialogMarker = ref({ show: false, data: { name: '', type: 'facility', x_position: 0.5, y_position: 0.5 } })
const dialogUser = ref({ show: false, data: { username: '', password: '', role: 'user' } })

onMounted(async () => {
  await loadAllData()
})

async function loadAllData() {
  try {
    const [fRes, rRes, mRes, uRes] = await Promise.all([
      api.get('/facilities/'),
      api.get('/rooms/'),
      api.get('/map-markers/'),
      api.get('/users/')
    ])
    facilities.value = fRes.data || []
    rooms.value = rRes.data || []
    mapMarkers.value = mRes.data || []
    users.value = uRes.data || []
  } catch (err) {
    console.error('Error loading data:', err)
    // Mock data for development
    facilities.value = [
      { id: 1, name: 'MST Building', description: 'Main Science and Technology Building' },
      { id: 2, name: 'JST Building', description: 'Junior Science and Technology Building' },
      { id: 3, name: 'RST Building', description: 'Research Science and Technology Building' },
    ]
    rooms.value = [
      { id: 1, name: 'CL1', description: 'Computer Lab 1', facility_id: 1 },
      { id: 2, name: 'CL2', description: 'Computer Lab 2', facility_id: 1 },
    ]
    mapMarkers.value = [
      { id: 1, name: 'MST Building', type: 'facility', x_position: 0.3, y_position: 0.4 },
      { id: 2, name: 'Library', type: 'facility', x_position: 0.6, y_position: 0.5 },
    ]
    users.value = [
      { id: 1, username: 'admin', role: 'super_admin' },
      { id: 2, username: 'dean', role: 'dean' },
    ]
  }
}

// Facility CRUD
function showFacilityDialog(facility = null) {
  dialogFacility.value = {
    show: true,
    data: facility ? { ...facility } : { name: '', description: '' }
  }
}

async function saveFacility() {
  try {
    if (dialogFacility.value.data.id) {
      await api.put(`/facilities/${dialogFacility.value.data.id}/`, dialogFacility.value.data)
    } else {
      await api.post('/facilities/', dialogFacility.value.data)
    }
    dialogFacility.value.show = false
    await loadAllData()
  } catch (err) {
    alert('Error saving facility: ' + err.message)
  }
}

async function deleteFacility(id) {
  if (!confirm('Delete this facility?')) return
  try {
    await api.delete(`/facilities/${id}/`)
    await loadAllData()
  } catch (err) {
    alert('Error deleting facility: ' + err.message)
  }
}

// Room CRUD
function showRoomDialog(room = null) {
  dialogRoom.value = {
    show: true,
    data: room ? { ...room } : { name: '', description: '', facility_id: '' }
  }
}

async function saveRoom() {
  try {
    if (dialogRoom.value.data.id) {
      await api.put(`/rooms/${dialogRoom.value.data.id}/`, dialogRoom.value.data)
    } else {
      await api.post('/rooms/', dialogRoom.value.data)
    }
    dialogRoom.value.show = false
    await loadAllData()
  } catch (err) {
    alert('Error saving room: ' + err.message)
  }
}

async function deleteRoom(id) {
  if (!confirm('Delete this room?')) return
  try {
    await api.delete(`/rooms/${id}/`)
    await loadAllData()
  } catch (err) {
    alert('Error deleting room: ' + err.message)
  }
}

// Map Marker CRUD
function showMarkerDialog(marker = null) {
  dialogMarker.value = {
    show: true,
    data: marker ? { ...marker } : { name: '', type: 'facility', x_position: 0.5, y_position: 0.5 }
  }
}

async function saveMapMarker() {
  try {
    if (dialogMarker.value.data.id) {
      await api.put(`/map-markers/${dialogMarker.value.data.id}/`, dialogMarker.value.data)
    } else {
      await api.post('/map-markers/', dialogMarker.value.data)
    }
    dialogMarker.value.show = false
    await loadAllData()
  } catch (err) {
    alert('Error saving marker: ' + err.message)
  }
}

async function deleteMapMarker(id) {
  if (!confirm('Delete this map marker?')) return
  try {
    await api.delete(`/map-markers/${id}/`)
    await loadAllData()
  } catch (err) {
    alert('Error deleting marker: ' + err.message)
  }
}

// User CRUD
function showUserDialog(user = null) {
  dialogUser.value = {
    show: true,
    data: user ? { ...user, password: '' } : { username: '', password: '', role: 'user' }
  }
}

async function saveUser() {
  try {
    const data = { ...dialogUser.value.data }
    if (!data.password) delete data.password
    
    if (data.id) {
      await api.put(`/users/${data.id}/`, data)
    } else {
      await api.post('/users/', data)
    }
    dialogUser.value.show = false
    await loadAllData()
  } catch (err) {
    alert('Error saving user: ' + err.message)
  }
}

async function deleteUser(id) {
  if (!confirm('Delete this user?')) return
  try {
    await api.delete(`/users/${id}/`)
    await loadAllData()
  } catch (err) {
    alert('Error deleting user: ' + err.message)
  }
}

function openMapEditor() {
  alert('Map Editor - Feature coming soon!')
}
</script>

<style scoped>
.admin-content-management {
  padding: 24px;
  max-width: 1400px;
}

.content-section {
  margin-bottom: 32px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #FF9800;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}

.btn-add:hover {
  background: #F57C00;
}

.btn-add .material-icons {
  font-size: 18px;
}

/* Items List */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #888;
  font-size: 14px;
  background: #f8f9fa;
  border-radius: 12px;
}

.item-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
  transition: box-shadow 0.15s;
}

.item-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon.blue { background: #E3F2FD; color: #2196F3; }
.item-icon.orange { background: #FFF3E0; color: #FF9800; }
.item-icon.red { background: #FFEBEE; color: #F44336; }
.item-icon.purple { background: #F3E5F5; color: #9C27B0; }

.item-icon .material-icons {
  font-size: 20px;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 2px;
}

.item-desc {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-actions {
  display: flex;
  gap: 4px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: #666;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.btn-icon:hover {
  background: #f0f0f0;
  color: #333;
}

.btn-icon.delete:hover {
  background: #FFEBEE;
  color: #F44336;
}

.btn-icon .material-icons {
  font-size: 18px;
}

/* Map Editor Card */
.map-editor-card {
  margin-top: 16px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.06);
}

.map-editor-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.map-editor-info .material-icons {
  font-size: 32px;
  color: #4CAF50;
}

.editor-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.editor-desc {
  font-size: 13px;
  color: #888;
  margin-top: 2px;
}

.map-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.control-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #f0f0f0;
  border-radius: 20px;
  font-size: 12px;
  color: #666;
}

.control-chip .material-icons {
  font-size: 14px;
}

.btn-edit-map {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.btn-edit-map:hover {
  background: #388E3C;
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
}

.modal-dialog {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  animation: modalSlideIn 0.2s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: #f0f0f0;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.btn-close:hover {
  background: #e0e0e0;
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: 50vh;
}

.form-group {
  margin-bottom: 16px;
}

.form-group.half {
  flex: 1;
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #555;
  margin-bottom: 6px;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  background: white;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #FF9800;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #f8f9fa;
}

.btn-secondary {
  padding: 10px 20px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  color: #555;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #f0f0f0;
}

.btn-primary {
  padding: 10px 20px;
  background: #FF9800;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  color: white;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover {
  background: #F57C00;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-content-management {
    padding: 12px;
  }
  
  .item-card {
    padding: 12px;
  }
  
  .item-actions {
    flex-direction: column;
    gap: 4px;
  }
  
  .modal-dialog {
    width: 95%;
    margin: 16px;
  }
  
  .modal-body {
    padding: 16px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
}
</style>
