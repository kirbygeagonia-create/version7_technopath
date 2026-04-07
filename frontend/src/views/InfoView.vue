<template>
  <div class="infoview-view">
    <header class="infoview-top-bar">
      <button class="infoview-back-btn" @click="goBack">
          <span class="material-icons">arrow_back</span>
        </button>
      <h1>{{ title }}</h1>
      <div class="infoview-spacer"></div>
    </header>

    <div class="infoview-content">
      <div v-if="loading" class="infoview-loading">
        <div class="infoview-spinner"></div>
        <p>Loading...</p>
      </div>

      <div v-else-if="items.length === 0" class="infoview-empty">
        <p>No {{ itemName }} found</p>
      </div>

      <div v-else class="infoview-items-list">
        <div
          v-for="item in items"
          :key="item.id"
          class="infoview-item-card"
          @click="selectItem(item)"
        >
          <div class="infoview-item-icon">
          <span class="material-icons">{{ getIcon(item) }}</span>
        </div>
          <div class="infoview-item-info">
            <h3>{{ item.name }}</h3>
            <p class="infoview-item-code">{{ item.code || item.building_code }}</p>
            <p class="infoview-item-description">{{ item.description || 'No description available' }}</p>
          </div>
          <div class="infoview-item-arrow">
          <span class="material-icons">arrow_forward_ios</span>
        </div>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedItem" class="infoview-modal-overlay" @click="selectedItem = null">
      <div class="infoview-detail-modal" @click.stop>
        <div class="infoview-modal-header">
          <h2>{{ selectedItem.name }}</h2>
          <button class="infoview-close-btn" @click="selectedItem = null">
            <span class="material-icons">close</span>
          </button>
        </div>
        
        <div class="infoview-modal-body">
          <div class="infoview-detail-section">
            <h4>Description</h4>
            <p>{{ selectedItem.description || 'No description available' }}</p>
          </div>
          
          <div v-if="selectedItem.total_floors" class="infoview-detail-section">
            <h4>Building Info</h4>
            <p>Total Floors: {{ selectedItem.total_floors }}</p>
            <p>Building Code: {{ selectedItem.building_code || selectedItem.code }}</p>
          </div>
          
          <div v-if="selectedItem.latitude && selectedItem.longitude" class="infoview-detail-section">
            <h4>Location</h4>
            <p>Coordinates: {{ selectedItem.latitude.toFixed(4) }}, {{ selectedItem.longitude.toFixed(4) }}</p>
          </div>
          
          <div v-if="type === 'rooms'" class="infoview-detail-section">
            <h4>Room Details</h4>
            <p>Room Number: {{ selectedItem.room_number }}</p>
            <p>Floor: {{ selectedItem.floor }}</p>
            <p>Type: {{ selectedItem.room_type }}</p>
            <p>Capacity: {{ selectedItem.capacity }} people</p>
            <p v-if="selectedItem.is_office">This is an office</p>
          </div>
          
          <div v-if="type === 'instructors' || type === 'employees'" class="infoview-detail-section">
            <h4>Contact Info</h4>
            <p>Department: {{ selectedItem.department || 'N/A' }}</p>
            <p>Email: {{ selectedItem.email || 'N/A' }}</p>
            <p>Office: {{ selectedItem.office || 'N/A' }}</p>
          </div>
        </div>
        
        <div class="infoview-modal-footer">
          <button class="infoview-navigate-btn" @click="navigateToItem(selectedItem)">
            Navigate Here
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../services/api.js'

const router = useRouter()
const route = useRoute()

const type = computed(() => route.params.type || 'buildings')
const loading = ref(true)
const items = ref([])
const selectedItem = ref(null)

const title = computed(() => {
  const titles = {
    'buildings': 'Building Information',
    'rooms': 'Rooms Information',
    'instructors': 'Instructor Information',
    'employees': 'Employees'
  }
  return titles[type.value] || 'Information'
})

