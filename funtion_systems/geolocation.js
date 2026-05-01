// GPS location service using Web Geolocation API — works offline

export function watchLocation(onUpdate, onError) {
  if (!navigator.geolocation) {
    onError('Geolocation is not supported by this browser.')
    return null
  }

  const watchId = navigator.geolocation.watchPosition(
    (position) => {
      onUpdate({
        lat: position.coords.latitude,
        lng: position.coords.longitude,
        accuracy: position.coords.accuracy
      })
    },
    (error) => onError(error.message),
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
  )

  return watchId
}

export function stopWatching(watchId) {
  if (watchId !== null) {
    navigator.geolocation.clearWatch(watchId)
  }
}

// Convert real GPS coordinates to SVG/image pixel coordinates
// Call this once with your campus boundary GPS points after map is finalized
export function gpsToMapCoords(lat, lng, mapBounds) {
  const { minLat, maxLat, minLng, maxLng, mapWidth, mapHeight } = mapBounds
  const x = ((lng - minLng) / (maxLng - minLng)) * mapWidth
  const y = ((maxLat - lat) / (maxLat - minLat)) * mapHeight
  return { x, y }
}
