<template>
  <div class="svg-navigate-view">
    <!-- Top bar -->
    <header class="svg-nav-header">
      <button class="svg-nav-back-btn" @click="$router.back()">
        <span class="material-icons">arrow_back</span>
      </button>
      <h1 class="svg-nav-title">Navigate</h1>
    </header>

    <!-- Path Selection Panel -->
    <div class="svg-nav-panel" v-if="!isNavigating">
      <div class="svg-nav-field">
        <span class="material-icons svg-nav-icon">route</span>
        <select v-model="selectedPathId" class="svg-nav-select">
          <option value="">Select a path</option>
          <option v-for="path in availablePaths" :key="path.id" :value="path.id">
            {{ path.name }}
          </option>
        </select>
      </div>

      <div class="svg-nav-actions">
        <button 
          class="svg-nav-start-btn" 
          @click="startNavigation" 
          :disabled="!selectedPathId"
        >
          <span class="material-icons">play_arrow</span>
          Start Navigation
        </button>
      </div>

      <!-- Path Preview -->
      <div v-if="selectedPath" class="svg-nav-preview">
        <h4>{{ selectedPath.name }}</h4>
        <p>{{ selectedPath.description }}</p>
        <div class="svg-nav-stops">
          <span class="svg-nav-stop" v-for="(stop, index) in selectedPath.elementIds" :key="index">
            {{ index + 1 }}. {{ stop }}
          </span>
        </div>
      </div>
    </div>

    <!-- Navigation Controls (visible during navigation) -->
    <div class="svg-nav-controls" v-if="isNavigating">
      <div class="svg-nav-progress">
        <span class="svg-nav-step-info">
          Step {{ currentStepInfo.step + 1 }} of {{ currentStepInfo.totalSteps }}
        </span>
        <span class="svg-nav-current-location">{{ currentStepInfo.elementId }}</span>
      </div>
      
      <div class="svg-nav-buttons">
        <button 
          class="svg-nav-btn" 
          @click="previousStep" 
          :disabled="currentStepInfo.isFirst"
        >
          <span class="material-icons">skip_previous</span>
          Previous
        </button>
        
        <button class="svg-nav-btn svg-nav-stop-btn" @click="stopNavigation">
          <span class="material-icons">stop</span>
          Stop
        </button>
        
        <button 
          class="svg-nav-btn" 
          @click="nextStep" 
          :disabled="currentStepInfo.isLast"
        >
          Next
          <span class="material-icons">skip_next</span>
        </button>
      </div>
    </div>

    <!-- SVG Map Container -->
    <div 
      class="svg-map-container" 
      ref="mapContainer" 
      @wheel="handleWheelZoom"
      @mousedown="startDrag"
      @mousemove="drag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
      @touchstart="startDrag"
      @touchmove="drag"
      @touchend="endDrag"
      :class="{ 'is-dragging': isDragging }"
    >
      <svg 
        ref="svgMap"
        class="svg-map"
        :viewBox="viewBoxString"
        preserveAspectRatio="xMidYMid meet"
        xmlns="http://www.w3.org/2000/svg"
        style="pointer-events: none;"
      >
        <!-- Map content will be loaded dynamically -->
        <g v-if="mapLoaded" v-html="svgContent" style="pointer-events: none;"></g>
        
        <!-- Navigation Path Overlay -->
        <g v-if="isNavigating && pathPositions.length > 0" class="nav-path-overlay" style="pointer-events: none;">
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
            :key="index"
            :cx="pos.x"
            :cy="pos.y"
            :r="index === currentStepInfo.step ? 30 : 18"
            :fill="index === currentStepInfo.step ? '#FF5722' : '#4CAF50'"
            :stroke="'white'"
            :stroke-width="index === currentStepInfo.step ? 6 : 3"
            filter="drop-shadow(0 0 8px rgba(0,0,0,0.5))"
          />
          
          <!-- Labels -->
          <text
            v-for="(pos, index) in pathPositions"
            :key="`label-${index}`"
            :x="pos.x"
            :y="pos.y - 30"
            text-anchor="middle"
            fill="#333"
            font-size="24"
            font-weight="bold"
            style="text-shadow: 2px 2px 4px white;"
          >
            {{ pos.id }}
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
      <div v-if="!mapLoaded" class="svg-map-loading">
        <div class="svg-map-spinner"></div>
        <p>Loading map...</p>
      </div>
    </div>

    <!-- Zoom Controls -->
    <div class="svg-zoom-controls">
      <button class="svg-zoom-btn" @click="zoomIn" title="Zoom In">
        <span class="material-icons">zoom_in</span>
      </button>
      <button class="svg-zoom-btn" @click="zoomOut" title="Zoom Out">
        <span class="material-icons">zoom_out</span>
      </button>
      <button class="svg-zoom-btn" @click="resetView" title="Reset View">
        <span class="material-icons">center_focus_strong</span>
      </button>
      <button class="svg-zoom-btn" @click="fitToPath" v-if="isNavigating" title="Fit to Path">
        <span class="material-icons">fit_screen</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import pathManager from '../services/pathManager.js'

