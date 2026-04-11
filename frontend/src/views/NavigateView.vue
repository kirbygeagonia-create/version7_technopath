<template>
  <div class="navview">
    <!-- Top bar -->
    <header class="navview-header">
      <button class="navview-back-btn" @click="$router.back()">
        <span class="material-icons">arrow_back</span>
      </button>
      <h1 class="navview-title">Navigate</h1>
    </header>

    <!-- Location Selectors Panel -->
    <div class="navview-panel">
      <div class="navview-field">
        <span class="material-icons navview-field-icon from">my_location</span>
        <select v-model="fromLocation" class="navview-select">
          <option value="">Select starting point</option>
          <option v-for="loc in locations" :key="'from-'+loc" :value="loc">{{ loc }}</option>
        </select>
      </div>
      
      <button class="navview-swap-btn" @click="swapLocations" title="Swap locations">
        <span class="material-icons">swap_vert</span>
      </button>

      <div class="navview-field">
        <span class="material-icons navview-field-icon to">place</span>
        <select v-model="toLocation" class="navview-select">
          <option value="">Select destination</option>
          <option v-for="loc in locations" :key="'to-'+loc" :value="loc">{{ loc }}</option>
        </select>
      </div>

      <div class="navview-actions-row">
        <button class="navview-find-btn" @click="findRoute" :disabled="!fromLocation || !toLocation">
          <span class="material-icons">directions</span>
          Find Route
        </button>
        <button v-if="routeFound" class="navview-clear-btn" @click="clearRoute">
          <span class="material-icons">clear</span>
        </button>
      </div>
    </div>

    <!-- Map with route overlay -->
    <div class="navview-map" ref="mapRef"
      @wheel.prevent="onWheel"
      @mousedown="onPointerDown"
      @mousemove="onPointerMove"
      @mouseup="onPointerUp"
      @mouseleave="onPointerUp"
      @touchstart.prevent="onTouchStart"
      @touchmove.prevent="onTouchMove"
      @touchend="onPointerUp"
    >
      <div class="navview-map-transform" :style="transformStyle">
        <!-- SVG Map -->
        <img 
          src="../assets/SEAIT_Map.svg" 
          class="navview-map-img"
          draggable="false"
          alt="Campus Map"
        />

        <!-- Route polyline overlay (SVG) -->
        <svg 
          v-if="routeFound && routePoints.length > 1"
          class="navview-route-svg"
          viewBox="0 0 800 600"
          preserveAspectRatio="none"
        >
          <!-- Route path shadow -->
          <polyline 
            :points="routePointsStr"
            fill="none"
            stroke="rgba(0,0,0,0.15)"
            stroke-width="8"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <!-- Animated route path -->
          <polyline
            :points="routePointsStr"
            fill="none"
            stroke="#FF9800"
            stroke-width="5"
            stroke-linecap="round"
            stroke-linejoin="round"
            class="navview-route-line"
            :style="{ strokeDasharray: routeLength, strokeDashoffset: routeAnimOffset }"
          />
          <!-- Start marker -->
          <circle
            :cx="routePoints[0].x" :cy="routePoints[0].y"
            r="8" fill="#388E3C" stroke="white" stroke-width="2"
          />
          <!-- End marker -->
          <circle
            :cx="routePoints[routePoints.length-1].x" :cy="routePoints[routePoints.length-1].y"
            r="8" fill="#D32F2F" stroke="white" stroke-width="2"
          />
          <!-- Waypoint markers -->
          <circle
            v-for="(pt, i) in routePoints.slice(1, -1)"
            :key="'wp-'+i"
            :cx="pt.x" :cy="pt.y"
            r="4" fill="#FF9800" stroke="white" stroke-width="1.5"
          />
        </svg>

        <!-- Markers -->
        <div 
          v-for="marker in mapMarkers" 
          :key="marker.id"
          class="navview-marker"
          :style="getMarkerPos(marker)"
        >
          <div class="navview-marker-dot" :class="marker.marker_type"></div>
          <span class="navview-marker-name">{{ marker.name }}</span>
        </div>
      </div>
    </div>

    <!-- Zoom controls -->
    <div class="navview-zoom">
      <button @click="zoomIn" class="navview-zoom-btn"><span class="material-icons">add</span></button>
      <button @click="zoomOut" class="navview-zoom-btn"><span class="material-icons">remove</span></button>
    </div>

    <!-- Route Info Panel -->
    <transition name="slide-up">
      <div v-if="routeFound && routeInfo" class="navview-route-info">
        <div class="navview-route-info-handle"></div>
        <div class="navview-route-info-header">
          <span class="material-icons" style="color: var(--color-primary)">navigation</span>
          <div class="navview-route-dest">
            <strong>{{ fromLocation }}</strong>
            <span class="material-icons" style="font-size:16px; color: var(--color-text-hint)">arrow_forward</span>
            <strong>{{ toLocation }}</strong>
          </div>
          <button class="navview-route-close" @click="clearRoute">
            <span class="material-icons">close</span>
          </button>
        </div>

        <div class="navview-route-stats">
          <div class="navview-stat">
            <span class="material-icons">straighten</span>
            <span>{{ routeInfo.distance }}</span>
          </div>
          <div class="navview-stat">
            <span class="material-icons">schedule</span>
            <span>{{ routeInfo.time }}</span>
          </div>
          <div class="navview-stat">
            <span class="material-icons">directions_walk</span>
            <span>{{ routeInfo.steps }} steps</span>
          </div>
        </div>

        <button class="navview-directions-btn" @click="showDirections = !showDirections">
          <span class="material-icons">{{ showDirections ? 'expand_less' : 'expand_more' }}</span>
          {{ showDirections ? 'Hide' : 'Show' }} Turn-by-Turn Directions
        </button>

        <!-- Turn-by-turn directions -->
        <div v-if="showDirections" class="navview-directions">
          <div 
            v-for="(step, idx) in routeSteps" :key="idx"
            class="navview-step"
          >
            <div 
              class="navview-step-num"
              :class="{ start: idx === 0, end: idx === routeSteps.length - 1 }"
            >
              {{ idx + 1 }}
            </div>
            <div class="navview-step-info">
              <span class="navview-step-text">{{ step.instruction }}</span>
              <span v-if="step.distance" class="navview-step-dist">{{ step.distance }}</span>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import useMapPanZoom from '../composables/useMapPanZoom.js'
