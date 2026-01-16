/**
 * main.js - Core Orquestador 3D para Juan Pablo Racing
 */

let scene, camera, renderer, clock;
let car, track;
let keys = {};

async function init() {
    scene = new THREE.Scene();
    // Niebla para profundidad estética tipo Mario Kart
    scene.fog = new THREE.Fog(0x87CEEB, 10, 500);

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    document.getElementById('game-container').appendChild(renderer.domElement);

    clock = new THREE.Clock();

    // Iluminación
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const sun = new THREE.DirectionalLight(0xffffff, 1.0);
    sun.position.set(100, 200, 100);
    sun.castShadow = true;
    scene.add(sun);

    // Inicializar Mundo y Coche
    createWorld();
    createCar();
    spawnPolice();

    window.addEventListener('keydown', e => keys[e.code] = true);
    window.addEventListener('keyup', e => keys[e.code] = false);
    window.addEventListener('resize', onWindowResize);

    animate();
}

function createWorld() {
    // Suelo / Césped
    const groundGeo = new THREE.PlaneGeometry(2000, 2000);
    const groundMat = new THREE.MeshPhongMaterial({ color: 0x448844 });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // Pista (Circuito simple ovalado)
    const trackGeo = new THREE.RingGeometry(80, 120, 128);
    const trackMat = new THREE.MeshPhongMaterial({ color: 0x222222, side: THREE.DoubleSide });
    track = new THREE.Mesh(trackGeo, trackMat);
    track.rotation.x = -Math.PI / 2;
    track.position.y = 0.05;
    track.receiveShadow = true;
    scene.add(track);

    // Líneas de la pista
    const lineGeo = new THREE.RingGeometry(98, 102, 128);
    const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });
    const line = new THREE.Mesh(lineGeo, lineMat);
    line.rotation.x = -Math.PI / 2;
    line.position.y = 0.1;
    scene.add(line);

    // Edificios detallados
    for (let i = 0; i < 40; i++) {
        createBuilding();
    }

    // Añadir rampas en puntos clave
    createRamp(0, 100, 0);
    createRamp(100, 0, Math.PI / 2);
    createRamp(0, -100, Math.PI);
    createRamp(-100, 0, -Math.PI / 2);
}

let buildings = [];
let policeSquad = [];
let spawnTimer = 0;
let gameTime = 0;

function createBuilding() {
    const width = 8 + Math.random() * 10;
    const height = 15 + Math.random() * 40;
    const depth = 8 + Math.random() * 10;

    const building = new THREE.Group();

    // Cuerpo principal
    const bodyGeo = new THREE.BoxGeometry(width, height, depth);
    const bodyMat = new THREE.MeshPhongMaterial({
        color: new THREE.Color().setHSL(Math.random(), 0.7, 0.3),
        flatShading: true
    });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = height / 2;
    body.castShadow = true;
    body.receiveShadow = true;
    building.add(body);

    // Ventanas luminosas (detalles)
    const windowGeo = new THREE.PlaneGeometry(width * 0.8, height * 0.8);
    const windowMat = new THREE.MeshBasicMaterial({ color: 0xffffaa, side: THREE.DoubleSide });

    // Añadimos ventanas en dos caras
    for (let face = 0; face < 2; face++) {
        const win = new THREE.Mesh(windowGeo, windowMat);
        if (face === 0) {
            win.position.set(0, height / 2, depth / 2 + 0.1);
        } else {
            win.rotation.y = Math.PI;
            win.position.set(0, height / 2, -depth / 2 - 0.1);
        }
        building.add(win);
    }

    // Techo
    const roofGeo = new THREE.BoxGeometry(width + 2, 2, depth + 2);
    const roofMat = new THREE.MeshPhongMaterial({ color: 0x222222 });
    const roof = new THREE.Mesh(roofGeo, roofMat);
    roof.position.y = height;
    building.add(roof);

    // Posicionamiento alrededor de la pista
    const angle = Math.random() * Math.PI * 2;
    const isInside = Math.random() > 0.5;
    const radius = isInside ? (40 + Math.random() * 30) : (140 + Math.random() * 100);

    building.position.set(Math.cos(angle) * radius, 0, Math.sin(angle) * radius);
    building.rotation.y = -angle + Math.PI / 2;

    // Al final, guardar en la lista de colisiones:
    building.userData = { width: width, depth: depth };
    scene.add(building);
    buildings.push(building);
}

