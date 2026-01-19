# Cableado lógico (resumen)

- Teensy 4.1 → ULN2803A (entradas) → MOSFET N (gates) → Bobinas 24 V (con diodos flyback).
- WS2812B en cadena: Data desde pin `LED_DATA` (por defecto 33). Inyectar 5 V cada ~20 LEDs.
- Switches con `INPUT_PULLUP` y retorno a GND; RC 1 kΩ/100 nF opcional.
- Masas en estrella: unir GND de 5 V, 24 V y lógica en un bus grueso cerca de PSU.

## Asignación ejemplo de pines

- Flipper izquierdo: IN=pin 22 (COIL_LEFT_FLIP) → MOSFET Q1 → bobina flipper L.
- Flipper derecho: IN=pin 23 (COIL_RIGHT_FLIP) → MOSFET Q2 → bobina flipper R.
- Bumpers: 24,25,26,27 → Q3..Q6.
- Kickers (acelerador): 28,29,30 → Q7..Q9.
- Switch flipper L: pin 2; switch flipper R: pin 3.
- Tilt: pin 4 (SW‑420 y plomada en serie con opto opcional).
- Targets: 5..13.

## Seguridad

- Diodo 1N5408 en paralelo con cada bobina (cátodo a +24 V, ánodo a drenaje).
- Fusibles por rama: flippers 10 A, bumpers 10 A, LEDs 5 A.
- Separar mazos: potencia/alta corriente alejados de señales y LED data.

