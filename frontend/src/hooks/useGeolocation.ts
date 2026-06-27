import { useState, useEffect } from 'react'
import { ObserverRequest } from '@/types'


const DEFAULT_LOCATION: ObserverRequest = {
  latitude: 50.4501,
  longitude: 30.5234,
  observed_at: new Date().toISOString(),
}

interface GeolocationState {
  request: ObserverRequest | null
  error: string | null
  loading: boolean
}

export function useGeolocation(): GeolocationState {
  const [state, setState] = useState<GeolocationState>({
    request: null,
    error: null,
    loading: true,
  })

  useEffect(() => {
    if (!navigator.geolocation) {
      setState({ request: DEFAULT_LOCATION, error: null, loading: false })
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setState({
          request: {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            observed_at: new Date().toISOString(),
          },
          error: null,
          loading: false,
        })
      },
      () => {
        // permission denied or error — fallback to Kyiv
        setState({ request: DEFAULT_LOCATION, error: null, loading: false })
      }
    )
  }, [])

  return state
}