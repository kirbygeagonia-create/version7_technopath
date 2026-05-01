// Dijkstra's algorithm for navigation pathfinding
// Uses backend API for navigation data
// Optimized with binary heap priority queue: O(n log n) instead of O(n²)

import api from './api.js'

/**
 * Binary Heap Priority Queue for O(log n) operations
 * Used to optimize Dijkstra's algorithm
 */
class PriorityQueue {
  constructor() {
    this.heap = []
  }

  push(item) {
    this.heap.push(item)
    this._bubbleUp(this.heap.length - 1)
  }

  pop() {
    if (this.heap.length === 0) return null
    if (this.heap.length === 1) return this.heap.pop()
    
    const min = this.heap[0]
    this.heap[0] = this.heap.pop()
    this._bubbleDown(0)
    return min
  }

  isEmpty() {
    return this.heap.length === 0
  }

  _bubbleUp(index) {
    while (index > 0) {
      const parentIndex = Math.floor((index - 1) / 2)
      if (this.heap[parentIndex].dist <= this.heap[index].dist) break
      [this.heap[parentIndex], this.heap[index]] = [this.heap[index], this.heap[parentIndex]]
      index = parentIndex
    }
  }

  _bubbleDown(index) {
    const length = this.heap.length
    while (true) {
      let smallest = index
      const leftChild = 2 * index + 1
      const rightChild = 2 * index + 2

      if (leftChild < length && this.heap[leftChild].dist < this.heap[smallest].dist) {
        smallest = leftChild
      }
      if (rightChild < length && this.heap[rightChild].dist < this.heap[smallest].dist) {
        smallest = rightChild
      }
      if (smallest === index) break

      [this.heap[index], this.heap[smallest]] = [this.heap[smallest], this.heap[index]]
      index = smallest
    }
  }
}

/**
 * Normalize edge fields for backward compatibility
 * Handles both from_node/to_node (object) and from_node_id/to_node_id (number) formats
 */
function normalizeEdge(edge) {
  return {
    from_node_id: edge.from_node_id ?? edge.from_node?.id ?? edge.from,
    to_node_id: edge.to_node_id ?? edge.to_node?.id ?? edge.to,
    distance: edge.distance ?? 1,
    is_bidirectional: edge.is_bidirectional ?? true,
    is_deleted: edge.is_deleted ?? false
  }
}

/**
 * Normalize node fields for backward compatibility
 * Handles both x/y and x_position/y_position field names
 */
function normalizeNode(node) {
  return {
    id: node.id,
    name: node.name,
    x_position: node.x_position ?? node.x ?? 0.5,
    y_position: node.y_position ?? node.y ?? 0.5,
    floor: node.floor ?? 1,
    map_svg_id: node.map_svg_id,
    node_type: node.node_type,
    is_deleted: node.is_deleted ?? false
  }
}

export function dijkstra(nodes, edges, startId, endId) {
  // Normalize nodes and edges for consistent field access
  const normalizedNodes = nodes.map(normalizeNode).filter(n => !n.is_deleted)
  const normalizedEdges = edges.map(normalizeEdge).filter(e => !e.is_deleted)
  
  const nodeMap = new Map(normalizedNodes.map(n => [n.id, n]))
  const distances = {}
  const previous = {}
  const visited = new Set()
  const queue = new PriorityQueue() // Optimized with binary heap

  normalizedNodes.forEach(n => {
    distances[n.id] = Infinity
    previous[n.id] = null
  })
  
  if (!nodeMap.has(startId) || !nodeMap.has(endId)) {
    return null // Start or end node not found or deleted
  }
  
  distances[startId] = 0
  queue.push({ id: startId, dist: 0 })

  while (!queue.isEmpty()) {
    const { id: currentId } = queue.pop()

    if (visited.has(currentId)) continue
    visited.add(currentId)

    if (currentId === endId) break

    const neighbors = normalizedEdges.filter(
      e => (!e.is_deleted) && (
        e.from_node_id === currentId ||
        (e.is_bidirectional && e.to_node_id === currentId)
      )
    )

    for (const edge of neighbors) {
      const neighborId = edge.from_node_id === currentId ? edge.to_node_id : edge.from_node_id
      if (visited.has(neighborId)) continue
      const newDist = distances[currentId] + edge.distance
      if (newDist < distances[neighborId]) {
        distances[neighborId] = newDist
        previous[neighborId] = currentId
        queue.push({ id: neighborId, dist: newDist })
      }
    }
  }

  // Reconstruct path
  const path = []
  let current = endId
  while (current !== null) {
    path.unshift(current)
    current = previous[current]
  }

  if (path[0] !== startId) return null // No path found
  return { path, distance: distances[endId] }
}

/**
 * Find path between two locations using backend navigation graph
 * @param {string} startName - Starting location name
 * @param {string} endName - Destination location name
 * @returns {Promise<{path: Array, totalDistance: number, totalTime: number, steps: Array}>}
 */
