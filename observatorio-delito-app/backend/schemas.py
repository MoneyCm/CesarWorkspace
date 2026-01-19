from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, time

class CrimeOut(BaseModel):
    id: int
    fecha: date
    hora: Optional[time] = None
    delito: str
    subdelito: Optional[str] = None
    municipio: Optional[str] = None
    zona: Optional[str] = None
    barrio: Optional[str] = None
    corregimiento: Optional[str] = None
    genero_victima: Optional[str] = None
    edad_victima: Optional[int] = None
    arma: Optional[str] = None
    modalidad: Optional[str] = None
    cantidad: int = 1
    lat: Optional[float] = None
    lon: Optional[float] = None

    class Config:
        from_attributes = True

class SerieItem(BaseModel):
    periodo: str = Field(..., description="YYYY-MM o YYYY")
    total: int

class SerieResponse(BaseModel):
    agrupacion: str
    delito: Optional[str] = None
    inicio: str
    fin: str
    serie: List[SerieItem]