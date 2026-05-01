<template>
  <div class="admin-path-manager">
    <h2>SVG Path Management</h2>
    <p class="admin-description">
      Create and manage navigation paths using SVG element IDs. 
      Each path is a sequence of SVG element IDs that will be connected to form a route.
    </p>

    <!-- Path List -->
    <div v-if="!isCreatingNew" class="admin-section">
      <div class="admin-section-header">
        <h3>Existing Paths</h3>
        <button class="admin-btn admin-btn-primary" @click="createNewPath">
          <span class="material-icons">add</span>
          Create New Path
        </button>
      </div>

      <div v-if="paths.length === 0" class="admin-empty">
        No paths created yet. Click "Create New Path" to start.
      </div>

      <div v-else class="admin-path-list">
        <div 
          v-for="path in paths" 
          :key="path.id"
          class="admin-path-item"
          :class="{ 'is-editing': editingPathId === path.id }"
          @click="editPath(path.id)"
        >
          <div class="admin-path-info">
            <h4>{{ path.name }}</h4>
            <p v-if="path.description">{{ path.description }}</p>
            <div class="admin-path-meta">
              <span>{{ path.elementIds.length }} stops</span>
              <span>Updated: {{ formatDate(path.updatedAt) }}</span>
            </div>
          </div>
          <div class="admin-path-actions">
            <button class="admin-icon-btn" @click.stop="navigateToPath(path.id)" title="Navigate">
              <span class="material-icons">navigation</span>
            </button>
            <button class="admin-icon-btn" @click.stop="previewPath(path.id)" title="Preview">
              <span class="material-icons">visibility</span>
            </button>
            <button class="admin-icon-btn" @click.stop="duplicatePath(path.id)" title="Duplicate">
              <span class="material-icons">content_copy</span>
            </button>
            <button class="admin-icon-btn admin-icon-btn-danger" @click.stop="deletePath(path.id)" title="Delete">
              <span class="material-icons">delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Path Editor -->
    <div v-if="isEditing" class="admin-section admin-editor">
      <div class="admin-section-header">
        <h3>{{ isCreatingNew ? 'Create New Path' : 'Edit Path' }}</h3>
        <button v-if="isCreatingNew" class="admin-btn admin-btn-primary" @click="createNewPath">
          <span class="material-icons">add</span>
          Create Another Path
        </button>
      </div>
      
      <div class="admin-form">
        <div class="admin-form-group">
          <label>Path Name</label>
          <input 
            v-model="editForm.name" 
            type="text" 
            placeholder="e.g., College Gate to Tailoring"
            class="admin-input"
          >
        </div>

        <div class="admin-form-group">
          <label>Description</label>
          <textarea 
            v-model="editForm.description" 
            placeholder="Brief description of this path"
            class="admin-input admin-textarea"
            rows="2"
          ></textarea>
        </div>

        <div class="admin-form-group">
          <label>Path Stops (SVG Element IDs in order)</label>
          <div class="admin-stops-editor">
            <div 
              v-for="(stop, index) in editForm.elementIds" 
              :key="index"
              class="admin-stop-item"
            >
              <span class="admin-stop-number">{{ index + 1 }}</span>
              <input 
                v-model="editForm.elementIds[index]" 
                type="text" 
                placeholder="SVG element ID (e.g., college_gate)"
                class="admin-input admin-stop-input"
              >
              <button 
                class="admin-icon-btn admin-icon-btn-small" 
                @click="moveStopUp(index)"
                :disabled="index === 0"
                title="Move up"
              >
                <span class="material-icons">arrow_upward</span>
              </button>
              <button 
                class="admin-icon-btn admin-icon-btn-small" 
                @click="moveStopDown(index)"
                :disabled="index === editForm.elementIds.length - 1"
                title="Move down"
              >
                <span class="material-icons">arrow_downward</span>
              </button>
              <button 
                class="admin-icon-btn admin-icon-btn-small admin-icon-btn-danger" 
                @click="removeStop(index)"
                title="Remove"
              >
                <span class="material-icons">remove_circle</span>
              </button>
            </div>
            
            <button class="admin-btn admin-btn-secondary" @click="addStop">
              <span class="material-icons">add_location</span>
              Add Stop
            </button>
          </div>
        </div>

        <div class="admin-form-actions">
          <button class="admin-btn" @click="cancelEdit">Cancel</button>
          <button class="admin-btn admin-btn-primary" @click="savePath">
            <span class="material-icons">save</span>
            Save Path
          </button>
        </div>
      </div>

      <!-- Interactive Visual Editor -->
      <div class="admin-preview-section">
        <h4>Interactive Path Editor (Click on map to add points)</h4>
        
        <!-- Editor Mode Toggle -->
        <div class="admin-editor-modes">
          <button 
            class="admin-btn" 
            :class="{ 'admin-btn-primary': editorMode === 'view' }"
            @click="editorMode = 'view'"
          >
            <span class="material-icons">visibility</span> View
          </button>
          <button 
            class="admin-btn" 
            :class="{ 'admin-btn-primary': editorMode === 'add' }"
            @click="editorMode = 'add'"
          >
            <span class="material-icons">add_location</span> Click to Add Points
          </button>
          <button 
            class="admin-btn" 
            :class="{ 'admin-btn-danger': editorMode === 'delete' }"
            @click="editorMode = 'delete'"
          >
            <span class="material-icons">delete</span> Delete Point
          </button>
        </div>

        <!-- Scale Controls -->
        <div class="admin-scale-controls">
          <span>Scale: {{ (scale * 100).toFixed(0) }}%</span>
          <input 
            type="range" 
            min="0.5" 
            max="5" 
            step="0.1" 
            v-model.number="scale"
            class="admin-scale-slider"
          >
          <button class="admin-btn admin-btn-small" @click="scale = 1">Reset</button>
          <button class="admin-btn admin-btn-small" @click="scale = 2">200%</button>
          <button class="admin-btn admin-btn-small" @click="scale = 5">500%</button>
        </div>
        
        <!-- Add Mode Overlay Indicator -->
        <div v-if="editorMode === 'add'" class="add-mode-indicator">
          <span class="material-icons">touch_app</span>
          CLICK ANYWHERE ON MAP TO ADD POINTS
        </div>
        
        <!-- Grid Toggle -->
        <div class="admin-grid-toggle">
          <label class="admin-checkbox-label">
            <input type="checkbox" v-model="showGrid" />
            <span>Show Grid</span>
          </label>
        </div>
        
        <div 
          class="admin-svg-preview admin-interactive-preview" 
          ref="previewContainer"
          :style="{ height: `${600 * scale}px`, cursor: editorMode === 'add' ? 'crosshair' : 'grab' }"
          :class="{ 'add-mode-active': editorMode === 'add', 'panning': isPanning }"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        >
          <svg 
            ref="previewSvg"
            class="admin-preview-svg"
            :viewBox="previewViewBox"
            preserveAspectRatio="xMidYMid meet"
            xmlns="http://www.w3.org/2000/svg"
            @click="handleSvgClick"
            :class="{ 'clickable-mode': editorMode === 'add', 'delete-mode': editorMode === 'delete' }"
          >
            <!-- Map content - pointer events disabled in add mode to allow clicking through -->
            <g 
              v-if="mapLoaded" 
              v-html="svgContent" 
              :style="editorMode === 'add' ? 'pointer-events: none;' : ''"
            ></g>
            
            <!-- Grid Overlay -->
            <g v-if="showGrid" class="grid-overlay" pointer-events="none">
              <defs>
                <pattern id="gridPattern" :width="gridSize" :height="gridSize" patternUnits="userSpaceOnUse">
                  <path :d="`M ${gridSize} 0 L 0 0 0 ${gridSize}`" fill="none" stroke="#2196F3" stroke-width="1" opacity="0.5"/>
                </pattern>
              </defs>
              <rect :width="svgWidth" :height="svgHeight" fill="url(#gridPattern)" />
              <!-- Coordinate labels every 1000 units -->
              <text 
                v-for="x in Math.floor(svgWidth / 1000)" 
                :key="`x-${x}`"
                :x="x * 1000" 
                :y="30" 
                font-size="20" 
                fill="#2196F3"
                opacity="0.7"
                text-anchor="middle"
              >{{ x * 1000 }}</text>
              <text 
                v-for="y in Math.floor(svgHeight / 1000)" 
                :key="`y-${y}`"
                x="40" 
                :y="y * 1000" 
                font-size="20" 
                fill="#2196F3"
                opacity="0.7"
                text-anchor="middle"
                dominant-baseline="middle"
              >{{ y * 1000 }}</text>
            </g>
            
            <!-- Visual Path Overlay with Lines -->
            <g v-if="visualPoints.length > 0" class="visual-path-overlay">
              <!-- Connecting Lines Between Points -->
              <line
                v-for="(line, index) in connectingLines"
                :key="`line-${index}`"
                :x1="line.x1"
                :y1="line.y1"
                :x2="line.x2"
                :y2="line.y2"
                stroke="#FF5722"
                stroke-width="4"
                stroke-linecap="round"
                opacity="0.9"
              />
              
              <!-- Point Markers -->
              <g 
                v-for="(point, index) in visualPoints" 
                :key="`point-${index}`"
                class="point-marker"
                @click.stop="handlePointClick(index)"
                :class="{ 'deletable': editorMode === 'delete' }"
              >
                <!-- Point Circle -->
                <circle
                  :cx="point.x"
                  :cy="point.y"
                  :r="editorMode === 'delete' ? 25 : 20"
                  :fill="editorMode === 'delete' ? '#ff4444' : '#2196F3'"
                  :stroke="index === selectedPointIndex ? '#FF9800' : 'white'"
                  :stroke-width="index === selectedPointIndex ? 4 : 3"
                  class="point-circle"
                />
                
                <!-- Point Number -->
                <text
                  :x="point.x"
                  :y="point.y"
                  text-anchor="middle"
                  dominant-baseline="central"
                  fill="white"
                  font-size="16"
                  font-weight="bold"
                  pointer-events="none"
                >
                  {{ index + 1 }}
                </text>
              </g>
            </g>
            
            <!-- Hover indicator for add mode -->
            <g v-if="editorMode === 'add' && hoverPoint">
              <circle
                :cx="hoverPoint.x"
                :cy="hoverPoint.y"
                r="15"
                fill="none"
                stroke="#4CAF50"
                stroke-width="2"
                stroke-dasharray="5,5"
                opacity="0.7"
              />
            </g>
          </svg>
          
          <div v-if="!mapLoaded" class="admin-preview-loading">
            <div class="spinner"></div>
            <p>Loading map...</p>
          </div>
          
          <div v-if="visualPoints.length === 0 && mapLoaded" class="admin-preview-hint">
            <p><strong>{{ editorMode === 'add' ? 'Click anywhere on the map to add your first point!' : 'Switch to "Click to Add Points" mode to start creating a path' }}</strong></p>
          </div>
        </div>
        
        <div class="admin-preview-info-panel">
          <div class="admin-preview-stats">
            <span class="stat-item">
              <span class="material-icons">place</span>
              {{ visualPoints.length }} points
            </span>
            <span class="stat-item">
              <span class="material-icons">timeline</span>
              {{ connectingLines.length }} connections
            </span>
            <span class="stat-item" v-if="selectedPointIndex >= 0">
              <span class="material-icons">adjust</span>
              Selected: Point {{ selectedPointIndex + 1 }}
            </span>
          </div>
          
          <div class="admin-preview-controls">
            <button class="admin-btn" @click="resetPreview">
              <span class="material-icons">center_focus_strong</span> Reset View
            </button>
            <button class="admin-btn" @click="fitToVisualPath" :disabled="visualPoints.length === 0">
              <span class="material-icons">zoom_in_map</span> Fit to Path
            </button>
            <button class="admin-btn admin-btn-danger" @click="clearAllPoints" :disabled="visualPoints.length === 0">
              <span class="material-icons">clear_all</span> Clear All
            </button>
          </div>
        </div>

        <!-- Point List Editor -->
        <div class="admin-point-list" v-if="visualPoints.length > 0">
          <h5>Path Points ({{ visualPoints.length }})</h5>
          <div class="point-list-container">
            <div 
              v-for="(point, index) in visualPoints" 
              :key="`list-${index}`"
              class="point-list-item"
              :class="{ 'selected': selectedPointIndex === index }"
              @click="selectedPointIndex = index"
            >
              <span class="point-number">{{ index + 1 }}</span>
              <input 
                v-model="point.id" 
                type="text" 
                class="point-id-input"
                placeholder="Point ID"
                @change="syncToElementIds"
              >
              <span class="point-coords">({{ Math.round(point.x) }}, {{ Math.round(point.y) }})</span>
              <button class="admin-icon-btn-small" @click.stop="removePoint(index)" title="Remove">
                <span class="material-icons">close</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Import/Export -->
    <div class="admin-section">
      <h3>Import / Export</h3>
      <div class="admin-import-export">
        <div class="admin-export">
          <h4>Export All Paths</h4>
          <button class="admin-btn" @click="exportAllPaths">
            <span class="material-icons">download</span>
            Download JSON
          </button>
        </div>
        
        <div class="admin-import">
          <h4>Import Paths</h4>
          <input 
            type="file" 
            accept=".json" 
            @change="handleImport"
            ref="importFile"
            style="display: none"
          >
          <button class="admin-btn" @click="$refs.importFile.click()">
            <span class="material-icons">upload</span>
            Import JSON
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import pathManager from '../../services/pathManager.js'
import api from '../../services/api.js'

