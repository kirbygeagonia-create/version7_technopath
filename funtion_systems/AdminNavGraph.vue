<template>
  <div class="adminnavgraph-section">
    <div class="section-header">
      <div>
        <h1>Navigation Graph</h1>
        <p class="subtitle">Manage navigation nodes and connections</p>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="showMapGallery = true">
          <span class="material-icons">map</span>
          Map Gallery
        </button>
        <button class="btn-secondary" @click="showImportModal = true">
          <span class="material-icons">upload</span>
          Import Map
        </button>
        <button class="btn-secondary" @click="resetView">
          <span class="material-icons">refresh</span>
          Reset
        </button>
        <button class="btn-primary" @click="showAddNodeModal = true">
          <span class="material-icons">add_location</span>
          Add Node
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-row">
      <div class="stat-box">
        <span class="stat-number">{{ nodes.length }}</span>
        <span class="stat-label">Total Nodes</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ edges.length }}</span>
        <span class="stat-label">Connections</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ nodes.filter(n => n.type === 'room').length }}</span>
        <span class="stat-label">Rooms</span>
      </div>
      <div class="stat-box">
        <span class="stat-number">{{ nodes.filter(n => n.type === 'junction').length }}</span>
        <span class="stat-label">Junctions</span>
      </div>
    </div>

    <!-- How to Create Paths -->
    <div class="help-section">
      <div class="help-title">
        <span class="material-icons">help_outline</span>
        How to Create Navigation Paths
      </div>
      <div class="help-content">
        <ol>
          <li><strong>Add Nodes:</strong> Click "Add Node" button → Enter name (e.g., "gate", "ground_cr") and X,Y coordinates → Save</li>
          <li><strong>Connect Nodes:</strong> Click the "Connect Nodes" (timeline) icon → Click first node → Click second node → Enter distance → Connection created!</li>
          <li><strong>Test:</strong> Go to Navigate page, select start and end points, click "Find Route"</li>
        </ol>
        <p class="help-note"><strong>Note:</strong> SVG ID is optional - only needed if linking to an SVG element. Name is required for route finding.</p>
      </div>
    </div>

    <!-- Visual Node Editor Canvas -->
    <div class="graph-container">
      <div class="graph-toolbar">
        <button class="btn-icon" @click="canvasZoomIn" title="Zoom In">
          <span class="material-icons">zoom_in</span>
        </button>
        <button class="btn-icon" @click="canvasZoomOut" title="Zoom Out">
          <span class="material-icons">zoom_out</span>
        </button>
        <button class="btn-icon" @click="canvasReset" title="Reset View">
          <span class="material-icons">center_focus_strong</span>
        </button>
        <div class="toolbar-divider"></div>
        <button class="btn-icon" :class="{ active: editorMode === 'select' }" @click="editorMode = 'select'" title="Select/Move">
          <span class="material-icons">pan_tool</span>
        </button>
        <button class="btn-icon" :class="{ active: editorMode === 'add' }" @click="editorMode = 'add'" title="Add Node">
          <span class="material-icons">add_location</span>
        </button>
        <button class="btn-icon" :class="{ active: editorMode === 'connect' }" @click="editorMode = 'connect'" title="Connect Nodes">
          <span class="material-icons">timeline</span>
        </button>
        <div class="toolbar-divider"></div>
        <div class="zoom-controls">
          <button class="btn-icon" @click="canvasZoomOut" title="Zoom Out">
            <span class="material-icons">zoom_out</span>
          </button>
          <span class="zoom-level">{{ Math.round(canvasScale * 100) }}%</span>
          <button class="btn-icon" @click="canvasZoomIn" title="Zoom In">
            <span class="material-icons">zoom_in</span>
          </button>
          <button class="btn-icon" @click="canvasReset" title="Reset View">
            <span class="material-icons">center_focus_strong</span>
          </button>
        </div>
        <div class="toolbar-divider"></div>
        <div class="map-selector">
          <span class="material-icons">map</span>
          <select v-model="selectedMap" @change="onMapChange">
            <option value="">No Map</option>
            <option v-for="map in availableMaps" :key="map.filename" :value="map.url">
              {{ map.filename }}
            </option>
          </select>
        </div>
        <div class="toolbar-info">{{ editorMode === 'select' ? 'Click to select, drag to move' : editorMode === 'add' ? 'Click canvas to add node' : 'Click two nodes to connect' }}</div>
      </div>
      <div class="canvas-wrapper" ref="canvasWrapper"
        @mousedown="onCanvasMouseDown"
        @mousemove="onCanvasMouseMove"
        @mouseup="onCanvasMouseUp"
        @wheel="onCanvasWheel"
      >
        <div class="canvas-transform" :style="canvasTransformStyle">
          <img 
            v-if="selectedMap" 
            :src="getFullMapUrl(selectedMap)" 
            class="canvas-background"
            @load="onMapLoaded"
            @error="onMapError"
            draggable="false"
          />
          <canvas
            ref="graphCanvas"
            class="graph-canvas"
            :class="{ 'with-background': selectedMap }"
          ></canvas>
        </div>
        <div class="graph-legend">
          <div class="legend-item"><span class="legend-dot entrance"></span>Entrance</div>
          <div class="legend-item"><span class="legend-dot room"></span>Room</div>
          <div class="legend-item"><span class="legend-dot junction"></span>Junction</div>
        </div>
      </div>
    </div>

    <!-- Nodes Table -->
    <div class="section-title">
      <h2>Navigation Nodes</h2>
    </div>
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Type</th>
            <th>Floor</th>
            <th>Building</th>
            <th>Connections</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="node in nodes" :key="node.id">
            <td><code>{{ node.map_svg_id }}</code></td>
            <td>{{ node.name }}</td>
            <td>
              <span :class="['type-badge', 'type-' + node.node_type]">{{ node.node_type }}</span>
            </td>
            <td>{{ node.floor }}</td>
            <td>{{ node.building }}</td>
            <td>{{ getConnectionCount(node.id) }}</td>
            <td>
              <div class="action-buttons">
                <button class="btn-icon" @click="editNode(node)" title="Edit">
                  <span class="material-icons">edit</span>
                </button>
                <button class="btn-icon" @click="connectNode(node)" title="Connect">
                  <span class="material-icons">timeline</span>
                </button>
                <button class="btn-icon btn-danger" @click="confirmDeleteNode(node)" title="Delete">
                  <span class="material-icons">delete</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Add/Edit Node Modal -->
    <div v-if="showAddNodeModal || showEditNodeModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>{{ showEditNodeModal ? 'Edit Node' : 'Add Navigation Node' }}</h2>
          <button class="btn-close" @click="closeModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <div class="form-group">
              <label>SVG ID</label>
              <input v-model="nodeForm.map_svg_id" type="text" placeholder="e.g., ROOM_101" />
            </div>
            <div class="form-group">
              <label>Type</label>
              <select v-model="nodeForm.node_type">
                <option value="room">Room</option>
                <option value="junction">Junction</option>
                <option value="entrance">Entrance</option>
                <option value="exit">Exit</option>
                <option value="stairs">Stairs</option>
                <option value="elevator">Elevator</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>Name</label>
            <input v-model="nodeForm.name" type="text" placeholder="Display name" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Building</label>
              <select v-model="nodeForm.facility">
                <option v-for="b in buildings" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Floor</label>
              <input v-model="nodeForm.floor" type="number" min="1" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>X Coordinate</label>
              <input v-model="nodeForm.x" type="number" step="0.1" />
            </div>
            <div class="form-group">
              <label>Y Coordinate</label>
              <input v-model="nodeForm.y" type="number" step="0.1" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Cancel</button>
          <button class="btn-primary" @click="saveNode">{{ showEditNodeModal ? 'Save' : 'Add Node' }}</button>
        </div>
      </div>
    </div>

    <!-- Import Map Modal -->
    <div v-if="showImportModal" class="modal-overlay" @click.self="closeImportModal">
      <div class="modal-dialog">
        <div class="modal-header">
          <h2>Import Navigation Map</h2>
          <button class="btn-close" @click="closeImportModal">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <div class="import-tabs">
            <button 
              :class="['tab-btn', { active: importTab === 'json' }]" 
              @click="importTab = 'json'"
            >
              JSON Graph
            </button>
            <button 
              :class="['tab-btn', { active: importTab === 'svg' }]" 
              @click="importTab = 'svg'"
            >
              SVG Map
            </button>
          </div>

          <!-- JSON Import Tab -->
          <div v-if="importTab === 'json'" class="import-section">
            <p class="import-desc">Import navigation nodes and edges from JSON file.</p>
            <div class="file-input-wrapper">
              <input 
                type="file" 
                ref="jsonFileInput"
                accept=".json" 
                @change="handleJsonFileSelect"
                class="file-input"
              />
              <div class="file-drop-zone" @click="$refs.jsonFileInput.click()">
                <span class="material-icons">upload_file</span>
                <p>{{ jsonFile ? jsonFile.name : 'Click to select JSON file' }}</p>
                <small>Supported: nodes/edges JSON format</small>
              </div>
            </div>
            <div v-if="jsonPreview" class="json-preview">
              <h4>Preview:</h4>
              <pre>{{ jsonPreview }}</pre>
            </div>
          </div>

          <!-- SVG Import Tab -->
          <div v-if="importTab === 'svg'" class="import-section">
            <p class="import-desc">Upload a new SVG campus map file.</p>
            <div class="file-input-wrapper">
              <input 
                type="file" 
                ref="svgFileInput"
                accept=".svg" 
                @change="handleSvgFileSelect"
                class="file-input"
              />
              <div class="file-drop-zone" @click="$refs.svgFileInput.click()">
                <span class="material-icons">image</span>
                <p>{{ svgFile ? svgFile.name : 'Click to select SVG file' }}</p>
                <small>Upload new campus map</small>
              </div>
            </div>
            <div v-if="svgPreview" class="svg-preview">
              <img :src="svgPreview" alt="SVG Preview" />
            </div>
          </div>

          <div v-if="importError" class="import-error">
            <span class="material-icons">error</span>
            {{ importError }}
          </div>
          <div v-if="importSuccess" class="import-success">
            <span class="material-icons">check_circle</span>
            {{ importSuccess }}
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeImportModal">Cancel</button>
          <button 
            class="btn-primary" 
            @click="submitImport"
            :disabled="!canImport || isImporting"
          >
            <span v-if="isImporting" class="material-icons spinning">sync</span>
            <span v-else class="material-icons">upload</span>
            {{ isImporting ? 'Importing...' : 'Import' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Map Gallery Modal -->
    <div v-if="showMapGallery" class="modal-overlay" @click.self="closeMapGallery">
      <div class="modal-dialog map-gallery-dialog">
        <div class="modal-header">
          <h2>Map Gallery</h2>
          <button class="btn-close" @click="closeMapGallery">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="modal-body">
          <p class="gallery-desc">
            View and manage uploaded SVG campus maps. 
            <strong>{{ maps.length }}</strong> map(s) available.
          </p>
          
          <div v-if="loadingMaps" class="loading-maps">
            <span class="material-icons spinning">sync</span>
            Loading maps...
          </div>
          
          <div v-else-if="maps.length === 0" class="no-maps">
            <span class="material-icons">map</span>
            <p>No maps uploaded yet.</p>
            <button class="btn-secondary" @click="switchToImport">
              <span class="material-icons">upload</span>
              Import Your First Map
            </button>
          </div>
          
          <div v-else class="maps-grid">
            <div 
              v-for="map in maps" 
              :key="map.filename"
              class="map-card"
              :class="{ active: map.is_active }"
            >
              <div class="map-preview">
                <img 
                  :src="getFullMapUrl(map.url)" 
                  :alt="map.filename"
                  @error="$event.target.src = '/assets/SEAIT_Map0.1.svg'"
                />
                <div v-if="map.is_active" class="active-badge">
                  <span class="material-icons">check_circle</span>
                  Active
                </div>
              </div>
              <div class="map-info">
                <h4>{{ map.filename }}</h4>
                <p class="map-meta">
                  {{ formatFileSize(map.size) }} • {{ formatDate(map.uploaded_at) }}
                </p>
                <div class="map-actions">
                  <button 
                    class="btn-icon" 
                    @click="viewMap(map)"
                    title="View Full Size"
                  >
                    <span class="material-icons">open_in_new</span>
                  </button>
                  <button 
                    class="btn-icon btn-danger" 
                    @click="deleteMap(map)"
                    title="Delete Map"
                  >
                    <span class="material-icons">delete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeMapGallery">Close</button>
          <button class="btn-primary" @click="switchToImport">
            <span class="material-icons">upload</span>
            Import New Map
          </button>
        </div>
      </div>
    </div>

    <!-- Full Size Map Viewer -->
    <div v-if="viewingMap" class="modal-overlay map-viewer-overlay" @click.self="closeMapViewer">
      <div class="map-viewer">
        <div class="map-viewer-header">
          <h3>{{ viewingMap.filename }}</h3>
          <button class="btn-close" @click="closeMapViewer">
            <span class="material-icons">close</span>
          </button>
        </div>
        <div class="map-viewer-content">
          <img :src="getFullMapUrl(viewingMap.url)" :alt="viewingMap.filename" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'

const nodes = ref([])
const edges = ref([])
const buildings = ref([])
const showAddNodeModal = ref(false)
const showEditNodeModal = ref(false)
const showImportModal = ref(false)

// Import state
const importTab = ref('json')
const jsonFile = ref(null)
const jsonPreview = ref('')
const svgFile = ref(null)
const svgPreview = ref('')
const importError = ref('')
const importSuccess = ref('')
const isImporting = ref(false)
const jsonFileInput = ref(null)
const svgFileInput = ref(null)

const canImport = computed(() => {
  return importTab.value === 'json' ? jsonFile.value !== null : svgFile.value !== null
})

// Map Gallery state
const showMapGallery = ref(false)
const maps = ref([])
const loadingMaps = ref(false)
const viewingMap = ref(null)

// Map selector for canvas background
const selectedMap = ref('')
const availableMaps = ref([])
const canvasWrapper = ref(null)

// Canvas zoom/pan state
const canvasScale = ref(1)
const canvasOffset = ref({ x: 0, y: 0 })
const isPanning = ref(false)
const panStart = ref({ x: 0, y: 0 })

const canvasTransformStyle = computed(() => ({
  transform: `translate(${canvasOffset.value.x}px, ${canvasOffset.value.y}px) scale(${canvasScale.value})`,
  transformOrigin: '0 0'
}))

// Watch for gallery opening to load maps
watch(showMapGallery, (isOpen) => {
  if (isOpen) {
    loadMaps()
  }
})

// Load available maps for selector
async function loadAvailableMaps() {
  try {
    const response = await api.get('/navigation/maps/')
    availableMaps.value = response.data.maps || []
    // Auto-select first map if none selected and maps available
    if (!selectedMap.value && availableMaps.value.length > 0) {
      selectedMap.value = availableMaps.value[0].url
    }
  } catch (error) {
    console.error('Failed to load maps for selector:', error)
    availableMaps.value = []
  }
}

function onMapChange() {
  // Redraw canvas when map changes
  drawCanvas()
  showToast(selectedMap.value ? 'Map loaded on canvas' : 'Map background removed', 'info')
}

function onMapLoaded() {
  console.log('Map loaded successfully')
  drawCanvas()
}

function onMapError() {
  showToast('Failed to load map image', 'error')
  selectedMap.value = ''
}

const nodeForm = ref({
  id: null,
  map_svg_id: '',
  name: '',
  node_type: 'room',
  facility: null,
  floor: 1,
  x: 0.5,
  y: 0.5
})

function getConnectionCount(nodeId) {
  return edges.value.filter(e => e.from_node === nodeId || e.to_node === nodeId).length
}

function editNode(node) {
  nodeForm.value = { ...node }
  showEditNodeModal.value = true
}

function connectNode(node) {
  showToast(`Connect node ${node.name} - Feature would open connection editor`, 'info')
}

function confirmDeleteNode(node) {
  if (confirm(`Delete node ${node.name}?`)) {
    deleteNode(node)
  }
}

function closeModal() {
  showAddNodeModal.value = false
  showEditNodeModal.value = false
  nodeForm.value = { id: null, map_svg_id: '', name: '', node_type: 'room', facility: null, floor: 1, x: 0.5, y: 0.5 }
}

// Import Map Functions
function closeImportModal() {
  showImportModal.value = false
  resetImportState()
}

function resetImportState() {
  importTab.value = 'json'
  jsonFile.value = null
  jsonPreview.value = ''
  svgFile.value = null
  svgPreview.value = ''
  importError.value = ''
  importSuccess.value = ''
  isImporting.value = false
  if (jsonFileInput.value) jsonFileInput.value.value = ''
  if (svgFileInput.value) svgFileInput.value.value = ''
}

function handleJsonFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return
  
  jsonFile.value = file
  importError.value = ''
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = JSON.parse(e.target.result)
      jsonPreview.value = JSON.stringify(content, null, 2).substring(0, 500) + '...'
    } catch (err) {
      importError.value = 'Invalid JSON file: ' + err.message
      jsonPreview.value = ''
    }
  }
  reader.readAsText(file)
}

