import pandas as pd
import sys
import os
from datetime import date, time

# Añadir el directorio raíz al path para importar db
sys.path.append(os.getcwd())

from db.database import save_events, get_kpis
from sqlalchemy import text, create_engine

def test_ingestion():
    print("--- Iniciando Prueba de Ingestión SEM 48 ---")
    
    # 1. Crear datos de prueba (Simulando columnas del CSV SEM 48)
    data = {
        "DEPARTAMENTO": ["VALLE", "VALLE"],
        "CONDUCTA": ["HOMICIDIO", "HURTO A PERSONAS"],
        "FECHA": ["2026-01-15", "2026-01-20"],
        "HORA": ["14:30:00", "09:00:00"],
        "MUNICIPIO": ["JAMUNDI", "JAMUNDI"],
        "CANTIDAD": [1, 1],
        "BARRIO": ["CENTRO", "ALFAGUARA"],
        "ZONA": ["URBANA", "URBANA"],
        "MODALIDAD": ["ARMA DE FUEGO", "ATRACO"]
    }
    df = pd.DataFrame(data)
    
    print(f"Enviando DataFrame con {len(df)} filas a save_events...")
    report = save_events(df)
    
    print(f"\nResultado Ingesta:")
    print(f"✅ Exitosos: {report['success']}")
    print(f"❌ Errores: {len(report['errors'])}")
    
    if report['errors']:
        print("\nDetalle de errores:")
        for err in report['errors']:
            print(f"- {err}")
            
    print(f"\n📍 Mapeo detectado:")
    for key, val in report['mappings'].items():
        print(f"  {key} -> {val}")
    
    # 2. Verificar KPIs
    print("\n--- Verificando KPIs dinámicos ---")
    current_year = date.today().year
    kpis = get_kpis(start_date=date(current_year, 1, 1))
    print(f"KPIs para el año {current_year}:")
    print(f"  Total Eventos: {kpis['total']}")
    print(f"  Homicidios: {kpis['homicidios']}")
    print(f"  Hurtos: {kpis['hurtos']}")
    print(f"  Tasa (proyectada): {kpis['tasa']}")

if __name__ == "__main__":
    try:
        test_ingestion()
    except Exception as e:
        print(f"ERROR DURANTE LA PRUEBA: {e}")