const router = useRouter()

// State
const paths = ref([])
const mapLoaded = ref(false)
const svgContent = ref('')
const editingPathId = ref(null)
const isCreatingNew = ref(false)
const importFile = ref(null)
const previewContainer = ref(null)
const previewSvg = ref(null)
// Computed viewBox for pan/zoom support
const previewViewBox = computed(() => {
  return `${viewBoxX.value} ${viewBoxY.value} ${viewBoxWidth.value} ${viewBoxHeight.value}`
})
const svgWidth = ref(3306)
const svgHeight = ref(7159)

// Grid State
const showGrid = ref(false)
const gridSize = ref(40) // Grid cell size in SVG units (40px for fine grid)

// Interactive Editor State
const editorMode = ref('view') // 'view', 'add', 'delete'
const scale = ref(2) // Default to 200% for better visibility
const visualPoints = ref([]) // Array of {x, y, id} points
const selectedPointIndex = ref(-1)
const hoverPoint = ref(null)
let pointCounter = 1

// Pan/Grab State
const isPanning = ref(false)
const panStartX = ref(0)
const panStartY = ref(0)
const viewBoxX = ref(0)
const viewBoxY = ref(0)
const viewBoxWidth = ref(3306)
const viewBoxHeight = ref(7159)

// Edit form
const editForm = ref({
  name: '',
  description: '',
  elementIds: []
})

