## Chronos Paradox — Prototipo de Pinball

Proyecto llave en mano con manual, firmware base (Teensy 4.1), documentación de electrónica y plano de playfield de referencia.

### Estructura

- `docs/Manual_Chronos_Paradox.md` — Manual técnico (concepto, mecánica, electrónica, software, arte, mantenimiento).
- `firmware/teensy/src/main.cpp` — Firmware base (FSM, escaneo de switches, control de bobinas/LEDs — stubs listos para cablear).
- `electronics/bom.csv` — Lista de materiales resumida (BOM).
- `electronics/wiring.md` — Mapa de cableado lógico (Teensy ↔ drivers ↔ actuadores/sensores).
- `electronics/led_map.json` — Mapa de LEDs direccionables por zonas.
- `cnc/playfield.svg` — Plano conceptual 1150×550 mm (aprox) con distribución de elementos.

### Uso rápido

1) Firmware
- Requisitos: Arduino IDE (con Teensyduino) o PlatformIO.
- Placa: Teensy 4.1.
- Abre `firmware/teensy/src/main.cpp`, ajusta pines en `io_pins` y compila.

2) Electrónica
- Revisa `electronics/wiring.md` para conexiones y `electronics/bom.csv` para compras iniciales.

3) Playfield
- Abre `cnc/playfield.svg` (Inkscape/Illustrator) y escala 1:1 (mm) para CNC/plantillas.

### Siguientes pasos sugeridos
- Completar asignación de pines reales según tu arnés.
- Añadir animaciones en `led_map.json` y efectos en firmware (`LedFx`).
- Sustituir `playfield.svg` por tu DXF final para corte.

