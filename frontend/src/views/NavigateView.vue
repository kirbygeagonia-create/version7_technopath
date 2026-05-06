<template>
  <div 
    class="svg-navigate-view"
    @mousemove="dragPathInfo"
    @mouseup="stopDragPathInfo"
    @mouseleave="stopDragPathInfo"
  >
    <!-- Navigate Header -->
    <div class="settings-header nav-header-bar">
      <div class="nav-header-left">
        <div class="settings-header-icon">
          <span class="material-icons">navigation</span>
        </div>
        <div class="settings-header-text">
          <h1>Navigate</h1>
          <p>Find your way around campus</p>
        </div>
      </div>
      <div class="nav-header-actions">
        <button class="nav-icon-btn" @click="$router.push('/chatbot')" title="Chatbot">
          <span class="material-icons">smart_toy</span>
        </button>
        <button class="nav-icon-btn" @click="$router.push('/notifications')" title="Notifications">
          <span class="material-icons">notifications</span>
        </button>
        <button class="nav-icon-btn" @click="$router.push('/feedback')" title="Rate App">
          <span class="material-icons">star</span>
        </button>
      </div>
    </div>

    <!-- Location Selection Panel -->
    <div class="svg-nav-panel" v-if="!isNavigating">
      <!-- Loading or no paths message -->
      <div v-if="availablePaths.length === 0 && locations.length === 0" class="svg-nav-empty">
        <span class="material-icons" style="font-size: 48px; color: #ccc;">map</span>
        <p>No navigation paths available.</p>
        <p class="svg-nav-hint">Go to Admin Panel → Map Management → SVG Paths to create paths first.</p>
      </div>

      <div v-else-if="locations.length === 0" class="svg-nav-empty">
        <span class="material-icons" style="font-size: 48px; color: #ccc;">refresh</span>
        <p>Loading navigation paths...</p>
      </div>

      <template v-else>
        <!-- From Location -->
        <div class="svg-nav-field">
          <span class="material-icons svg-nav-icon from">location_on</span>
          <select v-model="fromLocation" class="svg-nav-select">
            <option value="">Select From location</option>
            <option v-for="location in fromLocations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>

        <!-- To Locations (Multiple) -->
        <div class="svg-nav-field">
          <span class="material-icons svg-nav-icon to">flag</span>
          <select v-model="toLocation" class="svg-nav-select">
            <option value="">Select To location</option>
            <option v-for="location in toLocations" :key="location.id" :value="location.id">
              {{ location.name }}
            </option>
          </select>
        </div>

        <div class="svg-nav-actions">
          <button 
            class="svg-nav-start-btn" 
            @click="startNavigation" 
            :disabled="!fromLocation || !toLocation"
          >
            <span class="material-icons">play_arrow</span>
            Start Navigation
          </button>
        </div>
      </template>

      <!-- Route Preview with Path Details -->
      <div v-if="fromLocation && toLocation" class="svg-nav-preview">
        <h4>Route Preview</h4>
        
        <!-- Simple FROM → TO route -->
        <div v-if="getPathForDestination(toLocation)" class="svg-nav-full-route">
          <div class="route-line">
            <span class="route-from">{{ getLocationName(fromLocation) }}</span>
            <span class="route-arrow">→</span>
            <span class="route-to">{{ getLocationName(toLocation) }}</span>
          </div>
        </div>
        
        <!-- Path card for selected route -->
        <div class="svg-nav-path-card" v-if="getPathForDestination(toLocation)">
          <div class="path-card-header">
            <span class="path-card-destination">{{ getLocationName(toLocation) }}</span>
          </div>
          <div class="path-card-details">
            <div class="path-detail-item">
              <span class="material-icons">signpost</span>
              <span>{{ getPathForDestination(toLocation).name || 'Unnamed Path' }}</span>
            </div>
            <div class="path-detail-item" v-if="getPathForDestination(toLocation).description">
              <span class="material-icons">description</span>
              <span>{{ getPathForDestination(toLocation).description }}</span>
            </div>
            <div class="path-detail-item" v-if="getPathForDestination(toLocation).room">
              <span class="material-icons">meeting_room</span>
              <span>Room: {{ getPathForDestination(toLocation).room }}</span>
            </div>
            <div class="path-detail-item" v-if="getPathForDestination(toLocation).floor">
              <span class="material-icons">layers</span>
              <span>Floor: {{ getPathForDestination(toLocation).floor }}</span>
            </div>
          </div>
        </div>
        <div class="path-card-no-path" v-else>
          <span class="material-icons">error_outline</span>
          <span>No path found. Create in Admin → SVG Paths.</span>
        </div>
      </div>
    </div>

    <!-- Navigation Controls (visible during navigation) -->
    <div class="svg-nav-controls" v-if="isNavigating && currentStepInfo">
      <div class="svg-nav-progress">
        <span class="svg-nav-step-info">
          Step {{ (currentStepInfo.step ?? 0) + 1 }} of {{ currentStepInfo.totalSteps ?? 0 }}
        </span>
        <span class="svg-nav-current-location">{{ currentStepInfo.elementId ?? '-' }}</span>
      </div>
      
      <div class="svg-nav-buttons">
        <button 
          class="svg-nav-btn" 
          @click="previousStep" 
          :disabled="currentStepInfo.isFirst ?? true"
        >
          <span class="material-icons">skip_previous</span>
          Previous
        </button>
        
        <button class="svg-nav-btn svg-nav-stop" @click="stopNavigation">
          <span class="material-icons">stop</span>
          Stop
        </button>
        
        <button 
          class="svg-nav-btn" 
          @click="nextStep" 
          :disabled="currentStepInfo.isLast ?? true"
        >
          Next
          <span class="material-icons">skip_next</span>
        </button>
      </div>
    </div>

    <!-- Floating Draggable Path Info Panel -->
    <div 
      class="svg-nav-path-info" 
      v-if="isNavigating && currentPath"
      :style="{ left: pathInfoPos.x + 'px', top: pathInfoPos.y + 'px' }"
      @mousedown="startDragPathInfo"
    >
      <div class="svg-nav-path-info-header">
        <span class="material-icons svg-nav-drag-icon">drag_indicator</span>
        <span class="svg-nav-path-info-title">Path Info</span>
      </div>
      <div class="svg-nav-path-info-row">
        <div class="svg-nav-path-info-field">
          <span class="svg-nav-path-label">Name:</span>
          <span class="svg-nav-path-value">{{ currentPath?.name || 'Unnamed' }}</span>
        </div>
      </div>
      <div class="svg-nav-path-info-row">
        <div class="svg-nav-path-info-field">
          <span class="svg-nav-path-label">Room:</span>
          <span class="svg-nav-path-value">{{ currentPath?.room || 'N/A' }}</span>
        </div>
        <div class="svg-nav-path-info-field">
          <span class="svg-nav-path-label">Floor:</span>
          <span class="svg-nav-path-value">{{ currentPath?.floor || '1' }}</span>
        </div>
      </div>
      <div class="svg-nav-path-info-row" v-if="currentPath?.description">
        <div class="svg-nav-path-info-field svg-nav-path-description">
          <span class="svg-nav-path-label">Description:</span>
          <span class="svg-nav-path-value">{{ currentPath.description }}</span>
        </div>
      </div>
    </div>

    <!-- SVG Map + Controls wrapper — controls overlay the map -->
    <div class="svg-map-outer">
      <!-- SVG Map Container -->
      <div 
        class="svg-map-container" 
        ref="mapContainer" 
        @mousedown="startDrag"
        @mousemove="drag"
        @mouseup="endDrag"
        @mouseleave="endDrag"
        @touchstart.passive="startDrag"
        @touchmove.passive="drag"
        @touchend="endDrag"
        :class="{ 'is-dragging': isDragging }"
      >
      <svg 
        ref="svgMap"
        class="svg-map"
        :viewBox="viewBoxString"
        :style="{ transform: `rotate(${mapRotation}deg)`, transition: 'transform 0.3s ease' }"
        preserveAspectRatio="xMidYMid meet"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Map content will be loaded dynamically -->
        <g v-if="mapLoaded" v-html="svgContent"></g>
        
        <!-- Navigation Path Overlay -->
        <g v-if="isNavigating && pathPositions.length > 0" class="nav-path-overlay">
          <!-- Connecting Lines with glow effect -->
          <polyline
            :points="pathPoints"
            fill="none"
            stroke="#FF9800"
            stroke-width="20"
            stroke-linecap="round"
            stroke-linejoin="round"
            opacity="0.9"
            filter="drop-shadow(0 0 10px rgba(255,152,0,0.8))"
          />
          <!-- Secondary outline for better visibility -->
          <polyline
            :points="pathPoints"
            fill="none"
            stroke="#FFF"
            stroke-width="10"
            stroke-linecap="round"
            stroke-linejoin="round"
            opacity="0.5"
          />
          
          <!-- Path Points -->
          <circle
            v-for="(pos, index) in pathPositions"
            :key="`point-${pos.id}-${index}`"
            :cx="pos.x"
            :cy="pos.y"
            :r="index === (currentStepInfo?.step ?? -1) ? 30 : 18"
            :fill="index === (currentStepInfo?.step ?? -1) ? '#FF5722' : '#4CAF50'"
            :stroke="'white'"
            :stroke-width="index === (currentStepInfo?.step ?? -1) ? 6 : 3"
            filter="drop-shadow(0 0 8px rgba(0,0,0,0.5))"
          />
          
          <!-- Labels - Only show for first and last point -->
          <text
            v-for="(pos) in endpointLabels"
            :key="`label-${pos.id}-${pos.index}`"
            :x="pos.x"
            :y="pos.y - 30"
            text-anchor="middle"
            fill="#333"
            font-size="24"
            font-weight="bold"
            style="text-shadow: 2px 2px 4px white;"
          >
            {{ pos.label }}
          </text>
        </g>

        <!-- Current Position Indicator -->
        <g v-if="isNavigating && currentPosition" class="current-position">
          <circle
            :cx="currentPosition.x"
            :cy="currentPosition.y"
            r="30"
            fill="none"
            stroke="#FF5722"
            stroke-width="4"
            opacity="0.5"
          >
            <animate
              attributeName="r"
              values="25;35;25"
              dur="1.5s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.8;0.3;0.8"
              dur="1.5s"
              repeatCount="indefinite"
            />
          </circle>
        </g>
      </svg>

      <!-- Map Loading State -->
      <div v-if="!mapLoaded && !mapError" class="svg-map-skeleton-wrap">
        <AppSkeleton :loading="true" name="navigate-map" animate="shimmer" wrap-class="map-sk-full" />
        <div class="map-sk-center">
          <CometSpinner size="52px" />
          <p class="map-sk-hint">Loading campus map…</p>
        </div>
      </div>

      <div v-if="mapError" class="svg-map-error-state">
        <span class="material-icons">map_off</span>
        <p>{{ mapError }}</p>
      </div>
    </div>
    <!-- end svg-map-container -->

      <!-- Map Controls — overlaid on map, bottom-right -->
      <div class="map-controls">
        <button class="map-ctrl-btn" @click="zoomIn" title="Zoom in" aria-label="Zoom in">
          <span class="material-icons">add</span>
        </button>
        <div class="map-ctrl-divider"></div>
        <button class="map-ctrl-btn" @click="zoomOut" title="Zoom out" aria-label="Zoom out">
          <span class="material-icons">remove</span>
        </button>
        <div class="map-ctrl-divider"></div>
        <button class="map-ctrl-btn" @click="rotateLeft" title="Rotate left" aria-label="Rotate map left">
          <span class="material-icons">rotate_left</span>
        </button>
        <div class="map-ctrl-divider"></div>
        <button class="map-ctrl-btn" @click="rotateRight" title="Rotate right" aria-label="Rotate map right">
          <span class="material-icons">rotate_right</span>
        </button>
        <div class="map-ctrl-divider"></div>
        <button class="map-ctrl-btn map-ctrl-reset" @click="resetView" title="Reset view" aria-label="Reset map view">
          <span class="material-icons">center_focus_strong</span>
        </button>
      </div>

    </div>
    <!-- end svg-map-outer -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import pathManager from '../services/pathManager.js'
