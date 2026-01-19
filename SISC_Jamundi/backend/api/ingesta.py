from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from db.models import get_db, Event, EventType, Source
import pandas as pd
import io
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Recibe un archivo Excel/CSV, procesa los datos y los inserta en PostGIS.
    Columnas esperadas: fecha, hora, delito, latitud, longitud, id_externo
    """
    contents = await file.read()
    
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Formato de archivo no soportado")

        # Validar columnas mínimas
        required_cols = ['fecha', 'hora', 'delito', 'latitud', 'longitud']
        if not all(col in df.columns for col in required_cols):
            raise HTTPException(status_code=400, detail=f"Faltan columnas requeridas: {required_cols}")

        processed_count = 0
        for index, row in df.iterrows():
            # 1. Buscar o crear el tipo de evento
            delito_nombre = str(row['delito']).upper().strip()
            event_type = db.query(EventType).filter(EventType.category == delito_nombre).first()
            if not event_type:
                event_type = EventType(category=delito_nombre, is_delicto=True)
                db.add(event_type)
                db.flush()

            # 2. Crear el evento
            occ_date = pd.to_datetime(row['fecha']).date()
            occ_time = pd.to_datetime(row['hora']).time()

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

            # 3. Insertar geometría PostGIS
            geom_sql = "UPDATE events SET location_geom = ST_SetSRID(ST_Point(:lng, :lat), 4326) WHERE id = :id"
            db.execute(func.text(geom_sql), {"lng": float(row['longitud']), "lat": float(row['latitud']), "id": new_event.id})
            
            processed_count += 1

        db.commit()
        return {"status": "success", "message": f"Se procesaron {processed_count} registros correctamente."}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error procesando el archivo: {str(e)}")
