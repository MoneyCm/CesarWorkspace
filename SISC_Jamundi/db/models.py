from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import os

# Base para los modelos
Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role_id = Column(Integer, ForeignKey("roles.id"))
    is_active = Column(Boolean, default=True)

class EventType(Base):
    __tablename__ = "event_types"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(100))
    is_delicto = Column(Boolean, default=True)

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # --- Columnas del Formato SEM 48 ---
    juris_depto = Column(String(100))
    descripcion_conducta = Column(String(255))
    hechos_id = Column(Integer, index=True)
    anio = Column(Integer)
    mes = Column(String(20))
    fecha_hecho = Column(Date, nullable=False, index=True)
    nro_semana = Column(Integer)
    semana_hecho = Column(String(50))
    dia_semana = Column(String(20))
    intervalos_hora = Column(String(50))
    genero = Column(String(20))
    municipio = Column(String(100))
    barrio = Column(String(100))
    juris_distrito = Column(String(100))
    juris_estacion = Column(String(100))
    juris_cai = Column(String(100))
    juris_dependencia = Column(String(100))
    modalidad = Column(String(100))
    armas_medios = Column(String(100))
    zona = Column(String(50))
    movil_agresor = Column(String(100))
    movil_victima = Column(String(100))
    edad = Column(String(20))
    causas_lesion_muerte_persona = Column(String(255))
    spoa_caracterizacion = Column(Text)
    spoa_caracterizacion_id = Column(String(50))
    clase_sitio = Column(String(100))
    conductas_especiales = Column(String(100))
    turno = Column(String(20))
    hora24 = Column(Integer)
    nro_fuente_hecho = Column(Integer)
    hora_hecho = Column(Time, nullable=False)
    agrupa_edad_persona = Column(String(50))
    spoa_motivacion = Column(String(255))
    grupos_vulnerables_persona = Column(String(100))
    medio_conocimiento = Column(String(100))
    clase_empleado_descripcion = Column(String(100))
    cargo_persona = Column(String(100))
    profesiones = Column(String(100))
    grado_instruccion_persona = Column(String(100))
    pais_persona = Column(String(50))
    tipo_identificacion = Column(String(50))
    unidad_apoya = Column(String(100))
    razon_social = Column(String(100))
    nivel_gestion_estatal = Column(String(100))
    count_2024 = Column(Integer)
    count_2025 = Column(Integer)
    
    # Campo Legacy/Relacionales
    event_type_id = Column(Integer, ForeignKey("event_types.id"))
    estado = Column(String(50), default="Abierto")
    descripcion_adicional = Column(Text)
    
    event_type = relationship("EventType")
