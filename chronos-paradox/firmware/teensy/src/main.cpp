#include <Arduino.h>

// Firmware base — Chronos Paradox (Teensy 4.1)
// - FSM de juego
// - Escaneo de switches con debounce
// - Control de bobinas (hit/hold) — stubs
// - Esqueleto de efectos LED — stubs

// ============= Configuración de pines (AJUSTAR A TU ARNÉS) =============
namespace io_pins {
  // Entradas (microswitches / sensores) — usar pullups internos
  constexpr uint8_t SW_LEFT_FLIP   = 2;
  constexpr uint8_t SW_RIGHT_FLIP  = 3;
  constexpr uint8_t SW_TILT        = 4;
  constexpr uint8_t SW_TARGETS[]   = {5,6,7,8,9,10,11,12,13};

  // Salidas — bobinas (MOSFET gate a través de ULN2803A si aplica)
  constexpr uint8_t COIL_LEFT_FLIP  = 22;
  constexpr uint8_t COIL_RIGHT_FLIP = 23;
  constexpr uint8_t COIL_BUMPERS[]  = {24,25,26,27};
  constexpr uint8_t COIL_KICKERS[]  = {28,29,30};

  // LEDs direccionables (WS2812B) — ejemplo: pin 33
  constexpr uint8_t LED_DATA = 33;
}

// ================= Utilidades de tiempo =================
static inline uint32_t ms() { return millis(); }

// ================= Debounce simple =================
struct DebouncedIn {
  uint8_t pin; bool state=false; uint32_t last=0; uint16_t dly=10;
  void begin(){ pinMode(pin, INPUT_PULLUP); state = !digitalRead(pin); last = ms(); }
  bool read(){ bool v = !digitalRead(pin); if (v != state && (ms()-last) > dly) { state=v; last=ms(); } return state; }
};

// ================= Control de bobinas =================
struct Coil {
  uint8_t pin; bool on=false; uint32_t tOff=0; // tiempo de apagado programado
  void begin(){ pinMode(pin, OUTPUT); digitalWrite(pin, LOW); }
  void pulse(uint16_t hit_ms){ on=true; digitalWrite(pin, HIGH); tOff = ms()+hit_ms; }
  void hold(bool enable, uint8_t duty=64){
    // Stub: sustituir por PWM de baja frecuencia o driver de holding
    digitalWrite(pin, enable ? HIGH : LOW);
  }
  void task(){ if(on && (int32_t)(ms()-tOff) >= 0){ digitalWrite(pin, LOW); on=false; } }
};

// ============== FSM ==============
enum class GameState { STANDBY, JUGANDO, MISION_PASADO, MISION_PRESENTE, MISION_FUTURO, MULTIBALL, WIZARD, GAME_OVER };
GameState state = GameState::STANDBY;

// IO global
DebouncedIn swLeft{io_pins::SW_LEFT_FLIP};
DebouncedIn swRight{io_pins::SW_RIGHT_FLIP};
DebouncedIn swTilt{io_pins::SW_TILT};

Coil flL{io_pins::COIL_LEFT_FLIP};
Coil flR{io_pins::COIL_RIGHT_FLIP};
Coil bumpers[4] = {{io_pins::COIL_BUMPERS[0]},{io_pins::COIL_BUMPERS[1]},{io_pins::COIL_BUMPERS[2]},{io_pins::COIL_BUMPERS[3]}};
Coil kickers[3] = {{io_pins::COIL_KICKERS[0]},{io_pins::COIL_KICKERS[1]},{io_pins::COIL_KICKERS[2]}};

// ============== Lógica de juego (esqueleto) ==============
volatile uint32_t score = 0;

void onTargetHit(uint8_t id){ score += 10; /* avanzar misión */ }
void onBumperHit(uint8_t id){ score += 50; bumpers[id].pulse(30); }
void onRampPass(bool left){ score += 100; }
void onMultiballStart(){ state = GameState::MULTIBALL; /* lanzar bolas extra */ }
void onTilt(){ /* apagar coils unos segundos */ }

void ledsShowIdle(){ /* TODO */ }
void ledsShowMode(GameState s){ /* TODO */ }

// ============== Setup/Loop ==============
void setup(){
  // Entradas
  swLeft.begin(); swRight.begin(); swTilt.begin();
  // Salidas
  flL.begin(); flR.begin();
  for (auto &c : bumpers) c.begin();
  for (auto &c : kickers) c.begin();
  state = GameState::STANDBY;
}

void handleFlippers(){
  const bool L = swLeft.read();
  const bool R = swRight.read();
  if (L) flL.pulse(35); if (R) flR.pulse(35);
}

void coilsTask(){
  flL.task(); flR.task();
  for (auto &c : bumpers) c.task();
  for (auto &c : kickers) c.task();
}

void loop(){
  // Entrada básica
  handleFlippers();

  // FSM simplificada
  switch(state){
    case GameState::STANDBY:    ledsShowIdle(); /* esperar crédito/bola */ break;
    case GameState::JUGANDO:    ledsShowMode(state); break;
    case GameState::MISION_PASADO:
    case GameState::MISION_PRESENTE:
    case GameState::MISION_FUTURO:
    case GameState::MULTIBALL:
    case GameState::WIZARD:
    case GameState::GAME_OVER:  ledsShowMode(state); break;
  }

  // Servicio coils
  coilsTask();
}

