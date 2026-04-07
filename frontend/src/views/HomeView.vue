<template>
  <div class="home-view">
    <!-- Top bar with facility/room selectors - MOBILE ONLY -->
    <div class="top-selectors mobile-only">
      <div class="selector-container">
        <!-- Facilities Dropdown Wrapper -->
        <div class="homeview-dropdown-wrapper homeview-facilities-wrapper" @click.stop>
          <div 
            class="homeview-facilities-dropdown"
            :class="{ 'homeview-expanded': isFacilitiesExpanded }"
          >
            <button class="homeview-dropdown-header" @click.prevent="toggleFacilities">
              <span>Facilities</span>
              <span class="homeview-chevron material-icons">{{ isFacilitiesExpanded ? 'expand_less' : 'expand_more' }}</span>
            </button>
            <div v-if="isFacilitiesExpanded" class="homeview-dropdown-content" @click.stop>
              <div
                v-for="facility in facilities"
                :key="facility.id"
                class="homeview-dropdown-item"
                :class="{ 'homeview-selected': selectedFacility === facility.name }"
                @click.stop="selectFacility(facility.name)"
              >
                {{ facility.name }}
                <span v-if="selectedFacility === facility.name" class="homeview-check material-icons">check</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Rooms Dropdown Wrapper -->
        <div class="homeview-dropdown-wrapper homeview-rooms-wrapper" @click.stop>
          <div 
            class="homeview-rooms-dropdown"
            :class="{ 'homeview-expanded': isRoomsExpanded }"
          >
            <button class="homeview-dropdown-header" @click.prevent="toggleRooms">
              <span>Rooms</span>
              <span class="homeview-chevron material-icons">{{ isRoomsExpanded ? 'expand_less' : 'expand_more' }}</span>
            </button>
            <div v-if="isRoomsExpanded" class="homeview-dropdown-content" @click.stop>
              <div
                v-for="room in rooms"
                :key="room.id"
                class="homeview-dropdown-item"
                :class="{ 'homeview-selected': selectedRoom === room.name }"
                @click.stop="selectRoom(room.name)"
              >
                {{ room.name }}
                <span v-if="selectedRoom === room.name" class="homeview-check material-icons">check</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Map container with markers -->
    <div class="map-wrapper">
      <div 
        class="map-container"
        ref="mapContainer"
        @wheel.prevent="handleZoom"
      >
        <div 
          class="map-content"
          :style="mapTransformStyle"
        >
          <div class="map-fallback">
            <div class="campus-map-placeholder">
              <h2>SEAIT Campus Map</h2>
              <p>Interactive Campus Guide</p>
              <div class="buildings-legend">
                <div class="legend-item">
                  <div class="building-marker rst">
                    <span class="material-icons">business</span>
                  </div>
                  <span>RST Building</span>
                </div>
                <div class="legend-item">
                  <div class="building-marker jst">
                    <span class="material-icons">business</span>
                  </div>
                  <span>JST Building</span>
                </div>
                <div class="legend-item">
                  <div class="building-marker mst">
                    <span class="material-icons">business</span>
                  </div>
                  <span>MST Building</span>
                </div>
                <div class="legend-item">
                  <div class="building-marker lib">
                    <span class="material-icons">library_books</span>
                  </div>
                  <span>Library</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Map markers -->
          <div
            v-for="marker in filteredMarkers"
            :key="marker.id"
            class="map-marker"
            :style="getMarkerStyle(marker)"
            @click="showMarkerInfo(marker)"
          >
            <div class="marker-icon">
              <span class="material-icons">
                {{ marker.marker_type === 'facility' ? 'business' : 'meeting_room' }}
              </span>
            </div>
            <div class="marker-label">{{ marker.name }}</div>
          </div>
        </div>
      </div>

      <!-- Zoom controls -->
      <div class="zoom-controls">
        <button @click="zoomIn" class="zoom-btn" title="Zoom In">+</button>
        <button @click="zoomOut" class="zoom-btn" title="Zoom Out">−</button>
      </div>

      <!-- Desktop Search Bar -->
      <div class="desktop-search">
        <span class="material-icons">search</span>
        <input
          v-model="searchText"
          type="text"
          placeholder="Search location, building, room..."
          @keyup.enter="performSearch"
        />
        <button v-if="searchText" class="clear-btn" @click="searchText = ''">
          <span class="material-icons">close</span>
        </button>
        <button class="search-btn" @click="performSearch">
          <span class="material-icons">arrow_forward</span>
        </button>
      </div>

      <!-- Desktop Location Button -->
      <button 
        class="desktop-location-btn" 
        @click="showLocateDialog"
        :class="{ active: currentLocation }"
        title="Set Current Location"
      >
        <span class="material-icons">location_on</span>
      </button>
    </div>

    <!-- Bottom controls - MOBILE ONLY -->
    <div class="bottom-controls mobile-only">
      <!-- Menu and action buttons -->
      <div class="action-row">
        <button class="menu-btn" @click="showMenu = true">
          <span class="material-icons">menu</span>
        </button>
        
        <div class="action-buttons">
          <button 
            class="action-btn"
            :class="{ active: currentLocation }"
            @click="showLocateDialog"
          >
            <span class="material-icons">location_on</span>
          </button>
          
          <button class="action-btn" @click="showRatingDialog">
            <span class="material-icons">star</span>
          </button>
          
          <button class="action-btn notification-btn" @click="goToNotifications">
            <span class="material-icons">notifications</span>
            <span v-if="unreadNotifications > 0" class="badge">
              {{ unreadNotifications }}
            </span>
          </button>
          
          <button class="action-btn" @click="goToChatbot">
            <span class="material-icons">smart_toy</span>
          </button>
          
          <button class="action-btn" @click="goToQRScanner">
            <span class="material-icons">photo_camera</span>
          </button>
        </div>
      </div>

      <!-- Search bar -->
      <div class="search-container">
        <div class="search-bar">
          <span class="material-icons">search</span>
          <input
            v-model="searchText"
            type="text"
            placeholder="Search location, building, room..."
            @keyup.enter="performSearch"
          />
          <button v-if="searchText" class="clear-btn" @click="searchText = ''">
            <span class="material-icons">close</span>
          </button>
          <button class="search-btn" @click="performSearch">
            <span class="material-icons">arrow_forward</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Slide-up Menu Sheet -->
    <div v-if="showMenu" class="menu-sheet-overlay" @click="showMenu = false">
      <div class="menu-sheet" @click.stop>
        <div class="menu-sheet-header">
          <div class="menu-sheet-handle"></div>
          <h3>Menu</h3>
        </div>
        <div class="menu-sheet-content">
          <div class="menu-item" @click="goToBuildingInfo">
            <div class="menu-item-icon">
              <span class="material-icons">business</span>
            </div>
            <span>Building Information</span>
          </div>
          <div class="menu-item" @click="goToRoomsInfo">
            <div class="menu-item-icon">
              <span class="material-icons">meeting_room</span>
            </div>
            <span>Rooms Info</span>
          </div>
          <div class="menu-item" @click="goToInstructorInfo">
            <div class="menu-item-icon">
              <span class="material-icons">school</span>
            </div>
            <span>Instructor Info</span>
          </div>
          <div class="menu-item" @click="goToEmployees">
            <div class="menu-item-icon">
              <span class="material-icons">people</span>
            </div>
            <span>Employees</span>
          </div>
        </div>
        <div class="menu-sheet-footer">
          <button class="menu-close-btn" @click="showMenu = false">
            <span class="material-icons">close</span>
            Close
          </button>
        </div>
      </div>
    </div>

    <!-- Locate Dialog -->
    <div v-if="showLocate" class="modal-overlay" @click="showLocate = false">
      <div class="dialog" @click.stop>
        <h3>Where are you now?</h3>
        <input
          v-model="locateInput"
          type="text"
          placeholder="Enter your current location"
        />
        <div class="dialog-actions">
          <button @click="showLocate = false">Cancel</button>
          <button class="primary" @click="setLocation">Set Location</button>
        </div>
      </div>
    </div>

    <!-- Rating Dialog -->
    <div v-if="showRating" class="modal-overlay" @click="showRating = false">
      <div class="dialog" @click.stop>
        <h3>Rate this App</h3>
        <div class="star-rating">
          <span
            v-for="n in 5"
            :key="n"
            class="star material-icons"
            :class="{ filled: n <= rating }"
            @click="rating = n"
          >
            {{ n <= rating ? 'star' : 'star_border' }}
          </span>
        </div>
        <textarea
          v-model="ratingComment"
          placeholder="Leave a comment (optional)"
          rows="3"
        ></textarea>
        <div class="dialog-actions">
          <button @click="showRating = false">Cancel</button>
          <button class="primary" @click="submitRating">Submit</button>
        </div>
      </div>
    </div>

    <!-- Search Results Dialog -->
    <div v-if="searchResults.length > 0" class="modal-overlay" @click="searchResults = []">
      <div class="dialog results-dialog" @click.stop>
        <h3>Search Results ({{ searchResults.length }})</h3>
        <div class="results-list">
          <div
            v-for="result in searchResults"
            :key="result.name"
            class="result-item"
            @click="selectSearchResult(result)"
          >
            <div class="result-icon">
              <span class="material-icons" style="color: #FF9800;">
                {{ result.type === 'Facility' ? 'business' : 'meeting_room' }}
              </span>
            </div>
            <div class="result-info">
              <div class="result-name">{{ result.name }}</div>
              <div class="result-type">{{ result.type }} - {{ result.info }}</div>
            </div>
          </div>
        </div>
        <button class="close-btn" @click="searchResults = []">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSyncStore } from '../stores/syncStore.js'