// Computed
const isEditing = computed(() => editingPathId.value !== null)
const previewPositions = ref([])

// Calculate connecting lines between consecutive points
const connectingLines = computed(() => {
  const lines = []
  for (let i = 0; i < visualPoints.value.length - 1; i++) {
    const p1 = visualPoints.value[i]
    const p2 = visualPoints.value[i + 1]
    lines.push({
      x1: p1.x,
      y1: p1.y,
      x2: p2.x,
      y2: p2.y
    })
  }
  return lines
})

const previewPathPoints = computed(() => {
  if (previewPositions.value.length === 0) return ''
  return previewPositions.value
    .filter(p => !p.notFound)
    .map(p => `${p.x},${p.y}`)
    .join(' ')
})

// Load data
const loadPaths = async () => {
  try {
    console.log('[AdminPathManager] Loading paths...')
    await pathManager.loadPaths()
    paths.value = pathManager.getAllPaths()
    console.log('[AdminPathManager] Loaded', paths.value.length, 'paths')
  } catch (error) {
    console.error('[AdminPathManager] Error loading paths:', error)
    // Fallback: get paths from localStorage via pathManager
    paths.value = pathManager.getAllPaths()
  }
}

const loadMap = async () => {
  try {
    const response = await fetch('/SEAIT_Map0.1.svg')
    if (!response.ok) throw new Error('Failed to load map')
    
    const svgText = await response.text()
    const parser = new DOMParser()
    const doc = parser.parseFromString(svgText, 'image/svg+xml')
    const svg = doc.querySelector('svg')
    
    if (svg) {
      const viewBox = svg.getAttribute('viewBox')
      if (viewBox) {
        previewViewBox.value = viewBox
      }
      svgContent.value = svg.innerHTML
      mapLoaded.value = true
    }
  } catch (error) {
    console.error('Error loading map:', error)
  }
}

