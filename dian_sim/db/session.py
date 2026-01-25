import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dian_sim.db"))

# Priority: Streamlit Secrets > Environment Variable > Local SQLite
try:
    import streamlit as st
    raw_url = st.secrets.get("DATABASE_URL", os.getenv("DATABASE_URL", f"sqlite:///{db_path}"))
except:
    raw_url = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")

# Ensure PostgreSQL uses the correct driver for SQLAlchemy 2.0+
if raw_url.startswith("postgresql://"):
    raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://")

DATABASE_URL = raw_url

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Crucial for cloud databases like Supabase
    pool_recycle=300     # Recycle connections every 5 minutes
)

# --- AUTO-CREACIÓN DE TABLAS ---
from db.models import Base
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass 

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
