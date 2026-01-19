from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from ..models import Crime

router = APIRouter(prefix="/delitos", tags=["Delitos"])

@router.get("/disponibles")
def delitos_disponibles(db: Session = Depends(get_db)):
    q = select(Crime.delito).distinct().order_by(Crime.delito.asc())
    rows = db.execute(q).scalars().all()
    return {"delitos": rows}