function handleSvgFileSelect(event) {
  const file = event.target.files[0]
  if (!file) return
  
  svgFile.value = file
  importError.value = ''
  
  // Create preview URL
  svgPreview.value = URL.createObjectURL(file)
}

async function submitImport() {
  if (importTab.value === 'json' && !jsonFile.value) {
    importError.value = 'Please select a JSON file'
    return
  }
  if (importTab.value === 'svg' && !svgFile.value) {
    importError.value = 'Please select an SVG file'
    return
  }
  
  isImporting.value = true
  importError.value = ''
  importSuccess.value = ''
  
  try {
    const formData = new FormData()
    const file = importTab.value === 'json' ? jsonFile.value : svgFile.value
    formData.append('file', file)
    
    const response = await api.post('/navigation/import/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    importSuccess.value = response.data.message || 'Import successful!'
    showToast(importSuccess.value, 'success')
    
    // Refresh data after successful import
    await loadData()
    
    // Close modal after a short delay
    setTimeout(() => {
      closeImportModal()
    }, 1500)
  } catch (error) {
    importError.value = error.response?.data?.error || 'Import failed. Please try again.'
    showToast(importError.value, 'error')
  } finally {
    isImporting.value = false
  }
}

// Map Gallery Functions
function closeMapGallery() {
  showMapGallery.value = false
  viewingMap.value = null
}

function switchToImport() {
  closeMapGallery()
  showImportModal.value = true
}

async function loadMaps() {
  loadingMaps.value = true
  try {
    const response = await api.get('/navigation/maps/')
    maps.value = response.data.maps || []
  } catch (error) {
    console.error('Failed to load maps:', error)
    showToast('Failed to load maps', 'error')
    maps.value = []
  } finally {
    loadingMaps.value = false
  }
}

function getFullMapUrl(url) {
  // Prepend API base URL if relative
  if (url.startsWith('/')) {
    return `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}${url}`
  }
  return url
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function formatDate(timestamp) {
  return new Date(timestamp * 1000).toLocaleDateString()
}

function viewMap(map) {
  viewingMap.value = map
}

function closeMapViewer() {
  viewingMap.value = null
}

async function deleteMap(map) {
  if (!confirm(`Delete map "${map.filename}"? This cannot be undone.`)) {
    return
  }
  
  try {
    await api.delete(`/navigation/maps/${encodeURIComponent(map.filename)}/`)
    showToast(`Map ${map.filename} deleted`, 'success')
    await loadMaps() // Refresh the list
  } catch (error) {
    showToast('Failed to delete map', 'error')
  }
}

function resetView() {
  loadData()
}

async function loadData() {
  try {
    const [nodesRes, edgesRes, buildingsRes] = await Promise.all([
      api.get('/navigation/nodes/'),
      api.get('/navigation/edges/'),
      api.get('/facilities/')
    ])
    nodes.value = nodesRes.data
    edges.value = edgesRes.data
    buildings.value = buildingsRes.data
  } catch (e) {
    // Show empty state — no fake mock data that misleads admins
    console.warn('[AdminNavGraph] Could not load navigation data:', e.message)
    nodes.value     = []
    edges.value     = []
    buildings.value = []
  }
}

/**
 * Normalize coordinates to 0.0-1.0 range
 * If values are > 1, assumes they're on a 0-20 scale and normalizes
 */
function normalizeCoordinates(node) {
  const x = parseFloat(node.x)
  const y = parseFloat(node.y)
  
  return {
    ...node,
    x: x > 1 ? x / 20 : x,
    y: y > 1 ? y / 20 : y
  }
}

async function saveNode() {
  try {
    // Normalize coordinates before saving
    const normalizedNode = normalizeCoordinates(nodeForm.value)
    
    if (showEditNodeModal.value) {
      await api.put(`/navigation/nodes/${normalizedNode.id}/`, normalizedNode)
    } else {
      await api.post('/navigation/nodes/', normalizedNode)
    }
    closeModal()
    loadData()
  } catch (e) {
    console.error('Failed to save node:', e)
  }
}

async function deleteNode(node) {
  try {
    await api.delete(`/navigation/nodes/${node.id}/`)
    loadData()
  } catch (e) {
    console.error('Failed to delete node:', e)
  }
}

async function createEdge(fromNodeId, toNodeId) {
  // Ask for distance between nodes
  const distanceInput = prompt('Enter distance between these points (in meters):', '10')
  if (!distanceInput) return // User cancelled

  const distance = parseInt(distanceInput, 10)
  if (isNaN(distance) || distance <= 0) {
    showToast('Please enter a valid distance', 'error')
    return
  }

  try {
    await api.post('/navigation/edges/', {
      from_node: fromNodeId,
      to_node: toNodeId,
      distance: distance,
      is_bidirectional: true
    })
    showToast('Connection created successfully', 'success')
    loadData() // Refresh edges from backend
  } catch (e) {
    console.error('Failed to create edge:', e)
    showToast('Failed to create connection', 'error')
  }
}

// Canvas Node Editor
const graphCanvas = ref(null)
const editorMode = ref('select') // 'select', 'add', 'connect'
const isDragging = ref(false)
const dragNode = ref(null)
const dragStart = ref({ x: 0, y: 0 })
const selectedNode = ref(null)
const connectStartNode = ref(null)

const NODE_RADIUS = 20
const CANVAS_WIDTH = 800
const CANVAS_HEIGHT = 500

// Node type colors
const typeColors = {
  entrance: '#4CAF50',
  room: '#FF9800',
  junction: '#2196F3',
  stairs: '#9C27B0',
  elevator: '#E91E63'
}

function initCanvas() {
  const canvas = graphCanvas.value
  if (!canvas) return
  
  canvas.width = canvas.offsetWidth
  canvas.height = canvas.offsetHeight
  
  drawCanvas()
}

function drawCanvas() {
  const canvas = graphCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  // Draw grid
  drawGrid(ctx, canvas.width, canvas.height)
  
  // Draw edges
  ctx.strokeStyle = '#666'
  ctx.lineWidth = 2
  edges.value.forEach(edge => {
    const fromNode = nodes.value.find(n => n.id === edge.from_node)
    const toNode = nodes.value.find(n => n.id === edge.to_node)
    if (fromNode && toNode) {
      const fromPos = nodeToCanvas(fromNode)
      const toPos = nodeToCanvas(toNode)
      
      ctx.beginPath()
      ctx.moveTo(fromPos.x, fromPos.y)
      ctx.lineTo(toPos.x, toPos.y)
      ctx.stroke()
      
      // Draw arrow
      drawArrow(ctx, fromPos.x, fromPos.y, toPos.x, toPos.y)
    }
  })
  
  // Draw nodes
  nodes.value.forEach(node => {
    const pos = nodeToCanvas(node)
    const isSelected = selectedNode.value?.id === node.id
    const color = typeColors[node.node_type] || '#999'
    
    // Node circle
    ctx.beginPath()
    ctx.arc(pos.x, pos.y, NODE_RADIUS, 0, Math.PI * 2)
    ctx.fillStyle = color
    ctx.fill()
    
    // Selection ring
    if (isSelected) {
      ctx.strokeStyle = '#FF5722'
      ctx.lineWidth = 3
      ctx.stroke()
      
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, NODE_RADIUS + 5, 0, Math.PI * 2)
      ctx.strokeStyle = '#FF5722'
      ctx.lineWidth = 2
      ctx.stroke()
    } else {
      ctx.strokeStyle = 'white'
      ctx.lineWidth = 2
      ctx.stroke()
    }
    
    // Node label
    ctx.fillStyle = 'white'
    ctx.font = 'bold 11px Inter, sans-serif'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(node.name.substring(0, 8), pos.x, pos.y)
    
    // Node ID below
    ctx.fillStyle = '#333'
    ctx.font = '9px Inter, sans-serif'
    ctx.fillText(node.map_svg_id || node.name, pos.x, pos.y + NODE_RADIUS + 12)
  })
  
  // Draw connection line in progress
  if (connectStartNode.value && isDragging.value) {
    const startPos = nodeToCanvas(connectStartNode.value)
    ctx.beginPath()
    ctx.moveTo(startPos.x, startPos.y)
    ctx.lineTo(dragStart.value.x, dragStart.value.y)
    ctx.strokeStyle = '#4CAF50'
    ctx.setLineDash([5, 5])
    ctx.stroke()
    ctx.setLineDash([])
  }
}

function drawGrid(ctx, width, height) {
  ctx.strokeStyle = '#E0E0E0'
  ctx.lineWidth = 1
  const gridSize = 50 * canvasScale.value
  
  for (let x = 0; x < width; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, height)
    ctx.stroke()
  }
  
  for (let y = 0; y < height; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(width, y)
    ctx.stroke()
  }
}

