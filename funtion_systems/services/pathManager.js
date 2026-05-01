/**
 * Path Manager Service
 * Manages navigation paths - Connected to real database API
 * Provides CRUD operations for paths and viewBox animation
 */

import { ref, computed } from 'vue'
import api from './api.js'

const STORAGE_KEY = 'svg_navigation_paths_v2'

class PathManager {
  constructor() {
    this.paths = ref(this.loadFromStorage())
    this.currentPath = ref(null)
    this.currentStep = ref(0)
    this.isNavigating = ref(false)
    this.useApi = ref(true) // Flag to track if API is available
  }

  // Load from localStorage as fallback
  loadFromStorage() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        return JSON.parse(stored)
      }
    } catch (e) {
      console.warn('Failed to load from storage:', e)
    }
    return {}
  }

  // Save to localStorage
  saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.paths.value))
    } catch (e) {
      console.error('Failed to save to storage:', e)
    }
  }

  // Load all paths from API (with localStorage fallback)
  async loadPaths() {
    try {
      const response = await api.get('/navigation/paths/')
      const pathsArray = response.data || []
      // Convert array to object keyed by id
      const pathsObj = {}
      pathsArray.forEach(path => {
        pathsObj[path.id] = this.normalizePath(path)
      })
      this.paths.value = pathsObj
      this.saveToStorage() // Sync API data to localStorage
      return pathsObj
    } catch (error) {
      console.warn('API failed, using localStorage:', error)
      this.useApi.value = false
      // Fallback to localStorage - data already loaded in constructor
      return this.paths.value
    }
  }

  // Normalize path data from API format to internal format
  normalizePath(path) {
    return {
      id: path.id,
      name: path.name,
      description: path.description || '',
      from: path.from_node || '',
      to: path.to_node || '',
      points: path.points || [],
      elementIds: path.element_ids || [],
      distance: path.distance || 0,
      createdAt: path.created_at,
      updatedAt: path.updated_at
    }
  }

  // Convert internal format to API format
  toApiFormat(pathData) {
    return {
      id: pathData.id,
      name: pathData.name,
      description: pathData.description,
      from_node: pathData.from,
      to_node: pathData.to,
      points: pathData.points || [],
      element_ids: pathData.elementIds || []
    }
  }

  // Get all paths as array
  getAllPaths() {
    return Object.values(this.paths.value)
  }

  // Get a single path by ID (from local cache or API)
  getPath(id) {
    return this.paths.value[id] || null
  }

  // Fetch single path from API
  async fetchPath(id) {
    try {
      const response = await api.get(`/navigation/paths/${id}/`)
      const path = this.normalizePath(response.data)
      this.paths.value[id] = path
      return path
    } catch (error) {
      console.error(`Failed to fetch path ${id}:`, error)
      return null
    }
  }

  // Create a new path via API
  async createPath(pathData) {
    // Prepare data outside try block so catch can access it
    const id = pathData.id || `path_${Date.now()}`
    const name = pathData.name || 'Unnamed Path'
    const description = pathData.description || ''
    const from = pathData.from || ''
    const to = pathData.to || ''
    const points = pathData.points || pathData.visualPoints?.map(p => [p.x, p.y]) || []
    const elementIds = pathData.elementIds || []
    
    try {
      const apiData = this.toApiFormat({
        id, name, description, from, to, points, elementIds
      })
      
      const response = await api.post('/navigation/paths/', apiData)
      const newPath = this.normalizePath(response.data)
      this.paths.value[newPath.id] = newPath
      this.saveToStorage() // Also save to localStorage
      return newPath
    } catch (error) {
      console.warn('API failed, saving to localStorage:', error)
      // Fallback to localStorage
      this.useApi.value = false
      const newPath = {
        id,
        name,
        description,
        from,
        to,
        points,
        elementIds,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      this.paths.value[newPath.id] = newPath
      this.saveToStorage()
      return newPath
    }
  }

  // Update an existing path via API
  async updatePath(id, updates) {
    // Get current path outside try block
    const currentPath = this.paths.value[id]
    if (!currentPath) {
      throw new Error(`Path with ID ${id} not found`)
    }
    
    try {
      const apiData = this.toApiFormat({
        ...currentPath,
        ...updates,
        id
      })
      
      const response = await api.put(`/navigation/paths/${id}/`, apiData)
      const updatedPath = this.normalizePath(response.data)
      this.paths.value[id] = updatedPath
      this.saveToStorage() // Also save to localStorage
      return updatedPath
    } catch (error) {
      console.warn('API failed, saving to localStorage:', error)
      // Fallback to localStorage
      this.useApi.value = false
      const updatedPath = {
        ...currentPath,
        ...updates,
        updatedAt: new Date().toISOString()
      }
      this.paths.value[id] = updatedPath
      this.saveToStorage()
      return updatedPath
    }
  }

  // Delete a path via API
  async deletePath(id) {
    try {
      await api.delete(`/navigation/paths/${id}/`)
      delete this.paths.value[id]
      this.saveToStorage() // Also remove from localStorage
      return true
    } catch (error) {
      console.warn('API failed, deleting from localStorage:', error)
      // Fallback to localStorage
      this.useApi.value = false
      delete this.paths.value[id]
      this.saveToStorage()
      return true
    }
  }

  // Get element positions from SVG (for admin panel)
  getElementPositions(svgElement, elementIds) {
    const positions = []
    
    for (const id of elementIds) {
      const element = svgElement.querySelector(`#${id}`)
      if (element) {
        const bbox = element.getBBox()
        const ctm = element.getCTM()
        
        // Get center point of element
        const centerX = bbox.x + bbox.width / 2
        const centerY = bbox.y + bbox.height / 2
        
        // Transform to SVG coordinates
        const point = svgElement.createSVGPoint()
        point.x = centerX
        point.y = centerY
        
        const transformedPoint = point.matrixTransform(ctm)
        
        positions.push({
          id,
          x: transformedPoint.x,
          y: transformedPoint.y,
          width: bbox.width,
          height: bbox.height,
          element
        })
      } else {
        console.warn(`Element with ID "${id}" not found in SVG`)
        positions.push({
          id,
          x: 0,
          y: 0,
          width: 0,
          height: 0,
          element: null,
          notFound: true
        })
      }
    }
    
    return positions
  }

  // Calculate viewBox for a specific point with zoom
  calculateViewBox(x, y, zoom = 1, viewWidth = 800, viewHeight = 600) {
    const width = viewWidth / zoom
    const height = viewHeight / zoom
    const minX = x - width / 2
    const minY = y - height / 2
    
    return {
      x: minX,
      y: minY,
      width,
      height,
      zoom
    }
  }

  // Calculate viewBox for showing the entire path
  calculatePathViewBox(positions, padding = 100) {
    if (positions.length === 0) {
      return { x: 0, y: 0, width: 3306, height: 7159 }
    }

    const validPositions = positions.filter(p => !p.notFound && p.x !== undefined && p.y !== undefined)
    
    if (validPositions.length === 0) {
      return { x: 0, y: 0, width: 3306, height: 7159 }
    }

    const minX = Math.min(...validPositions.map(p => p.x)) - padding
    const maxX = Math.max(...validPositions.map(p => p.x)) + padding
    const minY = Math.min(...validPositions.map(p => p.y)) - padding
    const maxY = Math.max(...validPositions.map(p => p.y)) + padding
    
    return {
      x: minX,
      y: minY,
      width: maxX - minX,
      height: maxY - minY
    }
  }

  // Start navigation along a path
  startNavigation(pathId) {
    const path = this.paths.value[pathId]
    if (!path) {
      throw new Error(`Path with ID ${pathId} not found`)
    }

    this.currentPath.value = path
    this.currentStep.value = 0
    this.isNavigating.value = true
    
    return path
  }

  // Stop navigation
  stopNavigation() {
    this.currentPath.value = null
    this.currentStep.value = 0
    this.isNavigating.value = false
  }

  // Move to next step in navigation
  nextStep() {
    if (!this.currentPath.value) return null
    
    const points = this.currentPath.value.points || []
    if (this.currentStep.value < points.length - 1) {
      this.currentStep.value++
    }
    
    return this.currentStep.value
  }

  // Move to previous step in navigation
  previousStep() {
    if (!this.currentPath.value) return null
    
    if (this.currentStep.value > 0) {
      this.currentStep.value--
    }
    
    return this.currentStep.value
  }

  // Get current step data
  getCurrentStep() {
    if (!this.currentPath.value) return null
    
    const points = this.currentPath.value.points || []
    return {
      step: this.currentStep.value,
      totalSteps: points.length,
      point: points[this.currentStep.value],
      isFirst: this.currentStep.value === 0,
      isLast: this.currentStep.value === points.length - 1
    }
  }

  // Export path to JSON
  exportPath(pathId) {
    const path = this.paths.value[pathId]
    if (!path) {
      throw new Error(`Path with ID ${pathId} not found`)
    }
    
    return JSON.stringify(path, null, 2)
  }

  // Import path from JSON and save to API
  async importPath(jsonString) {
    try {
      const path = JSON.parse(jsonString)
      
      if (!path.id) {
        throw new Error('Invalid path data: missing ID')
      }
      
      // Generate new ID if it already exists
      if (this.paths.value[path.id]) {
        path.id = `${path.id}_${Date.now()}`
      }
      
      return await this.createPath(path)
    } catch (e) {
      throw new Error(`Failed to import path: ${e.message}`)
    }
  }

  // Find route between two nodes via API
  async findRoute(fromId, toId) {
    try {
      const response = await api.get('/navigation/route/', {
        params: { from: fromId, to: toId }
      })
      return response.data
    } catch (error) {
      console.error('Failed to find route:', error)
      throw error
    }
  }
}

// Create singleton instance
const pathManager = new PathManager()

export default pathManager
export { PathManager }
