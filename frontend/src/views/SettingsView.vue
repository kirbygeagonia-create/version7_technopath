<template>
  <div class="settings-view">
    <!-- Header -->
    <div class="settings-header">
      <div class="settings-header-content">
        <div class="settings-header-icon">
          <span class="material-icons">settings</span>
        </div>
        <div class="settings-header-text">
          <h1>App Settings</h1>
          <p>Customize your experience</p>
        </div>
      </div>
    </div>

    <!-- Settings List -->
    <div class="settings-content">
      <!-- Account Section -->
      <div class="settings-section">
        <h3 class="settings-section-title">Account</h3>
        <div class="settings-card">
          <div class="settings-item" @click="goToAdminLogin">
            <div class="settings-item-icon" style="background: #FFF3E0; color: #FF9800;">
              <span class="material-icons">admin_panel_settings</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Login Admin</div>
              <div class="settings-item-subtitle">Access admin dashboard</div>
            </div>
            <span class="material-icons settings-chevron">chevron_right</span>
          </div>
        </div>
      </div>

      <!-- Appearance Section -->
      <div class="settings-section">
        <h3 class="settings-section-title">Appearance</h3>
        <div class="settings-card">
          <div class="settings-item">
            <div class="settings-item-icon" style="background: #F3E5F5; color: #9C27B0;">
              <span class="material-icons">dark_mode</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Dark Mode</div>
              <div class="settings-item-subtitle">Toggle dark theme</div>
            </div>
            <label class="settings-switch">
              <input type="checkbox" v-model="isDarkMode" @change="toggleTheme">
              <span class="settings-slider"></span>
            </label>
          </div>
        </div>
      </div>

      <!-- Info Section -->
      <div class="settings-section">
        <h3 class="settings-section-title">Info</h3>
        <div class="settings-card">
          <div class="settings-item" @click="showFacilitiesDialog">
            <div class="settings-item-icon" style="background: #FFF3E0; color: #FF9800;">
              <span class="material-icons">business</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Facilities</div>
              <div class="settings-item-subtitle">Academic facilities - See more</div>
            </div>
            <span class="material-icons settings-chevron">chevron_right</span>
          </div>
          <div class="settings-divider"></div>
          <div class="settings-item" @click="showRoomsDialog">
            <div class="settings-item-icon" style="background: #E3F2FD; color: #2196F3;">
              <span class="material-icons">meeting_room</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Rooms</div>
              <div class="settings-item-subtitle">MST, JST, RST building rooms</div>
            </div>
            <span class="material-icons settings-chevron">chevron_right</span>
          </div>
        </div>
      </div>

      <!-- About Section -->
      <div class="settings-section">
        <h3 class="settings-section-title">About</h3>
        <div class="settings-card">
          <div class="settings-item">
            <div class="settings-item-icon" style="background: #E3F2FD; color: #2196F3;">
              <span class="material-icons">info_outline</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">About Us</div>
              <div class="settings-item-subtitle">Guide Map Navigation app for campus routing</div>
            </div>
          </div>
          <div class="settings-divider"></div>
          <div class="settings-item">
            <div class="settings-item-icon" style="background: #E8F5E9; color: #4CAF50;">
              <span class="material-icons">verified</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Version</div>
              <div class="settings-item-subtitle">1.0.0</div>
            </div>
          </div>
          <div class="settings-divider"></div>
          <div class="settings-item" @click="checkForUpdates">
            <div class="settings-item-icon" style="background: #FFF3E0; color: #FF5722;">
              <span class="material-icons">system_update</span>
            </div>
            <div class="settings-item-text">
              <div class="settings-item-title">Check for Updates</div>
              <div class="settings-item-subtitle">Verify you have the latest version</div>
              <div class="item-subtitle">Verify you have the latest version</div>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-spacer"></div>
    </div>

    <!-- Facilities Dialog -->
    <div v-if="showFacilities" class="modal-overlay" @click="showFacilities = false">
      <div class="dialog facilities-dialog" @click.stop>
        <div class="dialog-header">
          <span class="material-icons" style="color: #FF9800;">business</span>
          <h3>Academic Facilities</h3>
        </div>
        <div class="facilities-list">
          <div
            v-for="facility in campusFacilities"
            :key="facility.name"
            class="facility-card"
            @click="showFacilityDetails(facility)"
          >
            <div class="facility-icon" :style="{ background: facility.color + '20', color: facility.color }">
              <span class="material-icons">{{ facility.icon }}</span>
            </div>
            <div class="facility-info">
              <div class="facility-name">{{ facility.name }}</div>
              <div class="facility-type">{{ facility.type }}</div>
            </div>
            <span class="material-icons" style="color: #999; font-size: 16px;">arrow_forward_ios</span>
          </div>
        </div>
        <button class="close-btn" @click="showFacilities = false">Close</button>
      </div>
    </div>

    <!-- Facility Details Dialog -->
    <div v-if="selectedFacility" class="modal-overlay" @click="selectedFacility = null">
      <div class="dialog details-dialog" @click.stop>
        <div class="dialog-header">
          <div class="facility-icon-large" :style="{ background: selectedFacility.color + '20', color: selectedFacility.color }">
            <span class="material-icons" style="font-size: 28px;">{{ selectedFacility.icon }}</span>
          </div>
          <h3>{{ selectedFacility.name }}</h3>
        </div>
        <div class="facility-badge" :style="{ background: selectedFacility.color + '20', color: selectedFacility.color }">
          {{ selectedFacility.type }}
        </div>
        <p class="facility-description">{{ selectedFacility.description }}</p>
        <div class="facility-floors">
          <span class="material-icons" style="font-size: 18px; color: #666;">stairs</span>
          <span>{{ selectedFacility.floors }} Floor{{ selectedFacility.floors > 1 ? 's' : '' }}</span>
        </div>
        <div class="features-section">
          <h4>Features:</h4>
          <div v-for="feature in selectedFacility.features" :key="feature" class="feature-item">
            <span class="material-icons" style="font-size: 16px; color: #4CAF50;">check_circle</span>
            <span>{{ feature }}</span>
          </div>
        </div>
        <button class="close-btn" @click="selectedFacility = null">Close</button>
      </div>
    </div>

    <!-- Buildings for Rooms Dialog -->
    <div v-if="showBuildings" class="modal-overlay" @click="showBuildings = false">
      <div class="dialog buildings-dialog" @click.stop>
        <div class="dialog-header">
          <span class="material-icons" style="color: #2196F3;">meeting_room</span>
          <h3>Select Building</h3>
        </div>
        <div class="buildings-list">
          <div
            v-for="(rooms, building) in buildingRooms"
            :key="building"
            class="building-card"
            @click="showBuildingRooms(building)"
          >
            <div class="building-icon" style="background: #E3F2FD; color: #2196F3;">
              <span class="material-icons">business</span>
            </div>
            <div class="building-info">
              <div class="building-name">{{ building }}</div>
              <div class="building-rooms">{{ rooms.length }} rooms available</div>
            </div>
            <span class="material-icons" style="color: #999; font-size: 16px;">arrow_forward_ios</span>
          </div>
        </div>
        <button class="close-btn" @click="showBuildings = false">Close</button>
      </div>
    </div>

    <!-- Building Rooms Dialog -->
    <div v-if="selectedBuilding" class="modal-overlay" @click="selectedBuilding = null">
      <div class="dialog rooms-dialog" @click.stop>
        <div class="dialog-header">
          <div class="building-icon" style="background: #E3F2FD; color: #2196F3;">
            <span class="material-icons">meeting_room</span>
          </div>
          <h3>{{ selectedBuilding }} Rooms</h3>
        </div>
        <div class="rooms-list">
          <div v-if="buildingRooms[selectedBuilding].length === 0" class="empty-state">
            No rooms available for this building.
          </div>
          <div
            v-for="room in buildingRooms[selectedBuilding]"
            :key="room.name"
            class="room-card"
          >
            <div class="room-icon" style="background: #E3F2FD; color: #2196F3;">
              <span class="material-icons">door_front</span>
            </div>
            <div class="room-info">
              <div class="room-name">{{ room.name }}</div>
              <div class="room-type">{{ room.type }} • Floor {{ room.floor }}</div>
            </div>
            <div class="room-capacity">{{ room.capacity }}</div>
          </div>
        </div>
        <button class="close-btn" @click="selectedBuilding = null">Close</button>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="toastMessage" class="toast">{{ toastMessage }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const isDarkMode = ref(false)
const showFacilities = ref(false)
const showBuildings = ref(false)
const selectedFacility = ref(null)
const selectedBuilding = ref(null)
const toastMessage = ref('')

// Campus Facilities Data (from Flutter)
const campusFacilities = ref([
  {
    name: 'MST Building',
    type: 'Academic Building',
    description: 'Main Science and Technology Building',
    floors: 4,
    features: ['Computer Labs CL1, CL2 (1st Floor)', 'Computer Labs CL5, CL6 (2nd Floor)', 'Lecture Rooms CR1, CR2', 'Administrative Offices'],
    icon: 'business',
    color: '#FF9800'
  },
  {
    name: 'JST Building',
    type: 'Academic Building',
    description: 'Junior Science and Technology Building',
    floors: 4,
    features: ['Classrooms', 'Laboratories', 'Faculty Offices', 'Student Lounges'],
    icon: 'business',
    color: '#2196F3'
  },
  {
    name: 'RST Building',
    type: 'Research Building',
    description: 'Research Science and Technology Building',
    floors: 3,
    features: ['Research Labs', 'Graduate Studies', 'Specialized Equipment', 'Conference Rooms'],
    icon: 'science',
    color: '#9C27B0'
  },
  {
    name: 'Library',
    type: 'Facility',
    description: 'Main Campus Library',
    floors: 2,
    features: ['Book Lending', 'Study Areas', 'Research Materials', 'Digital Resources', 'Reading Rooms'],
    icon: 'library_books',
    color: '#4CAF50'
  },
  {
    name: 'Registrar Office',
    type: 'Administrative',
    description: 'Student Services and Records',
    floors: 1,
    features: ['Enrollment Services', 'Academic Records', 'Transcript Requests', 'Student Assistance'],
    icon: 'admin_panel_settings',
    color: '#FF5722'
  },
  {
    name: 'Cafeteria',
    type: 'Dining',
    description: 'Main Campus Dining Hall',
    floors: 1,
    features: ['Meal Service', 'Snacks & Beverages', 'Seating Area', 'Food Vendors'],
    icon: 'restaurant',
    color: '#795548'
  },
  {
    name: 'Gymnasium',
    type: 'Sports Facility',
    description: 'School Sports and Recreation Center',
    floors: 1,
    features: ['Basketball Court', 'Volleyball Court', 'Fitness Equipment', 'Locker Rooms', 'Sports Events'],
    icon: 'sports_basketball',
    color: '#009688'
  }
])

// Building Rooms Data (from Flutter)
const buildingRooms = ref({
  'MST Building': [
    { name: 'MST101', type: 'Lecture Room', floor: 1, capacity: '40 seats' },
    { name: 'MST102', type: 'Lecture Room', floor: 1, capacity: '40 seats' },
    { name: 'MST103', type: 'Lecture Room', floor: 1, capacity: '40 seats' },
    { name: 'CL1', type: 'Computer Lab', floor: 1, capacity: '30 PCs' },
    { name: 'CL2', type: 'Computer Lab', floor: 1, capacity: '30 PCs' },
    { name: 'CL5', type: 'Computer Lab', floor: 2, capacity: '30 PCs' },
    { name: 'CL6', type: 'Computer Lab', floor: 2, capacity: '30 PCs' },
    { name: 'CR1', type: 'Classroom', floor: 1, capacity: '35 seats' },
    { name: 'CR2', type: 'Classroom', floor: 1, capacity: '35 seats' },
  ],
  'JST Building': [
    { name: 'JST101', type: 'Lecture Room', floor: 1, capacity: '45 seats' },
    { name: 'JST102', type: 'Lecture Room', floor: 1, capacity: '45 seats' },
    { name: 'JST201', type: 'Laboratory', floor: 2, capacity: '25 students' },
    { name: 'JST202', type: 'Laboratory', floor: 2, capacity: '25 students' },
    { name: 'JST301', type: 'Seminar Room', floor: 3, capacity: '20 seats' },
    { name: 'JST302', type: 'Seminar Room', floor: 3, capacity: '20 seats' },
  ],
  'RST Building': [
    { name: 'RST101', type: 'Research Lab', floor: 1, capacity: '15 researchers' },
    { name: 'RST102', type: 'Research Lab', floor: 1, capacity: '15 researchers' },
    { name: 'RST201', type: 'Graduate Lab', floor: 2, capacity: '20 students' },
    { name: 'RST202', type: 'Conference Room', floor: 2, capacity: '50 seats' },
  ],
})

// Methods
const goToAdminLogin = () => {
  router.push('/admin/login')
}

const toggleTheme = () => {
  document.body.classList.toggle('dark-mode', isDarkMode.value)
  showToast(isDarkMode.value ? 'Dark mode enabled' : 'Light mode enabled')
}

const showFacilitiesDialog = () => {
  showFacilities.value = true
}

const showFacilityDetails = (facility) => {
  selectedFacility.value = facility
  showFacilities.value = false
}

const showRoomsDialog = () => {
  showBuildings.value = true
}

const showBuildingRooms = (building) => {
  selectedBuilding.value = building
  showBuildings.value = false
}

const checkForUpdates = () => {
  showToast('You are using the latest version.')
}

const showToast = (message) => {
  toastMessage.value = message
  setTimeout(() => {
    toastMessage.value = ''
  }, 2000)
}

onMounted(() => {
  // Check for saved theme preference
  const savedTheme = localStorage.getItem('darkMode')
  if (savedTheme) {
    isDarkMode.value = savedTheme === 'true'
    document.body.classList.toggle('dark-mode', isDarkMode.value)
  }
})
</script>

<style>
/* Styles moved to external file: src/assets/settings.css */
@import '../assets/settings.css';
</style>