function drawArrow(ctx, fromX, fromY, toX, toY) {
  const angle = Math.atan2(toY - fromY, toX - fromX)
  const arrowLength = 10
  const arrowAngle = Math.PI / 6
  
  const endX = toX - NODE_RADIUS * Math.cos(angle)
  const endY = toY - NODE_RADIUS * Math.sin(angle)
  
  ctx.beginPath()
  ctx.moveTo(endX, endY)
  ctx.lineTo(
    endX - arrowLength * Math.cos(angle - arrowAngle),
    endY - arrowLength * Math.sin(angle - arrowAngle)
  )
  ctx.stroke()
  
  ctx.beginPath()
  ctx.moveTo(endX, endY)
  ctx.lineTo(
    endX - arrowLength * Math.cos(angle + arrowAngle),
    endY - arrowLength * Math.sin(angle + arrowAngle)
  )
  ctx.stroke()
}

// Convert screen coordinates to canvas coordinates (accounting for zoom/pan)
function screenToCanvas(screenX, screenY) {
  const wrapper = canvasWrapper.value
  if (!wrapper) return { x: screenX, y: screenY }
  const rect = wrapper.getBoundingClientRect()
  // Adjust for offset and scale
  const x = (screenX - rect.left - canvasOffset.value.x) / canvasScale.value
  const y = (screenY - rect.top - canvasOffset.value.y) / canvasScale.value
  return { x, y }
}