import { useLocations } from '../composables/useLocations.js'
import AppSkeleton from '../components/AppSkeleton.vue'
import CometSpinner from '../components/CometSpinner.vue'

// DOM References
const mapContainer = ref(null)
const svgMap = ref(null)

// State
const mapLoaded = ref(false)
const svgContent = ref('')
const fromLocation = ref('')
const toLocation = ref('') // Single TO location
const viewBox = ref({ x: 0, y: 0, width: 3306, height: 7159 })
const zoomLevel = ref(1)
const pathPositions = ref([])
const unreadCount = ref(5) // TODO: Connect to notifications service
const mapError = ref(null)

// Floating Path Info Panel position
const pathInfoPos = ref({ x: 16, y: 80 })
const isDraggingPathInfo = ref(false)
const dragOffsetPathInfo = ref({ x: 0, y: 0 })

const startDragPathInfo = (e) => {
  isDraggingPathInfo.value = true
  dragOffsetPathInfo.value = {
    x: e.clientX - pathInfoPos.value.x,
    y: e.clientY - pathInfoPos.value.y
  }
}

const dragPathInfo = (e) => {
  if (!isDraggingPathInfo.value) return
  pathInfoPos.value = {
    x: e.clientX - dragOffsetPathInfo.value.x,
    y: e.clientY - dragOffsetPathInfo.value.y
  }
}

