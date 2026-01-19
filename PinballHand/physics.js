/**
 * physics.js - Motor de Físicas (Matter.js)
 */

const { Engine, Render, World, Bodies, Composite, Body, Events } = Matter;

let engine;
let world;
let flipperLeft, flipperRight;
let ball;

export function initPhysics() {
    engine = Engine.create();
    world = engine.world;
    world.gravity.y = 1.0; // Gravedad arcade fuerte

    // Crear la mesa (boundaries)
    const bounds = [
        Bodies.rectangle(400, 810, 810, 60, { isStatic: true, label: 'ground' }), // Suelo
        Bodies.rectangle(-10, 400, 60, 800, { isStatic: true }), // Pared izq
        Bodies.rectangle(810, 400, 60, 800, { isStatic: true }), // Pared der
        Bodies.rectangle(400, -10, 810, 60, { isStatic: true })  // Techo
    ];
    World.add(world, bounds);

    // Flippers
    flipperLeft = createFlipper(250, 700, -20);
    flipperRight = createFlipper(550, 700, 20);

    // La Bola
    ball = Bodies.circle(400, 100, 15, {
        restitution: 0.8,
        friction: 0.005,
        density: 0.01,
        label: 'ball'
    });
    World.add(world, ball);

    // Eventos de colisión
    Events.on(engine, 'collisionStart', (event) => {
        event.pairs.forEach(pair => {
            if (pair.bodyA.label === 'ball' || pair.bodyB.label === 'ball') {
                // Manejar colisiones para puntaje/sonido
            }
        });
    });
}

function createFlipper(x, y, angle) {
    const group = Body.nextGroup(true);
    const flipper = Bodies.trapezoid(x, y, 150, 40, 0.2, {
        collisionFilter: { group: group },
        chamfer: { radius: [20, 20, 20, 20] },
        render: { fillStyle: '#ff00ff' },
        label: 'flipper'
    });
    
    const pivot = Bodies.circle(x, y, 5, { isStatic: true, collisionFilter: { group: group } });
    
    // Restricción de giro
    // Simplificado para el ejemplo: usaremos fuerzas para el movimiento
    World.add(world, [flipper, pivot]);
    return flipper;
}

export function updatePhysics(handsData) {
    Engine.update(engine, 1000/60);

    // Control de flippers por manos o teclado
    if (handsData.leftUp) {
        Body.setAngularVelocity(flipperLeft, -0.3);
    } else {
        Body.setAngularVelocity(flipperLeft, 0.1);
    }

    if (handsData.rightUp) {
        Body.setAngularVelocity(flipperRight, 0.3);
    } else {
        Body.setAngularVelocity(flipperRight, -0.1);
    }
}

export function getBodies() {
    return Composite.allBodies(world);
}
