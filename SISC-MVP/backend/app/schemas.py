from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str

class FuenteIn(BaseModel):
    nombre: str
    responsable: Optional[str]
    canal: Optional[str]
    periodicidad: Optional[str]
    campos: Optional[dict]

class FuenteOut(FuenteIn):
    id: int

class EventoIn(BaseModel):
    fecha_hecho: date
    hora: Optional[time]
    tipo_evento: str
    modalidad: Optional[str]
    barrio: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    fuente: Optional[str]
    victima_sexo: Optional[str]
    victima_edad: Optional[int]
    arma: Optional[str]