const stopDragPathInfo = () => {
  isDraggingPathInfo.value = false
}

// Use shared locations composable (connects to AdminNavGraph)
const { locations, getLocationName, extractFromSVG, extractLocationsFromPaths } = useLocations()

// Show From and To endpoints (first and last points of paths)
// Allow any valid string ID
const validLocation = (l) => {
  return l && l.id && typeof l.id === 'string' && l.id.trim() !== ''
}


const fromLocations = computed(() => {
  const endpoints = locations.value.filter(l => l.subtype === 'from' && validLocation(l))
  return endpoints.length > 0 ? endpoints : locations.value.filter(validLocation)
})

const toLocations = computed(() => {
  const endpoints = locations.value.filter(l => l.subtype === 'to' && validLocation(l))
  return endpoints.length > 0 ? endpoints : locations.value.filter(validLocation)
})

// Drag/Pan state
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const viewBoxStart = ref({ x: 0, y: 0 })

// Pinch-to-zoom state
const pinchStartDist = ref(0)
const pinchStartZoom = ref(1)

// Get path manager state
const isNavigating = computed(() => pathManager.isNavigating.value)
const currentPath = computed(() => pathManager.currentPath.value)
const currentStepInfo = computed(() => {
  return pathManager.getCurrentStep() || {
    step: 0,
    totalSteps: 0,
    elementId: '',
    isFirst: true,
    isLast: true
  }
})

// Available paths
const availablePaths = computed(() => pathManager.getAllPaths())

// ViewBox string for SVG attribute
const viewBoxString = computed(() => {
  return `${viewBox.value.x} ${viewBox.value.y} ${viewBox.value.width} ${viewBox.value.height}`
})

// Current position based on step
const currentPosition = computed(() => {
  if (!isNavigating.value || pathPositions.value.length === 0) return null
  if (!currentStepInfo.value || currentStepInfo.value.step == null) return null
  const pos = pathPositions.value[currentStepInfo.value.step]
  if (!pos || pos.x == null || pos.y == null || isNaN(pos.x) || isNaN(pos.y)) return null
  return pos
})

// Path points for polyline
const pathPoints = computed(() => {
  if (pathPositions.value.length === 0) return ''
  return pathPositions.value
    .filter(p => !p.notFound && p.x != null && p.y != null && !isNaN(p.x) && !isNaN(p.y))
    .map(p => `${p.x},${p.y}`)
    .join(' ')
})

// Only show labels for first and last points (From and To) - middle stops are invisible
const endpointLabels = computed(() => {
  if (pathPositions.value.length === 0) return []
  const labels = []
  // Only add first point (FROM)
  if (pathPositions.value.length > 0) {
    const first = pathPositions.value[0]
    if (first && first.x != null && first.y != null && !isNaN(first.x) && !isNaN(first.y)) {
      labels.push({ ...first, index: 0, label: 'From: ' + first.id })
    }
  }
  // Only add last point (TO) if different from first
  if (pathPositions.value.length > 1) {
    const last = pathPositions.value[pathPositions.value.length - 1]
    // Skip if last is same as first (single point path)
    if (last && last.id !== pathPositions.value[0].id && last.x != null && last.y != null && !isNaN(last.x) && !isNaN(last.y)) {
      labels.push({ ...last, index: pathPositions.value.length - 1, label: 'To: ' + last.id })
    }
  }
  return labels
})

