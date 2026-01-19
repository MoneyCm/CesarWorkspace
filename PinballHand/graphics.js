/**
 * graphics.js - Renderizado con Three.js
 */

let scene, camera, renderer;
const meshes = new Map();

export function initGraphics(container) {
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050505);

    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.set(400, 400, 600);
    camera.lookAt(400, 400, 0);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Iluminación
    const ambientLight = new THREE.AmbientLight(0x404040, 2);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x00f3ff, 5, 1000);
    pointLight.position.set(400, 400, 200);
    scene.add(pointLight);
}

export function syncWithPhysics(bodies) {
    bodies.forEach(body => {
        let mesh = meshes.get(body.id);
        
        if (!mesh) {
            // Crear representación visual si no existe
            const geometry = body.label === 'ball' ? 
                new THREE.SphereGeometry(15, 32, 32) : 
                new THREE.BoxGeometry(150, 40, 10); // Simplificado para flipper
            
            const material = new THREE.MeshPhongMaterial({ 
                color: body.label === 'ball' ? 0xffffff : 0xff00ff,
                emissive: body.label === 'ball' ? 0x222222 : 0x440044,
                shininess: 100
            });
            
            mesh = new THREE.Mesh(geometry, material);
            scene.add(mesh);
            meshes.set(body.id, mesh);
        }

        // Actualizar posición y rotación (Matter.js 2D -> Three.js 3D)
        mesh.position.set(body.position.x, 800 - body.position.y, 0);
        mesh.rotation.z = -body.angle;
    });
}

export function renderGraphics() {
    renderer.render(scene, camera);
}
