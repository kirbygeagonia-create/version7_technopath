import { ref, computed } from 'vue'

/**
 * Composable for map pan and zoom functionality
 * Used by HomeView, MapView, and NavigateView
 */
export function useMapPanZoom(options = {}) {
  const {
    minScale = 0.5,
    maxScale = 5,
    zoomStep = 1.3,
    defaultScale = 1
  } = options

  // Transform state
  const scale = ref(defaultScale)
  const translateX = ref(0)
  const translateY = ref(0)
  const isPanning = ref(false)
  const panStart = ref({ x: 0, y: 0 })

  // Computed transform style
  const transformStyle = computed(() => {
    const style = {
      transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
      transformOrigin: '50% 50%'
    }
    console.log('[useMapPanZoom] transformStyle updated:', style.transform)
    return style
  })

  // Zoom functions
  function zoomIn() {
    scale.value = Math.min(scale.value * zoomStep, maxScale)
  }

  function zoomOut() {
    scale.value = Math.max(scale.value / zoomStep, minScale)
  }

  function setScale(newScale) {
    scale.value = Math.max(minScale, Math.min(newScale, maxScale))
  }

  function resetTransform() {
    scale.value = defaultScale
    translateX.value = 0
    translateY.value = 0
  }

  // Pan functions
  function onPointerDown(e) {
    console.log('[useMapPanZoom] onPointerDown', e.type)
    isPanning.value = true
    const clientX = e.clientX || (e.touches?.[0]?.clientX)
    const clientY = e.clientY || (e.touches?.[0]?.clientY)
    panStart.value = {
      x: clientX - translateX.value,
      y: clientY - translateY.value
    }
  }

  function onPointerMove(e) {
    if (!isPanning.value) return
    const clientX = e.clientX || (e.touches?.[0]?.clientX)
    const clientY = e.clientY || (e.touches?.[0]?.clientY)
    translateX.value = clientX - panStart.value.x
    translateY.value = clientY - panStart.value.y
  }

  function onPointerUp() {
    console.log('[useMapPanZoom] onPointerUp')
    isPanning.value = false
  }

  // Wheel zoom
  function onWheel(e) {
    console.log('[useMapPanZoom] onWheel', e.deltaY)
    e.preventDefault()
    if (e.deltaY < 0) {
      zoomIn()
    } else {
      zoomOut()
    }
  }

  // Touch pinch zoom
  let lastTouchDist = 0

  function onTouchStart(e) {
    if (e.touches.length === 2) {
      lastTouchDist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      )
    } else if (e.touches.length === 1) {
      onPointerDown(e)
    }
  }

  function onTouchMove(e) {
    if (e.touches.length === 2) {
      const dist = Math.hypot(
        e.touches[0].clientX - e.touches[1].clientX,
        e.touches[0].clientY - e.touches[1].clientY
      )
      if (lastTouchDist > 0) {
        const newScale = scale.value * (dist / lastTouchDist)
        setScale(newScale)
      }
      lastTouchDist = dist
    } else if (e.touches.length === 1 && isPanning.value) {
      onPointerMove(e)
    }
  }

  // Initialize transform based on container size
  function initTransform(containerWidth, containerHeight, contentWidth = 800, contentHeight = 600) {
    const baseScale = Math.min(1, containerWidth / contentWidth)
    scale.value = baseScale
    translateX.value = (containerWidth - contentWidth * baseScale) / 2
    translateY.value = (containerHeight - contentHeight * baseScale) / 2
  }

  return {
    // State
    scale,
    translateX,
    translateY,
    isPanning,
    // Computed
    transformStyle,
    // Methods
    zoomIn,
    zoomOut,
    setScale,
    resetTransform,
    onPointerDown,
    onPointerMove,
    onPointerUp,
    onWheel,
    onTouchStart,
    onTouchMove,
    initTransform
  }
}

export default useMapPanZoom
