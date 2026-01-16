import { FilesetResolver, HandLandmarker } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3";

class HandArtApp {
    constructor() {
        this.video = document.getElementById('webcam');
        this.canvas = document.getElementById('canvas-webgl');
        this.overlay = document.getElementById('overlay');
        this.loader = document.getElementById('loader');
        this.startBtn = document.getElementById('start-btn');

        this.handLandmarker = null;
        this.runningMode = "VIDEO";
        this.lastVideoTime = -1;

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.particles = null;

        this.init();
    }

    async init() {
        await this.setupHandDetection();
        this.setupThreeJS();
        this.setupUI();
        this.animate();
    }

    setupUI() {
        this.startBtn.addEventListener('click', () => {
            this.enableCam();
        });
    }

    async enableCam() {
        if (!this.handLandmarker) {
            console.log("Esperando a que el landmarker cargue...");
            return;
        }

        const constraints = {
            video: true
        };

        try {
            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = stream;
            this.video.addEventListener('loadeddata', () => {
                this.overlay.classList.add('hidden');
            });
        } catch (err) {
            console.error("Error al acceder a la cámara:", err);
            this.loader.innerText = "ERROR DE CÁMARA: " + err.message;
        }
    }

    async setupHandDetection() {
        const vision = await FilesetResolver.forVisionTasks(
            "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
        );
        this.handLandmarker = await HandLandmarker.createFromOptions(vision, {
            baseOptions: {
                modelAssetPath: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task`,
                delegate: "GPU"
            },
            runningMode: this.runningMode,
            numHands: 2
        });

        this.loader.innerText = "SISTEMA LISTO";
        this.startBtn.style.display = "block";
    }

    setupThreeJS() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.z = 5;

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Background dark glow
        this.scene.background = new THREE.Color(0x000000);

        // Initial setup for particles (placeholder)
        this.createParticleSystem();

        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    createParticleSystem() {
        const geometry = new THREE.BufferGeometry();
        this.particleCount = 15000;
        const positions = new Float32Array(this.particleCount * 3);
        const velocities = new Float32Array(this.particleCount * 3);
        const colors = new Float32Array(this.particleCount * 3);
        const sizes = new Float32Array(this.particleCount);

        const color = new THREE.Color();

        for (let i = 0; i < this.particleCount; i++) {
            // Random positions in a sphere
            const r = 5 * Math.pow(Math.random(), 0.5);
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);

            positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            positions[i * 3 + 2] = r * Math.cos(phi);

            velocities[i * 3] = (Math.random() - 0.5) * 0.02;
            velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.02;
            velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.02;

            color.setHSL(0.5 + Math.random() * 0.2, 0.8, 0.5);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;

            sizes[i] = Math.random() * 2.0;
        }

        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('velocity', new THREE.BufferAttribute(velocities, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1));

        this.particleMaterial = new THREE.ShaderMaterial({
            uniforms: {
                uTime: { value: 0 },
                uPointSize: { value: 2.0 }
            },
            vertexShader: `
                attribute float size;
                attribute vec3 velocity;
                varying vec3 vColor;
                uniform float uTime;
                void main() {
                    vColor = color;
                    vec3 pos = position + velocity * uTime * 50.0;
                    vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
                    gl_PointSize = size * (300.0 / -mvPosition.z);
                    gl_Position = projectionMatrix * mvPosition;
                }
            `,
            fragmentShader: `
                varying vec3 vColor;
                void main() {
                    float d = distance(gl_PointCoord, vec2(0.5));
                    if (d > 0.5) discard;
                    float strength = 1.0 - (d * 2.0);
                    gl_FragColor = vec4(vColor, strength);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
            vertexColors: true
        });

        this.particles = new THREE.Points(geometry, this.particleMaterial);
        this.scene.add(this.particles);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const time = performance.now() * 0.001;
        if (this.particleMaterial) {
            this.particleMaterial.uniforms.uTime.value = time;
        }

        if (this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
            let startTimeMs = performance.now();
            if (this.lastVideoTime !== this.video.currentTime) {
                this.lastVideoTime = this.video.currentTime;
                const results = this.handLandmarker.detectForVideo(this.video, startTimeMs);
                this.processResults(results);
            }
        }

        this.renderer.render(this.scene, this.camera);
    }

    processResults(results) {
        if (!results.landmarks || results.landmarks.length === 0) return;

        const positions = this.particles.geometry.attributes.position.array;
        const velocities = this.particles.geometry.attributes.velocity.array;
        const count = this.particleCount;

        results.landmarks.forEach((hand, handIndex) => {
            const thumbTip = hand[4];
            const indexTip = hand[8];
            const middleTip = hand[12];

            // Calculate "pinch" distance
            const dx_pinch = thumbTip.x - indexTip.x;
            const dy_pinch = thumbTip.y - indexTip.y;
            const dz_pinch = thumbTip.z - indexTip.z;
            const pinchDist = Math.sqrt(dx_pinch ** 2 + dy_pinch ** 2 + dz_pinch ** 2);

            // Calculate "open hand" (average distance from palm to tips)
            const palm = hand[0];
            const fingerTips = [hand[4], hand[8], hand[12], hand[16], hand[20]];
            let avgDist = 0;
            fingerTips.forEach(tip => {
                avgDist += Math.sqrt((tip.x - palm.x) ** 2 + (tip.y - palm.y) ** 2);
            });
            avgDist /= 5;

            const targetX = (0.5 - indexTip.x) * 10;
            const targetY = (0.5 - indexTip.y) * 10;
            const targetZ = -indexTip.z * 10;

            // Explosion trigger: if pinch is very close
            const isPinching = pinchDist < 0.05;

            for (let i = 0; i < count; i++) {
                const px = positions[i * 3];
                const py = positions[i * 3 + 1];
                const pz = positions[i * 3 + 2];

                const dx = targetX - px;
                const dy = targetY - py;
                const dz = targetZ - pz;
                const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

                if (isPinching && dist < 1.0) {
                    // Explosion force
                    const explosionForce = 0.5;
                    velocities[i * 3] -= dx * explosionForce;
                    velocities[i * 3 + 1] -= dy * explosionForce;
                    velocities[i * 3 + 2] -= dz * explosionForce;
                } else if (dist < 2.0) {
                    // Attraction force
                    const attractionForce = avgDist * 0.1; // Intensity based on hand openness
                    velocities[i * 3] += dx * attractionForce;
                    velocities[i * 3 + 1] += dy * attractionForce;
                    velocities[i * 3 + 2] += dz * attractionForce;
                }

                // Friction to prevent infinite speed
                velocities[i * 3] *= 0.95;
                velocities[i * 3 + 1] *= 0.95;
                velocities[i * 3 + 2] *= 0.95;

                // Update positions based on velocity
                positions[i * 3] += velocities[i * 3];
                positions[i * 3 + 1] += velocities[i * 3 + 1];
                positions[i * 3 + 2] += velocities[i * 3 + 2];
            }
        });

        this.particles.geometry.attributes.position.needsUpdate = true;
        this.particles.geometry.attributes.velocity.needsUpdate = true;
    }
}

new HandArtApp();