function nodeToCanvas(node) {
  // Node coordinates (0-1) to canvas coordinates
  const x = node.x * CANVAS_WIDTH * canvasScale.value + canvasOffset.value.x
  const y = node.y * CANVAS_HEIGHT * canvasScale.value + canvasOffset.value.y
  return { x, y }
}

function canvasToNode(canvasX, canvasY) {
  // Canvas coordinates to node coordinates (0-1)
  const nodeX = (canvasX - canvasOffset.value.x) / canvasScale.value / CANVAS_WIDTH
  const nodeY = (canvasY - canvasOffset.value.y) / canvasScale.value / CANVAS_HEIGHT
  return { x: Math.max(0, Math.min(1, nodeX)), y: Math.max(0, Math.min(1, nodeY)) }
}

function getNodeAtPosition(screenX, screenY) {
  const canvasPos = screenToCanvas(screenX, screenY)
  return nodes.value.find(node => {
    const nodeCanvasPos = nodeToCanvas(node)
    // Adjust for scale when checking distance
    const radius = NODE_RADIUS / canvasScale.value
    const dx = canvasPos.x - nodeCanvasPos.x / canvasScale.value
    const dy = canvasPos.y - nodeCanvasPos.y / canvasScale.value
    return Math.sqrt(dx * dx + dy * dy) <= radius
  })
}

