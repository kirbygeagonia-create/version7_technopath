<template>

  <div class="home-view">

    <!-- Onboarding Tutorial -->

    <OnboardingTutorial 

      v-if="showOnboarding" 

      ref="onboardingRef" 

      @complete="onOnboardingComplete" 

      @skip="onOnboardingSkip" 

    />



    <!-- Unified Top Search & Filter Area -->

    <div class="home-top-overlay">

      <!-- Primary Search Bar -->

      <div class="unified-search-container">

        <div class="unified-search-input-wrapper">

          <span class="material-icons search-icon">search</span>

          <input

            v-model="searchText"

            type="text"

            placeholder="Search locations, facilities..."

            @keyup.enter="performSearch"

            @input="debouncedSearch"

            class="unified-search-input"

          />

          <button v-if="searchText" class="clear-btn" @click="searchText = ''">

            <span class="material-icons">close</span>

          </button>

        </div>



        <!-- Search Autocomplete Suggestions -->

        <div v-if="searchSuggestions.length > 0 && searchText" class="search-suggestions unified-suggestions">

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

<<<<<<< HEAD


    </div>



    <!-- SEAIT Information Section -->

    <div class="seait-info-section">

      <div class="seait-header">

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



      <!-- Interactive Campus Map -->

      <div class="seait-map-section">

        <h2 class="seait-map-title">Interactive Campus Map</h2>

        <div class="map-wrapper seait-embedded-map">

          <div 

            class="map-container"

            ref="mapContainer"

            @wheel.prevent="handleZoom"

            @mousedown="startPan"

            @mousemove="handlePan"

            @mouseup="endPan"

            @mouseleave="endPan"

            @touchstart="startTouchPan"

            @touchmove="handleTouchPan"

            @touchend="endPan"

=======
      <!-- Scrollable Filter Chips -->
      <div class="filter-chips-container">
        <button 
          class="filter-chip" 
          :class="{ active: !selectedFacility && !selectedRoom }"
          @click="clearFilters"
        >
          All
        </button>
        <button 
          v-for="facility in facilities"
          :key="facility.id"
          class="filter-chip"
          :class="{ active: selectedFacility === facility.name }"
          @click="selectFacility(facility.name)"
        >
          {{ facility.name }}
        </button>
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
    <div class="map-wrapper">
      <div 
        class="map-container"
        ref="mapContainer"
        @wheel.prevent="handleZoom"
        @mousedown="startPan"
        @mousemove="handlePan"
        @mouseup="endPan"
        @mouseleave="endPan"
        @touchstart="startTouchPan"
        @touchmove="handleTouchPan"
        @touchend="endPan"
      >
        <div 
          class="map-content"
          :style="mapTransformStyle"
        >
          <!-- SEAIT Campus Map SVG -->
          <div class="seait-map-wrapper">
            <img 
              src="../assets/SEAIT_Map.svg" 
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
>>>>>>> 2120b5cc5792784b71f56272822728812e4d775e
          >

            <div 

              class="map-content"

              :style="mapTransformStyle"

            >

              <div class="campus-map-wrapper">

                <img

                  src="../assets/Map_labeled.svg"

                  class="campus-map-image"

                  alt="Campus Map"

                  draggable="false"

                />

              </div>

            </div>

          </div>

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

    </div>



    <!-- Bottom controls - MOBILE ONLY -->

    <div class="bottom-controls mobile-only">

      <!-- Menu and action buttons -->

      <div class="action-row">

        <button class="menu-btn" @click="showMenu = true">

          <span class="material-icons">menu</span>

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

          <div class="menu-divider"></div>

          <div class="menu-item" @click="openRateApp">

            <div class="menu-item-icon">

              <span class="material-icons">star</span>

            </div>

            <span>Rate App</span>

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

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import offlineData from '../services/offlineData.js'
import { useSyncStore } from '../stores/syncStore.js'
import { useAuthStore } from '../stores/authStore.js'
import { showToast } from '../services/toast.js'
import OnboardingTutorial from '../components/OnboardingTutorial.vue'
import { isOnline } from '../services/sync.js'
import api from '../services/api.js'
import useMapPanZoom from '../composables/useMapPanZoom.js'
import { registerBones } from 'boneyard-js'
import AppSkeleton from '../components/AppSkeleton.vue'

registerBones({
  'home-announcement': {
    width: 400, height: 90,
    bones: [
      { x: 0, y: 0,  w: 22, h: 18, r: 9 },
      { x: 0, y: 26, w: 68, h: 16, r: 6 },
      { x: 0, y: 50, w: 90, h: 12, r: 5 },
      { x: 0, y: 68, w: 72, h: 12, r: 5 },
    ]
  }
})



const router = useRouter()

const route = useRoute()

const syncStore = useSyncStore()

const authStore = useAuthStore()



// Data

const facilities = ref([])

const rooms = ref([])

// const mapMarkers = ref([]) // Disabled - markers removed from map

const selectedFacility = ref('')

const selectedRoom = ref('')
<<<<<<< HEAD

=======
// Course filter — populated from /api/rooms/courses/
const courses = ref([])
const activeCourse = ref(localStorage.getItem('tp_selected_course') || '')
>>>>>>> 2120b5cc5792784b71f56272822728812e4d775e
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

const recentSearches = ref([])

const searchSuggestions = ref([])

let searchDebounceTimer = null

const selectedMarker = ref(null)

const isMarkerInfoVisible = ref(false)



// Map zoom and pan — use shared composable

const mapContainer = ref(null)

const {

  scale, translateX, translateY,

  transformStyle: mapTransformStyle,

  zoomIn, zoomOut,

  onPointerDown: startPan,

  onPointerMove: handlePan,

  onPointerUp: endPan,

  onWheel: handleZoom,

  onTouchStart: startTouchPan,

  onTouchMove: handleTouchPan,

  initTransform

} = useMapPanZoom()

<<<<<<< HEAD


// Filtered markers - DISABLED (markers removed from map view)

// const filteredMarkers = computed(() => {

//   if (!selectedFacility.value && !selectedRoom.value) {

//     return mapMarkers.value

//   }

//   return mapMarkers.value.filter(marker => {

//     if (selectedFacility.value && marker.marker_type === 'facility') {

//       return marker.name === selectedFacility.value

//     }

//     if (selectedRoom.value && marker.marker_type === 'room') {

//       return marker.name === selectedRoom.value

//     }

//     return true

//   })

// })


=======
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
>>>>>>> 2120b5cc5792784b71f56272822728812e4d775e

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

    
<<<<<<< HEAD
=======
    // Load course list for filter chips
    if (isOnline()) {
      try {
        const coursesRes = await api.get('/rooms/courses/')
        courses.value = coursesRes.data
      } catch {
        courses.value = []
      }
    }
>>>>>>> 2120b5cc5792784b71f56272822728812e4d775e

    // Try to load search history from API if online

    if (isOnline()) {

      try {

        const searchRes = await api.get('/core/search-history/')

        recentSearches.value = searchRes.data.slice(0, 10)

      } catch {

        // Silently fail for search history

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



// Navigation

const goToNotifications = () => router.push('/notifications')

const goToChatbot = () => router.push('/chatbot')

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
}

</style>