import { useRoute } from 'vue-router'
import offlineData from '../services/offlineData.js'
import { isOnline } from '../services/sync.js'
import { findPath } from '../services/pathfinder.js'
import api from '../services/api.js'

const route = useRoute()

// Map state
const mapRef = ref(null)
const {
  scale, translateX: tx, translateY: ty,
  transformStyle: navTransformStyle,
  zoomIn, zoomOut, onPointerDown, onPointerMove, onPointerUp, onWheel,
  onTouchStart, onTouchMove, initTransform
} = useMapPanZoom()

// Navigation state
const fromLocation = ref('')
const toLocation = ref('')
const routeFound = ref(false)
const routeInfo = ref(null)
const routePoints = ref([])
const routeSteps = ref([])
const routeLength = ref(0)
const routeAnimOffset = ref(0)
const showDirections = ref(false)
const mapMarkers = ref([])

// Route query param support
onMounted(async () => {
  await loadData()
  if (route.query.to) {
    toLocation.value = route.query.to
  }
  if (route.query.from) {
    fromLocation.value = route.query.from
  }
  if (mapRef.value) {
    const rect = mapRef.value.getBoundingClientRect()
    initTransform(rect.width, rect.height)
  }
})

const locations = ref([])

// Fallback mock locations for offline/dev mode only
const mockLocations = import.meta.env.DEV ? [
  'Main Gate',
  'MST Building', 'JST Building', 'RST Building',
  'Library', 'Registrar Office', 'Cafeteria', 'Gymnasium',
  'CL1', 'CL2', 'CL3', 'CL4', 'CL5', 'CL6',
  'CR1', 'CR2', 'CR3', 'CR4',
] : []

const transformStyle = navTransformStyle