function onCanvasMouseDown(e) {
  // Middle mouse button or space+drag for panning
  if (e.button === 1 || (e.button === 0 && e.shiftKey)) {
    isPanning.value = true
    panStart.value = { x: e.clientX - canvasOffset.value.x, y: e.clientY - canvasOffset.value.y }
    e.preventDefault()
    return
  }
  
  const clickedNode = getNodeAtPosition(e.clientX, e.clientY)
  
  if (editorMode.value === 'select') {
    if (clickedNode) {
      isDragging.value = true
      dragNode.value = clickedNode
      selectedNode.value = clickedNode
    } else {
      selectedNode.value = null
      // Start panning if clicking empty space with left button
      if (e.button === 0) {
        isPanning.value = true
        panStart.value = { x: e.clientX - canvasOffset.value.x, y: e.clientY - canvasOffset.value.y }
      }
    }
  } else if (editorMode.value === 'add') {
    if (!clickedNode && !isPanning.value) {
      const pos = screenToCanvas(e.clientX, e.clientY)
      const coords = canvasToNode(pos.x, pos.y)
      nodeForm.value.x = coords.x
      nodeForm.value.y = coords.y
      showAddNodeModal.value = true
    }
  } else if (editorMode.value === 'connect') {
    if (clickedNode) {
      if (!connectStartNode.value) {
        connectStartNode.value = clickedNode
        isDragging.value = true
      } else if (connectStartNode.value.id !== clickedNode.id) {
        createEdge(connectStartNode.value.id, clickedNode.id)
        connectStartNode.value = null
        isDragging.value = false
        drawCanvas()
      }
    } else {
      connectStartNode.value = null
      isDragging.value = false
    }
  }
  
  drawCanvas()
}

