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
    const rawPaths = this.loadFromStorage()
    // Normalize all paths from storage to ensure coordinates are numbers
    const normalizedPaths = {}
    Object.keys(rawPaths).forEach(key => {
      normalizedPaths[key] = this.normalizePath(rawPaths[key])
    })
    this.paths = ref(normalizedPaths)
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
      
      // Get localStorage data to check if we have existing paths
      const localData = this.loadFromStorage()
      const hasLocalData = Object.keys(localData).length > 0
      
      // If API returns empty but we have localStorage data, preserve it
      if (pathsArray.length === 0 && hasLocalData) {
        console.warn('[PathManager] API returned empty paths, keeping localStorage data')
        // Ensure paths are loaded from localStorage
        this.paths.value = localData
        return localData
      }
      
      // If we have local data AND API data, merge them (API takes precedence for same IDs)
      if (hasLocalData && pathsArray.length > 0) {
        console.log('[PathManager] Merging API data with localStorage')
        const mergedPaths = { ...localData }
        pathsArray.forEach(path => {
          mergedPaths[path.id] = this.normalizePath(path)
        })
        this.paths.value = mergedPaths
        this.saveToStorage()
        return mergedPaths
      }
      
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
      // Fallback to localStorage
      const localData = this.loadFromStorage()
      this.paths.value = localData
      return localData
    }
  }

  // Normalize path data from API format to internal format
  normalizePath(path) {
    // Handle new API format where points is array of PathPoint objects
    let elementIds = path.element_ids || path.elementIds || []
    let visualPoints = (path.visualPoints || []).map(p => ({
      id: p.id,
      x: typeof p.x === 'string' ? parseFloat(p.x) : (p.x ?? 0),
      y: typeof p.y === 'string' ? parseFloat(p.y) : (p.y ?? 0),
      row: p.row,
      col: p.col,
      gridSize: p.gridSize
    }))
    
    // If API returns points array with element_id, extract elementIds
    if (path.points && path.points.length > 0 && typeof path.points[0] === 'object' && path.points[0].element_id) {
      elementIds = path.points.map(p => p.element_id)
      visualPoints = path.points.map(p => ({
        id: p.element_id,
        x: typeof p.x === 'string' ? parseFloat(p.x) : (p.x ?? 0),
        y: typeof p.y === 'string' ? parseFloat(p.y) : (p.y ?? 0)
      }))
    }
    
    return {
      id: path.id,
      name: path.name,
      description: path.description || '',
      facility: path.facility || null,
      room: path.room || '',
      floor: path.floor || 1,
      from: path.from_node || path.from || path.from_location || '',
      to: path.to_node || path.to || path.to_location || '',
      points: path.points || [],
      elementIds: elementIds,
      distance: path.distance || 0,
      createdAt: path.created_at || path.createdAt,
      updatedAt: path.updated_at || path.updatedAt,
      // Preserve visual points if they exist (frontend-only field)
      visualPoints: visualPoints
    }
  }

  // Convert internal format to API format
  toApiFormat(pathData) {
    return {
      id: pathData.id,
      name: pathData.name,
      description: pathData.description,
      facility: pathData.facility || null,
      room: pathData.room || null,
      floor: pathData.floor || 1,
      points_input: pathData.points || [],
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
      // Use reactive assignment to trigger Vue updates
      this.paths.value = { ...this.paths.value, [newPath.id]: newPath }
      this.saveToStorage() // Also save to localStorage
      return newPath
    } catch (error) {
      console.warn('API failed, saving to localStorage:', error)
      // Fallback to localStorage - preserve visualPoints!
      this.useApi.value = false
      const newPath = {
        id,
        name,
        description,
        from,
        to,
        points,
        elementIds,
        visualPoints: pathData.visualPoints || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      // Use reactive assignment to trigger Vue updates
      this.paths.value = { ...this.paths.value, [newPath.id]: newPath }
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
      let updatedPath = this.normalizePath(response.data)
      // Preserve visualPoints if API doesn't return them
      if ((!updatedPath.visualPoints || updatedPath.visualPoints.length === 0) && updates.visualPoints) {
        updatedPath = { ...updatedPath, visualPoints: updates.visualPoints }
      }
      // Use reactive assignment to trigger Vue updates
      this.paths.value = { ...this.paths.value, [updatedPath.id]: updatedPath }
      this.saveToStorage() // Also save to localStorage
      return updatedPath
    } catch (error) {
      console.warn('API failed, saving to localStorage:', error)
      // Fallback to localStorage - preserve visualPoints!
      this.useApi.value = false
      const updatedPath = {
        ...currentPath,
        ...updates,
        visualPoints: updates.visualPoints || currentPath.visualPoints || [],
        updatedAt: new Date().toISOString()
      }
      // Use reactive assignment to trigger Vue updates
      this.paths.value = { ...this.paths.value, [id]: updatedPath }
      this.saveToStorage()
      return updatedPath
    }
  }

  // Delete a path via API
  async deletePath(id) {
    try {
      await api.delete(`/navigation/paths/${id}/`)
      // Use reactive assignment to trigger Vue updates
      const newPaths = { ...this.paths.value }
      delete newPaths[id]
      this.paths.value = newPaths
      this.saveToStorage() // Also remove from localStorage
      return true
    } catch (error) {
      console.warn('API failed, deleting from localStorage:', error)
      // Fallback to localStorage
      this.useApi.value = false
      // Use reactive assignment to trigger Vue updates
      const newPaths = { ...this.paths.value }
      delete newPaths[id]
      this.paths.value = newPaths
      this.saveToStorage()
      return true
    }
  }

  // Get element positions from SVG or visualPoints (for admin panel)
  getElementPositions(svgElement, elementIds, visualPoints = []) {
    const positions = []
    
    for (const id of elementIds) {
      // First check if we have visualPoints with this ID
      const visualPoint = visualPoints.find(p => p.id === id)
      if (visualPoint && visualPoint.x !== undefined) {
        positions.push({
          id,
          x: visualPoint.x,
          y: visualPoint.y,
          width: visualPoint.width || 20,
          height: visualPoint.height || 20,
          element: null,
          fromVisualPoint: true
        })
        continue
      }
      
      // Try to find SVG element
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
        // No visual point and no SVG element - use placeholder
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
