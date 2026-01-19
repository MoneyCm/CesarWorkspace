/**
 * hands.js - Integración de MediaPipe Hands
 */

const videoElement = document.getElementById('webcam');
const canvasElement = document.getElementById('tracking-canvas');
const canvasCtx = canvasElement.getContext('2d');

let hands;
let movement = { leftUp: false, rightUp: false };

export async function initHands() {
    hands = new Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
    });

    hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5
    });

    hands.onResults(onResults);

    const camera = new Camera(videoElement, {
        onFrame: async () => {
            await hands.send({ image: videoElement });
        },
        width: 640,
        height: 480
    });
    camera.start();

    // Controles de teclado como backup
    window.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') movement.leftUp = true;
        if (e.key === 'ArrowRight') movement.rightUp = true;
    });
    window.addEventListener('keyup', (e) => {
        if (e.key === 'ArrowLeft') movement.leftUp = false;
        if (e.key === 'ArrowRight') movement.rightUp = false;
    });
}

function onResults(results) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    
    movement.leftUp = false;
    movement.rightUp = false;

    if (results.multiHandLandmarks) {
        for (const landmarks of results.multiHandLandmarks) {
            // Dibujar solo para feedback visual simple
            const x = landmarks[8].x; // Índice
            const y = landmarks[8].y;
            
            // Lógica simple: si la mano está en la mitad izquierda y sube
            if (x > 0.5) { // Espejado
                if (y < 0.4) movement.leftUp = true;
            } else {
                if (y < 0.4) movement.rightUp = true;
            }
        }
    }
    canvasCtx.restore();
}

export function getHandMovement() {
    return movement;
}