function onCanvasMouseMove(e) {
  if (isPanning.value) {
    canvasOffset.value = {
      x: e.clientX - panStart.value.x,
      y: e.clientY - panStart.value.y
    }
    drawCanvas()
    return
  }
  
  if (!isDragging.value) return
  
  if (editorMode.value === 'select' && dragNode.value) {
    const pos = screenToCanvas(e.clientX, e.clientY)
    const coords = canvasToNode(pos.x, pos.y)
    dragNode.value.x = coords.x
    dragNode.value.y = coords.y
    drawCanvas()
  } else if (editorMode.value === 'connect') {
    const pos = screenToCanvas(e.clientX, e.clientY)
    dragStart.value = { x: pos.x, y: pos.y }
    drawCanvas()
  }
}

function onCanvasMouseUp(e) {
  if (isPanning.value) {
    isPanning.value = false
    return
  }
  
  if (editorMode.value === 'select' && dragNode.value) {
    saveNodePosition(dragNode.value)
  }
  
  isDragging.value = false
  dragNode.value = null
}

async function saveNodePosition(node) {
  try {
    await api.patch(`/navigation/nodes/${node.id}/`, {
      x: node.x,
      y: node.y
    })
  } catch (e) {
    console.error('Failed to save node position:', e)
  }
}