// DOM References
const mapContainer = ref(null)
const svgMap = ref(null)

// State
const mapLoaded = ref(false)
const svgContent = ref('')
const selectedPathId = ref('')
const viewBox = ref({ x: 0, y: 0, width: 3306, height: 7159 })
const zoomLevel = ref(1)
const pathPositions = ref([])

// Drag/Pan state
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const viewBoxStart = ref({ x: 0, y: 0 })
const isTransitioning = ref(false)

// Get path manager state
const isNavigating = computed(() => pathManager.isNavigating.value)
const currentPath = computed(() => pathManager.currentPath.value)
const currentStepInfo = computed(() => pathManager.getCurrentStep() || {
  step: 0,
  totalSteps: 0,
  elementId: '',
  isFirst: true,
  isLast: true
})

// Available paths
const availablePaths = computed(() => pathManager.getAllPaths())

// Selected path
const selectedPath = computed(() => {
  if (!selectedPathId.value) return null
  return pathManager.getPath(selectedPathId.value)
})

// ViewBox string for SVG attribute
const viewBoxString = computed(() => {
  return `${viewBox.value.x} ${viewBox.value.y} ${viewBox.value.width} ${viewBox.value.height}`
})

// Current position based on step
const currentPosition = computed(() => {
  if (!isNavigating.value || pathPositions.value.length === 0) return null
  return pathPositions.value[currentStepInfo.value.step] || null
})

// Path points for polyline
const pathPoints = computed(() => {
  if (pathPositions.value.length === 0) return ''
  return pathPositions.value
    .filter(p => !p.notFound)
    .map(p => `${p.x},${p.y}`)
    .join(' ')
})

// Load SVG map
const loadMap = async () => {
  try {
    // Load SVG file
    const response = await fetch('/SEAIT_Map0.1.svg')
    if (!response.ok) throw new Error('Failed to load map')
    
    const svgText = await response.text()
    
    // Extract inner content from SVG
    const parser = new DOMParser()
    const doc = parser.parseFromString(svgText, 'image/svg+xml')
    const svg = doc.querySelector('svg')
    
    if (svg) {
      // Get viewBox from original SVG
      const originalViewBox = svg.getAttribute('viewBox')
      if (originalViewBox) {
        const [x, y, width, height] = originalViewBox.split(' ').map(Number)
        viewBox.value = { x, y, width, height }
      }
      
      // Extract inner content
      svgContent.value = svg.innerHTML
      mapLoaded.value = true
      
      // Wait for DOM update then calculate positions
      await nextTick()
      
      if (isNavigating.value && currentPath.value) {
        calculatePathPositions()
      }
    }
  } catch (error) {
    console.error('Error loading map:', error)
    // Use inline fallback SVG
    svgContent.value = getFallbackSvgContent()
    mapLoaded.value = true
  }
}

// Calculate positions of path elements
const calculatePathPositions = () => {
  if (!currentPath.value) return
  
  // Use path.points (coordinates) if available, fallback to elementIds lookup
  let positions = []
  
  if (currentPath.value.points && currentPath.value.points.length > 0) {
    // Use saved point coordinates directly
    positions = currentPath.value.points.map((p, index) => ({
      x: p[0],
      y: p[1],
      elementId: currentPath.value.elementIds?.[index] || `point_${index}`,
      notFound: false
    }))
  } else if (svgMap.value && currentPath.value.elementIds?.length > 0) {
    // Fallback: lookup SVG elements by ID
    positions = pathManager.getElementPositions(
      svgMap.value,
      currentPath.value.elementIds
    )
  }
  
  pathPositions.value = positions
  
  // If navigating, center on current step
  if (isNavigating.value && positions.length > 0) {
    const currentPos = positions[currentStepInfo.value.step]
    if (currentPos && !currentPos.notFound) {
      centerOnPoint(currentPos.x, currentPos.y, 2)
    }
  }
}

