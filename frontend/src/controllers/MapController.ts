interface MapControllerOptions {
  container: HTMLElement
  onLocationSelect: (lat: number, lng: number) => void
}

interface ImportMetaEnv {
  readonly VITE_GOOGLE_MAPS_API_KEY: string
  readonly VITE_GOOGLE_MAP_ID: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

class MapController {
    private map: google.maps.Map | null = null
    private marker: google.maps.marker.AdvancedMarkerElement | null = null
    private readonly options: MapControllerOptions

    constructor(options: MapControllerOptions) {
        this.options = options
    }

    async initialize(lat: number, lng: number): Promise<void> {
    this.map = new google.maps.Map(this.options.container, {
    center: { lat, lng },
    zoom: 10,
    mapId: import.meta.env.VITE_GOOGLE_MAP_ID,
    colorScheme: "DARK",
    disableDefaultUI: true,
    })

        this.placeMarker(lat, lng)

        this.map.addListener('click', (e: google.maps.MapMouseEvent) => {
        if (e.latLng) {
            this.placeMarker(e.latLng.lat(), e.latLng.lng())
            this.options.onLocationSelect(e.latLng.lat(), e.latLng.lng())
        }
        })
    }

        private placeMarker(lat: number, lng: number): void {
        if (this.marker) this.marker.map = null

        this.marker = new google.maps.marker.AdvancedMarkerElement({
            position: { lat, lng },
            map: this.map!,
        })
        }
}

export default MapController