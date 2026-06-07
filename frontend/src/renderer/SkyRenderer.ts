// src/renderer/SkyRenderer.ts
import * as THREE from 'three'
import { Constellation, Star } from '@/types'
import { CSS2DObject, CSS2DRenderer, EffectComposer, ImprovedNoise, PointerLockControls, RenderPass, UnrealBloomPass } from 'three/examples/jsm/Addons.js'
import Stats from 'stats.js'

class SkyRenderer {
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private renderer: THREE.WebGLRenderer
  private controls: PointerLockControls
  private starSphere: THREE.Group
  private _skyGroup: THREE.Group = new THREE.Group()

  private _milkyWayMaterial: THREE.ShaderMaterial | null = null
  private _tooltip: HTMLElement | null = null
  private _raycaster = new THREE.Raycaster()
  private _targetRotationY: number = 0
  private _targetRotationX: number = 0

  private labelRenderer: CSS2DRenderer
  private _constellationLines: Map<string, THREE.Line[]> = new Map()


  private readonly METEOR_INTERVAL_MS = { min: 2000, max: 3000 }
  private composer: EffectComposer
  private _crosshair: SVGElement | null = null
  private _starPositions: Array<{ position: THREE.Vector3, star: Star }> = []
  private _crosshairRadius: number = 10
  private _targetRadius: number = 10
  private _targetFov: number = 75
  private _currentFov: number = 75
  private _activeConstellationId: string | null = null


  private meteors: Array<{
    line: THREE.Points | THREE.Line
    velocity: THREE.Vector3
    opacity: number
    speed: number
  }> = []
  private readonly R: number = 1000
  private initialLstRad: number = 0
  private _twinklingMaterial: THREE.ShaderMaterial | null = null  // private observerLat: number = 0
  private stats: Stats

  constructor(container: HTMLElement) {
    this.scene = new THREE.Scene();

    this.stats = new Stats()
    this.stats.showPanel(0)
    document.body.appendChild(this.stats.dom)


    this.camera = new THREE.PerspectiveCamera(
      75,
      container.clientWidth / container.clientHeight,
      0.1,
      this.R * 2
    )

    this.renderer = new THREE.WebGLRenderer({ antialias: true })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    this.renderer.setSize(container.clientWidth, container.clientHeight)
    this.renderer.setClearColor(0x000000)
    container.appendChild(this.renderer.domElement)

    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1

    this.labelRenderer = new CSS2DRenderer()
    this.labelRenderer.setSize(container.clientWidth, container.clientHeight)
    this.labelRenderer.domElement.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      pointer-events: none;

    `

    container.appendChild(this.labelRenderer.domElement)


    this.composer = new EffectComposer(this.renderer)
    this.composer.addPass(new RenderPass(this.scene, this.camera))

    const bloomPass = new UnrealBloomPass(
      new THREE.Vector2(container.clientWidth / 2, container.clientHeight / 2),
      0.3,
      0.4,
      0.95
    )
    this.composer.addPass(bloomPass)

    this.controls = new PointerLockControls(this.camera, this.renderer.domElement)


    this.renderer.domElement.addEventListener('click', () => {
      this.controls.lock();
    });

    this.starSphere = new THREE.Group()
    this._skyGroup = new THREE.Group()

    this.setupLighting()
    this.setupSkyGradient()
    this.setupAtmosphericScattering()
    this.setupMilkyWay()
    this.setupBackgroundStars()
    this.setupTerrain()

    this.scene.add(this._skyGroup)
    this.scene.add(this.starSphere)

    this.setupTooltip(container)
    this.setupCrosshair(container)
    this.setupUI(container)
    const isMobile = /iPhone|iPad|Android/i.test(navigator.userAgent)

    if (isMobile) {
      this.setupTouchControls()
      this._crosshair!.style.transition = 'opacity 0.5s ease'
      this._crosshair!.style.opacity = '1'
    } else {
      this.setupStartOverlay(container)
    }
    this.setupMeteors()
    this.setupCompassPoints()

    this.renderer.setAnimationLoop((time) => this.animate(time))
  }

  private setupTouchControls(): void {
    let startX = 0
    let startY = 0

    this.renderer.domElement.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX
      startY = e.touches[0].clientY
    })

    this.renderer.domElement.addEventListener('touchmove', (e) => {
      const dx = e.touches[0].clientX - startX
      const dy = e.touches[0].clientY - startY

      this.theta -= dx * 0.005
      this.phi -= dy * 0.005
      this.phi = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.phi))

      this.camera.lookAt(
        Math.cos(this.phi) * Math.sin(this.theta),
        Math.sin(this.phi),
        Math.cos(this.phi) * Math.cos(this.theta),
      )

      startX = e.touches[0].clientX
      startY = e.touches[0].clientY
    })
  }
  private theta = 0
  private phi = 0


  private setupBackgroundStars(): void {
    const count = 5000
    const geometry = new THREE.BufferGeometry()
    const positions: number[] = []
    const sizes: number[] = []
    const randomOffsets: number[] = []

    for (let i = 0; i < count; i++) {
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(2 * Math.random() - 1)
      const r = this.R * 1.8

      positions.push(
        r * Math.sin(phi) * Math.cos(theta),
        r * Math.sin(phi) * Math.sin(theta),
        r * Math.cos(phi),
      )
      sizes.push(Math.random() * 1.5 + 0.5)
      randomOffsets.push(Math.random() * Math.PI * 2)

    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))
    geometry.setAttribute('offset', new THREE.Float32BufferAttribute(randomOffsets, 1))

    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
      },
      transparent: true,
      depthWrite: false,
      vertexShader: `
      attribute float size;
      attribute float offset;
      uniform float time;
      varying float vAlpha;

      void main() {
        float twinkle = 0.7 + 0.3 * sin(time * 2.0 + offset);
        vAlpha = twinkle;
        gl_PointSize = size * twinkle;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
      fragmentShader: `
      varying float vAlpha;

      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        float alpha = smoothstep(0.5, 0.3, d) * vAlpha;
        gl_FragColor = vec4(1.0, 1.0, 1.0, alpha);
      }
    `,
    })

