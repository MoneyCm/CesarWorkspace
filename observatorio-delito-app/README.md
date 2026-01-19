# Observatorio del Delito – Jamundí (MVP)

MVP funcional con **FastAPI + PostgreSQL/PostGIS + Frontend HTML/JS**.

## Requisitos
- Docker y Docker Compose
- (Opcional) Python 3.11 si ejecuta ETL localmente

## Puesta en marcha rápida
```bash
docker compose up --build
```
- API: http://localhost:8000 (docs: http://localhost:8000/docs)
- Frontend: http://localhost:8080

## Cargar datos (ETL)
1. Cree la carpeta `backend/etl/data_input/` y ponga allí los archivos `.xlsx`/`.csv` (Policía, Fiscalía, etc.).  
2. Ejecute (fuera de docker) o entre al contenedor del backend:
```bash
# Host (requiere tener variables de entorno o editar etl script)
python backend/etl/cargar_datos.py

# Dentro del contenedor
docker exec -it observatorio_backend bash -lc "python etl/cargar_datos.py"
```

El ETL normaliza categorías de delito, calcula un `hash_id` para evitar duplicados e inserta coordenadas como `geom` (SRID 4326).

## Endpoints útiles
- `/health` – estado del servicio
- `/delitos/disponibles` – lista de categorías
- `/estadisticas?delito=Homicidio&inicio=2024-01-01&fin=2024-12-31&agrupacion=mensual`
- `/geodatos?delito=Hurto a Personas&inicio=2024-06-01&fin=2024-08-01&limit=500`

## Notas
- La BD crea índices y habilita PostGIS automáticamente.
- El frontend muestra una serie temporal (Chart.js) y un mapa (Leaflet) con los registros filtrados.
- Para producción, se recomienda migrar el frontend a React/Vite o Next.js.
- Seguridad JWT y roles se pueden agregar en `main.py` (middleware) y proteger rutas según necesidad.