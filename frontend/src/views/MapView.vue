<template>
  <div class="mapview">
    <!-- Top bar -->
    <header class="mapview-header">
      <button class="mapview-back-btn" @click="$router.back()">
        <span class="material-icons">arrow_back</span>
      </button>
      <h1 class="mapview-title">Explore Campus</h1>
      <button class="mapview-action-btn" @click="showLabels = !showLabels" :title="showLabels ? 'Hide Labels' : 'Show Labels'">
        <span class="material-icons">{{ showLabels ? 'label' : 'label_off' }}</span>
      </button>
    </header>

    <!-- Map container with pan/zoom -->
    <div class="mapview-canvas" ref="canvasRef"
      @wheel.prevent="onWheel"
      @mousedown="onPointerDown"
      @mousemove="onPointerMove"
      @mouseup="onPointerUp"
      @mouseleave="onPointerUp"
      @touchstart.prevent="onTouchStart"
      @touchmove.prevent="onTouchMove"
      @touchend="onPointerUp"
    >
      <div class="mapview-transform" :style="transformStyle">
        <!-- SVG Map -->
        <img 
          src="../assets/SEAIT_Map.svg" 
          class="mapview-svg" 
          alt="SEAIT Campus Map" 
          draggable="false"
          @load="onMapLoad"
        />

        <!-- Markers overlay -->
        <div 
          v-for="marker in visibleMarkers" 
          :key="marker.id"
          class="mapview-marker"
          :class="{ 
            'mapview-marker-selected': selectedMarker?.id === marker.id,
            'mapview-marker-facility': marker.marker_type === 'facility',
            'mapview-marker-room': marker.marker_type === 'room'
          }"
          :style="getMarkerPosition(marker)"
          @click.stop="selectMarker(marker)"
        >
          <div class="mapview-marker-pin">
            <span class="material-icons">
              {{ getMarkerIcon(marker) }}
            </span>
          </div>
          <span v-if="showLabels" class="mapview-marker-label">{{ marker.name }}</span>
        </div>
      </div>
    </div>

    <!-- Zoom Controls -->
    <div class="mapview-zoom">
      <button @click="zoomIn" class="mapview-zoom-btn" title="Zoom In">
        <span class="material-icons">add</span>
      </button>
      <button @click="zoomOut" class="mapview-zoom-btn" title="Zoom Out">
        <span class="material-icons">remove</span>
      </button>
    </div>

    <!-- Filter chips -->
    <div class="mapview-filters">
      <button 
        v-for="ft in filterTypes" :key="ft.value"
        class="mapview-chip"
        :class="{ active: activeFilter === ft.value }"
        @click="activeFilter = activeFilter === ft.value ? 'all' : ft.value"
      >
        <span class="material-icons">{{ ft.icon }}</span>
        {{ ft.label }}
      </button>
    </div>

    <!-- Legend -->
    <div v-if="showLegend" class="mapview-legend">
      <div class="mapview-legend-title">Legend</div>
      <div class="mapview-legend-item" v-for="lt in legendItems" :key="lt.label">
        <span class="mapview-legend-dot" :style="{ background: lt.color }"></span>
        <span>{{ lt.label }}</span>
      </div>
      <button class="mapview-legend-close" @click="showLegend = false">
        <span class="material-icons">close</span>
      </button>
    </div>
    <button v-else class="mapview-legend-toggle" @click="showLegend = true" title="Show Legend">
      <span class="material-icons">layers</span>
    </button>

    <!-- Marker Detail Panel (Bottom Sheet) -->
    <transition name="slide-up">
      <div v-if="selectedMarker" class="mapview-detail" @click.stop>
        <div class="mapview-detail-handle"></div>
        <div class="mapview-detail-header">
          <div class="mapview-detail-icon" :class="selectedMarker.marker_type">
            <span class="material-icons">{{ getMarkerIcon(selectedMarker) }}</span>
          </div>
          <div class="mapview-detail-info">
            <h3>{{ selectedMarker.name }}</h3>
            <span class="mapview-detail-type">{{ formatType(selectedMarker.marker_type) }}</span>
          </div>
          <button class="mapview-detail-close" @click="selectedMarker = null">
            <span class="material-icons">close</span>
          </button>
        </div>

        <!-- Floor Selector (if building) -->
        <div v-if="selectedMarker.marker_type === 'facility' && floors.length > 1" class="mapview-floors">
          <button 
            v-for="f in floors" :key="f"
            class="mapview-floor-chip"
            :class="{ active: selectedFloor === f }"
            @click="selectedFloor = f"
          >
            {{ f === 1 ? 'Ground' : f === 2 ? '2nd' : f === 3 ? '3rd' : f + 'th' }} Floor
          </button>
        </div>

        <!-- Room list for selected building -->
        <div v-if="selectedMarker.marker_type === 'facility' && buildingRooms.length > 0" class="mapview-rooms">
          <div v-for="room in filteredRooms" :key="room.id" class="mapview-room-item" @click="navigateToRoom(room)">
            <div class="mapview-room-icon">
              <span class="material-icons">{{ room.is_office ? 'work' : 'meeting_room' }}</span>
            </div>
            <div class="mapview-room-info">
              <span class="mapview-room-name">{{ room.name }}</span>
              <span class="mapview-room-meta">{{ room.room_type || 'Room' }} • Floor {{ room.floor || 1 }}</span>
            </div>
            <button class="mapview-room-nav" @click.stop="navigateToRoom(room)" title="Get directions">
              <span class="material-icons">directions</span>
            </button>
          </div>
        </div>

        <!-- Actions -->
        <div class="mapview-detail-actions">
          <button class="mapview-action-primary" @click="getDirections">
            <span class="material-icons">directions</span>
            Get Directions
          </button>
          <button class="mapview-action-secondary" @click="addFavorite">
            <span class="material-icons">favorite_border</span>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import useMapPanZoom from '../composables/useMapPanZoom.js'