// Load SVG map — uses the Vite base URL so it works in both dev and production
const loadMap = async () => {
  try {
    // Build the correct URL regardless of base path (e.g. /seait-technopath/)
    const base = import.meta.env.BASE_URL || '/'
    const svgUrl = base.endsWith('/') ? `${base}Map_labeled.svg` : `${base}/Map_labeled.svg`

    const response = await fetch(svgUrl)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const svgText = await response.text()
    const parser  = new DOMParser()
    const doc     = parser.parseFromString(svgText, 'image/svg+xml')
    const svg     = doc.querySelector('svg')

    if (!svg) throw new Error('SVG element not found in file')

    // Preserve original viewBox dimensions
    const originalViewBox = svg.getAttribute('viewBox')
    if (originalViewBox) {
      const [x, y, width, height] = originalViewBox.split(/\s+/).map(Number)
      if (!isNaN(width) && !isNaN(height)) {
        viewBox.value = { x, y, width, height }
      }
    }

    svgContent.value = svg.innerHTML
    mapLoaded.value  = true

    await nextTick()
    if (isNavigating.value && currentPath.value) {
      calculatePathPositions()
    }
  } catch (error) {
    console.error('[NavigateView] Map load failed:', error)
    // Show the error state — do NOT leave mapLoaded=false (that causes infinite spinner)
    mapError.value  = `Could not load campus map (${error.message})`
    mapLoaded.value = true   // stop the spinner; error UI will show instead
    svgContent.value = ''
  }
}

// Calculate positions of path elements
const calculatePathPositions = () => {
  if (!currentPath.value || !currentPath.value.elementIds) {
    pathPositions.value = []
    return
  }
  
  const positions = []
  const svgWidth = viewBox.value.width
  const svgHeight = viewBox.value.height
  
  console.log('[NavigateView] Calculating positions for:', currentPath.value.elementIds)
  console.log('[NavigateView] SVG dimensions:', svgWidth, 'x', svgHeight)
  console.log('[NavigateView] Available locations:', locations.value?.length || 0)
  
  // Use saved coordinates from visualPoints or points if available
  const savedPoints = currentPath.value.visualPoints || currentPath.value.points || []
  
  for (let i = 0; i < currentPath.value.elementIds.length; i++) {
    const elementId = currentPath.value.elementIds[i]
    
    // Skip invalid elementIds
    if (!elementId || typeof elementId !== 'string') {
      console.warn('[NavigateView] Skipping invalid elementId:', elementId)
      positions.push({ x: 0, y: 0, id: elementId || 'unknown', notFound: true })
      continue
    }
    
    // FIRST: Try to use saved coordinates from visualPoints/points
    let savedCoord = null
    if (i < savedPoints.length) {
      const pt = savedPoints[i]
      if (pt && typeof pt === 'object') {
        // visualPoints format: {x, y, id, row, col, gridSize}
        if (pt.x !== undefined && pt.y !== undefined) {
          savedCoord = { x: pt.x, y: pt.y }
        }
        // points format: [x, y]
        else if (Array.isArray(pt) && pt.length >= 2) {
          savedCoord = { x: pt[0], y: pt[1] }
        }
      }
    }
    
    if (savedCoord && savedCoord.x !== undefined && savedCoord.y !== undefined) {
      console.log('[NavigateView] Using saved coord for', elementId, ':', savedCoord.x, savedCoord.y)
      positions.push({
        x: savedCoord.x,
        y: savedCoord.y,
        id: elementId
      })
      continue
    }
    
    // SECOND: Try to find position from locations (facilities)
    if (locations.value && Array.isArray(locations.value)) {
      const location = locations.value.find(l => l.id === elementId)
      if (location && (location.x !== undefined && location.x !== null)) {
        console.log('[NavigateView] Using location coord for', elementId, ':', location.x, location.y)
        positions.push({
          x: location.x,
          y: location.y,
          id: elementId
        })
        continue
      }
    }
    
    // THIRD: Fallback to finding SVG element
    if (svgMap.value) {
      const element = svgMap.value.querySelector(`#${elementId}`)
      if (element) {
        const bbox = element.getBBox()
        positions.push({
          x: bbox.x + bbox.width / 2,
          y: bbox.y + bbox.height / 2,
          id: elementId
        })
        continue
      }
    }
    
    // LAST RESORT: Not found
    positions.push({ x: 0, y: 0, id: elementId, notFound: true })
  }
  
  console.log('[NavigateView] Final path positions count:', positions.length)
  positions.forEach((p, i) => {
    const x = p.x != null ? p.x.toFixed(1) : 'null'
    const y = p.y != null ? p.y.toFixed(1) : 'null'
    console.log(`  [${i}] ${p.id}: x=${x}, y=${y}`)
  })
  pathPositions.value = positions
}

// Start navigation with from/to locations
const startNavigation = async () => {
  if (!fromLocation.value || !toLocation.value) return
  
  console.log('[NavigateView] Starting navigation from', fromLocation.value, 'to', toLocation.value)
  
  try {
    const pathId = await findOrCreatePath(fromLocation.value, toLocation.value)
    
    if (!pathId) {
      alert('No path found. Please create a path in Admin Panel → SVG Paths.')
      return
    }
    
    const path = pathManager.getPath(pathId)
    if (!path || !path.visualPoints || path.visualPoints.length === 0) {
      alert('Path has no coordinates! Please edit the path in Admin Panel and add X/Y coordinates.')
      return
    }
    
    pathManager.startNavigation(pathId)
    console.log('[NavigateView] Navigation started!', pathId)
    
    await nextTick()
    calculatePathPositions()
    
  } catch (error) {
    console.error('[NavigateView] Error starting navigation:', error)
    alert('Failed to start navigation: ' + error.message)
  }
}

// Find a path that contains all stops in order
const findMultiStopPath = async (from, toLocations) => {
  console.log('[NavigateView] Looking for multi-stop path from', from, 'through', toLocations)
  
  // Build the full route: from + all to locations
  const fullRoute = [from, ...toLocations]
  console.log('[NavigateView] Full route needed:', fullRoute)
  
  // Find a path where elementIds contains all route locations in order
  const matchingPath = availablePaths.value.find(p => {
    if (!p.elementIds || p.elementIds.length < fullRoute.length) return false
    
    // Check if all locations appear in order in elementIds
    let routeIndex = 0
    for (const elementId of p.elementIds) {
      if (elementId === fullRoute[routeIndex]) {
        routeIndex++
        if (routeIndex === fullRoute.length) break
      }
    }
    
    const match = routeIndex === fullRoute.length
    if (match) {
      console.log('[NavigateView] Found matching multi-stop path:', p.id, 'elementIds:', p.elementIds)
    }
    return match
  })
  
  if (matchingPath) {
    return matchingPath.id
  }
  
  // Fallback: try to find a path that at least contains from and first to
  console.log('[NavigateView] No exact multi-stop match, falling back to first segment')
  return await findOrCreatePath(from, toLocations[0])
}

