// src/api/ApiClient.ts
import { ObserverRequest, SkyResponse } from '@/types'

interface ApiClientInterface {
  getSky(request: ObserverRequest): Promise<SkyResponse>
}

class ApiClient implements ApiClientInterface {
  private readonly baseUrl: string = '/api'

  private buildUrlParams(request: ObserverRequest): URLSearchParams {
    return new URLSearchParams({
      latitude: request.latitude.toString(),
      longitude: request.longitude.toString(),
      observed_at: request.observed_at,
    })
  }

  private buildApiUrl(request: ObserverRequest): string {
    return `${this.baseUrl}/sky?${this.buildUrlParams(request)}`
  }

  async getSky(request: ObserverRequest): Promise<SkyResponse> {
    const url: string = this.buildApiUrl(request)
    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`)
    }

    return response.json()
  }
}

export const apiClient = new ApiClient()