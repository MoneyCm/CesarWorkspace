import os
from datetime import datetime, date
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, Text, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import func
from sqlalchemy.sql import func as sql_func
from typing import List, Optional
import json
import pandas as pd
import hashlib

# SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./observatorio.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Crime(Base):
    __tablename__ = "crimes"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=True)
    incident_id = Column(String(128), nullable=True)
    hash_id = Column(String(64), nullable=False)
    fecha = Column(Date, index=True, nullable=False)
    delito = Column(String(120), index=True, nullable=False)
    subdelito = Column(String(120), nullable=True)
    municipio = Column(String(120), default="Jamundí", index=True)
    zona = Column(String(20), nullable=True)
    barrio = Column(String(160), nullable=True)
    corregimiento = Column(String(160), nullable=True)
    genero_victima = Column(String(20), nullable=True)
    edad_victima = Column(Integer, nullable=True)
    arma = Column(String(80), nullable=True)
    modalidad = Column(String(120), nullable=True)
    cantidad = Column(Integer, default=1)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    extras = Column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint('hash_id', name='uq_crimes_hash_id'),
        Index('idx_crimes_periodo', 'fecha', 'delito'),
    )

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(title="Observatorio del Delito - Jamundí", version="0.1.0")

# CORS
origins = ["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"name": "Observatorio del Delito - Jamundí", "status": "running"}

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

@app.post("/cargar-excel")
async def cargar_excel(file: UploadFile = File(...), db: Session = next(get_db())):
    """Cargar datos desde archivo Excel"""
    try:
        # Leer el archivo Excel
        if file.filename.endswith('.xlsx'):
            df = pd.read_excel(file.file)
        elif file.filename.endswith('.csv'):
            df = pd.read_csv(file.file)
        else:
            raise HTTPException(status_code=400, detail="Solo se permiten archivos .xlsx o .csv")
        
        # Mapear columnas (ajustar según tu archivo Excel)
        column_mapping = {
            'fecha': 'fecha',
            'delito': 'delito', 
            'barrio': 'barrio',
            'latitud': 'lat',
            'longitud': 'lon',
            'municipio': 'municipio',
            'zona': 'zona',
            'genero_victima': 'genero_victima',
            'edad_victima': 'edad_victima',
            'arma': 'arma',
            'modalidad': 'modalidad'
        }
        
        # Normalizar nombres de columnas
        df.columns = df.columns.str.lower().str.strip()
        
        # Procesar cada fila
        registros_cargados = 0
        for index, row in df.iterrows():
            try:
                # Crear hash único
                hash_data = f"{row.get('fecha', '')}{row.get('delito', '')}{row.get('barrio', '')}{index}"
                hash_id = hashlib.md5(hash_data.encode()).hexdigest()
                
                # Preparar datos
                crime_data = {
                    "hash_id": hash_id,
                    "fecha": pd.to_datetime(row.get('fecha')).date() if pd.notna(row.get('fecha')) else date.today(),
                    "delito": str(row.get('delito', 'Sin especificar')).strip(),
                    "barrio": str(row.get('barrio', '')).strip() if pd.notna(row.get('barrio')) else None,
                    "lat": float(row.get('latitud', row.get('lat', 0))) if pd.notna(row.get('latitud', row.get('lat'))) else None,
                    "lon": float(row.get('longitud', row.get('lon', 0))) if pd.notna(row.get('longitud', row.get('lon'))) else None,
                    "municipio": str(row.get('municipio', 'Jamundí')).strip(),
                    "zona": str(row.get('zona', '')).strip() if pd.notna(row.get('zona')) else None,
                    "genero_victima": str(row.get('genero_victima', '')).strip() if pd.notna(row.get('genero_victima')) else None,
                    "edad_victima": int(row.get('edad_victima', 0)) if pd.notna(row.get('edad_victima')) else None,
                    "arma": str(row.get('arma', '')).strip() if pd.notna(row.get('arma')) else None,
                    "modalidad": str(row.get('modalidad', '')).strip() if pd.notna(row.get('modalidad')) else None,
                }
                
                # Verificar si ya existe
                existing = db.query(Crime).filter(Crime.hash_id == hash_id).first()
                if not existing:
                    crime = Crime(**crime_data)
                    db.add(crime)
                    registros_cargados += 1
                    
            except Exception as e:
                print(f"Error procesando fila {index}: {e}")
                continue
        
        db.commit()
        return {
            "message": f"Se cargaron {registros_cargados} registros exitosamente",
            "total_filas": len(df),
            "archivo": file.filename
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error procesando archivo: {str(e)}")

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
