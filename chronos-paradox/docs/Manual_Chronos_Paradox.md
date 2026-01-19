# Chronos Paradox — Manual Técnico (Prototipo)

Este documento especifica el prototipo de pinball “Chronos Paradox” listo para fabricación preliminar, integración electrónica y programación.

## 1. Concepto y Juego
- Tema: manipulación temporal retro‑futurista.
- Misiones: Pasado, Presente, Futuro.
- Flujo: Inicio → Misiones (targets) → Eventos temporales (Slow/Hyper) → Multiball (x2) → Wizard → Game Over.
- Puntuación: golpes base + combos y multiplicadores por modo; bonus “no‑tilt”.

## 2. Ingeniería Mecánica y Gabinete
- Dimensiones: gabinete 120×60×90 cm (MDF 18 mm); tablero 115×55 cm (abedul 12 mm). Inclinación: 6.8°.
- Plano (cuadrícula 0–100): ver `cnc/playfield.svg`.
  - Flippers: (30,92) y (70,92), paletas 7.5 cm, goma Shore A50.
  - Bumpers: B1 (30,25), B2 (70,25) alta potencia; B3 (50,18), B4 (50,35) baja.
  - Rampas: Pasado (22,55→15,20) con imán; Futuro (78,55→85,18) con 3 kickers.
  - Dianas: 3×Pasado, 3×Presente, 3×Futuro, 2×bonus.
  - Portal: (50,12) Ø80 mm; Scoop: (12,18) eyección a (45,52).
- Materiales: guías inox 0.8–1.0 mm, protectores PETG 0.5–1.0 mm, top vidrio 4 mm.
- Tolerancias: guía bola 1.2–1.4×Ø bola (27 mm); radios ≥1.5×Ø; altura flipper 0.6–0.8 mm.

## 3. Electrónica y Cableado
- Control: Teensy 4.1.
- Drivers: ULN2803A (señales), MOSFET N lógica‑nivel (IRLZ44N) + diodos 1N5408; TLC5940 (PWM) y WS2812B (80 uds) para efectos.
- Sensores: IR haz roto (10), microswitch (10+), reed/hall (2), tilt SW‑420 + plomada.
- Actuadores: flippers/bumpers/kickers/scoop 24 V; NEMA17 + TMC2209 (portal).
- Alimentación: 5 V/5–10 A (lógica/LEDs), 24 V/10 A (bobinas), 12 V/3 A (motores). Fusibles por rama y TVS.
- Cableado: masas en estrella; retorno grueso a PSU; separación potencia/lógica.
- Mapa lógico: ver `electronics/wiring.md`.

## 4. Software y Lógica
- Firmware (C++): FSM Estados `STANDBY → JUGANDO → (PASA/ PRES/ FUTU) → MULTIBALL → WIZARD → GAME_OVER`.
- Módulos: IO (debounce), Coils (hit/hold), LED FX (zonas), Audio (SFX/BGM), Scoring (EEPROM), Service (tests).
- Eventos: `onTargetHit`, `onRampPass`, `onMultiballStart`, `onScoopEnter`, `onTilt`.

## 5. Arte y Diseño
- Estilo retro‑futurista; paleta púrpuras/azules con cian/magenta. Backglass con reloj roto y cápsula temporal.
- Señalética en tablero: flechas hacia rampas, iconos de eras, camino al portal.

## 6. Calibración, Mantenimiento y Seguridad
- Calibración: inclinación 6.8° ±0.2°; flippers 30–40 ms hit 24 V + hold PWM 35–45%; tilt doble (SW‑420+plomada).
- Mantenimiento: limpieza IPA semanal; lubricación PTFE mensual en ejes; inspección soldaduras trimestral.
- Seguridad: fusibles por rama; cubiertas en bornes 24 V; no trabajar con tensión; separación lógica/potencia.

---
Este manual acompaña a: `firmware/teensy/`, `electronics/` y `cnc/playfield.svg`.

