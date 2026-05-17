// Observer location and time
export interface ObserverRequest {
  latitude: number
  longitude: number
  observed_at: string // ISO format
}

// Single star data
export interface Star {
  hip: string
  name: string
  constellation_name: string
  ra: number
  dec: number
  mag: number
  alt: number
  az: number
}

// Constellation with stars and lines
export interface Constellation {
  id: string
  full_name: string
  lines: string[][]
}

// API response
export interface SkyResponse {
  constellations: Constellation[]
  stars: Star[]
  astronomy_time: number
}