// Update preview positions
const updatePreview = () => {
  if (!previewSvg.value) return
  
  const positions = pathManager.getElementPositions(
    previewSvg.value,
    editForm.value.elementIds.filter(id => id.trim() !== '')
  )
  
  previewPositions.value = positions
}

// Watch for element ID changes
watch(() => editForm.value.elementIds, () => {
  nextTick(() => updatePreview())
}, { deep: true })

// Watch for map load to sync positions if editing
watch(mapLoaded, (loaded) => {
  if (loaded && isEditing.value && previewSvg.value && visualPoints.value.length > 0) {
    // Re-sync from element IDs now that SVG is available
    nextTick(() => {
      syncFromElementIds()
      updatePreview()
    })
  }
})

// Interactive SVG Editor Functions

// Pan/Grab handlers
const handleMouseDown = (event) => {
  // Only start panning in view mode or if holding space
  if (editorMode.value === 'view' || (editorMode.value === 'add' && event.button === 1)) {
    isPanning.value = true
    panStartX.value = event.clientX
    panStartY.value = event.clientY
    previewContainer.value.style.cursor = 'grabbing'
  }
}

const handleMouseMove = (event) => {
  if (!isPanning.value) return
  
  const dx = (event.clientX - panStartX.value) * (viewBoxWidth.value / (600 * scale.value))
  const dy = (event.clientY - panStartY.value) * (viewBoxHeight.value / (600 * scale.value))
  
  viewBoxX.value -= dx
  viewBoxY.value -= dy
  
  panStartX.value = event.clientX
  panStartY.value = event.clientY
}