import { useRouter } from 'vue-router'
import offlineData from '../services/offlineData.js'
import { isOnline } from '../services/sync.js'

const router = useRouter()

const isOffline = ref(false)
const lastSync = ref(null)

// Map state
const canvasRef = ref(null)
const {
  scale, translateX: tx, translateY: ty, isPanning, transformStyle: transformStylePanZoom,
  zoomIn, zoomOut, onPointerDown, onPointerMove, onPointerUp, onWheel,
  onTouchStart, onTouchMove, initTransform
} = useMapPanZoom()
const showLabels = ref(true)
const showLegend = ref(false)  // Default collapsed for cleaner UI
const activeFilter = ref('all')
const mapLoaded = ref(false)

// Data
const facilities = ref([])
const rooms = ref([])
const mapMarkers = ref([])
const selectedMarker = ref(null)
const selectedFloor = ref(1)
const buildingRooms = ref([])

// Filter types
const filterTypes = [
  { value: 'facility', label: 'Buildings', icon: 'business' },
  { value: 'room', label: 'Rooms', icon: 'meeting_room' },
]

const legendItems = [
  { label: 'Building', color: '#1976D2' },
  { label: 'Computer Lab', color: '#388E3C' },
  { label: 'Office', color: '#FF9800' },
  { label: 'Facility', color: '#7B1FA2' },
]

// Computed
const transformStyle = transformStylePanZoom

const visibleMarkers = computed(() => {
  if (activeFilter.value === 'all') return mapMarkers.value
  return mapMarkers.value.filter(m => m.marker_type === activeFilter.value)
})

const floors = computed(() => {
  if (!selectedMarker.value || selectedMarker.value.marker_type !== 'facility') return []
  // Use total_floors from the actual facility record in the database
  const facility = facilities.value.find(
    f => f.name === selectedMarker.value.name || f.id === selectedMarker.value.facility_id
  )
  const count = facility?.total_floors || 1
  return Array.from({ length: count }, (_, i) => i + 1)
})

const filteredRooms = computed(() => {
  return buildingRooms.value.filter(r => (r.floor || 1) === selectedFloor.value)
})

// Methods
function getMarkerPosition(marker) {
  return {
    left: `${(marker.x_position || 0.5) * 100}%`,
    top: `${(marker.y_position || 0.5) * 100}%`,
  }
}

function getMarkerIcon(marker) {
  const icons = {
    'facility': 'business',
    'room': 'meeting_room',
    'entrance': 'door_front',
    'lab': 'computer',
    'office': 'work',
  }
  return icons[marker.marker_type] || 'place'
}

function formatType(type) {
  return type ? type.charAt(0).toUpperCase() + type.slice(1) : 'Location'
}

function selectMarker(marker) {
  selectedMarker.value = marker
  selectedFloor.value = 1
  if (marker.marker_type === 'facility') {
    loadBuildingRooms(marker)
  } else {
    buildingRooms.value = []
  }
}

async function loadBuildingRooms(marker) {
  try {
    const res = await offlineData.getRooms(marker.id)
    buildingRooms.value = res.data
    
    // If offline and no rooms, use mock data
    if (res.data.length === 0 && !isOnline()) {
      useMockRooms(marker)
    }
  } catch {
    useMockRooms(marker)
  }
}

