import os
from datetime import datetime, date
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
import json

from database_simple import engine, get_db, Base
from models_simple import Crime

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Observatorio del Delito - Jamundí (Simplificado)", version="0.1.0")

# CORS
origins = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "Observatorio del Delito - Jamundí (Simplificado)", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/delitos/disponibles")
def get_delitos_disponibles(db: Session = next(get_db())):
    """Obtener lista de tipos de delitos disponibles"""
    delitos = db.query(Crime.delito).distinct().all()
    return {"delitos": [d[0] for d in delitos if d[0]]}

@app.get("/estadisticas")
def get_estadisticas(
    delito: Optional[str] = None,
    inicio: Optional[str] = None,
    fin: Optional[str] = None,
    agrupacion: str = "mensual",
    db: Session = next(get_db())
):
    """Obtener estadísticas de delitos"""
    query = db.query(Crime)
    
    # Filtros
    if delito:
        query = query.filter(Crime.delito == delito)
    
    if inicio:
        query = query.filter(Crime.fecha >= date.fromisoformat(inicio))
    
    if fin:
        query = query.filter(Crime.fecha <= date.fromisoformat(fin))
    
    # Agrupación
    if agrupacion == "mensual":
        serie = db.query(
            func.strftime('%Y-%m', Crime.fecha).label('periodo'),
            func.count(Crime.id).label('total')
        ).filter(query.whereclause).group_by('periodo').order_by('periodo').all()
    else:  # anual
        serie = db.query(
            func.strftime('%Y', Crime.fecha).label('periodo'),
            func.count(Crime.id).label('total')
        ).filter(query.whereclause).group_by('periodo').order_by('periodo').all()
    
    return {
        "serie": [{"periodo": s.periodo, "total": s.total} for s in serie],
        "total": sum(s.total for s in serie)
    }

@app.get("/geodatos")
def get_geodatos(
    delito: Optional[str] = None,
    inicio: Optional[str] = None,
    fin: Optional[str] = None,
    limit: int = 500,
    db: Session = next(get_db())
):
    """Obtener datos geográficos de delitos"""
    query = db.query(Crime).filter(Crime.lat.isnot(None), Crime.lon.isnot(None))
    
    # Filtros
    if delito:
        query = query.filter(Crime.delito == delito)
    
    if inicio:
        query = query.filter(Crime.fecha >= date.fromisoformat(inicio))
    
    if fin:
        query = query.filter(Crime.fecha <= date.fromisoformat(fin))
    
    items = query.limit(limit).all()
    
    return {
        "items": [
            {
                "id": item.id,
                "delito": item.delito,
                "fecha": item.fecha.isoformat() if item.fecha else None,
                "barrio": item.barrio,
                "lat": item.lat,
                "lon": item.lon
            }
            for item in items
        ]
    }

# Cargar datos de ejemplo
@app.post("/cargar-datos-ejemplo")
def cargar_datos_ejemplo(db: Session = next(get_db())):
    """Cargar datos de ejemplo para probar la aplicación"""
    datos_ejemplo = [
        {
            "hash_id": "ejemplo_001",
            "fecha": date(2024, 1, 15),
            "delito": "Hurto a Personas",
            "barrio": "Centro",
            "lat": 3.262,
            "lon": -76.540
        },
        {
            "hash_id": "ejemplo_002", 
            "fecha": date(2024, 2, 20),
            "delito": "Homicidio",
            "barrio": "San Juan",
            "lat": 3.265,
            "lon": -76.545
        },
        {
            "hash_id": "ejemplo_003",
            "fecha": date(2024, 3, 10),
            "delito": "Hurto a Personas",
            "barrio": "Villa del Prado",
            "lat": 3.260,
            "lon": -76.535
        }
    ]
    
    for dato in datos_ejemplo:
        crime = Crime(**dato)
        db.add(crime)
    
    db.commit()
    return {"message": f"Se cargaron {len(datos_ejemplo)} registros de ejemplo"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

