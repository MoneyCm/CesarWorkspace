# SISC-MVP

Minimal MVP del Sistema de Información para la Seguridad y la Convivencia (SISC) - Jamundí

Requisitos: Docker & Docker Compose

Arrancar localmente:

```bash
docker compose up --build
```

Acceder:
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

Este repositorio contiene una versión mínima funcional con:
- FastAPI backend con endpoints de autentificación, ingestión y indicadores.
- Frontend Vite + React con login y tablero básico.
- PostGIS en Docker para almacenar eventos geoespaciales (esquema mínimo).