    const stars = new THREE.Points(geometry, material)
    this._skyGroup.add(stars)

    this._twinklingMaterial = material
  }

  private setupTerrain(): void {
    const size = this.R * 2
    const segments = 128
    const geometry = new THREE.PlaneGeometry(size, size, segments, segments)

    // generate height map with Perlin noise
    const noise = new ImprovedNoise()
    const positions = geometry.attributes.position

    for (let i = 0; i < positions.count; i++) {
      const x = positions.getX(i)
      const z = positions.getY(i)

      // multiple octaves for realistic terrain
      const height =
        noise.noise(x / 200, z / 200, 0) * 60 +
        noise.noise(x / 80, z / 80, 0) * 25 +
        noise.noise(x / 30, z / 30, 0) * 10

      positions.setZ(i, height)
    }

    geometry.computeVertexNormals()

    const material = new THREE.MeshStandardMaterial({
      color: 0x1a2535,
      roughness: 0.9,
      metalness: 0.0,
      wireframe: false,
    })

    const terrain = new THREE.Mesh(geometry, material)
    terrain.rotation.x = -Math.PI / 2
    terrain.position.y = -10
    this.scene.add(terrain)
  }

  private setupLighting(): void {
    const ambientLight = new THREE.AmbientLight(0x111133, 0.3)
    this.scene.add(ambientLight)

    const moonLight = new THREE.DirectionalLight(0xc8d8ff, 0.6)
    moonLight.position.set(-300, 200, 100)
    this.scene.add(moonLight)

    const horizonLight = new THREE.HemisphereLight(
      0x1a1a3a,
      0x0a0a1a,
      0.4
    )
    this.scene.add(horizonLight)
  }

  private _renderTimeout: number = 0

  renderSky(
    constellations: Constellation[],
    stars: Star[],
    lst: number,
    observerLat: number
  ): void {
    this._targetRotationY = -this.initialLstRad

    this._targetRotationX = Math.PI / 2 - THREE.MathUtils.degToRad(observerLat)

    // this.observerLat = observerLat

    // tilt sphere axis by observer latitude
    // this.starSphere.rotation.x = Math.PI / 2 - THREE.MathUtils.degToRad(observerLat)
    clearTimeout(this._renderTimeout);
    // this._renderTimeout = window.setTimeout(() => { ... }, 800);

    this._renderTimeout = window.setTimeout(() => {
      this.initialLstRad = THREE.MathUtils.degToRad(lst)
      this.clearSphere()
      this.renderStars(stars)
      this.renderConstellationLines(constellations, stars)
      this.renderConstellationLabels(constellations, stars)
    }, 800)

  }

  private renderStars(stars: Star[]): void {
    const geometry = new THREE.BufferGeometry()
    const positions: number[] = []
    const sizes: number[] = []

    stars.forEach(star => {
      const pos = this.equatorialToXYZ(star.ra, star.dec)
      const vec = new THREE.Vector3(pos.x, pos.y, pos.z)
      this._starPositions.push({ position: vec, star })

      positions.push(pos.x, pos.y, pos.z)
      sizes.push(Math.max(2, 8 - star.mag))
    })

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))

    const material = new THREE.ShaderMaterial({
      uniforms: {},
      transparent: true,
      vertexShader: `
    attribute float size;
    void main() {
      gl_PointSize = size;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
      fragmentShader: `
    void main() {
      float distance = length(gl_PointCoord - vec2(0.5));
      
      if (distance > 0.5) {
        discard;
      }
      
      float alpha = smoothstep(0.5, 0.45, distance);
      
      gl_FragColor = vec4(1.0, 1.0, 1.0, alpha);
    }
  `,
    })


    this.starSphere.add(new THREE.Points(geometry, material))
  }

  private setupSkyGradient(): void {
    const geometry = new THREE.SphereGeometry(this.R * 1.9, 32, 32)
    const material = new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {},
      vertexShader: `
      varying vec3 vPosition;
      void main() {
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
      fragmentShader: `
      varying vec3 vPosition;
      void main() {
        float h = normalize(vPosition).y;
        vec3 zenith = vec3(0.0, 0.0, 0.02);
        vec3 horizon = vec3(0.02, 0.04, 0.08);
        vec3 color = mix(horizon, zenith, max(h, 0.0));
        gl_FragColor = vec4(color, 1.0);
      }
    `,
    })
    this.scene.add(new THREE.Mesh(geometry, material))
  }

  private renderConstellationLines(constellations: Constellation[], stars: Star[]): void {
    const starMap = new Map(stars.map(s => [s.hip, s]))

    constellations.forEach(constellation => {
      const lines: THREE.Line[] = []

      constellation.lines.forEach(line => {
        const points: THREE.Vector3[] = []
        const colors: number[] = []

        line.forEach((hip, index) => {
          const star = starMap.get(hip)
          if (star) {
            const { x, y, z } = this.equatorialToXYZ(star.ra, star.dec)
            points.push(new THREE.Vector3(x, y, z))
            const t = index / (line.length - 1)
            const brightness = 0.3 + 0.7 * (1 - Math.abs(t - 0.5) * 2)
            colors.push(0.4 * brightness, 0.6 * brightness, 1.0 * brightness)
          }
        })

        if (points.length >= 2) {
          const geometry = new THREE.BufferGeometry().setFromPoints(points)
          geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3))

          const material = new THREE.LineBasicMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 0,
            blending: THREE.AdditiveBlending,

          })

          const lineMesh = new THREE.Line(geometry, material)
          this.starSphere.add(lineMesh)
          lines.push(lineMesh)
        }
      })

      this._constellationLines.set(constellation.id, lines)
    })
  }

  private renderConstellationLabels(constellations: Constellation[], stars: Star[]): void {
    const starMap = new Map(stars.map(s => [s.hip, s]))

    constellations.forEach(constellation => {
      const positions: THREE.Vector3[] = []

      constellation.lines.forEach(line => {
        line.forEach(hip => {
          const star = starMap.get(hip)
          if (star) {
            const { x, y, z } = this.equatorialToXYZ(star.ra, star.dec)
            positions.push(new THREE.Vector3(x, y, z))
          }
        })
      })

      if (positions.length === 0) return

      const center = positions.reduce(
        (acc, p) => acc.add(p),
        new THREE.Vector3()
      ).divideScalar(positions.length)

      const label = document.createElement('div')
      label.style.cssText = `
      color: rgba(150, 200, 255, 0.6);
      font-family: monospace;
      font-size: 11px;
      letter-spacing: 2px;
      pointer-events: none;
      text-shadow: 0 0 8px rgba(100, 150, 255, 0.8);
    `
      label.textContent = constellation.full_name

      const cssObject = new CSS2DObject(label)
      cssObject.position.copy(center)
      this.starSphere.add(cssObject)
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
    this._starPositions = [];

    const labels = this.starSphere.domElement?.querySelectorAll('.sky-scene');
    labels?.forEach(label => label.remove());

    this.starSphere.traverse((object) => {
      if (object instanceof THREE.Points || object instanceof THREE.Mesh) {

        if (object.geometry) {
          object.geometry.dispose();
        }

        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach((material) => material.dispose());
          } else {
            object.material.dispose();
          }
        }
      }
    });

    while (this.starSphere.children.length > 0) {
      const child = this.starSphere.children[0];
      this.starSphere.remove(child);
    }
  }


  private animate(time: number): void {
    this.stats.begin();

    const timeInSeconds = time * 0.001;

    this._frameCount++;

    if (this._frameCount % 5 === 0) {
      this.checkStarHover();
    }

    this.animateCrosshair();
    this.animateZoom();
    this.updateMeteors();
    this.updateConstellationLines();
    this.animateSphere();

    if (this._twinklingMaterial) {
      this._twinklingMaterial.uniforms['time'].value = timeInSeconds;
    }
    if (this._milkyWayMaterial) {
      this._milkyWayMaterial.uniforms['time'].value = timeInSeconds;
    }

    this.composer.render();
    this.labelRenderer.render(this.scene, this.camera);

    this.stats.end();
  }


  private setupMilkyWay(): void {
    const count = 15000
    const geometry = new THREE.BufferGeometry()
    const positions: number[] = []
    const sizes: number[] = []
    const offsets: number[] = []

    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2

      const u = Math.random()
      const v = Math.random()
      const spread = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
      const diskRadius = Math.abs(spread) * 0.15
      const diskHeight = (Math.random() - 0.5) * 0.04
      const x = Math.cos(angle) * diskRadius
      const y = diskHeight
      const z = Math.sin(angle) * diskRadius

      const tiltAngle = Math.PI * 0.35
      const tiltedY = y * Math.cos(tiltAngle) - z * Math.sin(tiltAngle)
      const tiltedZ = y * Math.sin(tiltAngle) + z * Math.cos(tiltAngle)

      const dir = new THREE.Vector3(x, tiltedY, tiltedZ).normalize()
      const r = this.R * 1.75

      positions.push(dir.x * r, dir.y * r, dir.z * r)
      sizes.push(Math.random() * 0.8 + 0.2)
      offsets.push(Math.random() * Math.PI * 2)


    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))
    geometry.setAttribute('offset', new THREE.Float32BufferAttribute(offsets, 1))

    const material = new THREE.ShaderMaterial({
      uniforms: {
        time: { value: 0 },
      },
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexShader: `
      attribute float size;
      attribute float offset;
      uniform float time;
      varying float vAlpha;

      void main() {
        float twinkle = 0.6 + 0.4 * sin(time * 1.5 + offset);
        vAlpha = twinkle;
        gl_PointSize = size * twinkle;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
      fragmentShader: `
      varying float vAlpha;
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        vec3 color = mix(vec3(0.6, 0.75, 1.0), vec3(1.0, 1.0, 1.0), vAlpha);
        float glow = exp(-d * d * 4.0);
        float alpha = glow * vAlpha * 0.8;
        gl_FragColor = vec4(color * 1.5, alpha);
      }
    `,
    })

    const milkyWay = new THREE.Points(geometry, material)
    this._skyGroup.add(milkyWay)

    this._milkyWayMaterial = material
  }

  private setupMeteors(): void {
    const spawn = () => {
      this.spawnMeteor()
      setTimeout(spawn, Math.random() *
        (this.METEOR_INTERVAL_MS.max - this.METEOR_INTERVAL_MS.min) +
        this.METEOR_INTERVAL_MS.min
      )
    }
    spawn()
  }

  private spawnMeteor(): void {
    const points = 20
    const positions: number[] = []
    const alphas: number[] = []

    const theta = Math.random() * Math.PI * 2
    const phi = Math.random() * Math.PI * 0.4
    const r = this.R * 1.7

    const start = new THREE.Vector3(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.sin(phi) * Math.sin(theta),
      r * Math.cos(phi),
    )

    const direction = new THREE.Vector3(
      (Math.random() - 0.5) * 0.3,
      -Math.random() * 0.4 - 0.1,
      (Math.random() - 0.5) * 0.3,
    ).normalize()

    const length = Math.random() * 150 + 80

    for (let i = 0; i < points; i++) {
      const t = i / points
      const point = start.clone().add(direction.clone().multiplyScalar(t * length))
      positions.push(point.x, point.y, point.z)
      alphas.push(t)
    }

    const geometry = new THREE.BufferGeometry()
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
    geometry.setAttribute('alpha', new THREE.Float32BufferAttribute(alphas, 1))

    const material = new THREE.ShaderMaterial({
      transparent: true,
      depthWrite: false,
      uniforms: { opacity: { value: 1.0 } },
      vertexShader: `
  attribute float alpha;
  varying float vAlpha;
  uniform float opacity;
  void main() {
    vAlpha = alpha * opacity;
    gl_PointSize = vAlpha * 6.0 + 2.0; 
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`,
      fragmentShader: `
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - vec2(0.5));
  
    float blur = exp(-d * d * 8.0);
    gl_FragColor = vec4(1.0, 1.0, 1.0, vAlpha * blur);
  }