function checkCollisions() {
    const data = car.userData;
    const pos = car.position;

    // Colisión con Edificios (Cajas AABB simples)
    buildings.forEach(b => {
        const bData = b.userData;
        const dx = Math.abs(pos.x - b.position.x);
        const dz = Math.abs(pos.z - b.position.z);

        if (dx < (bData.width / 2 + 2) && dz < (bData.depth / 2 + 4)) {
            // Rebotar o detener
            data.velocity *= -0.5;
            car.translateZ(-2); // Retroceder un poco para no quedar trabado
        }
    });

    // Colisión con Rampas (Subir si estás alineado)
    ramps.forEach(ramp => {
        const dx = Math.abs(pos.x - ramp.position.x);
        const dz = Math.abs(pos.z - ramp.position.z);

        if (dx < 12 && dz < 18) {
            if (data.onGround && data.velocity > 0.2) {
                data.verticalVelocity = 0.6;
                data.onGround = false;
            }
        }
    });
}

function createCar() {
    // Representación simple del Kart: Chasis + 4 ruedas
    car = new THREE.Group();

    const bodyGeo = new THREE.BoxGeometry(4, 2, 8);
    const bodyMat = new THREE.MeshPhongMaterial({ color: 0xff0000 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 1.5;
    body.castShadow = true;
    car.add(body);

    const wheelGeo = new THREE.CylinderGeometry(1, 1, 1, 16);
    const wheelMat = new THREE.MeshPhongMaterial({ color: 0x222222 });

    const wheelPos = [
        { x: 2.5, y: 1, z: 2.5 }, { x: -2.5, y: 1, z: 2.5 },
        { x: 2.5, y: 1, z: -2.5 }, { x: -2.5, y: 1, z: -2.5 }
    ];

    wheelPos.forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeo, wheelMat);
        wheel.rotation.z = Math.PI / 2;
        wheel.position.set(pos.x, pos.y, pos.z);
        car.add(wheel);
    });

    car.position.set(100, 0, 0); // Posición inicial en la pista
    scene.add(car);

    // Estado físico del carro
    car.userData = {
        velocity: 0,
        rotation: 0,
        maxSpeed: 1.5,
        accel: 0.02,
        friction: 0.98,
        turnSpeed: 0.04,
        verticalVelocity: 0,
        y: 0,
        onGround: true
    };
}

let ramps = [];

function createRamp(x, z, rotation) {
    const rampGroup = new THREE.Group();

    const rampGeo = new THREE.BoxGeometry(20, 2, 30);
    const rampMat = new THREE.MeshPhongMaterial({ color: 0xffff00 });
    const ramp = new THREE.Mesh(rampGeo, rampMat);

    // Inclinar la rampa
    ramp.rotation.x = -Math.PI / 6;
    ramp.position.y = 4;
    rampGroup.add(ramp);

    rampGroup.position.set(x, 0, z);
    rampGroup.rotation.y = rotation;
    scene.add(rampGroup);
    ramps.push(rampGroup);
}

let policeCar;
let isGameOver = false;

function updatePhysics() {
    const data = car.userData;

    // Gravedad
    if (!data.onGround) {
        data.verticalVelocity -= 0.01;
        data.y += data.verticalVelocity;
    }

    if (data.y <= 0) {
        data.y = 0;
        data.verticalVelocity = 0;
        data.onGround = true;
    }

    car.position.y = data.y;
}

