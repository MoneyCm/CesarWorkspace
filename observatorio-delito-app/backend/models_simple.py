from sqlalchemy import Column, Integer, String, Date, Time, Float, Text, Index, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_mixin
from database_simple import Base

@declarative_mixin
class TimestampMixin:
    created_at = Column(String, default=func.now())
    updated_at = Column(String, default=func.now(), onupdate=func.now())

class Crime(Base, TimestampMixin):
    __tablename__ = "crimes"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=True)               # Policía, Fiscalía, etc.
    incident_id = Column(String(128), nullable=True)         # ID externo opcional
    hash_id = Column(String(64), nullable=False)             # Hash de unicidad
    fecha = Column(Date, index=True, nullable=False)
    hora = Column(Time, nullable=True)
    delito = Column(String(120), index=True, nullable=False)
    subdelito = Column(String(120), nullable=True)
    municipio = Column(String(120), default="Jamundí", index=True)
    zona = Column(String(20), nullable=True)                 # urbano/rural
    barrio = Column(String(160), nullable=True)
    corregimiento = Column(String(160), nullable=True)
    genero_victima = Column(String(20), nullable=True)
    edad_victima = Column(Integer, nullable=True)
    arma = Column(String(80), nullable=True)
    modalidad = Column(String(120), nullable=True)
    cantidad = Column(Integer, default=1)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    extras = Column(Text, nullable=True)  # JSON as text for SQLite

    __table_args__ = (
        UniqueConstraint('hash_id', name='uq_crimes_hash_id'),
        Index('idx_crimes_periodo', 'fecha', 'delito'),
    )

