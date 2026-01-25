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
if raw_url.startswith("postgres://") or raw_url.startswith("postgresql://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg2://", 1)
    raw_url = raw_url.replace("postgresql://", "postgresql+psycopg2://", 1)

DATABASE_URL = raw_url

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True,  # Crucial for cloud databases like Supabase
    pool_recycle=300     # Recycle connections every 5 minutes
)

# Auto-create tables and handle migrations (PostgreSQL/SQLite)
from db.models import Base
from sqlalchemy import text
try:
    # 1. Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # 2. Universal Migration Logic (SQLite & Postgres)
    db_type = "postgres" if "postgres" in DATABASE_URL.lower() else "sqlite"
    print(f"🔍 Database: {db_type.upper()} detected. Checking schema synchronization...")
    
    with engine.begin() as conn:
        # Tables to check
        tables_to_migrate = ["questions", "skills"]
        new_cols = ["macro_dominio", "micro_competencia"]
        
        for table in tables_to_migrate:
            # Check existing columns
            if db_type == "sqlite":
                existing_cols = [row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()]
            else:
                # Postgres
                existing_cols = [row[0] for row in conn.execute(text(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}';")).fetchall()]
            
            for col in new_cols:
                if col not in existing_cols:
                    print(f"🔨 Adding column {col} to table {table}...")
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} VARCHAR;"))
        
        print("✅ Database schema synchronized successfully.")

except Exception as e:
    # In Streamlit Cloud, this will show up in the Logs (Manage App -> Logs)
    print(f"❌ DATABASE MIGRATION ERROR: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