const handleMouseUp = () => {
  isPanning.value = false
  if (previewContainer.value) {
    previewContainer.value.style.cursor = editorMode.value === 'add' ? 'crosshair' : 'grab'
  }
}

// Handle SVG click to add points
const handleSvgClick = (event) => {
  if (isPanning.value) return // Don't add point if we were panning
  if (editorMode.value !== 'add') return
  
  if (!previewSvg.value) return
  
  // Get click coordinates in SVG space
  const pt = previewSvg.value.createSVGPoint()
  pt.x = event.clientX
  pt.y = event.clientY
  
  // Transform to SVG coordinates (accounting for pan)
  const svgP = pt.matrixTransform(previewSvg.value.getScreenCTM().inverse())
  
  // Snap to grid and calculate row/column
  const grid = gridSize.value
  const col = Math.round((svgP.x - viewBoxX.value) / grid)
  const row = Math.round((svgP.y - viewBoxY.value) / grid)
  const snapX = col * grid
  const snapY = row * grid
  
  // Add new point with grid cell info (row, col) for navigation
  const newPoint = {
    id: `cell_${row}_${col}`,
    x: snapX,
    y: snapY,
    row: row,
    col: col,
    gridSize: grid
  }
  
  console.log(`[AdminPathManager] Added grid cell: Row ${row}, Col ${col} at (${snapX}, ${snapY})`)
  
  visualPoints.value.push(newPoint)
  syncToElementIds()
  
  // Auto-select the new point
  selectedPointIndex.value = visualPoints.value.length - 1
}

// Handle point click (select or delete)
const handlePointClick = (index) => {
  if (editorMode.value === 'delete') {
    removePoint(index)
  } else {
    selectedPointIndex.value = index
  }
}

// Remove a point
const removePoint = (index) => {
  visualPoints.value.splice(index, 1)
  if (selectedPointIndex.value === index) {
    selectedPointIndex.value = -1
  } else if (selectedPointIndex.value > index) {
    selectedPointIndex.value--
  }
  syncToElementIds()
}

// Clear all points
const clearAllPoints = () => {
  if (!confirm('Clear all points?')) return
  visualPoints.value = []
  selectedPointIndex.value = -1
  pointCounter = 1
  syncToElementIds()
}

// Sync visual points to elementIds form
const syncToElementIds = () => {
  editForm.value.elementIds = visualPoints.value.map(p => p.id)
}

// Sync elementIds form to visual points (when loading existing path)
const syncFromElementIds = () => {
  const ids = editForm.value.elementIds.filter(id => id.trim() !== '')

  if (!previewSvg.value || ids.length === 0) {
    visualPoints.value = []
    return
  }

  // Look up actual element positions from SVG
  const positions = pathManager.getElementPositions(previewSvg.value, ids)
  const grid = gridSize.value

  // Distribute points in a zigzag pattern when not found in SVG
  visualPoints.value = positions.map((pos, index) => ({
    id: pos.id,
    x: pos.notFound ? 500 + ((index % 3) * grid * 2) : pos.x,
    y: pos.notFound ? 5000 + (Math.floor(index / 3) * grid * 2) : pos.y
  }))
}

// Fit view to visual path
const fitToVisualPath = () => {
  if (visualPoints.value.length === 0) return
  
  let minX = Infinity, minY = Infinity
  let maxX = -Infinity, maxY = -Infinity
  
  visualPoints.value.forEach(p => {
    minX = Math.min(minX, p.x)
    minY = Math.min(minY, p.y)
    maxX = Math.max(maxX, p.x)
    maxY = Math.max(maxY, p.y)
  })
  
  const padding = 200
  const width = maxX - minX + (padding * 2)
  const height = maxY - minY + (padding * 2)
  
  previewViewBox.value = `${minX - padding} ${minY - padding} ${width} ${height}`
}