`,
    })

    const meteor = new THREE.Points(geometry, material)
    this.scene.add(meteor)

    this.meteors.push({
      line: meteor as unknown as THREE.Line,
      velocity: direction.multiplyScalar(Math.random() * 3 + 1),
      speed: Math.random() * 0.6 + 0.2,
      opacity: 1.0,
    })
  }

  private updateMeteors(): void {
    this.meteors = this.meteors.filter(meteor => {
      meteor.opacity -= 0.015 * meteor.speed

      const mat = meteor.line.material as THREE.ShaderMaterial
      mat.uniforms['opacity'].value = meteor.opacity

      meteor.line.position.addScaledVector(meteor.velocity, 0.016)

      if (meteor.opacity <= 0) {
        this.scene.remove(meteor.line)
        return false
      }
      return true
    })
  }

  private setupAtmosphericScattering(): void {
    const geometry = new THREE.SphereGeometry(this.R * 1.85, 64, 32)
    const material = new THREE.ShaderMaterial({
      side: THREE.BackSide,
      depthWrite: false,
      uniforms: {},
      vertexShader: `
      varying vec3 vPosition;
      void main() {
        vPosition = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
      fragmentShader: `
  varying vec3 vPosition;
  void main() {
    float h = normalize(vPosition).y;

    vec3 horizon = vec3(0.15, 0.12, 0.25);
    vec3 horizonGlow = vec3(0.3, 0.15, 0.05);
    vec3 zenith = vec3(0.0, 0.0, 0.0);

    float horizonFactor = exp(-abs(h) * 8.0);       
    float glowFactor = exp(-abs(h + 0.1) * 12.0);   

    vec3 color = mix(zenith, horizon, horizonFactor);  
color += horizonGlow * glowFactor * 0.2;  // ← 0.8 → 0.4
float alpha = horizonFactor * 0.2;               

    gl_FragColor = vec4(color, alpha);
  }
`,
    })

    this.scene.add(new THREE.Mesh(geometry, material))
  }
  private setupCrosshair(container: HTMLElement): void {
    const crosshair = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    crosshair.style.cssText = `
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    pointer-events: none;
    z-index: 10;
    opacity: 0;
    width: 32px;
    height: 32px;
  `
    crosshair.innerHTML = `
    <circle 
      cx="16" cy="16" r="10" 
      fill="none" 
      stroke="rgba(255,255,255,0.8)" 
      stroke-width="0.8"
      filter="url(#glow)"
    />
    <circle cx="16" cy="16" r="1.5" fill="rgba(255,255,255,0.9)"/>
    <defs>
      <filter id="glow">
        <feGaussianBlur stdDeviation="1" result="blur"/>
        <feMerge>
          <feMergeNode in="blur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
  `

    container.style.position = 'relative'
    container.appendChild(crosshair)
    this._crosshair = crosshair
  }
  private setupTooltip(container: HTMLElement): void {
    const tooltip = document.createElement('div')
    tooltip.style.cssText = `
    position: absolute;
    display: none;
    pointer-events: none;
    z-index: 20;
    color: rgba(255, 255, 255, 0.9);
    font-family: monospace;
    font-size: 12px;
    background: rgba(0, 10, 30, 0.7);
    border: 0.5px solid rgba(100, 150, 255, 0.4);
    border-radius: 4px;
    padding: 8px 12px;
    backdrop-filter: blur(4px);
    letter-spacing: 0.5px;
    line-height: 1.6;
    min-width: 140px;
  `
    container.appendChild(tooltip)
    this._tooltip = tooltip
  }
  private _frameCount: number = 0

  private checkStarHover(): void {
    if (!this._tooltip) return

    const center = new THREE.Vector2(0, 0)
    this._raycaster.setFromCamera(center, this.camera)

    let closestStar: Star | null = null
    let closestDistance = Infinity
    const threshold = 15

    this._starPositions.forEach(({ position, star }) => {
      const projected = position.clone()
      projected.applyMatrix4(this.starSphere.matrixWorld)
      projected.project(this.camera)

      const dx = projected.x
      const dy = projected.y
      const dist = Math.sqrt(dx * dx + dy * dy) * window.innerWidth / 2

      if (dist < threshold && dist < closestDistance && projected.z < 1) {
        closestDistance = dist
        closestStar = star
      }
    })

    if (closestStar) {
      const star = closestStar as Star

      this._tooltip.style.display = 'block'
      this._tooltip.style.left = '50%'
      this._tooltip.style.top = '45%'
      this._tooltip.style.transform = 'translate(-50%, -100%)'
      this._tooltip.innerHTML = `
      <div style="color: rgba(150,200,255,0.9); margin-bottom: 4px;">
        ✦ ${star.name || 'Unknown'}
      </div>
      <div>mag: ${star.mag.toFixed(2)}</div>
      <div>ra: ${star.ra.toFixed(3)}h</div>
      <div>dec: ${star.dec.toFixed(2)}°</div>
      <div>az: ${star.az.toFixed(2)}°</div>
    `

      if (this._crosshair) {
        this._targetRadius = 14
        this._targetFov = 65
      }

      this._activeConstellationId = star.constellation_name
    } else {
      this._activeConstellationId = null

      this._tooltip.style.display = 'none'
      if (this._crosshair) {
        this._targetRadius = 10
        this._targetFov = 75
      }
    }
  }
  private animateCrosshair(): void {
    this._crosshairRadius += (this._targetRadius - this._crosshairRadius) * 0.1

    if (this._crosshair) {
      const circle = this._crosshair.querySelector('circle')
      if (circle) circle.setAttribute('r', this._crosshairRadius.toFixed(1))
    }
  }
  private animateZoom(): void {
    this._currentFov += (this._targetFov - this._currentFov) * 0.05
    this.camera.fov = this._currentFov
    this.camera.updateProjectionMatrix()
  }

  private updateConstellationLines(): void {
    this._constellationLines.forEach((lines, id) => {
      const isActive = id === this._activeConstellationId
      const targetOpacity = isActive ? 0.9 : 0

      lines.forEach(line => {
        const mat = line.material as THREE.LineBasicMaterial
        mat.opacity += (targetOpacity - mat.opacity) * 0.2
      })
    })
  }

  private animateSphere(): void {
    let diffY = this._targetRotationY - this.starSphere.rotation.y
    while (diffY > Math.PI) diffY -= Math.PI * 2
    while (diffY < -Math.PI) diffY += Math.PI * 2
    this.starSphere.rotation.y += diffY * 0.05

    let diffX = this._targetRotationX - this.starSphere.rotation.x
    this.starSphere.rotation.x += diffX * 0.05

    this._skyGroup.rotation.y = this.starSphere.rotation.y
    this._skyGroup.rotation.x = this.starSphere.rotation.x
  }

  private setupStartOverlay(container: HTMLElement): void {
    const overlay = document.createElement('div')
    overlay.style.cssText = `
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,1);
    z-index: 100;
    cursor: pointer;
    color: rgba(255,255,255,0.8);
    font-family: monospace;
    font-size: 14px;
    letter-spacing: 2px;
  `
    overlay.textContent = 'CLICK TO EXPLORE'
    overlay.addEventListener('click', () => {
      this.controls.lock()

      overlay.style.transition = 'opacity 0.8s ease'
      overlay.style.opacity = '0'

      setTimeout(() => {
        overlay.remove()
        if (this._crosshair) {
          this._crosshair.style.transition = 'opacity 0.5s ease'
          this._crosshair.style.opacity = '1'
        }
      }, 800)
    })
    container.appendChild(overlay)
  }

  private setupCompassPoints(): void {
    const directions = [
      { label: 'N', az: 0 },
      { label: 'E', az: 90 },
      { label: 'S', az: 180 },
      { label: 'W', az: 270 },
    ]

    directions.forEach(({ label, az }) => {
      const azRad = THREE.MathUtils.degToRad(az)
      const r = this.R * 1.5

      const x = r * Math.sin(azRad)
      const y = -10
      const z = -r * Math.cos(azRad)

      const div = document.createElement('div')
      div.style.cssText = `
  color: rgba(255, 255, 255, 0.9);
  font-family: monospace;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 4px;
  pointer-events: none;
  text-shadow: 
    0 0 10px rgba(100, 180, 255, 1.0),
    0 0 20px rgba(100, 180, 255, 0.6),
    0 0 40px rgba(100, 180, 255, 0.3);
  padding: 4px 8px;
  background: rgba(0, 10, 30, 0.4);
  backdrop-filter: blur(4px);
`
      div.textContent = label

      const cssObject = new CSS2DObject(div)
      cssObject.position.set(x, y, z)
      this.scene.add(cssObject)
    })
  }

  private setupUI(container: HTMLElement): void {
    const title = document.createElement('div')
    title.style.cssText = `
    position: absolute;
    top: 24px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255, 255, 255, 0.8);
    font-family: monospace;
    font-size: 13px;
    letter-spacing: 4px;
    text-transform: uppercase;
    pointer-events: none;
    text-shadow: 0 0 20px rgba(100, 180, 255, 0.6);
    z-index: 10;
  `
    title.textContent = 'Star Compass'
    container.appendChild(title)

    const tutorial = document.createElement('div')
    tutorial.style.cssText = `
    position: absolute;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    color: rgba(255, 255, 255, 0.4);
    font-family: monospace;
    font-size: 11px;
    letter-spacing: 2px;
    pointer-events: none;
    text-align: center;
    line-height: 1.8;
    z-index: 10;
    transition: opacity 2s ease;
  `
    tutorial.innerHTML = `
    move to look around &nbsp;·&nbsp; hover stars for info<br>
    select location on globe
  `
    container.appendChild(tutorial)
  }

}

export default SkyRenderer