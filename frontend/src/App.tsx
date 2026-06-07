import { useEffect, useRef, useState } from 'react'
import { useGeolocation } from '@/hooks/useGeolocation'
import { apiClient } from '@/api/ApiClient'
import SkyRenderer from '@/renderer/SkyRenderer'
import GlobeRenderer from '@/renderer/GlobeRender'
import { SkyResponse } from '@/types'

function App() {
  const skyRef = useRef<HTMLDivElement>(null)
  const globeRef = useRef<HTMLDivElement>(null)
  const rendererRef = useRef<SkyRenderer | null>(null)
  const globeRendererRef = useRef<GlobeRenderer | null>(null)

  const { request, loading, error } = useGeolocation()
  const [skyData, setSkyData] = useState<SkyResponse | null>(null)

  const fetchSky = async (lat: number, lng: number) => {
    const data = await apiClient.getSky({
      latitude: lat,
      longitude: lng,
      observed_at: new Date().toISOString(),
    })
    setSkyData(data)
  }

  useEffect(() => {
    if (!request) return
    if (!skyRef.current || !globeRef.current) return

    // SkyRenderer
    if (!rendererRef.current) {
      rendererRef.current = new SkyRenderer(skyRef.current)
    }

    // GlobeRenderer
    if (!globeRendererRef.current) {
      globeRendererRef.current = new GlobeRenderer(globeRef.current, fetchSky)
    }

    globeRendererRef.current.setLocation(request.latitude, request.longitude)
    fetchSky(request.latitude, request.longitude)
  }, [request])

  useEffect(() => {
    if (!skyData || !request || !rendererRef.current) return
    rendererRef.current.renderSky(
      skyData.constellations,
      skyData.stars,
      skyData.astronomy_time,
      request.latitude
    )
  }, [skyData])

  if (loading) return <div className="loading">Detecting location...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="app">
      <div
        className="sky-scene"
        ref={skyRef}
      // style={{ opacity: skyData ? 1 : 0, transition: 'opacity 1s ease' }}
      />
      <div className="map-panel"
        style={{
          opacity: skyData ? 1 : 0,
          transition: 'opacity 1s ease'
        }}
        ref={globeRef} />
    </div>
  )
}

export default App