import api from '../services/api.js'

const router = useRouter()
const syncStore = useSyncStore()

// Data
const facilities = ref([])
const rooms = ref([])
const mapMarkers = ref([])
const selectedFacility = ref('')
const selectedRoom = ref('')
const isFacilitiesExpanded = ref(false)
const isRoomsExpanded = ref(false)
const searchText = ref('')
const currentLocation = ref('')
const unreadNotifications = ref(0)
const showMenu = ref(false)
const showLocate = ref(false)
const showRating = ref(false)
const locateInput = ref('')
const rating = ref(5)
const ratingComment = ref('')
const searchResults = ref([])

// Map zoom and pan
const scale = ref(1)
const mapTransformStyle = computed(() => ({
  transform: `scale(${scale.value})`,
  transformOrigin: 'center center'
}))

// Filtered markers based on selection
const filteredMarkers = computed(() => {
  if (!selectedFacility.value && !selectedRoom.value) {
    return mapMarkers.value
  }
  return mapMarkers.value.filter(marker => {
    if (selectedFacility.value && marker.marker_type === 'facility') {
      return marker.name === selectedFacility.value
    }
    if (selectedRoom.value && marker.marker_type === 'room') {
      return marker.name === selectedRoom.value
    }
    return false
  })
})

// Methods
const loadData = async () => {
  try {
    const [facRes, roomRes, markerRes] = await Promise.all([
      api.get('/facilities/'),
      api.get('/rooms/'),
      api.get('/core/map-markers/')
    ])
    facilities.value = facRes.data
    rooms.value = roomRes.data
    mapMarkers.value = markerRes.data
    if (facilities.value.length > 0) selectedFacility.value = facilities.value[0].name
    if (rooms.value.length > 0) selectedRoom.value = rooms.value[0].name
  } catch (error) {
    console.error('Error loading data:', error)
    // Fallback mock data when backend fails
    facilities.value = [
      { id: 1, name: 'MST Building', description: 'Main Science and Technology Building' },
      { id: 2, name: 'JST Building', description: 'Junior Science and Technology Building' },
      { id: 3, name: 'RST Building', description: 'Research Science and Technology Building' },
      { id: 4, name: 'Library', description: 'Main Campus Library' },
      { id: 5, name: 'Gymnasium', description: 'School Sports and Recreation Center' },
      { id: 6, name: 'Cafeteria', description: 'Main Campus Dining Hall' },
      { id: 7, name: 'Registrar Office', description: 'Student Services and Records' },
    ]
    rooms.value = [
      { id: 1, name: 'CL1', description: 'Computer Lab 1', facility: 'MST Building' },
      { id: 2, name: 'CL2', description: 'Computer Lab 2', facility: 'MST Building' },
      { id: 3, name: 'CL5', description: 'Computer Lab 5', facility: 'MST Building' },
      { id: 4, name: 'CL6', description: 'Computer Lab 6', facility: 'MST Building' },
      { id: 5, name: 'CR1', description: 'Classroom 1', facility: 'MST Building' },
      { id: 6, name: 'CR2', description: 'Classroom 2', facility: 'MST Building' },
      { id: 7, name: 'JST101', description: 'Lecture Room', facility: 'JST Building' },
      { id: 8, name: 'JST201', description: 'Laboratory', facility: 'JST Building' },
    ]
    mapMarkers.value = [
      { id: 1, name: 'MST Building', marker_type: 'facility', x_position: 0.3, y_position: 0.4 },
      { id: 2, name: 'JST Building', marker_type: 'facility', x_position: 0.6, y_position: 0.3 },
      { id: 3, name: 'RST Building', marker_type: 'facility', x_position: 0.5, y_position: 0.6 },
      { id: 4, name: 'Library', marker_type: 'facility', x_position: 0.2, y_position: 0.5 },
      { id: 5, name: 'CL1', marker_type: 'room', x_position: 0.32, y_position: 0.42 },
    ]
    if (facilities.value.length > 0) selectedFacility.value = facilities.value[0].name
    if (rooms.value.length > 0) selectedRoom.value = rooms.value[0].name
  }
}

