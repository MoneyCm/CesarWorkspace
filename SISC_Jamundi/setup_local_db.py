import sys
import os
from sqlalchemy import create_engine, text
from db.models import Base
import pandas as pd

# Configuración local por defecto
DB_URL = os.getenv("DATABASE_URL", "postgresql://sisc_user:sisc_password@localhost:5432/sisc_jamundi")

def init_db():
    print(f"--- Iniciando Configuración de Base de Datos Local ---")
    print(f"Conectando a: {DB_URL}")
    try:
        engine = create_engine(DB_URL)
        
        with engine.connect() as conn:
            print("Verificando extensiones (PostGIS y UUID)...")
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
            conn.commit()
            print("✅ Extensiones listas.")
            
        print("Limpiando base de datos y creando tablas basadas en el nuevo formato SEM 48...")
        # Forzar la recreación para asegurar el formato SEM 48
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        print("✅ Tablas creadas correctamente.")
        print("\n¡Todo listo! Ya puedes abrir Streamlit y empezar a importar datos.")
        
    except Exception as e:
        print(f"\n❌ ERROR: No se pudo conectar a PostgreSQL local.")
        print(f"Detalle del error: {e}")
        print("\n--- PASOS PARA SOLUCIONAR ---")
        print("1. ¿Está instalado PostgreSQL? Si no, descárgalo e instálalo.")
        print("2. ¿El servicio está corriendo? Revisa en 'Servicios' de Windows si 'postgresql' dice 'En ejecución'.")
        print("3. ¿El usuario y la contraseña son correctos? Por defecto el código usa:")
        print("   Usuario: sisc_user")
        print("   Contraseña: sisc_password")
        print("   Base de Datos: sisc_jamundi")
        print("\nSi usas datos diferentes, crea un archivo .env y pon: DATABASE_URL=postgresql://usuario:pass@localhost:5432/db_nombre")

if __name__ == "__main__":
    init_db()
