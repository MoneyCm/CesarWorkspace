from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from ..database import get_db

router = APIRouter(prefix="/geodatos", tags=["Geodatos"])

@router.get("")
def geodatos(
    db: Session = Depends(get_db),
    delito: str | None = None,
    inicio: date | None = None,
    fin: date | None = None,
    limit: int = Query(1000, ge=1, le=10000)
):
    # Defaults: last 90 days
    if not inicio or not fin:
        res = db.execute(text("SELECT now()::date AS hoy, (now()::date - INTERVAL '90 days')::date AS hace FROM now()")).first()
        hoy = res.hoy
        hace = res.hace
    else:
        hoy = fin
        hace = inicio

    filtro_delito = " AND delito = :delito" if delito else ""
    sql = f"""
    SELECT id, fecha, delito, barrio, zona, lat, lon
    FROM crimes
    WHERE fecha BETWEEN :inicio AND :fin {filtro_delito}
    AND lat IS NOT NULL AND lon IS NOT NULL
    ORDER BY fecha DESC
    LIMIT :limit
    """
    params = {"inicio": hace, "fin": hoy, "limit": limit}
    if delito: params["delito"] = delito

    rows = db.execute(text(sql), params).all()
    data = [dict(r._mapping) for r in rows]
    return {"count": len(data), "items": data}