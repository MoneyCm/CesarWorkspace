from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.models import get_db, Event, EventType
import pandas as pd
import io
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Recibe un archivo Excel/CSV, procesa los datos y los inserta en PostGIS.
    Reporta éxitos y fallos individuales por fila.
    """
    contents = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Formato de archivo no soportado")

        # Normalizar nombres de columnas a minúsculas
        df.columns = [c.lower().strip() for c in df.columns]

        required_cols = ['fecha', 'hora', 'delito', 'latitud', 'longitud']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"Faltan columnas requeridas: {required_cols}")

        report = {
            "total": len(df),
            "success_count": 0,
            "error_count": 0,
            "errors": []
        }

        for index, row in df.iterrows():
            row_num = index + 2 # +1 for 0-index, +1 for header row
            try:
                # 1. Validar y normalizar Categoría
                delito_nombre = str(row.get('delito', '')).upper().strip()
                if not delito_nombre:
                    raise ValueError("El campo 'delito' no puede estar vacío")

                event_type = db.query(EventType).filter(EventType.category == delito_nombre).first()
                if not event_type:
                    event_type = EventType(category=delito_nombre, is_delicto=True)
                    db.add(event_type)
                    db.flush()

                # 2. Parsing de Fecha y Hora con validación
                try:
                    occ_date = pd.to_datetime(row['fecha']).date()
                    occ_time = pd.to_datetime(row['hora']).time()
                except Exception:
                    raise ValueError(f"Formato de fecha/hora inválido (Fecha: {row['fecha']}, Hora: {row['hora']})")

                # 3. Datos de Geometría
                try:
                    lng = float(row['longitud'])
                    lat = float(row['latitud'])
                    if not (-180 <= lng <= 180) or not (-90 <= lat <= 90):
                        raise ValueError("Coordenadas fuera de rango válido")
                except (ValueError, TypeError):
                    raise ValueError(f"Coordenadas inválidas (Lat: {row.get('latitud')}, Lng: {row.get('longitud')})")

                # 4. Crear el evento
                new_event = Event(
                    external_id=str(row.get('id_externo', uuid.uuid4())),
                    event_type_id=event_type.id,
                    occurrence_date=occ_date,
                    occurrence_time=occ_time,
                    barrio=str(row.get('barrio', 'Sin especificar')),
                    descripcion=str(row.get('descripcion', '')),
                    estado=str(row.get('estado', 'Abierto'))
                )
                db.add(new_event)
                db.flush()

                # 5. Insertar geometría PostGIS
                db.execute(
                    func.text("UPDATE events SET location_geom = ST_SetSRID(ST_Point(:lng, :lat), 4326) WHERE id = :id"),
                    {"lng": lng, "lat": lat, "id": new_event.id}
                )
                
                report["success_count"] += 1

            except Exception as row_err:
                report["error_count"] += 1
                report["errors"].append({"fila": row_num, "error": str(row_err)})

        db.commit()
        return {
            "status": "success" if report["error_count"] == 0 else "partial_success",
            "message": f"Carga completada: {report['success_count']} éxitos, {report['error_count']} errores.",
            "report": report
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error fatal procesando el archivo: {str(e)}")
