/**
 * useLocations composable
 * 
 * Manages shared locations across the application
 * - Fetches from API (navigation nodes)
 - Falls back to cached data
 * - Can extract from SVG elements
 * - Provides reactive location list for all components
 */

import { ref, computed, watch } from 'vue'
import api from '../services/api.js'
import db from '../services/db.js'
import pathManager from '../services/pathManager.js'

const locations = ref([])
const isLoading = ref(false)
const error = ref(null)

// Shared composable state (singleton)
let initialized = false

export function useLocations() {
  // Initialize on first use
  if (!initialized) {
    initialized = true
    loadLocations()
    
    // Extract existing paths immediately
    extractLocationsFromPaths()
    
    // Watch for path changes and extract locations from paths
    watch(pathManager.paths, (newPaths) => {
      extractLocationsFromPaths()
    }, { deep: true })
  }
  
  // Extract unique locations from paths (using visualPoints for coordinates)
  async function extractLocationsFromPaths() {
    const paths = pathManager.getAllPaths()
    const locationMap = new Map()
    
    console.log('[useLocations] Processing', paths.length, 'paths from SVG Paths')
    
    paths.forEach(path => {
      // Extract from elementIds and visualPoints
      if (path.elementIds && path.elementIds.length > 0) {
        console.log('[useLocations] Processing path:', path.name, 'with IDs:', path.elementIds)
        console.log('[useLocations] Visual points:', path.visualPoints)
        
        path.elementIds.forEach((id, index) => {
          // Determine type based on position
          let type = 'path-point'
          let subtype = 'stop'
          if (index === 0) {
            type = 'path-endpoint'
            subtype = 'from'
          } else if (index === path.elementIds.length - 1) {
            type = 'path-endpoint'  
            subtype = 'to'
          }
          
          // Get coordinates from visualPoints (set when clicking on map in SVG Paths)
          // Try to match by id first, then by index position
          let visualPoint = path.visualPoints?.find(vp => vp.id === id)
          if (!visualPoint && path.visualPoints?.[index]) {
            visualPoint = path.visualPoints[index]
          }
          
          if (visualPoint) {
            console.log(`[useLocations] Found visual point for "${id}" at index ${index}:`, {x: visualPoint.x, y: visualPoint.y})
          } else {
            console.warn(`[useLocations] NO visual point found for "${id}" at index ${index}. Available:`, path.visualPoints)
          }
          
          // Skip if id is not a valid string
          if (!id || typeof id !== 'string') {
            console.warn('[useLocations] Skipping invalid id:', id)
            return
          }
          
          if (!locationMap.has(id)) {
            locationMap.set(id, {
              id: id,
              name: id.replace(/[_-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              type: type,
              subtype: subtype,
              source: 'path',
              pathIds: [path.id],
              // Add coordinates from visualPoints (pixel coordinates from SVG)
              x: visualPoint?.x ?? null,
              y: visualPoint?.y ?? null,
              floor: 1
            })
          } else {
            const loc = locationMap.get(id)
            if (!loc.pathIds.includes(path.id)) {
              loc.pathIds.push(path.id)
            }
            // Update to endpoint if it's first or last
            if (index === 0 || index === path.elementIds.length - 1) {
              loc.type = 'path-endpoint'
              loc.subtype = index === 0 ? 'from' : 'to'
            }
          }
        })
      }
    })
    
    // Merge with existing locations (don't duplicate)
    const pathLocations = Array.from(locationMap.values())
    const existingIds = new Set(locations.value.map(l => l.id))
    
    pathLocations.forEach(loc => {
      if (!existingIds.has(loc.id)) {
        locations.value.push(loc)
      }
    })
  }

  // Computed
  const activeLocations = computed(() => 
    locations.value.filter(l => !l.is_deleted && !l.deleted)
  )

  const locationsByType = computed(() => {
    const grouped = {}
    activeLocations.value.forEach(loc => {
      const type = loc.type || loc.node_type || 'location'
      if (!grouped[type]) grouped[type] = []
      grouped[type].push(loc)
    })
    return grouped
  })

  const roomLocations = computed(() => 
    activeLocations.value.filter(l => 
      (l.type || l.node_type) === 'room'
    )
  )

  const junctionLocations = computed(() => 
    activeLocations.value.filter(l => 
      (l.type || l.node_type) === 'junction'
    )
  )

  // Methods
  async function loadLocations() {
    if (isLoading.value) return
    isLoading.value = true
    error.value = null

    try {
      // Try API first
      const response = await api.get('/navigation/nodes/')
      if (response.data && response.data.length > 0) {
        locations.value = normalizeLocations(response.data)
        // Cache to IndexedDB
        await cacheLocations(locations.value)
        return
      }
    } catch (e) {
      console.warn('API failed, trying cache:', e)
    }

    // Fallback to cache
    try {
      const cached = await db.navigation_nodes.toArray()
      if (cached && cached.length > 0) {
        locations.value = normalizeLocations(cached)
        return
      }
    } catch (e) {
      console.warn('Cache failed:', e)
    }

    // Final fallback to hardcoded
    locations.value = getDefaultLocations()
    error.value = 'Using default locations (API unavailable)'
    
    isLoading.value = false
  }

  async function cacheLocations(data) {
    try {
      // Convert to plain objects (remove Vue proxies)
      const plainData = JSON.parse(JSON.stringify(data))
      
      await db.transaction('rw', db.navigation_nodes, async () => {
        await db.navigation_nodes.clear()
        await db.navigation_nodes.bulkPut(plainData)
      })
    } catch (e) {
      console.warn('Failed to cache locations:', e.message)
    }
  }

  function normalizeLocations(nodes) {
    return nodes.map(node => ({
      id: node.id,
      name: node.name || node.label || `Location ${node.id}`,
      type: node.type || node.node_type || 'location',
      x: node.x_position || node.x || 0,
      y: node.y_position || node.y || 0,
      floor: node.floor || 1,
      map_svg_id: node.map_svg_id || '',
      is_deleted: node.is_deleted || false,
      deleted: node.deleted || false
    }))
  }

  function getDefaultLocations() {
    return [
      { id: 'entrance', name: 'Main Entrance', type: 'junction', x: 0.5, y: 0.9 },
      { id: 'lobby', name: 'Lobby', type: 'junction', x: 0.5, y: 0.8 },
      { id: 'office1', name: 'Office 1', type: 'room', x: 0.2, y: 0.7 },
      { id: 'office2', name: 'Office 2', type: 'room', x: 0.4, y: 0.7 },
      { id: 'office3', name: 'Office 3', type: 'room', x: 0.6, y: 0.7 },
      { id: 'office4', name: 'Office 4', type: 'room', x: 0.8, y: 0.7 },
      { id: 'office5', name: 'Office 5', type: 'room', x: 0.3, y: 0.5 },
      { id: 'classroom1', name: 'Classroom 1', type: 'room', x: 0.5, y: 0.5 },
      { id: 'classroom2', name: 'Classroom 2', type: 'room', x: 0.7, y: 0.5 },
      { id: 'classroom3', name: 'Classroom 3', type: 'room', x: 0.2, y: 0.3 },
      { id: 'library', name: 'Library', type: 'room', x: 0.5, y: 0.3 },
      { id: 'cafeteria', name: 'Cafeteria', type: 'room', x: 0.8, y: 0.3 },
      { id: 'restroom1', name: 'Restroom 1', type: 'room', x: 0.3, y: 0.2 },
      { id: 'restroom2', name: 'Restroom 2', type: 'room', x: 0.7, y: 0.2 },
      { id: 'exit', name: 'Emergency Exit', type: 'junction', x: 0.5, y: 0.1 }
    ]
  }

  // Extract locations from SVG elements (Option C)
  async function extractFromSVG(svgContent) {
    const parser = new DOMParser()
    const doc = parser.parseFromString(svgContent, 'image/svg+xml')
    
    // Find all elements with IDs that look like location markers
    const elements = doc.querySelectorAll('[id]')
    const extracted = []
    
    elements.forEach((el, index) => {
      const id = el.id
      // Skip non-location IDs
      if (id.match(/^(rect|path|circle|polyline|g\d+|layer)/i)) return
      
      const bbox = el.getBBox ? el.getBBox() : { x: 0, y: 0, width: 0, height: 0 }
      
      extracted.push({
        id: `svg_${id}`,
        name: id.replace(/[_-]/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        type: 'room',
        x: bbox.x + bbox.width / 2,
        y: bbox.y + bbox.height / 2,
        map_svg_id: id,
        source: 'svg'
      })
    })
    
    if (extracted.length > 0) {
      locations.value = [...locations.value.filter(l => l.source !== 'svg'), ...extracted]
    }
    
    return extracted
  }

  function getLocationById(id) {
    return locations.value.find(l => l.id === id) || null
  }

  function getLocationName(id) {
    const loc = getLocationById(id)
    return loc ? loc.name : id
  }

  return {
    // State
    locations,
    activeLocations,
    locationsByType,
    roomLocations,
    junctionLocations,
    isLoading,
    error,
    
    // Methods
    loadLocations,
    extractFromSVG,
    extractLocationsFromPaths,
    getLocationById,
    getLocationName,
    refresh: loadLocations
  }
}
