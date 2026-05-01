import { reactive, ref } from 'vue'

/**
 * Navigation Graph Service
 * 
 * Manages nodes (locations) and edges (connections) for pathfinding.
 * Uses Dijkstra's algorithm for finding shortest paths.
 */

// Reactive state
const nodes = ref([])
const edges = ref([])

// Initialize with mock data if empty
function initMockData() {
  if (nodes.value.length === 0) {
    nodes.value = [
      { id: 'college', name: 'College Building', type: 'building', x: 800, y: 1000 },
      { id: 'tailoring', name: 'Tailoring Workshop', type: 'building', x: 1200, y: 1500 },
      { id: 'library', name: 'Library', type: 'building', x: 600, y: 800 },
      { id: 'cafeteria', name: 'Cafeteria', type: 'building', x: 1000, y: 1200 },
      { id: 'gate', name: 'Main Gate', type: 'entrance', x: 500, y: 2000 },
      { id: 'junction1', name: 'Junction 1', type: 'junction', x: 800, y: 1200 },
      { id: 'junction2', name: 'Junction 2', type: 'junction', x: 1000, y: 1000 },
    ]
    
    edges.value = [
      { id: 'e1', from: 'college', to: 'junction1', distance: 200 },
      { id: 'e2', from: 'junction1', to: 'tailoring', distance: 350 },
      { id: 'e3', from: 'junction1', to: 'cafeteria', distance: 200 },
      { id: 'e4', from: 'college', to: 'junction2', distance: 200 },
      { id: 'e5', from: 'junction2', to: 'library', distance: 250 },
      { id: 'e6', from: 'junction2', to: 'cafeteria', distance: 200 },
      { id: 'e7', from: 'gate', to: 'library', distance: 400 },
      { id: 'e8', from: 'gate', to: 'cafeteria', distance: 500 },
    ]
  }
}

// Node CRUD
function addNode(node) {
  const newNode = {
    id: node.id || `node_${Date.now()}`,
    name: node.name || 'Unnamed Node',
    type: node.type || 'junction',
    x: node.x || 0,
    y: node.y || 0,
    ...node
  }
  nodes.value.push(newNode)
  return newNode
}

function updateNode(id, updates) {
  const index = nodes.value.findIndex(n => n.id === id)
  if (index >= 0) {
    nodes.value[index] = { ...nodes.value[index], ...updates }
    return nodes.value[index]
  }
  return null
}

function deleteNode(id) {
  // Remove edges connected to this node
  edges.value = edges.value.filter(e => e.from !== id && e.to !== id)
  // Remove node
  const index = nodes.value.findIndex(n => n.id === id)
  if (index >= 0) {
    nodes.value.splice(index, 1)
    return true
  }
  return false
}

function getNode(id) {
  return nodes.value.find(n => n.id === id)
}

// Edge CRUD
function addEdge(edge) {
  const newEdge = {
    id: edge.id || `edge_${Date.now()}`,
    from: edge.from,
    to: edge.to,
    distance: edge.distance || 0,
    ...edge
  }
  edges.value.push(newEdge)
  return newEdge
}

function deleteEdge(id) {
  const index = edges.value.findIndex(e => e.id === id)
  if (index >= 0) {
    edges.value.splice(index, 1)
    return true
  }
  return false
}

function getEdgesForNode(nodeId) {
  return edges.value.filter(e => e.from === nodeId || e.to === nodeId)
}

// Dijkstra's Algorithm for shortest path
function findShortestPath(fromId, toId) {
  if (!fromId || !toId || fromId === toId) return null
  
  const startNode = getNode(fromId)
  const endNode = getNode(toId)
  if (!startNode || !endNode) return null
  
  // Initialize distances
  const distances = {}
  const previous = {}
  const unvisited = new Set()
  
  nodes.value.forEach(node => {
    distances[node.id] = node.id === fromId ? 0 : Infinity
    previous[node.id] = null
    unvisited.add(node.id)
  })
  
  while (unvisited.size > 0) {
    // Find node with minimum distance
    let currentId = null
    let minDistance = Infinity
    unvisited.forEach(id => {
      if (distances[id] < minDistance) {
        minDistance = distances[id]
        currentId = id
      }
    })
    
    if (!currentId || distances[currentId] === Infinity) break
    if (currentId === toId) break // Found target
    
    unvisited.delete(currentId)
    
    // Check neighbors
    const neighborEdges = edges.value.filter(e => e.from === currentId || e.to === currentId)
    neighborEdges.forEach(edge => {
      const neighborId = edge.from === currentId ? edge.to : edge.from
      if (!unvisited.has(neighborId)) return
      
      const altDistance = distances[currentId] + edge.distance
      if (altDistance < distances[neighborId]) {
        distances[neighborId] = altDistance
        previous[neighborId] = currentId
      }
    })
  }
  
  // Reconstruct path
  if (!previous[toId] && fromId !== toId) return null // No path found
  
  const path = []
  let current = toId
  while (current) {
    const node = getNode(current)
    if (node) {
      path.unshift({
        id: node.id,
        name: node.name,
        x: node.x,
        y: node.y,
        type: node.type
      })
    }
    current = previous[current]
  }
  
  return {
    nodes: path,
    distance: distances[toId],
    edges: [] // Could add edge details here
  }
}

// Get all path options for UI
function getAllLocations() {
  return nodes.value.map(n => ({
    id: n.id,
    name: n.name,
    type: n.type,
    x: n.x,
    y: n.y
  }))
}

// Export/Import for persistence
function exportData() {
  return {
    nodes: nodes.value,
    edges: edges.value,
    exportedAt: new Date().toISOString()
  }
}

function importData(data) {
  if (data.nodes) nodes.value = data.nodes
  if (data.edges) edges.value = data.edges
}

// Initialize
initMockData()

export default {
  nodes,
  edges,
  addNode,
  updateNode,
  deleteNode,
  getNode,
  addEdge,
  deleteEdge,
  getEdgesForNode,
  findShortestPath,
  getAllLocations,
  exportData,
  importData
}