// CRUD operations
const createNewPath = () => {
  isCreatingNew.value = true
  editingPathId.value = 'new'
  pointCounter = 1
  visualPoints.value = []
  selectedPointIndex.value = -1
  editForm.value = {
    name: '',
    description: '',
    elementIds: []
  }
  previewPositions.value = []
  editorMode.value = 'add' // Start in add mode for new paths
}

// Edit an existing path - preserve saved point positions
const editPath = (id) => {
  const path = pathManager.getPath(id)
  if (!path) return
  
  isCreatingNew.value = false
  editingPathId.value = id
  editForm.value = {
    name: path.name,
    description: path.description,
    elementIds: [...(path.elementIds || [])]
  }

  // Load saved visualPoints if available, otherwise generate from elementIds
  nextTick(() => {
    if (path.visualPoints && path.visualPoints.length > 0) {
      // Use saved point positions
      visualPoints.value = path.visualPoints.map((p, index) => ({
        id: p.id || editForm.value.elementIds[index] || `point_${index}`,
        x: p.x,
        y: p.y
      }))
      pointCounter = visualPoints.value.length + 1
      updatePreview()
    } else if (mapLoaded.value && previewSvg.value) {
      syncFromElementIds()
      pointCounter = visualPoints.value.length + 1
      updatePreview()
    } else {
      // Default positions if no saved data
      visualPoints.value = editForm.value.elementIds
        .filter(id => id.trim() !== '')
        .map((id, index) => ({
          id,
          x: 500 + (index % 3) * 80,
          y: 5000 + Math.floor(index / 3) * 80
        }))
      pointCounter = visualPoints.value.length + 1
    }
  })
}

const savePath = async () => {
  try {
    console.log('[AdminPathManager] Saving path...')
    
    // Filter out empty element IDs
    const elementIds = editForm.value.elementIds.filter(id => id.trim() !== '')

    if (elementIds.length === 0) {
      alert('Please add at least one stop')
      return
    }

    // Build points array from visualPoints
    const points = visualPoints.value.map(p => [p.x, p.y])
    console.log('[AdminPathManager] Points:', points)

    const pathData = {
      name: editForm.value.name || 'Unnamed Path',
      description: editForm.value.description,
      from: elementIds[0] || '',
      to: elementIds[elementIds.length - 1] || '',
      points,
      elementIds,
      visualPoints: visualPoints.value
    }
    console.log('[AdminPathManager] Path data:', pathData)

    if (isCreatingNew.value) {
      const newPath = await pathManager.createPath(pathData)
      console.log('[AdminPathManager] Created path:', newPath)
    } else {
      const updatedPath = await pathManager.updatePath(editingPathId.value, pathData)
      console.log('[AdminPathManager] Updated path:', updatedPath)
    }

    await loadPaths()
    console.log('[AdminPathManager] Paths reloaded, count:', paths.value.length)
    cancelEdit()
    alert('Path saved successfully!')
  } catch (error) {
    console.error('[AdminPathManager] Failed to save path:', error)
    alert('Failed to save path: ' + error.message)
  }
}

const deletePath = async (id) => {
  if (!confirm('Are you sure you want to delete this path?')) return
  
  await pathManager.deletePath(id)
  await loadPaths()
  
  if (editingPathId.value === id) {
    cancelEdit()
  }
}

const duplicatePath = async (id) => {
  const path = pathManager.getPath(id)
  if (!path) return
  
  const newPath = {
    name: `${path.name} (Copy)`,
    description: path.description,
    from: path.from || (path.elementIds?.[0] || ''),
    to: path.to || (path.elementIds?.[path.elementIds.length - 1] || ''),
    points: path.points || [],
    elementIds: [...(path.elementIds || [])],
    visualPoints: path.visualPoints || []
  }
  
  await pathManager.createPath(newPath)
  await loadPaths()
}

const cancelEdit = () => {
  editingPathId.value = null
  isCreatingNew.value = false
  editForm.value = { name: '', description: '', elementIds: [] }
  previewPositions.value = []
}

// Stop editor functions
const addStop = () => {
  editForm.value.elementIds.push('')
}

const removeStop = (index) => {
  editForm.value.elementIds.splice(index, 1)
  if (editForm.value.elementIds.length === 0) {
    editForm.value.elementIds.push('')
  }
}