const routePointsStr = computed(() => {
  return routePoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

// Methods
function swapLocations() {
  const tmp = fromLocation.value
  fromLocation.value = toLocation.value
  toLocation.value = tmp
}

async function findRoute() {
  if (!fromLocation.value || !toLocation.value) return

  try {
    const result = await findPath(fromLocation.value, toLocation.value)
    if (result && result.path && result.path.length > 0) {
      routePoints.value = result.path.map(node => ({
        x: node.x * 800,
        y: node.y * 600,
      }))
      routeInfo.value = {
        distance: result.totalDistance ? `${result.totalDistance}m` : '~150m',
        time: result.totalTime ? `${result.totalTime} min` : '~3 min',
        steps: result.path.length,
      }
      routeSteps.value = result.steps || []
      routeFound.value = true
      animateRoute()
    } else {
      // Fallback: generate mock route
      generateMockRoute()
    }
  } catch (err) {
    console.error('[NavigateView] Pathfinding failed:', err)
    generateMockRoute()
  }
}

function generateMockRoute() {
  // Create a visual mock route for demonstration
  const locationCoords = {
    'Main Gate': { x: 0.5, y: 0.95 },
    'MST Building': { x: 0.3, y: 0.4 },
    'JST Building': { x: 0.6, y: 0.3 },
    'RST Building': { x: 0.5, y: 0.6 },
    'Library': { x: 0.2, y: 0.5 },
    'Cafeteria': { x: 0.8, y: 0.7 },
    'Gymnasium': { x: 0.15, y: 0.8 },
    'Registrar Office': { x: 0.7, y: 0.5 },
    'CL1': { x: 0.28, y: 0.38 },
    'CL2': { x: 0.32, y: 0.38 },
    'CL5': { x: 0.28, y: 0.42 },
    'CL6': { x: 0.32, y: 0.42 },
    'CR1': { x: 0.34, y: 0.36 },
    'CR2': { x: 0.34, y: 0.44 },
  }

  const start = locationCoords[fromLocation.value] || { x: 0.5, y: 0.9 }
  const end = locationCoords[toLocation.value] || { x: 0.5, y: 0.3 }
  
  // Generate intermediate waypoints
  const mid1 = { x: start.x, y: (start.y + end.y) / 2 }
  const mid2 = { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 }

  routePoints.value = [
    { x: start.x * 800, y: start.y * 600 },
    { x: mid1.x * 800, y: mid1.y * 600 },
    { x: mid2.x * 800, y: mid2.y * 600 },
    { x: end.x * 800, y: end.y * 600 },
  ]

  const dist = Math.round(Math.hypot((end.x - start.x) * 200, (end.y - start.y) * 200))
  routeInfo.value = {
    distance: `~${dist}m`,
    time: `~${Math.max(1, Math.round(dist / 60))} min`,
    steps: 4,
  }
  routeSteps.value = generateMockSteps()
  routeFound.value = true
  animateRoute()
}

function generateMockSteps() {
  return [
    { instruction: `Start at ${fromLocation.value}`, distance: '' },
    { instruction: 'Walk along the main pathway', distance: '~50m' },
    { instruction: `Turn towards ${toLocation.value}`, distance: '~60m' },
    { instruction: `Arrive at ${toLocation.value}`, distance: '' },
  ]
}

function animateRoute() {
  // Calculate total path length for stroke-dasharray animation
  let total = 0
  for (let i = 1; i < routePoints.value.length; i++) {
    const dx = routePoints.value[i].x - routePoints.value[i-1].x
    const dy = routePoints.value[i].y - routePoints.value[i-1].y
    total += Math.sqrt(dx*dx + dy*dy)
  }
  routeLength.value = total
  routeAnimOffset.value = total

  // Animate with requestAnimationFrame
  const startTime = performance.now()
  const duration = 1500

  function step(now) {
    const progress = Math.min((now - startTime) / duration, 1)
    // Ease out cubic
    const eased = 1 - Math.pow(1 - progress, 3)
    routeAnimOffset.value = total * (1 - eased)
    if (progress < 1) {
      requestAnimationFrame(step)
    }
  }
  requestAnimationFrame(step)
}

function clearRoute() {
  routeFound.value = false
  routePoints.value = []
  routeInfo.value = null
  routeSteps.value = []
  showDirections.value = false
}

function getMarkerPos(marker) {
  return {
    left: `${(marker.x_position || 0.5) * 100}%`,
    top: `${(marker.y_position || 0.5) * 100}%`,
  }
}

// pan/zoom handled by useMapPanZoom composable

// Data
async function loadData() {
  try {
    // Load map markers
    const res = await offlineData.getMapMarkers()
    mapMarkers.value = res.data
    
    // If no markers and we're offline, use mock data
    if (res.data.length === 0 && !isOnline()) {
      mapMarkers.value = [
        { id: 1, name: 'MST Building', marker_type: 'facility', x_position: 0.3, y_position: 0.4 },
        { id: 2, name: 'JST Building', marker_type: 'facility', x_position: 0.6, y_position: 0.3 },
        { id: 3, name: 'RST Building', marker_type: 'facility', x_position: 0.5, y_position: 0.6 },
        { id: 4, name: 'Library', marker_type: 'facility', x_position: 0.2, y_position: 0.5 },
        { id: 5, name: 'CL1', marker_type: 'room', x_position: 0.32, y_position: 0.42 },
      ]
    }
    
    // Load locations from API (facilities and rooms)
    try {
      const [facilitiesRes, roomsRes] = await Promise.all([
        api.get('/facilities/').catch(() => ({ data: [] })),
        api.get('/rooms/').catch(() => ({ data: [] }))
      ])
      
      const facilityNames = facilitiesRes.data.map(f => f.name)
      const roomNames = roomsRes.data.map(r => r.name)
      
      locations.value = [...facilityNames, ...roomNames].sort()
      
      // If API returned no data and we're offline, use mock data (dev only)
      if (locations.value.length === 0 && !isOnline() && import.meta.env.DEV) {
        locations.value = mockLocations
      }
    } catch (apiErr) {
      console.error('[NavigateView] Error loading locations from API:', apiErr)
      if (import.meta.env.DEV) {
        locations.value = mockLocations
      }
    }
  } catch (err) {
    console.error('[NavigateView] Error loading markers:', err)
    // Fallback to mock data
    mapMarkers.value = [
      { id: 1, name: 'MST Building', marker_type: 'facility', x_position: 0.3, y_position: 0.4 },
      { id: 2, name: 'JST Building', marker_type: 'facility', x_position: 0.6, y_position: 0.3 },
      { id: 3, name: 'RST Building', marker_type: 'facility', x_position: 0.5, y_position: 0.6 },
      { id: 4, name: 'Library', marker_type: 'facility', x_position: 0.2, y_position: 0.5 },
      { id: 5, name: 'CL1', marker_type: 'room', x_position: 0.32, y_position: 0.42 },
    ]
    locations.value = mockLocations
  }
}
</script>

<style>
@import '../assets/navigate.css';
</style>
