// src/renderer/SkyRenderer.ts
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { Constellation, Star } from '@/types'

class SkyRenderer {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private controls: OrbitControls
  private starSphere: THREE.Group
  private readonly R: number = 1000
  private initialLstRad: number = 0
  // private observerLat: number = 0

  constructor(container: HTMLElement) {
    this.scene = new THREE.Scene()

    this.camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      2000
    )
    this.camera.position.set(0, 20, 0.1)

    this.renderer = new THREE.WebGLRenderer({ antialias: true })
    this.renderer.setSize(container.clientWidth, container.clientHeight)
    this.renderer.setClearColor(0x000000)
    container.appendChild(this.renderer.domElement)

    this.controls = new OrbitControls(this.camera, this.renderer.domElement)
    this.controls.enableZoom = false
    this.controls.enablePan = false
    this.controls.target.set(0, 20, 0)

    this.starSphere = new THREE.Group()

    const horizonGeometry = new THREE.CircleGeometry(this.R - 10, 64);
    const horizonMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x111111, 
        side: THREE.DoubleSide,
        transparent: false,
        opacity: 0.8 
    });
    const horizon = new THREE.Mesh(horizonGeometry, horizonMaterial);
    horizon.rotation.x = Math.PI / 2; 
    horizon.position.y = -20
    this.scene.add(horizon); // Додаємо в SCENE, а не в starSphere, бо горизонт НЕ крутиться разом із Землею!


    this.scene.add(this.starSphere)
    // this.setupScene()

    this.animate()
  }

  renderSky(
    constellations: Constellation[],
    stars: Star[],
    lst: number,
    // observerLat: number
  ): void {
    this.clearSphere()

    // this.observerLat = observerLat
    this.initialLstRad = THREE.MathUtils.degToRad(lst)

    // tilt sphere axis by observer latitude
    // this.starSphere.rotation.x = Math.PI / 2 - THREE.MathUtils.degToRad(observerLat)
    this.starSphere.rotation.y = -this.initialLstRad

    this.renderStars(stars)
    this.renderConstellationLines(constellations, stars)
  }

  private setupScene(): void {
    const gridMaterial = new THREE.LineBasicMaterial({
      color: 0x00ffcc,
      transparent: true,
      opacity: 0.3,
    })

    const createGridCircle = (radius: number, segments: number = 128): THREE.LineLoop => {
      const points: THREE.Vector3[] = []
      for (let i = 0; i <= segments; i++) {
        const theta = (i / segments) * Math.PI * 2
        points.push(new THREE.Vector3(Math.cos(theta) * radius, 0, Math.sin(theta) * radius))
      }
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      return new THREE.LineLoop(geometry, gridMaterial)
    }

    // celestial equator — rotates with stars
    const celestialEquator = createGridCircle(this.R)
    this.scene.add(celestialEquator)

    // local meridian — fixed, does not rotate
    const localMeridian = createGridCircle(this.R)
    localMeridian.rotation.x = Math.PI / 2
    this.scene.add(localMeridian)

    const localMeridian2 = createGridCircle(this.R)
    localMeridian2.rotation.z = Math.PI / 2
    this.scene.add(localMeridian2)
  }

private renderStars(stars: Star[]): void {
  const geometry = new THREE.BufferGeometry()
  const positions: number[] = []
  const sizes: number[] = []

  stars.forEach(star => {
    const { x, y, z } = this.equatorialToXYZ(star.ra, star.dec)
    positions.push(x, y, z)
    sizes.push(Math.max(1, 6 - star.mag))
  })

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
  geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))

  const material = new THREE.ShaderMaterial({
    uniforms: {},
    vertexShader: `
      attribute float size;
      void main() {
        gl_PointSize = size;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      void main() {
        gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
      }
    `,
  })

  this.starSphere.add(new THREE.Points(geometry, material))
}

  private renderConstellationLines(constellations: Constellation[], stars: Star[]): void {
    const starMap = new Map(stars.map((s) => {
      return [s.hip, s]
    }))
    const lineMaterial = new THREE.LineBasicMaterial({
      color: 0x4444ff,
      transparent: true,
      opacity: 0.4,
    })

    console.log(constellations, stars)

    constellations.forEach(constellation => {
      constellation.lines.forEach(line => {
        const points: THREE.Vector3[] = []

        line.forEach(hip => {

          const star = starMap.get(hip)
          if (star) {
            const { x, y, z } = this.equatorialToXYZ(star.ra, star.dec)
            points.push(new THREE.Vector3(x, y, z))
          }
          if (!star) {
          console.log("missing star")
          console.log(hip)
          console.log(star)
          console.log(starMap)
      }
        })

        if (points.length >= 2) {
          const geometry = new THREE.BufferGeometry().setFromPoints(points)
          this.starSphere.add(new THREE.Line(geometry, lineMaterial))
        }
      })
    })
  }

  private equatorialToXYZ(ra: number, dec: number): { x: number; y: number; z: number } {
    // ra is in hours (0-24), convert to radians
    const raRad = THREE.MathUtils.degToRad(ra * 15)  // 1 hour = 15 degrees
    const decRad = THREE.MathUtils.degToRad(dec)

    return {
      x: this.R * Math.cos(decRad) * Math.cos(raRad),
      y: this.R * Math.sin(decRad),
      z: this.R * Math.cos(decRad) * Math.sin(raRad),
    }
  }

  updateTime(hoursElapsed: number): void {
    const angleDelta = THREE.MathUtils.degToRad(hoursElapsed * 15)
    this.starSphere.rotation.y = -this.initialLstRad - angleDelta
  }

  private clearSphere(): void {
    while (this.starSphere.children.length > 0) {
      this.starSphere.remove(this.starSphere.children[0])
    }
  }

  private animate(): void {
    requestAnimationFrame(() => this.animate())
    this.controls.update()
    this.renderer.render(this.scene, this.camera)
  }
}

export default SkyRenderer