// Find or create a path between two locations
const findOrCreatePath = async (from, to) => {
  console.log('[NavigateView] Looking for path from', from, 'to', to)
  console.log('[NavigateView] Available paths count:', availablePaths.value.length)
  
  // Debug: Log each path with visualPoints
  availablePaths.value.forEach((p, i) => {
    console.log(`[NavigateView] Path ${i}:`, p.id, 'from:', p.from, 'to:', p.to, 'elementIds:', p.elementIds, 'visualPoints:', p.visualPoints?.length || 0)
  })
  
  // First, try to find an existing path
  // Match by: (from/to fields) OR (elementIds first/last) OR (any path containing both points)
  const existingPath = availablePaths.value.find(p => {
    // Check 1: Match by from/to fields
    const matchFromTo = p.from === from && p.to === to
    
    // Check 2: Match by elementIds first and last
    const matchElementIds = p.elementIds && 
      p.elementIds.length >= 2 &&
      p.elementIds[0] === from && 
      p.elementIds[p.elementIds.length - 1] === to
    
    // Check 3: Match if path contains both from and to anywhere in elementIds
    const matchContainsBoth = p.elementIds && 
      p.elementIds.includes(from) && 
      p.elementIds.includes(to)
    
    const match = matchFromTo || matchElementIds || matchContainsBoth
    
    if (match) {
      console.log('[NavigateView] Found matching path:', p.id, 
        'from:', p.from, 'to:', p.to, 
        'elementIds:', p.elementIds,
        'visualPoints:', p.visualPoints?.length || 0)
    }
    return match
  })
  
  if (existingPath) {
    // Verify path has coordinates
    if (!existingPath.visualPoints || existingPath.visualPoints.length === 0) {
      console.warn('[NavigateView] Found path but it has no coordinates:', existingPath.id)
      alert('Selected path has no coordinates! Please go to Admin Panel → Map Management → SVG Paths and add X/Y coordinates for each point.')
      return null
    }
    console.log('[NavigateView] Using existing path with', existingPath.visualPoints.length, 'visual points:', existingPath.id)
    return existingPath.id
  }
  console.log('[NavigateView] No existing path found, creating temp')
  
  // If no existing path, create a temporary one
  const tempPathId = `temp_${from}_${to}_${Date.now()}`
  const tempPath = {
    id: tempPathId,
    name: `${getLocationName(from)} → ${getLocationName(to)}`,
    from: from,
    to: to,
    elementIds: [from, to],
    points: [],
    visualPoints: []
  }
  
  // Add to path manager using proper reactivity
  pathManager.paths.value = {
    ...pathManager.paths.value,
    [tempPathId]: tempPath
  }
  
  return tempPathId
}

// Helper function to get path info for a specific destination
const getPathForDestination = (toLocation) => {
  if (!fromLocation.value || !toLocation) return null
  
  // Find path from FROM to this TO
  return availablePaths.value.find(p => {
    // Match by elementIds array
    if (p.elementIds && p.elementIds.length === 2) {
      return p.elementIds[0] === fromLocation.value && p.elementIds[1] === toLocation
    }
    // Match by from/to fields
    return (p.from === fromLocation.value && p.to === toLocation) ||
           (p.from === fromLocation.value && p.elementIds?.includes(toLocation))
  })
}

// Stop navigation
const stopNavigation = () => {
  pathManager.stopNavigation()
  pathPositions.value = []
  fromLocation.value = ''
  toLocation.value = ''
  resetView()
}

// Navigate to next step
const nextStep = () => {
  pathManager.nextStep()
  updateViewToCurrentStep()
}

// Navigate to previous step
const previousStep = () => {
  pathManager.previousStep()
  updateViewToCurrentStep()
}

// Update viewBox to current step position with smooth animation
const updateViewToCurrentStep = () => {
  if (!currentPosition.value || currentPosition.value.notFound) return
  
  // Smooth transition to new position - use current zoom level
  const targetX = currentPosition.value.x
  const targetY = currentPosition.value.y
  
  centerOnPoint(targetX, targetY, zoomLevel.value, true)
}


// Drag/Grab handlers
const startDrag = (e) => {
  // Only drag with left mouse button or single touch
  if (e.type === 'mousedown' && e.button !== 0) return
  if (e.touches && e.touches.length === 2) {
    // Two-finger pinch start
    isDragging.value = false
    pinchStartDist.value = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    )
    pinchStartZoom.value = zoomLevel.value
    return
  }

  isDragging.value = true
  const clientX = e.clientX ?? e.touches?.[0]?.clientX
  const clientY = e.clientY ?? e.touches?.[0]?.clientY

  dragStart.value = { x: clientX, y: clientY }
  viewBoxStart.value = {
    x: viewBox.value.x,
    y: viewBox.value.y
  }
}

const drag = (e) => {
  // Two-finger pinch-to-zoom
  if (e.touches && e.touches.length === 2) {
    const dist = Math.hypot(
      e.touches[0].clientX - e.touches[1].clientX,
      e.touches[0].clientY - e.touches[1].clientY
    )
    if (pinchStartDist.value > 0) {
      const rawRatio = dist / pinchStartDist.value
      const dampened = 1 + (rawRatio - 1) * 0.55
      const newZoom  = Math.max(0.3, Math.min(5, pinchStartZoom.value * dampened))
      applyZoom(newZoom)
    }
    return
  }

  if (!isDragging.value) return

  const clientX = e.clientX ?? e.touches?.[0]?.clientX
  const clientY = e.clientY ?? e.touches?.[0]?.clientY
  if (clientX == null) return

  const deltaX = clientX - dragStart.value.x
  const deltaY = clientY - dragStart.value.y

  const container = mapContainer.value
  if (!container) return

  const rect = container.getBoundingClientRect()
  const svgUnitsPerPixelX = viewBox.value.width  / rect.width
  const svgUnitsPerPixelY = viewBox.value.height / rect.height

  viewBox.value = {
    ...viewBox.value,
    x: viewBoxStart.value.x - deltaX * svgUnitsPerPixelX,
    y: viewBoxStart.value.y - deltaY * svgUnitsPerPixelY
  }
}

