// src/App.tsx
import { useEffect, useRef, useState } from 'react'
import { useGeolocation } from '@/hooks/useGeolocation'
import { apiClient } from '@/api/ApiClient'
import MapController from '@/controllers/MapController'
import SkyRenderer from '@/renderer/SkyRenderer'
import { SkyResponse } from '@/types'

function App() {
  const skyRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<HTMLDivElement>(null)
  const rendererRef = useRef<SkyRenderer | null>(null)
  const mapControllerRef = useRef<MapController | null>(null)

  const { request, loading, error } = useGeolocation()
  const [skyData, setSkyData] = useState<SkyResponse | null>(null)

  // initialize Three.js renderer
  useEffect(() => {
    if (skyRef.current && !rendererRef.current) {
      rendererRef.current = new SkyRenderer(skyRef.current)
    }
  }, [])

  // initialize Google Maps when location is ready
  useEffect(() => {
    if (!mapRef.current || !request) return

    mapControllerRef.current = new MapController({
      container: mapRef.current,
      onLocationSelect: async (lat, lng) => {
        const data = await apiClient.getSky({
          latitude: lat,
          longitude: lng,
          observed_at: new Date().toISOString(),
        })
        setSkyData(data)
      },
    })

    mapControllerRef.current.initialize(request.latitude, request.longitude)

    // fetch sky data for initial location
    apiClient.getSky(request).then(setSkyData)

  }, [request])

  // render sky when data changes
useEffect(() => {
  if (!skyRef.current) return
  rendererRef.current = new SkyRenderer(skyRef.current)
}, [skyRef.current])

// render sky when data arrives
useEffect(() => {
  if (!skyData || !rendererRef.current) return
rendererRef.current.renderSky(
  skyData.constellations,
  skyData.stars,
  skyData.astronomy_time,
  // request!.latitude
)}, [skyData])

  if (loading) return <div className="loading">Detecting location...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="app">
      <div className="sky-scene" ref={skyRef} />
      <div className="map-panel" ref={mapRef} />
    </div>
  )
}

export default App