const moveStopUp = (index) => {
  if (index === 0) return
  const temp = editForm.value.elementIds[index]
  editForm.value.elementIds[index] = editForm.value.elementIds[index - 1]
  editForm.value.elementIds[index - 1] = temp
}

const moveStopDown = (index) => {
  if (index >= editForm.value.elementIds.length - 1) return
  const temp = editForm.value.elementIds[index]
  editForm.value.elementIds[index] = editForm.value.elementIds[index + 1]
  editForm.value.elementIds[index + 1] = temp
}

// Preview controls
const resetPreview = () => {
  previewViewBox.value = '0 0 3306 7159'
}

const fitToPreview = () => {
  if (previewPositions.value.length === 0) return
  
  const bbox = pathManager.calculatePathViewBox(previewPositions.value, 150)
  previewViewBox.value = `${bbox.x} ${bbox.y} ${bbox.width} ${bbox.height}`
}

// Import / Export
const exportAllPaths = () => {
  const data = {
    paths: paths.value,
    exportedAt: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `svg_paths_${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const handleImport = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = JSON.parse(e.target.result)
      
      if (data.paths && Array.isArray(data.paths)) {
        let imported = 0
        data.paths.forEach(path => {
          try {
            if (path.id && path.elementIds) {
              pathManager.importPath(JSON.stringify(path))
              imported++
            }
          } catch (err) {
            console.warn('Failed to import path:', path.name, err)
          }
        })
        
        loadPaths()
        alert(`Successfully imported ${imported} paths`)
      } else {
        alert('Invalid file format')
      }
    } catch (error) {
      alert('Error reading file: ' + error.message)
    }
  }
  reader.readAsText(file)
  
  // Reset file input
  event.target.value = ''
}

// Preview path
const previewPath = (id) => {
  const path = pathManager.getPath(id)
  if (!path) return
  
  // Create a temporary navigation to show preview
  editPath(id)
  fitToPreview()
}

// Navigate to path in NavigateView
const navigateToPath = (id) => {
  const path = pathManager.getPath(id)
  if (!path || path.elementIds.length < 2) {
    alert('Path needs at least 2 points to navigate')
    return
  }
  
  // Navigate to /navigate with pathId
  router.push({
    path: '/navigate',
    query: { pathId: id }
  })
}

// Utilities
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
}

// Load grid settings from database
const loadGridSettings = async () => {
  try {
    const response = await api.get('/navigation/grid-settings/')
    const settings = response.data
    showGrid.value = settings.show_grid
    gridSize.value = settings.grid_size
    console.log('[AdminPathManager] Grid settings loaded:', settings)
  } catch (error) {
    console.warn('[AdminPathManager] Failed to load grid settings, using defaults:', error)
    // Keep default values
  }
}

// Save grid settings to database
const saveGridSettings = async () => {
  try {
    const settings = {
      show_grid: showGrid.value,
      grid_size: gridSize.value
    }
    await api.put('/navigation/grid-settings/', settings)
    console.log('[AdminPathManager] Grid settings saved')
  } catch (error) {
    console.warn('[AdminPathManager] Failed to save grid settings:', error)
  }
}

// Watch for grid changes and save
watch([showGrid, gridSize], () => {
  saveGridSettings()
}, { debounce: 500 })

// Lifecycle
onMounted(async () => {
  await loadGridSettings()
  await loadPaths()
  await loadMap()
})
</script>

<style scoped>
.admin-path-manager {
  padding: 20px;
  max-width: 1200px;
}

.admin-description {
  color: #666;
  margin-bottom: 20px;
}

.admin-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.admin-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.admin-section h3 {
  margin: 0;
  font-size: 18px;
}

/* Path List */
.admin-path-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.admin-path-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-path-item:hover,
.admin-path-item.is-editing {
  border-color: #1976d2;
  background: #f5f9ff;
}

.admin-path-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
}

.admin-path-info p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #666;
}

.admin-path-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.admin-path-actions {
  display: flex;
  gap: 8px;
}

.admin-icon-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-icon-btn:hover {
  background: #f5f5f5;
  border-color: #1976d2;
}

.admin-icon-btn-danger:hover {
  border-color: #f44336;
  color: #f44336;
}

.admin-icon-btn-small {
  width: 28px;
  height: 28px;
}

.admin-icon-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Editor */
.admin-editor {
  border: 2px solid #1976d2;
}

.admin-form {
  margin-bottom: 24px;
}

.admin-form-group {
  margin-bottom: 16px;
}

.admin-form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.admin-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.admin-input:focus {
  outline: none;
  border-color: #1976d2;
}

.admin-textarea {
  resize: vertical;
  min-height: 60px;
}

/* Stops Editor */
.admin-stops-editor {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.admin-stop-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.admin-stop-number {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1976d2;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 500;
}

.admin-stop-input {
  flex: 1;
}

/* Buttons */
.admin-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.admin-btn:hover {
  background: #f5f5f5;
}

.admin-btn-primary {
  background: #1976d2;
  color: white;
  border-color: #1976d2;
}

.admin-btn-primary:hover {
  background: #1565c0;
}

.admin-btn-secondary {
  background: #f5f5f5;
  border-style: dashed;
}

.admin-form-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

/* Preview */
.admin-preview-section {
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.admin-preview-section h4 {
  margin: 0 0 16px 0;
}

.admin-svg-preview {
  position: relative;
  height: 400px;
  background: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.admin-preview-svg {
  width: 100%;
  height: 100%;
}

.admin-preview-loading,
.admin-preview-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-size: 14px;
}

.admin-preview-controls {
  display: flex;
  gap: 12px;
  margin-top: 12px;
  align-items: center;
}

.admin-preview-info {
  margin-left: auto;
  font-size: 13px;
  color: #666;
}

/* Import/Export */
.admin-import-export {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.admin-export,
.admin-import {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.admin-export h4,
.admin-import h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
}

/* Empty State */
.admin-empty {
  text-align: center;
  padding: 40px;
  color: #999;
}

/* Responsive */
@media (max-width: 768px) {
  .admin-path-manager {
    padding: 12px;
  }
  
  .admin-path-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .admin-path-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .admin-import-export {
    grid-template-columns: 1fr;
  }
  
  .admin-svg-preview {
    height: 250px;
  }
}

/* Interactive Editor Styles */
.admin-interactive-preview {
  position: relative;
  transition: height 0.3s ease;
  border: 3px solid transparent;
}

.admin-interactive-preview.add-mode-active {
  border-color: #4CAF50;
  box-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
}

.add-mode-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: linear-gradient(135deg, #4CAF50, #45a049);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  font-weight: bold;
  font-size: 14px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.9; transform: scale(1.02); }
}

.admin-editor-modes {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.admin-editor-modes .admin-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.admin-scale-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.admin-scale-controls span {
  font-weight: 500;
  min-width: 80px;
}

.admin-scale-slider {
  flex: 1;
  max-width: 300px;
}

.admin-btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.admin-preview-svg.clickable-mode {
  cursor: crosshair;
}

.admin-preview-svg.delete-mode {
  cursor: not-allowed;
}

.admin-preview-svg .point-marker {
  cursor: pointer;
}

.admin-preview-svg .point-marker:hover .point-circle {
  filter: brightness(1.2);
}

.admin-preview-svg .point-marker.deletable:hover .point-circle {
  fill: #ff6666 !important;
}

.admin-preview-info-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 16px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 6px;
}

.admin-preview-stats {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #555;
}

.stat-item .material-icons {
  font-size: 18px;
  color: #1976d2;
}

.admin-preview-controls {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.admin-preview-controls .admin-btn {
  display: flex;
  align-items: center;
  gap: 4px;
}

.admin-point-list {
  margin-top: 20px;
  padding: 16px;
  background: #f9f9f9;
  border-radius: 6px;
}

.admin-point-list h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #333;
}

.point-list-container {
  max-height: 200px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.point-list-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.point-list-item:hover {
  background: #e3f2fd;
}

.point-list-item.selected {
  background: #bbdefb;
  border: 2px solid #1976d2;
}

.point-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #1976d2;
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: bold;
}

.point-id-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.point-id-input:focus {
  outline: none;
  border-color: #1976d2;
}

.point-coords {
  font-size: 12px;
  color: #666;
  font-family: monospace;
  min-width: 100px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Grid Toggle */
.admin-grid-toggle {
  margin: 10px 0;
}

.admin-checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
}

.admin-checkbox-label input {
  cursor: pointer;
}

/* Grid Overlay */
.grid-overlay {
  pointer-events: none;
}

/* Grid Cell Display */
.grid-cell {
  background: #1976d2;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  margin-left: 4px;
}

/* Panning State */
.admin-interactive-preview.panning {
  cursor: grabbing !important;
}

.admin-interactive-preview:active {
  cursor: grabbing;
}
</style>
