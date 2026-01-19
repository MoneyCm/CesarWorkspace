from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import csv
import io
from .db import SessionLocal
from .models import Fuente, IngestLog, Evento
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
import hashlib

router = APIRouter()

@router.post('/ingesta/cargar')
def upload_csv(fuente_id: int, file: UploadFile = File(...), uploaded_by: str = "anonymous"):
    content = file.file.read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(content))
    db = SessionLocal()
    total = 0
    errors = 0
    for row in reader:
        try:
            lat = row.get('lat') or row.get('latitude')
            lon = row.get('lon') or row.get('longitude')
            geom = None
            if lat and lon:
                try:
                    p = Point(float(lon), float(lat))
                    geom = from_shape(p, srid=4326)
                except Exception:
                    geom = None
            # seudonimización mínima: hash de fuente + sexo + edad
            victima_sexo = row.get('victima_sexo') or None
            victima_edad = row.get('victima_edad') or None
            pseudo = None
            try:
                pseudo_source = f"{fuente_id}:{victima_sexo}:{victima_edad}"
                pseudo = hashlib.sha256(pseudo_source.encode('utf-8')).hexdigest()
            except Exception:
                pseudo = None

            ev = Evento(
                fecha_hecho=row.get('fecha_hecho'),
                hora=row.get('hora') or None,
                tipo_evento=row.get('tipo_evento'),
                modalidad=row.get('modalidad'),
                barrio=row.get('barrio'),
                fuente_id=fuente_id,
                victima_sexo=victima_sexo,
                victima_edad=victima_edad or None,
                victima_pseudo=pseudo,
                arma=row.get('arma') or None,
                geom=geom
            )
            db.add(ev)
            total += 1
        except Exception:
            errors += 1
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    log = IngestLog(fuente_id=fuente_id, filename=file.filename, uploaded_by=uploaded_by, registros=total, errores=errors)
    db.add(log)
    db.commit()
    return {"registros": total, "errores": errors}