const itemName = computed(() => {
  const names = {
    'buildings': 'buildings',
    'rooms': 'rooms',
    'instructors': 'instructors',
    'employees': 'employees'
  }
  return names[type.value] || 'items'
})

const loadData = async () => {
  loading.value = true
  try {
    let endpoint = ''
    switch (type.value) {
      case 'buildings':
        endpoint = '/facilities/'
        break
      case 'rooms':
        endpoint = '/rooms/'
        break
      case 'instructors':
      case 'employees':
        // These would need a users endpoint with role filtering
        endpoint = '/users/'
        break
      default:
        endpoint = '/facilities/'
    }
    
    const response = await api.get(endpoint)
    items.value = response.data
  } catch (error) {
    console.error('Error loading data:', error)
    // Use fallback data
    items.value = getFallbackData()
  } finally {
    loading.value = false
  }
}

const getFallbackData = () => {
  const fallbacks = {
    'buildings': [
      { id: 1, name: 'RST Building', building_code: 'RST', description: 'Research Science and Technology Building', total_floors: 3, latitude: 14.1001, longitude: 121.0801 },
      { id: 2, name: 'JST Building', building_code: 'JST', description: 'Junior Science and Technology Building', total_floors: 4, latitude: 14.1002, longitude: 121.0802 },
      { id: 3, name: 'MST Building', building_code: 'MST', description: 'Main Science and Technology Building', total_floors: 4, latitude: 14.1003, longitude: 121.0803 },
      { id: 4, name: 'Library', building_code: 'LIB', description: 'School Library and Resource Center', total_floors: 2, latitude: 14.1006, longitude: 121.0806 },
    ],
    'rooms': [
      { id: 1, name: 'CL1', room_number: 'RST-GF-CL1', description: 'Computer Lab 1', floor: 1, room_type: 'lab', capacity: 40 },
      { id: 2, name: 'CL2', room_number: 'RST-GF-CL2', description: 'Computer Lab 2', floor: 1, room_type: 'lab', capacity: 40 },
      { id: 3, name: 'CICT Office', room_number: 'MST-2F-CICT', description: 'CICT Department Office', floor: 2, room_type: 'office', capacity: 15, is_office: true },
      { id: 4, name: 'Dean Office', room_number: 'MST-3F-DEAN', description: 'College Dean Office', floor: 3, room_type: 'office', capacity: 8, is_office: true },
    ],
    'instructors': [
      { id: 1, name: 'Dr. Juan Dela Cruz', department: 'Computer Science', email: 'j.delacruz@seait.edu.ph', office: 'MST-2F-CICT' },
      { id: 2, name: 'Prof. Maria Santos', department: 'Information Technology', email: 'm.santos@seait.edu.ph', office: 'MST-2F-CICT' },
    ],
    'employees': [
      { id: 1, name: 'Admin Office', department: 'Administration', email: 'admin@seait.edu.ph', office: 'REG-1F' },
      { id: 2, name: 'Registrar Staff', department: 'Registrar', email: 'registrar@seait.edu.ph', office: 'REG-1F' },
    ]
  }
  return fallbacks[type.value] || fallbacks['buildings']
}

const getIcon = (item) => {
  if (type.value === 'buildings') return 'business'
  if (type.value === 'rooms') return item.is_office ? 'meeting_room' : 'computer'
  if (type.value === 'instructors') return 'school'
  if (type.value === 'employees') return 'person'
  return 'place'
}

const selectItem = (item) => {
  selectedItem.value = item
}

const navigateToItem = (item) => {
  selectedItem.value = null
  router.push({
    path: '/navigate',
    query: { destination: item.name }
  })
}

const goBack = () => router.back()

onMounted(() => {
  loadData()
})
</script>

<style>
/* Styles moved to external file: src/assets/infoview.css */
@import '../assets/infoview.css';
</style>
