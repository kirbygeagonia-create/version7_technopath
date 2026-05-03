<template>
  <div class="home-view-wrapper">
    <div class="home-view">

      <!-- Home Header — icon + title on left, search + action icons on right -->
      <div class="settings-header home-header">
        <div class="home-header-left">
          <div class="settings-header-icon">
            <span class="material-icons">home</span>
          </div>
          <div class="settings-header-text">
            <h1>Home</h1>
            <p>Explore SEAIT campus and facilities</p>
          </div>
        </div>
      </div>

      <!-- Onboarding Tutorial -->
      <OnboardingTutorial
        v-if="showOnboarding"
        ref="onboardingRef"
        @complete="onOnboardingComplete"
        @skip="onOnboardingSkip"
      />

    <!-- SEAIT Information Section -->

    <div class="seait-info-section">

      <div class="seait-header reveal">

        <h1 class="seait-title">SEAIT</h1>

        <p class="seait-subtitle">South East Asian Institute of Technology</p>

      </div>



      <div class="seait-highlights">

        <div class="highlight-card">

          <span class="material-icons highlight-icon">school</span>

          <h3>Quality Education</h3>

          <p>Providing excellent technical and vocational education since establishment</p>

        </div>



        <div class="highlight-card">

          <span class="material-icons highlight-icon">engineering</span>

          <h3>Modern Facilities</h3>

          <p>State-of-the-art classrooms, laboratories, and workshop areas</p>

        </div>



        <div class="highlight-card">

          <span class="material-icons highlight-icon">location_on</span>

          <h3>Strategic Location</h3>

          <p>Conveniently located in the heart of the community with easy access</p>

        </div>



        <div class="highlight-card">

          <span class="material-icons highlight-icon">groups</span>

          <h3>Expert Faculty</h3>

          <p>Dedicated instructors and staff committed to student success</p>

        </div>

      </div>

      <!-- Announcements Feed -->
      <div v-if="announcementsLoading" class="home-announcement-sk-wrap">
        <AppSkeleton :loading="announcementsLoading" />
      </div>
      <div class="home-announcements" v-else-if="announcementsRef.length > 0">
        <h2 class="home-section-title">
          <span class="material-icons">campaign</span>
          Announcements
        </h2>
        <div
          v-for="ann in announcementsRef"
          :key="ann.id"
          class="announcement-card"
        >
          <div class="announcement-header">
            <span
              class="announcement-dept-chip"
              :style="{ background: getDeptColor(ann.department_color) }"
            >{{ ann.department_label || 'Campus' }}</span>
            <span class="announcement-date">{{ formatDate(ann.published_at || ann.created_at) }}</span>
          </div>
          <h3 class="announcement-title">{{ ann.title }}</h3>
          <p class="announcement-body" v-if="ann.body">{{ ann.body.substring(0, 120) }}{{ ann.body.length > 120 ? '…' : '' }}</p>
        </div>
      </div>


      <!-- Course Filter Row — highlight rooms by academic program -->
      <div v-if="courses.length > 0" class="course-filter-row">
        <span class="course-filter-label">
          <span class="material-icons" style="font-size:13px;vertical-align:middle">school</span>
          My Course:
        </span>
        <div class="course-chips-scroll">
          <button
            class="course-chip"
            :class="{ active: !activeCourse }"
            @click="setCourse('')"
          >All</button>
          <button
            v-for="course in courses"
            :key="course.course_code"
            class="course-chip"
            :class="{ active: activeCourse === course.course_code }"
            :style="activeCourse === course.course_code
              ? { background: course.course_color, color: '#fff', borderColor: course.course_color }
              : { borderColor: course.course_color, color: course.course_color }"
            @click="setCourse(course.course_code)"
          >{{ course.course_code }}</button>
        </div>
      </div>
    </div>

    <!-- Map container with markers -->
    <div class="home-map-outer">
      <div class="map-wrapper">
        <div 
          class="map-container"
          ref="mapContainer"
          @mousedown="startPan"
          @mousemove="handlePan"
          @mouseup="endPan"
          @mouseleave="endPan"
          @touchstart.passive="startTouchPan"
          @touchmove.passive="handleTouchPan"
          @touchend="endTouchPan"
        >
          <div 
            class="map-content"
            :style="mapTransformStyle"
          >
            <!-- SEAIT Campus Map SVG -->
            <div class="seait-map-wrapper">
              <img 
                src="../assets/Map_labeled.svg" 
                class="seait-map-image"
                alt="SEAIT Campus Map"
                draggable="false"
              />
            </div>
            
            <!-- Map markers overlay -->
            <div
              v-for="marker in filteredMarkers"
              :key="marker.id"
              class="map-marker"
              :style="[getMarkerStyle(marker), markerCourseStyle(marker)]"
              @click.stop="showMarkerInfo(marker)"
            >
            </div>
          </div>
        </div>
      </div>

      <!-- Map zoom controls — outside overflow:hidden, overlaid via outer wrapper -->
      <div class="home-map-controls">
        <button class="map-ctrl-btn" @click="zoomIn" title="Zoom in" aria-label="Zoom in">
          <span class="material-icons">add</span>
        </button>
        <div class="map-ctrl-divider"></div>
        <button class="map-ctrl-btn" @click="zoomOut" title="Zoom out" aria-label="Zoom out">
          <span class="material-icons">remove</span>
        </button>
        <div class="map-ctrl-divider"></div>
        <button class="map-ctrl-btn map-ctrl-reset" @click="resetTransform" title="Reset view" aria-label="Reset map view">
          <span class="material-icons">center_focus_strong</span>
        </button>
      </div>
    </div>

    <!-- Campus Image Gallery -->

      <div class="seait-gallery">

        <h2 class="gallery-title">Campus Gallery</h2>

        <div class="gallery-grid">

          <div class="gallery-item">

            <img src="../assets/campus-1.jpg" alt="SEAIT Campus Aerial View 1" />

          </div>

          <div class="gallery-item">

            <img src="../assets/campus-2.jpg" alt="SEAIT Campus Aerial View 2" />

          </div>

          <div class="gallery-item">

            <img src="../assets/campus-3.jpg" alt="SEAIT Campus Aerial View 3" />

          </div>

          <div class="gallery-item">

            <img src="../assets/campus-4.jpg" alt="SEAIT Campus Aerial View 4" />

          </div>

          <div class="gallery-item gallery-item-wide">

            <img src="../assets/campus-5.jpg" alt="SEAIT Campus Panoramic View" />

          </div>

        </div>

      </div>



    <!-- Bottom controls - MOBILE ONLY -->
    <div class="bottom-controls mobile-only">
      <!-- Menu button, Chatbot, Search, Notifications, Star -->
      <div class="action-row">
        <!-- Hamburger menu -->
        <button class="menu-btn" @click="showMenu = true">
          <span class="material-icons">menu</span>
        </button>

        <!-- Chatbot button (next to hamburger) -->
        <button
          class="bottom-action-btn"
          @click="goToChatbot"
          title="Chatbot"
          aria-label="Open chatbot"
        >
          <span class="material-icons">smart_toy</span>
        </button>

        <!-- Search bar -->
        <div class="bottom-search-bar">
          <div class="bottom-search-inner" :class="{ 'is-focused': searchFocused }">
            <span class="material-icons bottom-search-icon">search</span>
            <input
              v-model="searchText"
              type="text"
              placeholder="Search locations..."
              @keyup.enter="performSearch"
              @input="debouncedSearch"
              @focus="searchFocused = true"
              @blur="searchFocused = false"
              class="bottom-search-input"
            />
            <button v-if="searchText" class="bottom-search-clear" @click="searchText = ''; searchSuggestions = []">
              <span class="material-icons">close</span>
            </button>
          </div>

          <!-- Autocomplete dropdown -->
          <div v-if="searchSuggestions.length > 0 && searchText" class="bottom-search-suggestions">
            <div
              v-for="suggestion in searchSuggestions.slice(0, 6)"
              :key="suggestion.name"
              class="suggestion-item"
              @click="selectSuggestion(suggestion)"
            >
              <span class="material-icons">
                {{ suggestion.type === 'Facility' ? 'business' : 'meeting_room' }}
              </span>
              <div class="suggestion-info">
                <span class="suggestion-name">{{ suggestion.name }}</span>
                <span class="suggestion-type">{{ suggestion.info }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Notifications button -->
        <button
          class="bottom-action-btn"
          @click="goToNotifications"
          title="Notifications"
          aria-label="Notifications"
        >
          <span class="material-icons">notifications</span>
          <span v-if="unreadNotifications > 0" class="bottom-action-badge">
            {{ unreadNotifications > 9 ? '9+' : unreadNotifications }}
          </span>
        </button>

        <!-- Star/Ratings button -->
        <button
          class="bottom-action-btn"
          @click="showRatingDialog"
          title="Rate App"
          aria-label="Rate app"
        >
          <span class="material-icons">star</span>
        </button>
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



    <!-- Rating Sheet -->
    <BottomSheetOverlay v-model="showRating" max-height="60vh">
      <div class="rating-sheet-content">
        <h3 class="rating-sheet-title">Rate TechnoPath</h3>
        <div class="star-rating">
          <span
            v-for="n in 5"
            :key="n"
            class="star material-icons"
            :class="{ filled: n <= rating }"
            @click="rating = n"
          >{{ n <= rating ? 'star' : 'star_border' }}</span>
        </div>
        <p class="rating-hint">{{ ratingHint }}</p>
        <textarea
          v-model="ratingComment"
          class="rating-textarea"
          placeholder="Leave a comment (optional)"
          rows="3"
        ></textarea>
        <div class="rating-actions">
          <button class="rating-cancel-btn" @click="showRating = false">Cancel</button>
          <button class="rating-submit-btn" @click="submitRating">Submit</button>
        </div>
      </div>
    </BottomSheetOverlay>



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

    <!-- Floating Action Buttons — chatbot only (notifications + ratings now in bottom nav) -->
    <div class="home-fab-stack">
      <button class="home-fab home-fab-chatbot" @click="goToChatbot" title="Open Chatbot" aria-label="Open chatbot">
        <span class="material-icons">smart_toy</span>
      </button>
      <!-- Desktop-only extras since desktop has sidebar nav instead of bottom nav -->
      <button class="home-fab home-fab-notifications desktop-only" @click="goToNotifications" title="Notifications" aria-label="Notifications">
        <span class="material-icons">notifications</span>
        <span v-if="unreadNotifications > 0" class="fab-badge">{{ unreadNotifications }}</span>
      </button>
      <button class="home-fab home-fab-ratings desktop-only" @click="showRatingDialog" title="Rate App" aria-label="Rate app">
        <span class="material-icons">star</span>
      </button>
    </div>

    <!-- Chatbot Overlay Sheet -->
    <BottomSheetOverlay v-model="showChatbotSheet" max-height="90vh">
      <ChatbotView :embedded="true" @close="showChatbotSheet = false" />
    </BottomSheetOverlay>

    <!-- Notifications Overlay Sheet -->
    <BottomSheetOverlay v-model="showNotificationsSheet" max-height="88vh">
      <NotificationsView :embedded="true" @close="showNotificationsSheet = false" />
    </BottomSheetOverlay>

  </div>
  </div>

</template>



<script setup>

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import offlineData from '../services/offlineData.js'
import { useSyncStore } from '../stores/syncStore.js'
import { useAuthStore } from '../stores/authStore.js'
import { showToast } from '../services/toast.js'
import OnboardingTutorial from '../components/OnboardingTutorial.vue'
import useMapPanZoom from '../composables/useMapPanZoom.js'
import AppSkeleton from '../components/AppSkeleton.vue'
import { isOnline } from '../services/sync.js'
import api from '../services/api.js'
import BottomSheetOverlay from '../components/BottomSheetOverlay.vue'
import ChatbotView        from './ChatbotView.vue'
import NotificationsView  from './NotificationsView.vue'

const router = useRouter()

const route = useRoute()

const syncStore = useSyncStore()

const authStore = useAuthStore()



// Data

const facilities = ref([])

const rooms = ref([])

const mapMarkers = ref([])

const selectedFacility = ref('')

const selectedRoom = ref('')
// Course filter — populated from /api/rooms/courses/
const courses = ref([])
const activeCourse = ref(localStorage.getItem('tp_selected_course') || '')
const isFacilitiesExpanded = ref(false)

const isRoomsExpanded = ref(false)

const searchText = ref('')
const searchFocused = ref(false)

const currentLocation = ref('')

const unreadNotifications = ref(0)

const showMenu = ref(false)

const showLocate = ref(false)

const showRating = ref(false)

const locateInput = ref('')

const rating = ref(5)

const ratingComment = ref('')

const searchResults = ref([])

const recentSearches = ref([])

const searchSuggestions = ref([])

let searchDebounceTimer = null

// Announcements
const announcementsRef = ref([])
const announcementsLoading = ref(false)
async function loadAnnouncements() {
  const now = Date.now()
  if (now - lastFetchTime.announcements < CACHE_DURATION) return
  lastFetchTime.announcements = now

  announcementsLoading.value = true
  try {
    const res = await api.get('/announcements/')
    announcementsRef.value = (res.data || [])
      .filter(a => a.status === 'published')
      .slice(0, 3) // Show max 3 on home
  } catch (e) {
    if (e.response?.status !== 429) {
      console.error('Error loading announcements:', e)
    }
  }
  announcementsLoading.value = false
}

function getDeptColor(colorName) {
  const colors = {
    orange: '#FF9800', teal: '#009688', blue: '#2196F3',
    green: '#4CAF50', red: '#F44336', purple: '#9C27B0',
    amber: '#FFC107', charcoal: '#607D8B', dark_blue: '#1565C0',
    brown: '#795548', indigo: '#3F51B5', dark_green: '#2E7D32',
  }
  return colors[colorName] || '#FF9800'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
}

const selectedMarker = ref(null)

const isMarkerInfoVisible = ref(false)



// Map zoom and pan — use shared composable

const mapContainer = ref(null)

const {

  scale, translateX, translateY,

  transformStyle: mapTransformStyle,

  zoomIn, zoomOut, resetTransform,

  onPointerDown: startPan,

  onPointerMove: handlePan,

  onPointerUp: endPan,

  onWheel: handleZoom,

  onTouchStart: startTouchPan,

  onTouchMove: handleTouchPan,

  onTouchEnd: endTouchPan,

  initTransform

} = useMapPanZoom()

// Filtered markers based on selection
const filteredMarkers = computed(() => {
  let base = mapMarkers.value

  // Facility/room type filter
  if (selectedFacility.value || selectedRoom.value) {
    base = base.filter(marker => {
      if (selectedFacility.value && marker.marker_type === 'facility') {
        return marker.name === selectedFacility.value
      }
      if (selectedRoom.value && marker.marker_type === 'room') {
        return marker.name === selectedRoom.value
      }
      return false
    })
  }

  return base
})

// Separate from filter — dim markers that don't belong to selected course
function markerCourseStyle(marker) {
  if (!activeCourse.value) return {}
  if (marker.marker_type === 'facility') return {}
  const matched = marker.course_code === activeCourse.value
  if (!matched) return { opacity: '0.15', filter: 'grayscale(1)', pointerEvents: 'none' }
  const course = courses.value.find(c => c.course_code === activeCourse.value)
  return course ? { '--marker-color': course.course_color } : {}
}

function setCourse(code) {
  activeCourse.value = activeCourse.value === code ? '' : code
  if (activeCourse.value) {
    localStorage.setItem('tp_selected_course', activeCourse.value)
  } else {
    localStorage.removeItem('tp_selected_course')
  }
}

// Methods

const loadData = async () => {

  try {

    // Use offline-aware data service

    const [facilitiesRes, roomsRes] = await Promise.all([

      offlineData.getFacilities(),

      offlineData.getRooms()

      // offlineData.getMapMarkers() // Disabled - markers removed

    ])

    

    facilities.value = facilitiesRes.data

    rooms.value = roomsRes.data

    // mapMarkers.value = markerRes.data // Disabled - markers removed

    

    // Log data source for debugging

    console.log(`[HomeView] Data loaded - Facilities: ${facilitiesRes.source}, Rooms: ${roomsRes.source}`)

    

    // If any data came from cache and is stale, show a subtle notification

    if (facilitiesRes.stale || roomsRes.stale) {

      console.log('[HomeView] Using cached data - will sync when connection is available')

    }

    // Load course list for filter chips
    if (isOnline()) {
      try {
        const coursesRes = await api.get('/rooms/courses/')
        courses.value = coursesRes.data
      } catch {
        courses.value = []
      }
    }

    // Try to load search history from API if online (with cache)
    if (isOnline()) {
      const now = Date.now()
      if (now - lastFetchTime.searchHistory >= CACHE_DURATION) {
        lastFetchTime.searchHistory = now
        try {
          const searchRes = await api.get('/core/search-history/')
          recentSearches.value = searchRes.data.slice(0, 10)
        } catch (e) {
          if (e.response?.status !== 429) {
            console.error('Error loading search history:', e)
          }
        }
      }
    }

  } catch (error) {

    console.error('Error loading data:', error)

    // Final fallback mock data

    useFallbackData()

  }

}



const useFallbackData = () => {

  facilities.value = [

    { id: 1, name: 'Library', description: 'Main Campus Library' },

    { id: 2, name: 'Gymnasium', description: 'School Sports and Recreation Center' },

    { id: 3, name: 'Cafeteria', description: 'Main Campus Dining Hall' },

    { id: 4, name: 'Registrar Office', description: 'Student Services and Records' },

    { id: 5, name: 'CL1', description: 'Classroom Building 1' },

  ]

  rooms.value = []

  // mapMarkers disabled - markers removed from map

  // mapMarkers.value = [

  //   { id: 1, name: 'Library', marker_type: 'facility', x_position: 0.2, y_position: 0.5 },

  //   { id: 2, name: 'Registrar Office', marker_type: 'facility', x_position: 0.7, y_position: 0.5 },

  //   { id: 3, name: 'Cafeteria', marker_type: 'facility', x_position: 0.8, y_position: 0.7 },

  //   { id: 4, name: 'Gymnasium', marker_type: 'facility', x_position: 0.15, y_position: 0.8 },

  //   { id: 5, name: 'CL1', marker_type: 'facility', x_position: 0.5, y_position: 0.6 },

  // ]

}



const getMarkerStyle = (marker) => ({
  left: `${((marker.x_position ?? 0.5) * 100).toFixed(2)}%`,
  top: `${((marker.y_position ?? 0.5) * 100).toFixed(2)}%`,
  color: marker.marker_type === 'facility' ? '#FF9800' : '#4CAF50'
})



const handleDeepLink = () => {

  const source = route.query.source

  const location = route.query.location

  const welcome = route.query.welcome

  

  // Handle welcome parameter for first-time visitors

  if (welcome === 'true') {

    showToast('Welcome to SEAIT Campus! Use the map to find your way around.', 'success', 5000)

    // Default to first facility

    if (facilities.value.length > 0 && !selectedFacility.value) {

      selectedFacility.value = facilities.value[0].name

    }

    return

  }

  

  // Default facility and room selection

  if (facilities.value.length > 0 && !selectedFacility.value) selectedFacility.value = facilities.value[0].name

  if (rooms.value.length > 0 && !selectedRoom.value) selectedRoom.value = rooms.value[0].name

}



watch(() => route.query, () => {

  handleDeepLink()

})



// Cache for API requests to prevent 429 errors
const lastFetchTime = {
  notifications: 0,
  announcements: 0,
  searchHistory: 0
}
const CACHE_DURATION = 30000 // 30 seconds

const loadNotificationCount = async () => {
  const now = Date.now()
  if (now - lastFetchTime.notifications < CACHE_DURATION) return
  lastFetchTime.notifications = now

  try {
    const res = await api.get('/notifications/')
    unreadNotifications.value = res.data.filter(n => !n.is_read).length
  } catch (error) {
    if (error.response?.status !== 429) {
      console.error('Error loading notifications:', error)
    }
  }
}



const toggleFacilities = () => {

  isFacilitiesExpanded.value = !isFacilitiesExpanded.value

  if (isFacilitiesExpanded.value) isRoomsExpanded.value = false

}



const toggleRooms = () => {

  isRoomsExpanded.value = !isRoomsExpanded.value

  if (isRoomsExpanded.value) isFacilitiesExpanded.value = false

}



// Filtered rooms based on selected facility

const filteredRooms = computed(() => {

  if (!selectedFacility.value) {

    return rooms.value

  }

  return rooms.value.filter(room => {

    // Support both facility name and facility_id matching

    const roomFacility = room.facility || room.facility_name

    const roomFacilityId = room.facility_id

    

    // Check if room belongs to selected facility by name

    if (roomFacility === selectedFacility.value) return true

    

    // Check if room belongs by facility_id - find facility ID

    const facility = facilities.value.find(f => f.name === selectedFacility.value)

    if (facility && roomFacilityId === facility.id) return true

    

    return false

  })

})



const selectFacility = (name) => {

  selectedFacility.value = name

  isFacilitiesExpanded.value = false

  // Reset room selection if current room is not in this facility

  if (selectedRoom.value) {

    const roomInFacility = filteredRooms.value.find(r => r.name === selectedRoom.value)

    if (!roomInFacility) {

      selectedRoom.value = ''

    }

  }

}



const clearFilters = () => {

  selectedFacility.value = ''

  selectedRoom.value = ''

}



const selectRoom = (name) => {

  selectedRoom.value = name

  isRoomsExpanded.value = false

  // Auto-select the parent facility

  const room = rooms.value.find(r => r.name === name)

  if (room && room.facility) {

    selectedFacility.value = room.facility

  }

}



const showMarkerInfo = (marker) => {

  selectedMarker.value = marker

  isMarkerInfoVisible.value = true

}



const closeMarkerInfo = () => {

  isMarkerInfoVisible.value = false

  selectedMarker.value = null

}



const addToFavorites = () => {

  if (!selectedMarker.value) return

  

  const marker = selectedMarker.value

  const favorites = JSON.parse(localStorage.getItem('tp_favorites') || '[]')

  

  // Generate composite key to prevent ID collisions between views

  const compositeId = `${marker.marker_type}_${marker.id || marker.name}`

  

  // Check if already in favorites using composite ID

  if (favorites.some(f => f.id === compositeId)) {

    showToast('This location is already in your favorites!', 'info')

    return

  }

  

  // Add to favorites with composite ID

  favorites.push({

    id: compositeId,

    name: marker.name,

    type: marker.marker_type,

    description: marker.description || marker.marker_type,

    addedAt: new Date().toISOString()

  })

  

  localStorage.setItem('tp_favorites', JSON.stringify(favorites))

  showToast(`${marker.name} added to favorites!`, 'success')

}



const navigateToMarker = () => {

  if (!selectedMarker.value) return

  router.push({

    path: '/navigate',

    query: { to: selectedMarker.value.name }

  })

  closeMarkerInfo()

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

    showToast('Thank you for your rating!', 'success')

  } catch (error) {

    console.error('Error submitting rating:', error)

  }

}



