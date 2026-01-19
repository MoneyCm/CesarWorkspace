/**
 * main.js - Orquestador del Juego HandyPinball
 * Gestiona el ciclo de vida del juego, motores y estados.
 */

import { initPhysics, updatePhysics, getBodies } from './physics.js';
import { initGraphics, renderGraphics, syncWithPhysics } from './graphics.js';
import { initHands, getHandMovement } from './hands.js';
import { initAudio, playSound } from './audio.js';

let score = 0;
let multiplier = 1;
let ballsRemaining = 3;
let gameState = 'START'; // START, PLAYING, GAMEOVER

const startBtn = document.getElementById('start-btn');
const overlay = document.getElementById('overlay');
const scoreDisplay = document.getElementById('score');

async function init() {
    console.log('Finalizando preparativos para el lanzamiento...');
    
    // Inicializar subsistemas
    initPhysics();
    initGraphics(document.getElementById('render-target'));
    initAudio();
    
    try {
        await initHands();
        console.log('Control por movimiento listo.');
    } catch (e) {
        console.warn('No se pudo activar la cámara, usando controles de teclado (flechas).', e);
    }

    startBtn.addEventListener('click', () => {
        startGame();
    });

    gameLoop();
}

function startGame() {
    gameState = 'PLAYING';
    overlay.classList.add('hidden');
    score = 0;
    multiplier = 1;
    ballsRemaining = 3;
    updateHUD();
    playSound('start');
}

function gameLoop() {
    if (gameState === 'PLAYING') {
        const handsData = getHandMovement();
        updatePhysics(handsData);
        syncWithPhysics(getBodies());
    }
    
    renderGraphics();
    requestAnimationFrame(gameLoop);
}

function updateHUD() {
    scoreDisplay.textContent = score.toString().padStart(6, '0');
    document.getElementById('multiplier').textContent = `x${multiplier}`;
}

// Iniciar aplicación
window.addEventListener('load', () => {
    init();
});
