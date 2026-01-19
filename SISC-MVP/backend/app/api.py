from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from . import auth as auth_mod
from .db import SessionLocal
from .models import Fuente, Evento
from .schemas import FuenteIn, FuenteOut, EventoIn
from .ingest import router as ingest_router
from .reportes import router as reportes_router
from .models import User

router = APIRouter()
router.include_router(auth_mod.router)
router.include_router(ingest_router)
router.include_router(reportes_router)

@router.post('/users')
def create_user(payload: dict, admin: auth_mod.User = Depends(auth_mod.require_role('admin'))):
    db = SessionLocal()
    from .utils import hash_password
    from .models import User as UserModel
    u = db.query(UserModel).filter(UserModel.username == payload.get('username')).first()
    if u:
        raise HTTPException(status_code=400, detail='User exists')
    new = UserModel(username=payload.get('username'), password_hash=hash_password(payload.get('password')), role=payload.get('role','analyst'))
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"id": new.id, "username": new.username, "role": new.role}

@router.post('/fuentes', response_model=FuenteOut)
def create_fuente(payload: FuenteIn):
    db = SessionLocal()
    f = Fuente(**payload.dict())
    db.add(f)
    db.commit()
    db.refresh(f)
    return f

@router.get('/fuentes')
def list_fuentes():
    db = SessionLocal()
    return db.query(Fuente).all()

@router.get('/eventos')
def list_eventos(limit: int = 100):
    db = SessionLocal()
    q = db.query(Evento).limit(limit).all()
    out = []
    for e in q:
        out.append({
            "id": e.id,
            "fecha_hecho": str(e.fecha_hecho),
            "tipo_evento": e.tipo_evento,
            "barrio": e.barrio
        })
    return out

@router.get('/indicadores')
def indicadores():
    db = SessionLocal()
    # simple counts by tipo_evento
    res = db.execute("SELECT tipo_evento, count(*) as cnt FROM eventos GROUP BY tipo_evento ORDER BY cnt DESC").fetchall()
    return [{"tipo_evento": r[0], "count": r[1]} for r in res]

@router.get('/publico/agregados')
def publico_agregados():
    db = SessionLocal()
    res = db.execute("SELECT date_trunc('month', fecha_hecho) as mes, tipo_evento, count(*) FROM eventos GROUP BY mes, tipo_evento ORDER BY mes DESC").fetchall()
    out = []
    for r in res:
        out.append({"mes": str(r[0]), "tipo_evento": r[1], "count": r[2]})
    return out
