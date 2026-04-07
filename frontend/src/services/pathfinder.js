// Dijkstra's algorithm — ported from pathfinder.dart
// Works fully offline using navigation_nodes and navigation_edges from IndexedDB

export function dijkstra(nodes, edges, startId, endId) {
  const distances = {}
  const previous = {}
  const visited = new Set()
  const queue = []

  nodes.forEach(n => {
    distances[n.id] = Infinity
    previous[n.id] = null
  })
  distances[startId] = 0
  queue.push({ id: startId, dist: 0 })

  while (queue.length > 0) {
    queue.sort((a, b) => a.dist - b.dist)
    const { id: currentId } = queue.shift()

    if (visited.has(currentId)) continue
    visited.add(currentId)

    if (currentId === endId) break

    const neighbors = edges.filter(
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
