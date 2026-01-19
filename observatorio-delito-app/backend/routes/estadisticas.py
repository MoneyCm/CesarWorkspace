from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from ..database import get_db

router = APIRouter(prefix="/estadisticas", tags=["Estadísticas"])

@router.get("")
def estadisticas(
    db: Session = Depends(get_db),
    delito: str | None = None,
    inicio: date | None = None,
    fin: date | None = None,
    agrupacion: str = Query("mensual", pattern="^(mensual|anual)$"),
    zona: str | None = Query(None),
    barrio: str | None = Query(None)
):
    # Defaults: last 365 days if not provided
    if not inicio or not fin:
        res = db.execute(text("SELECT now()::date AS hoy, (now()::date - INTERVAL '365 days')::date AS hace FROM now()")).first()
        hoy = res.hoy
        hace = res.hace
    else:
        hoy = fin
        hace = inicio

    group_expr = "to_char(date_trunc('month', fecha), 'YYYY-MM')" if agrupacion == "mensual" else "to_char(date_trunc('year', fecha), 'YYYY')"

    base_sql = f"""
    SELECT {group_expr} AS periodo, SUM(cantidad)::int AS total
    FROM crimes
    WHERE fecha BETWEEN :inicio AND :fin
    {{filtro_delito}}
    {{filtro_zona}}
    {{filtro_barrio}}
    GROUP BY 1
    ORDER BY 1
    """
    filtro_delito = " AND delito = :delito" if delito else ""
    filtro_zona = " AND zona = :zona" if zona else ""
    filtro_barrio = " AND barrio = :barrio" if barrio else ""

    sql = base_sql.replace("{filtro_delito}", filtro_delito).replace("{filtro_zona}", filtro_zona).replace("{filtro_barrio}", filtro_barrio)
    params = {"inicio": hace, "fin": hoy}
    if delito: params["delito"] = delito
    if zona: params["zona"] = zona
    if barrio: params["barrio"] = barrio

    rows = db.execute(text(sql), params).all()
    serie = [{"periodo": r.periodo, "total": r.total} for r in rows]
    return {"agrupacion": agrupacion, "delito": delito, "inicio": str(hace), "fin": str(hoy), "serie": serie}