const endDrag = (e) => {
  isDragging.value = false
  if (e?.touches?.length === 0) {
    pinchStartDist.value = 0
  }
}

// applyZoom — shared by buttons and pinch
const applyZoom = (newZoom, centerX, centerY) => {
  const container = mapContainer.value
  const rect = container?.getBoundingClientRect()

  // Default center: middle of the current viewBox
  const cx = centerX ?? (viewBox.value.x + viewBox.value.width  / 2)
  const cy = centerY ?? (viewBox.value.y + viewBox.value.height / 2)

  const oldZoom = zoomLevel.value
  const ratio   = oldZoom / newZoom

  viewBox.value = {
    x:      cx - (cx - viewBox.value.x) * ratio,
    y:      cy - (cy - viewBox.value.y) * ratio,
    width:  viewBox.value.width  * ratio,
    height: viewBox.value.height * ratio
  }
  zoomLevel.value = newZoom
}

// Zoom controls — button-only (wheel disabled)
const zoomIn = () => {
  applyZoom(Math.min(zoomLevel.value * 1.25, 5))
}

const zoomOut = () => {
  applyZoom(Math.max(zoomLevel.value / 1.25, 0.3))
}

// Rotation
const mapRotation = ref(0)

const rotateLeft = () => {
  mapRotation.value = (mapRotation.value - 90 + 360) % 360
}

const rotateRight = () => {
  mapRotation.value = (mapRotation.value + 90) % 360
}

const resetView = () => {
  viewBox.value = { x: 0, y: 0, width: 3306, height: 7159 }
  zoomLevel.value = 1
  mapRotation.value = 0
}

// Fallback SVG content
// Center viewBox on a specific point with optional zoom
const centerOnPoint = (targetX, targetY, zoom = 1, animate = false) => {
  const width = viewBox.value.width / zoom
  const height = viewBox.value.height / zoom
  
  const newX = targetX - width / 2
  const newY = targetY - height / 2
  
  if (animate) {
    // Animate the transition
    const startX = viewBox.value.x
    const startY = viewBox.value.y
    const startWidth = viewBox.value.width
    const startHeight = viewBox.value.height
    
    const duration = 500
    const startTime = performance.now()
    
    const animateFrame = (currentTime) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // Ease out cubic
      const ease = 1 - Math.pow(1 - progress, 3)
      
      viewBox.value = {
        x: startX + (newX - startX) * ease,
        y: startY + (newY - startY) * ease,
        width: startWidth + (width - startWidth) * ease,
        height: startHeight + (height - startHeight) * ease
      }
      
      if (progress < 1) {
        requestAnimationFrame(animateFrame)
      }
    }
    
    requestAnimationFrame(animateFrame)
  } else {
    viewBox.value = {
      x: newX,
      y: newY,
      width: width,
      height: height
    }
  }
}

const getFallbackSvgContent = () => {
  return `
    <rect width="3306" height="7159" fill="#f0f0f0"/>
    <text x="1653" y="3580" text-anchor="middle" font-size="100" fill="#999">
      Map Loading Failed
    </text>
  `
}

// Watch for path changes
watch(currentPath, (newPath) => {
  if (newPath && mapLoaded.value) {
    nextTick(() => calculatePathPositions())
  }
})

// Watch for path changes and extract locations
watch(availablePaths, () => {
  console.log('[NavigateView] Paths changed, extracting locations...')
  extractLocationsFromPaths()
}, { immediate: true })

// Watch for TO location changes and recalculate path
watch(toLocation, () => {
  if (isNavigating.value && currentPath.value) {
    console.log('[NavigateView] TO location changed, recalculating...')
    calculatePathPositions()
  }
})

// Lifecycle
onMounted(async () => {
  loadMap()
  // Wait for paths to load from storage/API, then extract locations
  await new Promise(resolve => setTimeout(resolve, 500))
  extractLocationsFromPaths()
  console.log('[NavigateView] Locations extracted:', locations.value.length)
  console.log('[NavigateView] From locations:', fromLocations.value.length)
  console.log('[NavigateView] To locations:', toLocations.value.length)
})

onUnmounted(() => {
  pathManager.stopNavigation()
})
</script>

<style scoped>
@import '../assets/settings.css';

/* ── Navigate header bar with icon buttons ── */
.nav-header-bar,
.settings-header.nav-header-bar {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 100 !important;
  padding: 12px 14px !important;
  overflow: hidden !important;
}

.nav-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
  position: relative;
  z-index: 1;
}

.nav-header-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  position: relative;
  z-index: 1;
}

.nav-icon-btn {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  background: rgba(255,255,255,0.18);
  border: 1.5px solid rgba(255,255,255,0.3);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.12s ease;
  -webkit-tap-highlight-color: transparent;
  min-height: unset;
  min-width: unset;
}

.nav-icon-btn:hover  { background: rgba(255,255,255,0.32); }
.nav-icon-btn:active { transform: scale(0.90); }
.nav-icon-btn .material-icons { font-size: 20px; color: white; }

.svg-navigate-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  background: var(--color-surface);
  overflow: auto;
  padding-top: 70px;
}

/* Header */
.svg-nav-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #FF9800;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.svg-nav-back-btn {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
  margin-right: 12px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.svg-nav-back-btn:hover {
  background: rgba(255,255,255,0.1);
}

