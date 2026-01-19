import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, Base
from .routes import delitos, estadisticas, geodatos, health

app = FastAPI(title="Observatorio del Delito - Jamundí", version="0.1.0")

# CORS
origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5500").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (if using SQLAlchemy to manage schema)
Base.metadata.create_all(bind=engine)
# Ensure PostGIS extension and indexes exist
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    conn.commit()

# Routers
app.include_router(health.router)
app.include_router(delitos.router)
app.include_router(estadisticas.router)
app.include_router(geodatos.router)

@app.get("/")
def root():
    return {"name": "Observatorio del Delito - Jamundí", "status": "running"}