function spawnPolice() {
    const police = new THREE.Group();

    // Chasis Policía (Negro y Blanco)
    const bodyGeo = new THREE.BoxGeometry(4.5, 2.2, 8.5);
    const bodyMat = new THREE.MeshPhongMaterial({ color: 0x000000 });
    const body = new THREE.Mesh(bodyGeo, bodyMat);
    body.position.y = 1.5;
    body.castShadow = true;
    police.add(body);

    const whitePartGeo = new THREE.BoxGeometry(4.6, 1.5, 3);
    const whitePartMat = new THREE.MeshPhongMaterial({ color: 0xffffff });
    const part = new THREE.Mesh(whitePartGeo, whitePartMat);
    part.position.y = 1.6;
    police.add(part);

    // Sirenas
    const sirenGeo = new THREE.BoxGeometry(2, 0.5, 1);
    const sirenRedMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const sirenBlueMat = new THREE.MeshBasicMaterial({ color: 0x0000ff });

    const sirenR = new THREE.Mesh(sirenGeo, sirenRedMat);
    sirenR.position.set(1, 3, 0);
    police.add(sirenR);

    const sirenB = new THREE.Mesh(sirenGeo, sirenBlueMat);
    sirenB.position.set(-1, 3, 0);
    police.add(sirenB);

    // Posicionar detrás del jugador de forma aleatoria
    const offset = new THREE.Vector3((Math.random() - 0.5) * 40, 0, -50 - Math.random() * 50);
    const spawnPos = offset.applyMatrix4(car.matrixWorld);
    police.position.copy(spawnPos);

    police.userData = {
        speed: 0.6 + Math.random() * 0.4,
        sirenTimer: Math.random() * Math.PI,
        sirenR: sirenR,
        sirenB: sirenB
    };

    scene.add(police);
    policeSquad.push(police);
}

function updatePolice(deltaTime) {
    if (isGameOver) return;

    policeSquad.forEach(p => {
        const data = p.userData;
        p.lookAt(car.position);
        p.translateZ(data.speed);

        // Sirenas
        data.sirenTimer += deltaTime;
        const s = Math.sin(data.sirenTimer * 10);
        data.sirenR.visible = s > 0;
        data.sirenB.visible = s <= 0;

        // Atrapado?
        if (p.position.distanceTo(car.position) < 6) {
            triggerGameOver();
        }
    });

    // Spawn gradual
    gameTime += deltaTime;
    spawnTimer += deltaTime;
    if (spawnTimer > 10) { // Cada 10 segundos una patrulla más
        spawnPolice();
        spawnTimer = 0;
    }
}

function triggerGameOver() {
    isGameOver = true;
    const hud = document.getElementById('hud');
    if (hud) {
        hud.innerHTML = "<h1 style='color:red; font-size:60px;'>¡ATRAPADO POR LA LEY!</h1><p style='font-size:30px;'>GAME OVER</p><button onclick='location.reload()' style='font-size:20px; padding:10px;'>REINTENTAR</button>";
    }
    car.userData.velocity = 0;
}

function animate() {
    requestAnimationFrame(animate);
    const deltaTime = clock.getDelta();

    if (!isGameOver) {
        const data = car.userData;

        // Controles básicos
        if (keys['ArrowUp'] || keys['KeyW']) data.velocity += data.accel;
        if (keys['ArrowDown'] || keys['KeyS']) data.velocity -= data.accel;

        if (Math.abs(data.velocity) > 0.1) {
            const turnDir = data.velocity > 0 ? 1 : -1;
            if (keys['ArrowLeft'] || keys['KeyA']) car.rotation.y += data.turnSpeed * turnDir;
            if (keys['ArrowRight'] || keys['KeyD']) car.rotation.y -= data.turnSpeed * turnDir;
        }

        data.velocity *= data.friction;
        car.translateZ(data.velocity);

        // Físicas y Colisiones
        updatePhysics();
        checkCollisions();
        updatePolice(deltaTime);
    }

    // Actualizar HUD
    const speedDisplay = document.getElementById('speed');
    if (speedDisplay) speedDisplay.textContent = Math.round(car.userData.velocity * 100);

    // Cámara
    const relativeCameraOffset = new THREE.Vector3(0, 10, -25);
    const cameraOffset = relativeCameraOffset.applyMatrix4(car.matrixWorld);
    camera.position.set(cameraOffset.x, cameraOffset.y, cameraOffset.z);
    camera.lookAt(car.position);

    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

init();