const loadNotificationCount = async () => {
  try {
    const res = await api.get('/notifications/')
    unreadNotifications.value = res.data.filter(n => !n.is_read).length
  } catch (error) {
    console.error('Error loading notifications:', error)
  }
}

const toggleFacilities = () => {
  isFacilitiesExpanded.value = !isFacilitiesExpanded.value
  // Close rooms when facilities opens
  if (isFacilitiesExpanded.value) {
    isRoomsExpanded.value = false
  }
  console.log('Facilities toggled:', isFacilitiesExpanded.value, 'Rooms:', isRoomsExpanded.value)
}

const toggleRooms = () => {
  isRoomsExpanded.value = !isRoomsExpanded.value
  // Close facilities when rooms opens
  if (isRoomsExpanded.value) {
    isFacilitiesExpanded.value = false
  }
  console.log('Rooms toggled:', isRoomsExpanded.value, 'Facilities:', isFacilitiesExpanded.value)
}

const selectFacility = (name) => {
  selectedFacility.value = name
  isFacilitiesExpanded.value = false
}

const selectRoom = (name) => {
  selectedRoom.value = name
  isRoomsExpanded.value = false
}

const zoomIn = () => {
  scale.value = Math.min(scale.value * 1.2, 4)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value / 1.2, 0.8)
}

