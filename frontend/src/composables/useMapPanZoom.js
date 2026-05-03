import { ref, computed } from 'vue'

/**
 * Composable for map pan and zoom functionality.
 *
 * Zoom is BUTTON-ONLY — mouse wheel and trackpad scroll are intentionally
 * disabled because they are too sensitive and conflict with page scrolling.
 *
 * Touch behaviour:
 *   - 1 finger  → pan (drag)
 *   - 2 fingers → pinch-to-zoom (gentle, dampened)
 *
 * Used by HomeView and MapView.
 */
export function useMapPanZoom(options = {}) {
  const {
    minScale   = 0.3,
    maxScale   = 5,
    zoomStep   = 1.25,   // gentler than the old 1.3
    defaultScale = 1
  } = options

  // ── State ──────────────────────────────────────────────────
  const scale      = ref(defaultScale)
  const translateX = ref(0)
  const translateY = ref(0)
  const isPanning  = ref(false)
  const panStart   = ref({ x: 0, y: 0 })

  // ── Computed transform ─────────────────────────────────────
  const transformStyle = computed(() => ({
    transform: `translate(${translateX.value}px, ${translateY.value}px) scale(${scale.value})`,
    transformOrigin: '50% 50%',
    willChange: 'transform'
  }))

  // ── Zoom helpers ───────────────────────────────────────────
  function clampScale(s) {
    return Math.max(minScale, Math.min(s, maxScale))
  }

  function zoomIn() {
    scale.value = clampScale(scale.value * zoomStep)
  }

  function zoomOut() {
    scale.value = clampScale(scale.value / zoomStep)
  }

  function setScale(newScale) {
    scale.value = clampScale(newScale)
  }

  function resetTransform() {
    scale.value   = defaultScale
    translateX.value = 0
    translateY.value = 0
  }

  // ── Mouse pan ──────────────────────────────────────────────
  function onPointerDown(e) {
    // Only left-button drag
    if (e.button !== undefined && e.button !== 0) return
    isPanning.value = true
    panStart.value = {
      x: e.clientX - translateX.value,
      y: e.clientY - translateY.value
    }
  }

  function onPointerMove(e) {
    if (!isPanning.value) return
    translateX.value = e.clientX - panStart.value.x
    translateY.value = e.clientY - panStart.value.y
  }

  function onPointerUp() {
    isPanning.value = false
  }

  // ── Wheel — DISABLED (buttons only) ───────────────────────
  // We intentionally do nothing on wheel so the page can scroll
  // normally and the map doesn't zoom unexpectedly.
  function onWheel(e) {
    // Do not call e.preventDefault() — let the page scroll.
    // Zoom is handled exclusively by the +/- buttons.
  }

  // ── Touch handling ─────────────────────────────────────────
  let lastTouchDist  = 0
  let lastTouchMidX  = 0
  let lastTouchMidY  = 0
  let touchPanActive = false

  function getTouchDist(touches) {
    return Math.hypot(
      touches[0].clientX - touches[1].clientX,
      touches[0].clientY - touches[1].clientY
    )
  }

  function onTouchStart(e) {
    if (e.touches.length === 2) {
      // Pinch start — record distance and midpoint
      touchPanActive  = false
      isPanning.value = false
      lastTouchDist   = getTouchDist(e.touches)
      lastTouchMidX   = (e.touches[0].clientX + e.touches[1].clientX) / 2
      lastTouchMidY   = (e.touches[0].clientY + e.touches[1].clientY) / 2
    } else if (e.touches.length === 1) {
      // Single-finger pan start
      touchPanActive  = true
      isPanning.value = true
      panStart.value  = {
        x: e.touches[0].clientX - translateX.value,
        y: e.touches[0].clientY - translateY.value
      }
    }
  }

  function onTouchMove(e) {
    if (e.touches.length === 2) {
      // ── Pinch-to-zoom ──────────────────────────────────────
      const dist = getTouchDist(e.touches)
      if (lastTouchDist > 0) {
        // Dampen the raw ratio so it feels less jumpy
        const rawRatio  = dist / lastTouchDist
        const dampened  = 1 + (rawRatio - 1) * 0.55   // 55% of raw change
        const newScale  = clampScale(scale.value * dampened)
        scale.value     = newScale
      }
      lastTouchDist = dist

      // Also pan with the midpoint movement
      const midX = (e.touches[0].clientX + e.touches[1].clientX) / 2
      const midY = (e.touches[0].clientY + e.touches[1].clientY) / 2
      translateX.value += midX - lastTouchMidX
      translateY.value += midY - lastTouchMidY
      lastTouchMidX = midX
      lastTouchMidY = midY

    } else if (e.touches.length === 1 && touchPanActive && isPanning.value) {
      // ── Single-finger pan ──────────────────────────────────
      translateX.value = e.touches[0].clientX - panStart.value.x
      translateY.value = e.touches[0].clientY - panStart.value.y
    }
  }

  function onTouchEnd(e) {
    if (e.touches.length === 0) {
      isPanning.value = false
      touchPanActive  = false
      lastTouchDist   = 0
    } else if (e.touches.length === 1) {
      // Finger lifted during pinch — switch back to pan mode
      lastTouchDist   = 0
      touchPanActive  = true
      isPanning.value = true
      panStart.value  = {
        x: e.touches[0].clientX - translateX.value,
        y: e.touches[0].clientY - translateY.value
      }
    }
  }

  // ── Init ───────────────────────────────────────────────────
  function initTransform(containerWidth, containerHeight, contentWidth = 800, contentHeight = 600) {
    const baseScale  = Math.min(1, containerWidth / contentWidth)
    scale.value      = clampScale(baseScale)
    translateX.value = (containerWidth  - contentWidth  * scale.value) / 2
    translateY.value = (containerHeight - contentHeight * scale.value) / 2
  }

  return {
    // State
    scale, translateX, translateY, isPanning,
    // Computed
    transformStyle,
    // Zoom buttons
    zoomIn, zoomOut, setScale, resetTransform,
    // Mouse events
    onPointerDown, onPointerMove, onPointerUp,
    // Wheel (no-op — kept for API compatibility)
    onWheel,
    // Touch events
    onTouchStart, onTouchMove,
    onTouchEnd,
    // Alias kept for backward compat with old callers
    onTouchMove: onTouchMove,
    initTransform
  }
}

export default useMapPanZoom
