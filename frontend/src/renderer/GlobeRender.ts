// src/renderer/GlobeRenderer.ts
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

class GlobeRenderer {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private globe: THREE.Mesh
  private marker: THREE.Mesh | null = null
  private onLocationSelect: (lat: number, lng: number) => void

  constructor(
    container: HTMLElement,
    onLocationSelect: (lat: number, lng: number) => void
  ) {
    this.onLocationSelect = onLocationSelect

    this.scene = new THREE.Scene()
    this.camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000)
    this.camera.position.set(0, 0, 3)

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    this.renderer.setSize(container.clientWidth, container.clientHeight)
    this.renderer.setClearColor(0x000000, 0)
    container.appendChild(this.renderer.domElement)

    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableZoom = false
    this.controls.enablePan = false
    this.controls.autoRotate = true
    this.controls.autoRotateSpeed = 0.5

    const geometry = new THREE.SphereGeometry(1, 128, 128)
    const textureLoader = new THREE.TextureLoader()
    const texture = textureLoader.load('/2k_earth_nightmap.jpg')
    const nightTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_lights_2048.png')

    const material = new THREE.MeshPhongMaterial({
      map: texture,
      emissiveMap: nightTexture,
      emissive: new THREE.Color(0x112244),
      emissiveIntensity: 0.8,
      specular: new THREE.Color(0x333333),
      shininess: 15,
    })

    this.globe = new THREE.Mesh(geometry, material)
    this.globe.rotation.y = -Math.PI / 2
    this.scene.add(this.globe)

    const atmosGeometry = new THREE.SphereGeometry(1.02, 64, 64)
    const atmosMaterial = new THREE.MeshPhongMaterial({
      color: 0x4488ff,
      transparent: true,
      opacity: 0.08,
      side: THREE.FrontSide,
    })
    this.scene.add(new THREE.Mesh(atmosGeometry, atmosMaterial))

    const ambientLight = new THREE.AmbientLight(0xffffff, 2)
    this.scene.add(ambientLight)

    this.setupClickHandler(container)
    this.animate()
  }

  private _mouseDownTime = 0

  private setupClickHandler(container: HTMLElement): void {
    const raycaster = new THREE.Raycaster()
    const mouse = new THREE.Vector2()

    container.addEventListener('mousedown', () => {
      this._mouseDownTime = Date.now()
    })

    container.addEventListener('click', (e) => {
      if (Date.now() - this._mouseDownTime > 200) {
        this._mouseDownTime = 0
        return
      }

      const rect = container.getBoundingClientRect()
      mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1
      mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1

      raycaster.setFromCamera(mouse, this.camera)
      const intersects = raycaster.intersectObject(this.globe)

      if (intersects.length > 0) {
        const point = intersects[0].point

        const lat = Math.asin(point.y) * (180 / Math.PI)
        const lng = Math.atan2(point.x, point.z) * (180 / Math.PI)

        this.placeMarker(lat, lng)
        this.onLocationSelect(lat, lng)
      }
    })
  }

  private placeMarker(lat: number, lng: number): void {
    if (this.marker) this.scene.remove(this.marker)

    console.log('placing marker at:', lat, lng)


    const latRad = lat * (Math.PI / 180)
    const lngRad = lng * (Math.PI / 180)

    const x = Math.cos(latRad) * Math.sin(lngRad)
    const y = Math.sin(latRad)
    const z = Math.cos(latRad) * Math.cos(lngRad)
    console.log('xyz:', x, y, z)

    const geometry = new THREE.SphereGeometry(0.05, 16, 16)
    const material = new THREE.MeshBasicMaterial({
      color: 0x88bbff,
      transparent: true,
      opacity: 0.8,
    })

    this.marker = new THREE.Mesh(geometry, material)
    this.marker.position.set(x, y, z)
    this.marker.lookAt(0, 0, 0)
    this.scene.add(this.marker)
  }

  setLocation(lat: number, lng: number): void {
    console.log(lat, lng)
    this.placeMarker(lat, lng)
  }

  private animate(): void {
    requestAnimationFrame(() => this.animate())
    this.controls.update()
    this.renderer.render(this.scene, this.camera)
  }
}

export default GlobeRenderer