const handleZoom = (e) => {
  if (e.deltaY < 0) zoomIn()
  else zoomOut()
}

const getMarkerStyle = (marker) => ({
  left: `${marker.x_position * 100}%`,
  top: `${marker.y_position * 100}%`,
  color: marker.marker_type === 'facility' ? '#FF9800' : '#4CAF50'
})

const showMarkerInfo = (marker) => {
  alert(marker.name)
}

const showLocateDialog = () => {
  locateInput.value = currentLocation.value
  showLocate.value = true
}

const setLocation = () => {
  currentLocation.value = locateInput.value
  showLocate.value = false
}

const showRatingDialog = () => {
  rating.value = 5
  ratingComment.value = ''
  showRating.value = true
}

const submitRating = async () => {
  try {
    await api.post('/core/ratings/', {
      rating: rating.value,
      comment: ratingComment.value,
      category: 'app'
    })
    showRating.value = false
    alert('Thank you for your rating!')
  } catch (error) {
    console.error('Error submitting rating:', error)
  }
}

const performSearch = () => {
  if (!searchText.value) return
  
  const query = searchText.value.toLowerCase()
  const allLocations = [
    ...facilities.value.map(f => ({ name: f.name, type: 'Facility', info: f.description || 'Campus facility' })),
    ...rooms.value.map(r => ({ name: r.name, type: 'Room', info: r.description || 'Classroom/Lab' }))
  ]
  
  searchResults.value = allLocations.filter(loc => {
    return loc.name.toLowerCase().includes(query) || 
           loc.info.toLowerCase().includes(query)
  })
  
  if (searchResults.value.length === 0) {
    alert(`No locations found for "${searchText.value}"\n\nTry searching for:\n• CL1, CL2, CL3, CL4, CL5, CL6\n• CR1, CR2, CR3, CR4\n• MST Building, JST Building, RST Building\n• Library, Registrar, Cafeteria`)
  }
}

const selectSearchResult = (result) => {
  if (result.type === 'Facility') {
    selectedFacility.value = result.name
  } else {
    selectedRoom.value = result.name
  }
  searchResults.value = []
  searchText.value = ''
}

// Navigation
const goToNotifications = () => router.push('/notifications')
const goToChatbot = () => router.push('/chatbot')
const goToQRScanner = () => router.push('/qr-scanner')
const goToBuildingInfo = () => { showMenu.value = false; router.push('/building-info') }
const goToRoomsInfo = () => { showMenu.value = false; router.push('/rooms-info') }
const goToInstructorInfo = () => { showMenu.value = false; router.push('/instructor-info') }
const goToEmployees = () => { showMenu.value = false; router.push('/employees') }

// Lifecycle
let notificationTimer

onMounted(() => {
  loadData()
  loadNotificationCount()
  if (!syncStore.lastSyncedAt) {
    syncStore.sync()
  }
  // Auto-refresh notifications every 5 seconds
  notificationTimer = setInterval(loadNotificationCount, 5000)
})

onUnmounted(() => {
  if (notificationTimer) clearInterval(notificationTimer)
})
</script>

<style>
/* Styles moved to external file: src/assets/homeview.css */
@import '../assets/homeview.css';
</style>