function onCanvasWheel(e) {
  e.preventDefault()
  const wrapper = canvasWrapper.value
  if (!wrapper) return
  
  const rect = wrapper.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top
  
  // Zoom towards mouse pointer
  const oldScale = canvasScale.value
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newScale = Math.max(0.3, Math.min(5, oldScale * delta))
  
  // Adjust offset to zoom towards mouse
  const scaleRatio = newScale / oldScale
  canvasOffset.value = {
    x: mouseX - (mouseX - canvasOffset.value.x) * scaleRatio,
    y: mouseY - (mouseY - canvasOffset.value.y) * scaleRatio
  }
  canvasScale.value = newScale
  
  drawCanvas()
}

function canvasZoomIn() {
  const newScale = Math.min(5, canvasScale.value * 1.2)
  const wrapper = canvasWrapper.value
  if (wrapper) {
    const rect = wrapper.getBoundingClientRect()
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    const scaleRatio = newScale / canvasScale.value
    canvasOffset.value = {
      x: centerX - (centerX - canvasOffset.value.x) * scaleRatio,
      y: centerY - (centerY - canvasOffset.value.y) * scaleRatio
    }
  }
  canvasScale.value = newScale
  drawCanvas()
}

function canvasZoomOut() {
  const newScale = Math.max(0.3, canvasScale.value / 1.2)
  const wrapper = canvasWrapper.value
  if (wrapper) {
    const rect = wrapper.getBoundingClientRect()
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    const scaleRatio = newScale / canvasScale.value
    canvasOffset.value = {
      x: centerX - (centerX - canvasOffset.value.x) * scaleRatio,
      y: centerY - (centerY - canvasOffset.value.y) * scaleRatio
    }
  }
  canvasScale.value = newScale
  drawCanvas()
}

function canvasReset() {
  canvasScale.value = 1
  canvasOffset.value = { x: 0, y: 0 }
  drawCanvas()
}

onMounted(() => {
  loadData()
  loadAvailableMaps()
  initCanvas()
  window.addEventListener('resize', initCanvas)
})
</script>