.svg-nav-title {
  font-size: 1.25rem;
  font-weight: 500;
  margin: 0;
}

/* Panel */
.svg-nav-panel {
  padding: 16px;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
}

.svg-nav-field {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

/* Multi-destination styles */
.svg-nav-multi-to {
  align-items: flex-start;
}

.svg-nav-to-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.svg-nav-to-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.svg-nav-remove-btn {
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.svg-nav-remove-btn:hover {
  background: #cc0000;
}

.svg-nav-remove-btn .material-icons {
  font-size: 14px;
}

.svg-nav-add-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  margin-top: 4px;
  width: fit-content;
}

.svg-nav-add-btn:hover {
  background: #45a049;
}

.svg-nav-add-btn:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.svg-nav-add-btn .material-icons {
  font-size: 16px;
}

.svg-nav-icon {
  color: #666;
  font-size: 24px;
}

.svg-nav-icon.from { color: #4CAF50; }
.svg-nav-icon.to { color: #FF5722; }

/* Empty state */
.svg-nav-empty {
  text-align: center;
  padding: 20px 16px;
  color: #666;
}

.svg-nav-empty .material-icons {
  margin-bottom: 8px;
  font-size: 36px;
}

.svg-nav-empty p {
  margin: 0 0 4px 0;
  font-size: 14px;
}

.svg-nav-hint {
  font-size: 12px;
  color: #999;
  font-style: italic;
}

.svg-nav-select {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 16px;
  background: var(--color-bg);
  color: var(--color-text-primary);
  cursor: pointer;
}

.svg-nav-actions {
  display: flex;
  gap: 12px;
}

.svg-nav-start-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 24px;
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border: none;
  border-radius: var(--radius-md);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background var(--duration-fast), transform var(--duration-fast);
  box-shadow: 0 2px 8px rgba(255,152,0,0.3);
}

.svg-nav-start-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.svg-nav-start-btn:disabled {
  background: var(--color-border);
  color: var(--color-text-hint);
  cursor: not-allowed;
  box-shadow: none;
}

/* Path Preview */
.svg-nav-preview {
  margin-top: 16px;
  padding: 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.svg-nav-preview h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary);
}

.svg-nav-full-route {
  margin-bottom: 12px;
  padding: 8px 12px;
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  font-size: 13px;
  border: 1px solid var(--color-border);
}

.route-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.route-from { color: var(--color-primary); font-weight: 600; }
.route-arrow { color: var(--color-text-hint); }
.route-stop  { color: var(--color-primary-dark); }
.route-to    { color: var(--color-primary-dark); font-weight: 600; }

.svg-nav-stops {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.svg-nav-stop {
  font-size: 13px;
  color: #555;
  padding: 4px 8px;
  background: white;
  border-radius: 4px;
}

.svg-nav-stop.from-stop {
  background: #E8F5E9;
  color: #2E7D32;
  border-left: 3px solid #4CAF50;
}

.svg-nav-stop.to-stop {
  background: #FFEBEE;
  color: #C62828;
  border-left: 3px solid #FF5722;
}

/* Path Cards for Multi-Destination */
.svg-nav-path-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.svg-nav-path-card {
  background: var(--color-bg);
  border-radius: var(--radius-md);
  padding: 12px;
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-xs);
}

.path-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border);
}

.path-card-number {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.path-card-destination {
  font-weight: 600;
  color: var(--color-text-primary);
  font-size: 14px;
}

.path-card-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.path-detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}

.path-detail-item .material-icons {
  font-size: 14px;
  color: var(--color-primary);
}

.path-card-no-path {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-warning);
  font-size: 12px;
  padding: 8px;
  background: var(--color-warning-bg);
  border-radius: var(--radius-sm);
}

.path-card-no-path .material-icons { font-size: 16px; }

/* Floating Draggable Path Info Panel */
.svg-nav-path-info {
  position: absolute;
  background: var(--color-primary);
  border-radius: var(--radius-lg);
  padding: 12px;
  color: var(--color-text-inverse);
  font-size: 12px;
  width: 220px;
  z-index: 100;
  box-shadow: var(--shadow-xl);
  cursor: move;
  user-select: none;
}

.svg-nav-path-info-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255,255,255,0.3);
}

.svg-nav-drag-icon { font-size: 18px; color: rgba(255,255,255,0.8); }

.svg-nav-path-info-title {
  font-weight: 700;
  font-size: 13px;
  color: var(--color-text-inverse);
}

.svg-nav-path-info-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.svg-nav-path-info-row:last-child { margin-bottom: 0; }

.svg-nav-path-info-field {
  background: rgba(255,255,255,0.2);
  border-radius: var(--radius-sm);
  padding: 6px 10px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.svg-nav-path-label {
  font-weight: 700;
  color: rgba(255,255,255,0.75);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}

.svg-nav-path-value {
  color: var(--color-text-inverse);
  font-size: 12px;
  font-weight: 500;
}

.svg-nav-path-description .svg-nav-path-value {
  font-size: 10px;
  line-height: 1.3;
}

/* Navigation Controls */
.svg-nav-controls {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  gap: 10px;
}

.svg-nav-progress {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.svg-nav-step-info {
  font-size: 14px;
  color: #666;
}

.svg-nav-current-location {
  font-size: 16px;
  font-weight: 500;
  color: #FF9800;
}

.svg-nav-buttons {
  display: flex;
  gap: 12px;
}

.svg-nav-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px 16px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  border: 1.5px solid rgba(255,152,0,0.25);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
  font-family: var(--font-primary);
}

.svg-nav-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: var(--color-text-inverse);
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255,152,0,0.35);
}

.svg-nav-btn:disabled {
  background: var(--color-surface);
  color: var(--color-text-hint);
  border-color: var(--color-border);
  cursor: not-allowed;
}

.svg-nav-stop {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border-color: rgba(211,47,47,0.2);
}