// Center viewBox on a specific point with smooth animation
const centerOnPoint = (x, y, zoom = 1, animate = false) => {
  const container = mapContainer.value
  if (!container) return
  
  const rect = container.getBoundingClientRect()
  const viewWidth = rect.width / zoom
  const viewHeight = rect.height / zoom
  
  const targetViewBox = {
    x: x - viewWidth / 2,
    y: y - viewHeight / 2,
    width: viewWidth,
    height: viewHeight,
    zoom
  }
  
  if (animate && !isTransitioning.value) {
    isTransitioning.value = true
    animateViewBoxTransition(viewBox.value, targetViewBox, 400)
  } else {
    viewBox.value = targetViewBox
    zoomLevel.value = zoom
  }
}

// Smooth animation between viewBox states
const animateViewBoxTransition = (from, to, duration) => {
  const startTime = performance.now()
  
  const animate = (currentTime) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)
    
    // Ease-out-cubic easing
    const easeProgress = 1 - Math.pow(1 - progress, 3)
    
    viewBox.value = {
      x: from.x + (to.x - from.x) * easeProgress,
      y: from.y + (to.y - from.y) * easeProgress,
      width: from.width + (to.width - from.width) * easeProgress,
      height: from.height + (to.height - from.height) * easeProgress
    }
    
    if (progress < 1) {
      requestAnimationFrame(animate)
    } else {
      viewBox.value = to
      zoomLevel.value = to.zoom
      isTransitioning.value = false
    }
  }
  
  requestAnimationFrame(animate)
}

// Fit view to show entire path
const fitToPath = () => {
  if (pathPositions.value.length === 0) return
  
  const bbox = pathManager.calculatePathViewBox(pathPositions.value, 200)
  viewBox.value = bbox
  zoomLevel.value = 1
}

// Start navigation
const startNavigation = async () => {
  if (!selectedPathId.value) return
  
  pathManager.startNavigation(selectedPathId.value)
  
  await nextTick()
  calculatePathPositions()
}

// Stop navigation
const stopNavigation = () => {
  pathManager.stopNavigation()
  pathPositions.value = []
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
  // Only drag with left mouse button or touch
  if (e.type === 'mousedown' && e.button !== 0) return
  
  isDragging.value = true
  const clientX = e.clientX || (e.touches?.[0]?.clientX)
  const clientY = e.clientY || (e.touches?.[0]?.clientY)
  
  dragStart.value = { x: clientX, y: clientY }
  viewBoxStart.value = { 
    x: viewBox.value.x, 
    y: viewBox.value.y 
  }
}

const drag = (e) => {
  if (!isDragging.value) return
  e.preventDefault()
  
  const clientX = e.clientX || (e.touches?.[0]?.clientX)
  const clientY = e.clientY || (e.touches?.[0]?.clientY)
  
  // Calculate the drag delta in screen pixels
  const deltaX = clientX - dragStart.value.x
  const deltaY = clientY - dragStart.value.y
  
  // Convert screen pixels to SVG viewBox units
  const svgUnitsPerPixelX = viewBox.value.width / (mapContainer.value?.getBoundingClientRect().width || 1)
  const svgUnitsPerPixelY = viewBox.value.height / (mapContainer.value?.getBoundingClientRect().height || 1)
  
  // Update viewBox (inverse direction for natural panning)
  viewBox.value = {
    ...viewBox.value,
    x: viewBoxStart.value.x - deltaX * svgUnitsPerPixelX,
    y: viewBoxStart.value.y - deltaY * svgUnitsPerPixelY
  }
}

const endDrag = () => {
  isDragging.value = false
}