function useMockRooms(marker) {
  const mockRooms = {
    'MST Building': [
      { id: 1, name: 'MST 101', room_type: 'Classroom', floor: 1, is_office: false },
      { id: 2, name: 'MST 201', room_type: 'Classroom', floor: 2, is_office: false },
      { id: 3, name: 'CL1', room_type: 'Computer Lab', floor: 3, is_office: false },
      { id: 4, name: 'CL2', room_type: 'Computer Lab', floor: 3, is_office: false },
      { id: 5, name: 'CL5', room_type: 'Computer Lab', floor: 3, is_office: false },
      { id: 6, name: 'CL6', room_type: 'Computer Lab', floor: 3, is_office: false },
      { id: 7, name: 'MST 401', room_type: 'Classroom', floor: 4, is_office: false },
    ],
    'JST Building': [
      { id: 8, name: 'JST101', room_type: 'Lecture Room', floor: 1, is_office: false },
      { id: 9, name: 'JST201', room_type: 'Laboratory', floor: 2, is_office: false },
    ],
    'RST Building': [
      { id: 10, name: 'Registrar', room_type: 'Office', floor: 1, is_office: true },
      { id: 11, name: 'Accounting', room_type: 'Office', floor: 1, is_office: true },
      { id: 12, name: 'Guidance', room_type: 'Office', floor: 2, is_office: true },
      { id: 13, name: 'Safety & Security', room_type: 'Office', floor: 2, is_office: true },
      { id: 14, name: 'IT Office', room_type: 'Office', floor: 3, is_office: true },
    ],
  }
  buildingRooms.value = mockRooms[marker.name] || []
}

async function loadData() {
  try {
    const [facilitiesRes, markerRes] = await Promise.all([
      offlineData.getFacilities(),
      offlineData.getMapMarkers()
    ])
    
    facilities.value = facilitiesRes.data
    mapMarkers.value = markerRes.data
    
    // Track offline status
    isOffline.value = !isOnline() || facilitiesRes.source === 'cache'
    if (markerRes.lastSync) {
      lastSync.value = new Date(markerRes.lastSync).toLocaleString()
    }
    
    // If using stale cache, try to refresh in background
    if (facilitiesRes.stale && isOnline()) {
      console.log('[MapView] Cache is stale, will refresh on next load')
    }
  } catch (err) {
    console.error('[MapView] Error loading data:', err)
    // Final fallback - empty arrays
    facilities.value = []
    mapMarkers.value = []
  }
}

function getDirections() {
  if (!selectedMarker.value) return
  router.push({ path: '/navigate', query: { to: selectedMarker.value.name } })
}

function navigateToRoom(room) {
  router.push({ path: '/navigate', query: { to: room.name } })
}

function addFavorite() {
  if (!selectedMarker.value) return
  const favorites = JSON.parse(localStorage.getItem('tp_favorites') || '[]')
  
  // Generate composite key to prevent ID collisions
  const compositeId = `${selectedMarker.value.marker_type}_${selectedMarker.value.id || selectedMarker.value.name}`
  
  const exists = favorites.find(f => f.id === compositeId)
  if (!exists) {
    favorites.push({
      id: compositeId,  // Use composite key: type_id or type_name
      name: selectedMarker.value.name,
      type: selectedMarker.value.marker_type,
      addedAt: new Date().toISOString(),
    })
    localStorage.setItem('tp_favorites', JSON.stringify(favorites))
    showToast(`${selectedMarker.value.name} added to favorites!`, 'success')
  } else {
    showToast('This location is already in your favorites!', 'info')
  }
}

// Pan & Zoom
// pan/zoom handled by useMapPanZoom composable

let lastTouchDist = 0
function onTouchStart(e) {
  if (e.touches.length === 2) {
    lastTouchDist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    )
  } else if (e.touches.length === 1) {
    isPanning.value = true
    panStart.value = { x: e.touches[0].clientX - tx.value, y: e.touches[0].clientY - ty.value }
  }
}

function onTouchMove(e) {
  if (e.touches.length === 2) {
    const dist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    )
    if (lastTouchDist > 0) {
      const delta = dist / lastTouchDist
      scale.value = Math.max(0.5, Math.min(5, scale.value * delta))
    }
    lastTouchDist = dist
  } else if (e.touches.length === 1 && isPanning.value) {
    tx.value = e.touches[0].clientX - panStart.value.x
    ty.value = e.touches[0].clientY - panStart.value.y
  }
}

onMounted(async () => {
  await loadData()
  if (canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect()
    initTransform(rect.width, rect.height)
  }
})
</script>

<style>
@import '../assets/mapview.css';
</style>
