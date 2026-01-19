from sqlalchemy import Column, Integer, Text, TIMESTAMP, Date, Time, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Fuente(Base):
    __tablename__ = "fuentes"
    id = Column(Integer, primary_key=True)
    nombre = Column(Text, nullable=False)
    responsable = Column(Text)
    canal = Column(Text)
    periodicidad = Column(Text)
    campos = Column(JSONB)
    created_at = Column(TIMESTAMP, server_default=func.now())

class IngestLog(Base):
    __tablename__ = "ingest_logs"
    id = Column(Integer, primary_key=True)
    fuente_id = Column(Integer, ForeignKey("fuentes.id"))
    filename = Column(Text)
    uploaded_by = Column(Text)
    uploaded_at = Column(TIMESTAMP, server_default=func.now())
    registros = Column(Integer)
    errores = Column(Integer)
    sha256 = Column(Text)

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True)
    fecha_hecho = Column(Date)
    hora = Column(Time)
    tipo_evento = Column(Text)
    modalidad = Column(Text)
    barrio = Column(Text)
    fuente_id = Column(Integer, ForeignKey("fuentes.id"))
    victima_sexo = Column(Text)
    victima_edad = Column(Integer)
    victima_pseudo = Column(Text)
    arma = Column(Text)
    geom = Column(Geometry(geometry_type='POINT', srid=4326))