// Handle mouse wheel zoom
const handleWheelZoom = (event) => {
  event.preventDefault()
  
  const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
  const newZoom = Math.max(0.3, Math.min(5, zoomLevel.value * zoomFactor))
  
  // Zoom towards mouse pointer
  const rect = mapContainer.value?.getBoundingClientRect()
  if (rect) {
    const mouseX = event.clientX - rect.left
    const mouseY = event.clientY - rect.top
    
    const svgUnitsPerPixelX = viewBox.value.width / rect.width
    const svgUnitsPerPixelY = viewBox.value.height / rect.height
    
    const mouseViewBoxX = viewBox.value.x + mouseX * svgUnitsPerPixelX
    const mouseViewBoxY = viewBox.value.y + mouseY * svgUnitsPerPixelY
    
    const newWidth = (rect.width / newZoom) * svgUnitsPerPixelX
    const newHeight = (rect.height / newZoom) * svgUnitsPerPixelY
    
    viewBox.value = {
      x: mouseViewBoxX - (mouseX / rect.width) * newWidth,
      y: mouseViewBoxY - (mouseY / rect.height) * newHeight,
      width: newWidth,
      height: newHeight
    }
    zoomLevel.value = newZoom
  } else {
    const centerX = viewBox.value.x + viewBox.value.width / 2
    const centerY = viewBox.value.y + viewBox.value.height / 2
    centerOnPoint(centerX, centerY, newZoom)
  }
}

// Zoom controls
const zoomIn = () => {
  const centerX = viewBox.value.x + viewBox.value.width / 2
  const centerY = viewBox.value.y + viewBox.value.height / 2
  zoomLevel.value = Math.min(zoomLevel.value * 1.3, 5)
  centerOnPoint(centerX, centerY, zoomLevel.value)
}

const zoomOut = () => {
  const centerX = viewBox.value.x + viewBox.value.width / 2
  const centerY = viewBox.value.y + viewBox.value.height / 2
  zoomLevel.value = Math.max(zoomLevel.value / 1.3, 0.3)
  centerOnPoint(centerX, centerY, zoomLevel.value)
}

const resetView = () => {
  viewBox.value = { x: 0, y: 0, width: 3306, height: 7159 }
  zoomLevel.value = 1
}

// Fallback SVG content
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

// Lifecycle
onMounted(() => {
  loadMap()
})

onUnmounted(() => {
  pathManager.stopNavigation()
})
</script>

<style scoped>
.svg-navigate-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
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
  background: white;
  border-bottom: 1px solid #e0e0e0;
}

.svg-nav-field {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.svg-nav-icon {
  color: #666;
  font-size: 24px;
}

.svg-nav-select {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  background: white;
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
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.svg-nav-start-btn:hover:not(:disabled) {
  background: #45a049;
}

.svg-nav-start-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* Path Preview */
.svg-nav-preview {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 8px;
}

.svg-nav-preview h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.svg-nav-preview p {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

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

/* Navigation Controls */
.svg-nav-controls {
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  gap: 12px;
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
  background: #FF9800;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.svg-nav-btn:hover:not(:disabled) {
  background: #F57C00;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255,152,0,0.4);
}

.svg-nav-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.svg-nav-stop-btn {
  background: #f44336;
}

.svg-nav-stop-btn:hover {
  background: #d32f2f;
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

/* Ensure container captures all pointer events */
.svg-map-container * {
  pointer-events: none !important;
}

.svg-map {
  width: 100%;
  height: 100%;
  display: block;
  will-change: transform;
}

/* Smooth transitions during navigation */
.svg-map.smooth-transition {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.svg-map-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.9);
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

/* Zoom Controls */
.svg-zoom-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.svg-zoom-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.svg-zoom-btn:hover {
  background: #f5f5f5;
  border-color: #1976d2;
}

.svg-zoom-btn .material-icons {
  font-size: 24px;
  color: #666;
}

/* Navigation Path Overlay */
.nav-path-overlay {
  pointer-events: none;
}

/* Responsive */
@media (max-width: 768px) {
  .svg-nav-panel,
  .svg-nav-controls {
    padding: 12px;
  }
  
  .svg-nav-buttons {
    flex-wrap: wrap;
  }
  
  .svg-nav-btn {
    font-size: 13px;
    padding: 10px 12px;
  }
  
  .svg-zoom-controls {
    bottom: 12px;
    right: 12px;
  }
}
</style>
