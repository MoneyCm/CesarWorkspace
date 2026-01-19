# Arquitectura

- Base de datos: PostgreSQL + PostGIS (contenedor)
- Backend: FastAPI (Docker)
- Frontend: React (Vite, Docker)
- Jobs/ETL: APScheduler + tareas en backend (MVP)
- Observabilidad: logs estructurados, endpoint `/health` y `/ready`.

Decisiones de seguridad:
- HTTPS en producción (Let's Encrypt)
- JWT con refresh, roles RBAC, hashing de contraseñas
- Seudonimización de identificadores personales en la capa analítica

Despliegue: `docker compose up --build`
