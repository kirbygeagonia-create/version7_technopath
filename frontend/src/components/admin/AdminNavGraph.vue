<template>
  <div class="adminnavgraph-section">
    <div class="section-header">
      <div>
        <h1>Navigation Graph</h1>
        <p class="subtitle">Manage navigation nodes and connections</p>
      </div>
      <div class="header-actions">
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
        <div class="toolbar-info">{{ editorMode === 'select' ? 'Click to select, drag to move' : editorMode === 'add' ? 'Click canvas to add node' : 'Click two nodes to connect' }}</div>
      </div>
      <canvas
        ref="graphCanvas"
        class="graph-canvas"
        @mousedown="onCanvasMouseDown"
        @mousemove="onCanvasMouseMove"
        @mouseup="onCanvasMouseUp"
        @wheel="onCanvasWheel"
      ></canvas>
      <div class="graph-legend">
        <div class="legend-item"><span class="legend-dot entrance"></span>Entrance</div>
        <div class="legend-item"><span class="legend-dot room"></span>Room</div>
        <div class="legend-item"><span class="legend-dot junction"></span>Junction</div>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../../services/api.js'
import { showToast } from '../../services/toast.js'

const nodes = ref([])
const edges = ref([])
const buildings = ref([])
const showAddNodeModal = ref(false)
const showEditNodeModal = ref(false)

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
    const normalizedNode = normalizeCoordinates(nodeForm.value)

    // Explicit payload — only the fields the backend serializer accepts.
    // Spreading the whole nodeForm would include client-only fields and
    // potentially overwrite read-only fields on the backend.
    const payload = {
      name:       normalizedNode.name,
      node_type:  normalizedNode.node_type,
      map_svg_id: normalizedNode.map_svg_id,
      x:          normalizedNode.x,
      y:          normalizedNode.y,
      floor:      normalizedNode.floor,
      facility:   normalizedNode.facility ?? null,
      room:       normalizedNode.room ?? null,
    }

    if (showEditNodeModal.value) {
      await api.put(`/navigation/nodes/${normalizedNode.id}/`, payload)
    } else {
      await api.post('/navigation/nodes/', payload)
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
  try {
    await api.post('/navigation/edges/', {
      from_node: fromNodeId,
      to_node: toNodeId,
      distance: 10,
      is_bidirectional: true
    })
    loadData() // Refresh edges from backend
  } catch (e) {
    console.error('Failed to create edge:', e)
  }
}

// Canvas Node Editor
const graphCanvas = ref(null)
const editorMode = ref('select') // 'select', 'add', 'connect'
const canvasScale = ref(1)
const canvasOffset = ref({ x: 0, y: 0 })
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

function nodeToCanvas(node) {
  const x = (node.x * CANVAS_WIDTH + canvasOffset.value.x) * canvasScale.value
  const y = (node.y * CANVAS_HEIGHT + canvasOffset.value.y) * canvasScale.value
  return { x, y }
}

function canvasToNode(x, y) {
  const nodeX = (x / canvasScale.value - canvasOffset.value.x) / CANVAS_WIDTH
  const nodeY = (y / canvasScale.value - canvasOffset.value.y) / CANVAS_HEIGHT
  return { x: Math.max(0, Math.min(1, nodeX)), y: Math.max(0, Math.min(1, nodeY)) }
}

function getNodeAtPosition(x, y) {
  return nodes.value.find(node => {
    const pos = nodeToCanvas(node)
    const dx = x - pos.x
    const dy = y - pos.y
    return Math.sqrt(dx * dx + dy * dy) <= NODE_RADIUS
  })
}

function onCanvasMouseDown(e) {
  const canvas = graphCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  const clickedNode = getNodeAtPosition(x, y)
  
  if (editorMode.value === 'select') {
    if (clickedNode) {
      isDragging.value = true
      dragNode.value = clickedNode
      selectedNode.value = clickedNode
      dragStart.value = { x, y }
    } else {
      selectedNode.value = null
    }
  } else if (editorMode.value === 'add') {
    if (!clickedNode) {
      const coords = canvasToNode(x, y)
      nodeForm.value.x = coords.x
      nodeForm.value.y = coords.y
      showAddNodeModal.value = true
    }
  } else if (editorMode.value === 'connect') {
    if (clickedNode) {
      if (!connectStartNode.value) {
        connectStartNode.value = clickedNode
        isDragging.value = true
        dragStart.value = { x, y }
      } else if (connectStartNode.value.id !== clickedNode.id) {
        // Create connection and persist to backend
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
  if (!isDragging.value) return
  
  const canvas = graphCanvas.value
  const rect = canvas.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  
  if (editorMode.value === 'select' && dragNode.value) {
    const coords = canvasToNode(x, y)
    dragNode.value.x = coords.x
    dragNode.value.y = coords.y
    drawCanvas()
  } else if (editorMode.value === 'connect') {
    dragStart.value = { x, y }
    drawCanvas()
  }
}

function onCanvasMouseUp() {
  if (editorMode.value === 'select' && dragNode.value) {
    // Save position to backend
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
  const delta = e.deltaY > 0 ? 0.9 : 1.1
  canvasScale.value = Math.max(0.5, Math.min(3, canvasScale.value * delta))
  drawCanvas()
}

function canvasZoomIn() {
  canvasScale.value = Math.min(3, canvasScale.value * 1.2)
  drawCanvas()
}

function canvasZoomOut() {
  canvasScale.value = Math.max(0.5, canvasScale.value / 1.2)
  drawCanvas()
}

function canvasReset() {
  canvasScale.value = 1
  canvasOffset.value = { x: 0, y: 0 }
  drawCanvas()
}

onMounted(() => {
  loadData()
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
</style>