.svg-nav-stop:hover:not(:disabled) {
  background: var(--color-danger);
  color: white;
  border-color: var(--color-danger);
}

/* Multi-stop navigation styles */
.svg-nav-multi-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.svg-nav-multi-info strong {
  color: #2196F3;
  font-size: 14px;
}

.svg-nav-multi-info small {
  color: #666;
  font-size: 11px;
}

.svg-nav-next-dest {
  background: #2196F3;
}

.svg-nav-next-dest:hover:not(:disabled) {
  background: #1976D2;
}

/* Map Outer Wrapper — holds map container + overlaid controls */
.svg-map-outer {
  flex: 1;
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Map Container */
.svg-map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #fafafa;
  cursor: grab;
  touch-action: none;
  user-select: none;
}

.svg-map-container:active,
.svg-map-container.is-dragging {
  cursor: grabbing;
}

.svg-map {
  width: 100%;
  height: 100%;
  display: block;
  transition: all 0.5s ease-out;
}

.svg-map-loading {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  z-index: 10;
}

.svg-map-error {
  color: #F44336;
  font-size: 14px;
  margin-top: 8px;
  padding: 8px 16px;
  background: #FFEBEE;
  border-radius: 4px;
}

.svg-map-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #FF9800;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}


/* Navigation Path Overlay */
.nav-path-overlay {
  pointer-events: none;
}

/* Responsive - Liquid Design */
@media (max-width: 768px) {
  .svg-navigate-view {
    height: 100vh;
    height: 100dvh;
  }
  
  .svg-nav-panel,
  .svg-nav-controls {
    padding: 12px;
  }
  
  .svg-nav-header {
    padding: 10px 12px;
  }
  
  .svg-nav-title {
    font-size: 1.1rem;
  }
  
  .svg-nav-field {
    gap: 8px;
    margin-bottom: 12px;
  }
  
  .svg-nav-input,
  .svg-nav-select {
    font-size: 16px; /* Prevents zoom on iOS */
    padding: 10px 12px;
  }
  
  .svg-nav-buttons {
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .svg-nav-btn {
    font-size: 13px;
    padding: 10px 12px;
    flex: 1;
    min-width: 100px;
  }
  
  /* Map container mobile */
  .svg-nav-map-container {
    min-height: 250px;
  }
  
  /* Navigation path info mobile */
  .svg-nav-path-info {
    max-width: calc(100vw - 24px);
    font-size: 14px;
  }
  
  .svg-nav-path-info-header {
    padding: 10px 12px;
  }
  
  /* Step counter mobile */
  .svg-nav-step-counter {
    font-size: 13px;
    padding: 8px 12px;
  }

  .nav-fab-container {
    bottom: 12px;
    right: 12px;
  }
}

/* Small mobile devices */
@media (max-width: 480px) {
  .svg-nav-header {
    padding: 8px 10px;
  }
  
  .svg-nav-title {
    font-size: 1rem;
  }
  
  .svg-nav-panel {
    padding: 10px;
  }
  
  .svg-nav-field {
    flex-direction: column;
    align-items: stretch;
  }
  
  .svg-nav-field > * {
    width: 100%;
  }
  
  .svg-nav-btn {
    font-size: 12px;
    padding: 8px 10px;
  }
  
  .svg-nav-multi-to {
    flex-direction: column;
  }
}

/* Navigation FAB Buttons */
.nav-fab-container {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 101;
}

.nav-fab-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  position: relative;
}

.nav-fab-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
}

.nav-notification-btn {
  background: #1a2b3c;
  color: white;
}

.nav-chatbot-btn {
  background: #FF9800;
  color: white;
}

.nav-fab-btn .material-icons {
  font-size: 24px;
}

.nav-fab-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #F44336;
  color: white;
  font-size: 11px;
  font-weight: bold;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.svg-map-skeleton-wrap { position: absolute; inset: 0; z-index: 10; }
.map-sk-full { width: 100%; height: 100%; }
.map-sk-center {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center; gap: 12px;
  pointer-events: none;
}
.map-sk-hint {
  font-size: 13px; font-weight: 500; color: #FF9800;
  background: linear-gradient(90deg, rgba(255,152,0,0.4), #FF9800 50%, rgba(255,152,0,0.4));
  background-size: 200% auto;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: mapHintShimmer 2s linear infinite;
}
@keyframes mapHintShimmer {
  0% { background-position: 200% center; } 100% { background-position: -200% center; }
}
.svg-map-error-state {
  position: absolute; inset: 0; z-index: 10;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;
  background: var(--color-surface, #fff); color: #F44336;
}

/* ── Outer wrapper: fills remaining height, holds map + controls ── */
.svg-map-outer {
  flex: 1;
  position: relative;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

/* ── Map container fills the outer wrapper ── */
.svg-map-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--color-surface);
  cursor: grab;
  touch-action: none;
  user-select: none;
  min-height: 200px;
}

.svg-map-container.is-dragging { cursor: grabbing; }

/* ── Zoom + Rotate controls — bottom-right of outer wrapper ── */
.map-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 50;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  background: var(--color-bg);
}

.map-ctrl-btn {
  width: 46px;
  height: 46px;
  background: var(--color-bg);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--color-text-primary);
  transition: background var(--duration-fast) var(--ease-out),
              transform  var(--duration-fast) var(--ease-spring);
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  min-height: unset;
  min-width: unset;
}

.map-ctrl-btn:hover  { background: var(--color-surface); }
.map-ctrl-btn:active {
  transform: scale(0.88);
  background: var(--color-primary-light);
}

.map-ctrl-btn .material-icons {
  font-size: 22px;
  color: var(--color-text-secondary);
}

.map-ctrl-reset .material-icons { color: var(--color-primary); }

.map-ctrl-divider {
  width: 100%;
  height: 1px;
  background: var(--color-border);
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .map-controls { bottom: 12px; right: 12px; }
  .map-ctrl-btn { width: 44px; height: 44px; }
}
</style>