// Search suggestions with debouncing

const updateSearchSuggestions = () => {

  if (!searchText.value) {

    searchSuggestions.value = []

    return

  }

  

  const query = searchText.value.toLowerCase()

  const allLocations = [

    ...facilities.value.map(f => ({ name: f.name, type: 'Facility', info: f.description || 'Campus facility' })),

    ...rooms.value.map(r => ({ name: r.name, type: 'Room', info: r.description || 'Classroom/Lab' }))

  ]

  

  searchSuggestions.value = allLocations.filter(loc => {

    return loc.name.toLowerCase().includes(query) || 

           loc.info.toLowerCase().includes(query)

  })

}



const debouncedSearch = () => {

  clearTimeout(searchDebounceTimer)

  searchDebounceTimer = setTimeout(updateSearchSuggestions, 200) // 200ms debounce

}



const selectSuggestion = (suggestion) => {

  searchText.value = suggestion.name

  searchSuggestions.value = []

  performSearch()

}



const performSearch = async () => {

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

  

  // Save search to history if results found

  if (searchResults.value.length > 0) {

    try {

      await api.post('/core/search-history/', {

        query: searchText.value,

        results_count: searchResults.value.length,

        was_clicked: false

      })

      // Refresh recent searches

      const res = await api.get('/core/search-history/')

      recentSearches.value = res.data.slice(0, 10)

    } catch (error) {

      console.log('Failed to save search history')

    }

  }

  

  if (searchResults.value.length === 0) {

    showToast(`No locations found for "${searchText.value}"`, 'warning')

  }

}