export async function findPath(startName, endName) {
  try {
    // Get navigation data from backend API
    const [nodesRes, edgesRes] = await Promise.all([
      api.get('/navigation/nodes/').catch(() => ({ data: [] })),
      api.get('/navigation/edges/').catch(() => ({ data: [] }))
    ])
    
    const rawNodes = nodesRes.data || []
    const rawEdges = edgesRes.data || []

    // Normalize nodes for consistent field access
    const nodes = rawNodes.map(normalizeNode)
    const edges = rawEdges.map(normalizeEdge)

    if (!nodes || nodes.length === 0) {
      throw new Error('No navigation data available')
    }

    // Find nodes by name (or map_svg_id), excluding soft-deleted nodes
    const activeNodes = nodes.filter(n => !n.is_deleted)
    const startNode = activeNodes.find(n => 
      n.name?.toLowerCase() === startName.toLowerCase() || 
      n.map_svg_id?.toLowerCase() === startName.toLowerCase()
    )
    const endNode = activeNodes.find(n => 
      n.name?.toLowerCase() === endName.toLowerCase() || 
      n.map_svg_id?.toLowerCase() === endName.toLowerCase()
    )

    if (!startNode) {
      throw new Error(`Start location "${startName}" not found`)
    }
    if (!endNode) {
      throw new Error(`Destination "${endName}" not found`)
    }

    // Run Dijkstra (it normalizes internally)
    const result = dijkstra(rawNodes, rawEdges, startNode.id, endNode.id)
    
    if (!result) {
      throw new Error('No path found between locations')
    }

    // Build path with node details (using only active nodes)
    const pathNodes = result.path.map(nodeId => {
      const node = activeNodes.find(n => n.id === nodeId)
      return {
        id: node.id,
        name: node.name,
        x: node.x_position ?? node.x,
        y: node.y_position ?? node.y,
        floor: node.floor
      }
    })

    // Generate turn-by-turn steps
    const steps = generateSteps(pathNodes, result.distance)

    // Estimate time (assume 1.4 m/s walking speed + 30s per turn)
    const walkingTime = result.distance / 1.4 / 60 // minutes
    const turnTime = (pathNodes.length - 1) * 0.5 // 30s per transition
    const totalTime = Math.max(1, Math.round(walkingTime + turnTime))

    return {
      path: pathNodes,
      totalDistance: Math.round(result.distance),
      totalTime: totalTime,
      steps: steps
    }
  } catch (err) {
    console.error('[Pathfinder] Error finding path:', err)
    throw err
  }
}

/**
 * Generate turn-by-turn directions from path nodes
 */
function generateSteps(pathNodes, totalDistance) {
  if (pathNodes.length === 0) return []
  
  const steps = []
  
  // Start step
  steps.push({
    instruction: `Start at ${pathNodes[0].name}`,
    distance: ''
  })

  // Intermediate steps
  // Calculate proportional segment distances from the total Dijkstra distance
  const segmentDistances = []
  let totalPixelDist = 0
  for (let i = 1; i < pathNodes.length; i++) {
    const dx = pathNodes[i].x - pathNodes[i-1].x
    const dy = pathNodes[i].y - pathNodes[i-1].y
    const pixDist = Math.sqrt(dx * dx + dy * dy)
    segmentDistances.push(pixDist)
    totalPixelDist += pixDist
  }

  for (let i = 1; i < pathNodes.length - 1; i++) {
    const prev = pathNodes[i - 1]
    const curr = pathNodes[i]
    const next = pathNodes[i + 1]
    
    // Proportional real-world distance for this segment
    const segmentDist = totalPixelDist > 0
      ? Math.round((segmentDistances[i - 1] / totalPixelDist) * totalDistance)
      : 0
    
    // Determine turn direction
    let turn = 'Continue'
    if (next) {
      const angle = calculateAngle(prev, curr, next)
      if (angle > 30) turn = 'Turn right'
      else if (angle < -30) turn = 'Turn left'
      else if (Math.abs(angle) > 150) turn = 'Make a U-turn'
    }
    
    steps.push({
      instruction: `${turn} toward ${curr.name}`,
      distance: segmentDist > 0 ? `~${segmentDist}m` : ''
    })
  }

  // End step
  if (pathNodes.length > 1) {
    steps.push({
      instruction: `Arrive at ${pathNodes[pathNodes.length - 1].name}`,
      distance: ''
    })
  }

  return steps
}

/**
 * Calculate turn angle between three points
 */
function calculateAngle(p1, p2, p3) {
  const dx1 = p2.x - p1.x
  const dy1 = p2.y - p1.y
  const dx2 = p3.x - p2.x
  const dy2 = p3.y - p2.y
  
  const angle1 = Math.atan2(dy1, dx1)
  const angle2 = Math.atan2(dy2, dx2)
  
  let angle = (angle2 - angle1) * 180 / Math.PI
  if (angle > 180) angle -= 360
  if (angle < -180) angle += 360
  
  return angle
}
