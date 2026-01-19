# Botón de Pánico y Alertas Ciudadanas — Prototipo

Prototipo web listo para demo con app ciudadana (botón de pánico), panel central (mapa + avisos) y backend mínimo (FastAPI). Funciona sin backend en modo demo (cola offline), y cuando hay backend disponible envía/recibe en tiempo real (SSE simple).

## Carpetas

- `citizen/` — App ciudadana (PWA): botón de pánico, evidencia (fotos/video), geolocalización, cola offline y reintento.
- `admin/` — Panel central: lista de alertas, mapa, envío de avisos a usuarios (demo con SSE o pull).
- `server/` — Backend FastAPI de referencia con endpoints REST + SSE.

## Endpoints del backend (referencia)

- `POST /api/alerts` — Recibe alerta (JSON o multipart con media). Responde `{id}`.
- `GET /api/alerts` — Lista alertas (paginación simple query `?limit=&offset=`).
- `POST /api/evidence` — Sube evidencia asociada a un `alert_id` (multipart).
- `GET /api/events` — SSE para eventos en vivo (alertas nuevas, avisos).
- `POST /api/broadcasts` — Envía mensaje broadcast (admin → ciudadanos).

## Ejecución rápida

Opción A — Demo sin backend (solo abrir archivos)
- Abre `citizen/index.html` para probar el botón de pánico (se guardan envíos en cola offline).
- Abre `admin/index.html` para ver un mapa y cargar alertas de ejemplo (modo demo).
- Nota: para PWA/service worker o cámara en móviles, sirve por `http://localhost` (no `file://`).

Opción B — Con backend FastAPI
- Requisitos: Python 3.10+
- Instalar:
  ```bash
  cd panic-app/server
  python -m venv .venv
  . .venv/Scripts/Activate.ps1  # Windows PowerShell
  pip install -r requirements.txt
  uvicorn main:app --reload
  ```
- Abre en otra terminal un servidor estático para frontend (por ejemplo):
  ```bash
  cd panic-app
  python -m http.server 8080
  ```
- App ciudadana: `http://localhost:8080/citizen/`
- Panel admin: `http://localhost:8080/admin/`

## Integración de datos (idea)
- Fuentes: alertas ciudadanas (esta app), informes policiales (CSV/ETL), bomberos/movilidad (API), etc.
- Plataforma: el backend puede volcar a PostgreSQL y alimentar un pipeline de analítica/ML para patrones y predicción.

## Seguridad
- No expongas el backend sin autenticación real (tokens, rate limit, validación CORS). Este prototipo es solo demostrativo.