const selectRecentSearch = (query) => {

  searchText.value = query

  performSearch()

}



const clearRecentSearches = async () => {

  try {

    // Delete each search history entry

    await Promise.all(recentSearches.value.map(search => 

      api.delete(`/core/search-history/${search.id}/`).catch(() => {})

    ))

    recentSearches.value = []

  } catch (error) {

    console.error('Error clearing search history:', error)

    recentSearches.value = []

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



// Navigation - Using overlay sheets instead of full page navigation
const showChatbotSheet       = ref(false)
const showNotificationsSheet = ref(false)

const goToNotifications = () => { showNotificationsSheet.value = true }

const goToChatbot       = () => { showChatbotSheet.value       = true }

const goToBuildingInfo = () => { showMenu.value = false; router.push('/building-info') }

const goToRoomsInfo = () => { showMenu.value = false; router.push('/rooms-info') }

const goToInstructorInfo = () => { showMenu.value = false; router.push('/instructor-info') }

const goToEmployees = () => { showMenu.value = false; router.push('/employees') }

const goToAdmin = () => { showMenu.value = false; router.push('/admin') }

const goToNavGraph = () => { showMenu.value = false; router.push({ path: '/admin', query: { section: 'navigation' } }) }

const openRateApp = () => { showMenu.value = false; showRating.value = true }



const onboardingRef = ref(null)

const showOnboarding = ref(false)



const onOnboardingComplete = () => {

  localStorage.setItem('tp_onboarding_completed', 'true')

  localStorage.setItem('tp_onboarding_completed_at', Date.now().toString())

  showOnboarding.value = false

}



const onOnboardingSkip = () => {

  localStorage.setItem('tp_onboarding_completed', 'true')

  localStorage.setItem('tp_onboarding_completed_at', Date.now().toString())

  showOnboarding.value = false

}



// Lifecycle

onMounted(async () => {

  await loadData()

  loadAnnouncements()

  handleDeepLink()

  loadNotificationCount()

  if (!syncStore.lastSyncedAt) {

    syncStore.sync()

  }

  // Note: Removed 5-second aggressive polling

  // sync.js handles periodic sync (30s interval) which includes notifications

  

  // Check if onboarding should be shown (only first time)

  const onboardingCompleted = localStorage.getItem('tp_onboarding_completed')

  if (!onboardingCompleted) {

    showOnboarding.value = true

  }

})

</script>



<style>

/* Styles moved to external file: src/assets/homeview.css */

@import '../assets/homeview.css';
@import '../assets/settings.css';

/* Desktop Floating Action Buttons - Aligned to the right */
.desktop-fab-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  z-index: 100;
}

.desktop-notification-btn,
.desktop-chatbot-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #1a2b3c;
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
}

.desktop-notification-btn:hover,
.desktop-chatbot-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.desktop-notification-btn .material-icons,
.desktop-chatbot-btn .material-icons {
  font-size: 24px;
  color: white;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ff4444;
  color: white;
  font-size: 11px;
  font-weight: bold;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.home-announcement-sk-wrap {
  height: 90px;
  margin-bottom: 12px;
  border-radius: 12px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .desktop-fab-container {
    bottom: 20px;
    right: 20px;
    left: auto;
  }
  .home-fab-stack,
  .home-fab-chatbot,
  .home-fab-notifications.desktop-only,
  .home-fab-ratings.desktop-only {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
  }
}

</style>