<style scoped>
.adminnavgraph-section { padding: 0; font-family: var(--font-primary); max-width: 1400px; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-secondary {
  background: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-surface-2);
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-box {
  display: flex;
  flex-direction: column;
  padding: 14px 20px;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  min-width: 100px;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

/* Help Section */
.help-section {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border-radius: var(--radius-lg);
  border: 1px solid #bbdefb;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.help-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: var(--text-sm);
  color: var(--color-primary);
  margin-bottom: 12px;
}

.help-content ol {
  margin: 0;
  padding-left: 20px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.help-content li {
  margin-bottom: 8px;
}

.help-note {
  margin-top: 12px;
  padding: 8px 12px;
  background: rgba(255, 152, 0, 0.1);
  border-left: 3px solid var(--color-primary);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.graph-container {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  height: 500px;
  position: relative;
  overflow: hidden;
}

.graph-toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.graph-toolbar .btn-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.graph-toolbar .btn-icon:hover {
  background: var(--color-surface-2);
}

.graph-toolbar .btn-icon.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.graph-toolbar .toolbar-divider {
  width: 1px;
  height: 24px;
  background: var(--color-border);
  margin: 0 8px;
}

.graph-toolbar .toolbar-info {
  margin-left: auto;
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.graph-canvas {
  flex: 1;
  width: 100%;
  cursor: crosshair;
}

.graph-canvas:active {
  cursor: grabbing;
}

.graph-legend {
  position: absolute;
  bottom: 12px;
  right: 12px;
  display: flex;
  gap: 12px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.entrance { background: #4CAF50; }
.legend-dot.room { background: #FF9800; }
.legend-dot.junction { background: #2196F3; }

.section-title {
  margin-bottom: 16px;
}

.section-title h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.table-container {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 14px 16px;
  text-align: left;
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  font-size: var(--text-sm);
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table tr:hover {
  background: var(--color-surface);
}

.data-table code {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: var(--color-surface);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
}

.type-badge {
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: capitalize;
}

.type-room { background: var(--color-primary-light); color: var(--color-primary); }
.type-junction { background: var(--color-info-bg); color: var(--color-info); }
.type-entrance { background: var(--color-success-bg); color: var(--color-success); }
.type-exit { background: var(--color-danger-bg); color: var(--color-danger); }
.type-stairs { background: #FFF3E0; color: #E65100; }
.type-elevator { background: #E8EAF6; color: #3F51B5; }

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-icon.btn-danger:hover {
  background: var(--color-danger-bg);
  color: var(--color-danger);
  border-color: var(--color-danger);
}

.btn-icon .material-icons {
  font-size: 16px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-dialog {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.btn-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-hint);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 6px;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px 12px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-family: var(--font-primary);
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  outline: none;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

/* Import Modal Styles */
.import-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 12px;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  background: var(--color-surface);
}

.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.import-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}

.file-input-wrapper {
  position: relative;
}

.file-input {
  display: none;
}

.file-drop-zone {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--color-bg);
}

.file-drop-zone:hover {
  border-color: var(--color-primary);
  background: var(--color-surface);
}

.file-drop-zone .material-icons {
  font-size: 48px;
  color: var(--color-text-hint);
  margin-bottom: 12px;
}

.file-drop-zone p {
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  margin: 0 0 4px 0;
}

.file-drop-zone small {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}

.json-preview, .svg-preview {
  margin-top: 16px;
  padding: 12px;
  background: var(--color-surface);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.json-preview h4, .svg-preview h4 {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin: 0 0 8px 0;
}

.json-preview pre {
  font-family: var(--font-mono);
  font-size: 11px;
  background: var(--color-bg);
  padding: 12px;
  border-radius: var(--radius-sm);
  max-height: 200px;
  overflow: auto;
  margin: 0;
}

.svg-preview img {
  max-width: 100%;
  max-height: 200px;
  border-radius: var(--radius-sm);
}

.import-error, .import-success {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  margin-top: 16px;
  font-size: var(--text-sm);
}

.import-error {
  background: var(--color-danger-bg);
  color: var(--color-danger);
}

.import-success {
  background: var(--color-success-bg);
  color: var(--color-success);
}

.import-error .material-icons,
.import-success .material-icons {
  font-size: 20px;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Map Gallery Styles */
.map-gallery-dialog {
  max-width: 900px;
  width: 90vw;
}

.gallery-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: 20px;
}

.loading-maps, .no-maps {
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}

.loading-maps .material-icons,
.no-maps .material-icons {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.no-maps p {
  margin-bottom: 20px;
}

.maps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 8px;
}

.map-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-bg);
  transition: all 0.2s ease;
}

.map-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.map-card.active {
  border-color: var(--color-success);
  box-shadow: 0 0 0 2px var(--color-success-bg);
}

.map-preview {
  position: relative;
  height: 150px;
  background: var(--color-surface);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.map-preview img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.active-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--color-success);
  color: white;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  display: flex;
  align-items: center;
  gap: 4px;
}

.active-badge .material-icons {
  font-size: 14px;
}

.map-info {
  padding: 12px;
}

.map-info h4 {
  font-size: var(--text-sm);
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.map-meta {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  margin: 0 0 12px 0;
}

.map-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* Map Viewer Overlay */
.map-viewer-overlay {
  z-index: 1100;
}

.map-viewer {
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  width: 95vw;
  height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.map-viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
}

.map-viewer-header h3 {
  margin: 0;
  font-size: var(--text-lg);
}

.map-viewer-content {
  flex: 1;
  overflow: auto;
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
}

.map-viewer-content img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* Map Selector in Toolbar */
.map-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
}

.map-selector .material-icons {
  font-size: 18px;
  color: var(--color-text-secondary);
}

.map-selector select {
  border: none;
  background: transparent;
  font-size: var(--text-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  outline: none;
  min-width: 150px;
  max-width: 200px;
}

/* Zoom Controls */
.zoom-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.zoom-level {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  min-width: 40px;
  text-align: center;
}

/* Canvas with Background and Transform */
.canvas-wrapper {
  position: relative;
  flex: 1;
  overflow: hidden;
  background: var(--color-bg);
  cursor: grab;
}

.canvas-wrapper:active {
  cursor: grabbing;
}

.canvas-transform {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  will-change: transform;
}

.canvas-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
  z-index: 1;
}

.graph-canvas {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 2;
  width: 100%;
  height: 100%;
}

.graph-canvas.with-background {
  background: transparent;
}

.graph-legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  padding: 8px 12px;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
</style>
