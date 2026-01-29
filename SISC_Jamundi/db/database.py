import streamlit as st
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from .models import Base, Event, EventType
import os
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la base de datos (Supabase ready)
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    # Fallback local para desarrollo si no hay variable de entorno
    DB_URL = "postgresql://sisc_user:sisc_password@localhost:5432/sisc_jamundi"

@st.cache_resource
def get_engine():
    # Supabase requiere SSL a veces, SQLAlchemy lo maneja bien con el query param ?sslmode=require
    return create_engine(DB_URL)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def get_kpis(start_date=None, end_date=None):
    session = get_session()
    try:
        query = session.query(func.count(Event.id))
        if start_date:
            query = query.filter(Event.fecha_hecho >= start_date)
        if end_date:
            query = query.filter(Event.fecha_hecho <= end_date)
        
        total_events = query.scalar() or 0
        
        # Tasa de homicidios usando la nueva columna descripcion_conducta
        homicidios = session.query(func.count(Event.id)).filter(Event.descripcion_conducta.ilike("%HOMICIDIO%"))
        if start_date:
            homicidios = homicidios.filter(Event.fecha_hecho >= start_date)
        if end_date:
            homicidios = homicidios.filter(Event.fecha_hecho <= end_date)
        
        h_count = homicidios.scalar() or 0
        
        # Hurto a personas
        hurtos = session.query(func.count(Event.id)).filter(Event.descripcion_conducta.ilike("%HURTO A PERSONAS%"))
        if start_date:
            hurtos = hurtos.filter(Event.fecha_hecho >= start_date)
        if end_date:
            hurtos = hurtos.filter(Event.fecha_hecho <= end_date)
        
        hu_count = hurtos.scalar() or 0
        
        # Tasa (Homicidios por cada 100k hab - Jamundí aprox 160,000 hab)
        poblacion = 160000
        tasa = (h_count / poblacion) * 100000 if h_count > 0 else 0
        
        return {
            "total": f"{total_events:,}",
            "homicidios": f"{h_count:,}",
            "hurtos": f"{hu_count:,}",
            "tasa": round(tasa, 1)
        }
    finally:
        session.close()

import difflib

def find_best_match(target, candidates, threshold=0.8):
    """Encuentra la mejor coincidencia difusa para un nombre de columna."""
    matches = difflib.get_close_matches(target, candidates, n=1, cutoff=threshold)
    return matches[0] if matches else None

def save_events(df):
    """Procesa un DataFrame SEM 48 e inserta registros en la DB con mapeo inteligente."""
    session = get_session()
    report = {"success": 0, "errors": [], "mappings": {}}
    
    # Atributos del modelo objetivo (lo que espera SQLAlchemy)
    model_attributes = {
        "juris_depto": ["juris.metropolitana / depto", "departamento", "depto"],
        "descripcion_conducta": ["descripcion_conducta", "delito", "conducta"],
        "hechos_id": ["hechos_id", "id_hecho", "id"],
        "anio": ["año", "anio", "year"],
        "mes": ["mes", "month"],
        "fecha_hecho": ["fecha_hecho", "fecha"],
        "nro_semana": ["nosemana", "semana", "nro_semana"],
        "semana_hecho": ["semana_hecho"],
        "dia_semana": ["dia_semana", "dia"],
        "intervalos_hora": ["intervalos_hora", "rango_hora"],
        "genero": ["genero", "sexo"],
        "municipio": ["hechos.municipio", "municipio"],
        "barrio": ["barrios_hecho", "barrio"],
        "juris_distrito": ["juris.distrito / seccional", "distrito"],
        "juris_estacion": ["juris.estación / área", "estacion"],
        "juris_cai": ["juris.cai", "cai"],
        "juris_dependencia": ["juris.dependencia"],
        "modalidad": ["modalidad"],
        "armas_medios": ["armas_medios", "arma"],
        "zona": ["zona"],
        "movil_agresor": ["movil_agresor"],
        "movil_victima": ["movil_victima"],
        "edad": ["edad"],
        "causas_lesion_muerte_persona": ["causas_lesion_muerte_persona", "causa_muerte"],
        "spoa_caracterizacion": ["spoa_caracterizacion"],
        "spoa_caracterizacion_id": ["spoa_caracterizacion_id"],
        "clase_sitio": ["clase_sitio", "sitio"],
        "conductas_especiales": ["conductas_especiales"],
        "turno": ["turno"],
        "hora24": ["hora24"],
        "nro_fuente_hecho": ["nro_fuente_hecho"],
        "hora_hecho": ["hora_hecho", "hora"],
        "agrupa_edad_persona": ["agrupa_edad_persona"],
        "spoa_motivacion": ["spoa_motivacion", "motivacion"],
        "grupos_vulnerables_persona": ["grupos_vulnerables_persona"],
        "medio_conocimiento": ["medio_conocimiento"],
        "clase_empleado_descripcion": ["clase_empleado_descripcion"],
        "cargo_persona": ["cargo_persona"],
        "profesiones": ["profesiones", "profesion"],
        "grado_instruccion_persona": ["grado_instruccion_persona", "escolaridad"],
        "pais_persona": ["pais_persona", "pais"],
        "tipo_identificacion": ["tipo_identificacion"],
        "unidad_apoya": ["unidad_apoya"],
        "razon_social": ["razon_social"],
        "nivel_gestion_estatal": ["nivel gestion_estatal"],
        "count_2024": ["2.024", "count_2024"],
        "count_2025": ["2.025", "count_2025"]
    }

    try:
        # 1. Normalización de columnas del CSV a minúsculas y limpieza
        csv_columns = [str(c).lower().strip() for c in df.columns]
        df.columns = csv_columns

        # 2. Análisis Inteligente de Mapeo
        final_mapping = {} # model_attr -> csv_col
        for model_attr, synonyms in model_attributes.items():
            # Intentar coincidencia exacta con sinónimos
            match = next((s for s in synonyms if s in csv_columns), None)
            
            # Si no hay exacta, intentar difusa
            if not match:
                match = find_best_match(model_attr.replace("_", " "), csv_columns)
                if not match and synonyms:
                    match = find_best_match(synonyms[0], csv_columns)
            
            if match:
                final_mapping[model_attr] = match

        report["mappings"] = final_mapping
        print(f"DEBUG: Mapeo Detectado: {final_mapping}")

        # 3. Inserción de Filas
        total_rows = len(df)
        print(f"DEBUG: Iniciando inserción de {total_rows} filas.")
        for index, row in df.iterrows():
            try:
                event_data = {}
                for model_attr, csv_col in final_mapping.items():
                    val = row.get(csv_col)
                    
                    # Limpiar y transformar tipos
                    if pd.isna(val) or val == "":
                        val = None
                    elif model_attr == "fecha_hecho":
                        val = pd.to_datetime(val).date()
                    elif model_attr == "hora_hecho":
                        val = pd.to_datetime(val).time()
                    elif model_attr in ["hechos_id", "anio", "nro_semana", "hora24", "nro_fuente_hecho", "count_2024", "count_2025"]:
                        try: val = int(float(val))
                        except: val = 0
                    
                    event_data[model_attr] = val

                new_event = Event(**event_data)
                session.add(new_event)
                session.commit() # Commit granular para evitar fallos de batch
                report["success"] += 1
                
                if index % 100 == 0:
                    print(f"DEBUG: Insertadas {index} / {total_rows} filas...")

            except Exception as e:
                session.rollback()
                report["errors"].append(f"Fila {index+2}: {str(e)}")
        
    except Exception as e:
        import traceback
        error_msg = f"Error fatal en proceso de ingesta: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        report["errors"].append(f"Error fatal: {str(e)}")
    finally:
        session.close()
    return report

def get_events_geojson(start_date=None, end_date=None):
    session = get_session()
    try:
        # Adaptado a las nuevas columnas
        sql = """
            SELECT json_build_object(
                'type', 'FeatureCollection',
                'features', json_agg(ST_AsGeoJSON(t.*)::json)
            )
            FROM (
                SELECT e.id, e.fecha_hecho, e.barrio, e.descripcion_conducta as category, e.location_geom
                FROM events e
                WHERE e.location_geom IS NOT NULL
        """
        params = {}
        if start_date:
            sql += " AND e.fecha_hecho >= :start"
            params["start"] = start_date
        if end_date:
            sql += " AND e.fecha_hecho <= :end"
            params["end"] = end_date
        
        sql += ") t;"
        
        result = session.execute(text(sql), params).scalar()
        return result
    finally:
        session.close()

def get_monthly_stats(start_date=None, end_date=None):
    session = get_session()
    try:
        month_expr = func.to_char(Event.fecha_hecho, 'YYYY-MM')
        query = session.query(
            month_expr.label('mes'),
            func.count(Event.id).label('total')
        ).group_by(month_expr).order_by('mes')
        
        if start_date:
            query = query.filter(Event.fecha_hecho >= start_date)
        if end_date:
            query = query.filter(Event.fecha_hecho <= end_date)
            
        result = query.all()
        return pd.DataFrame([{"Mes": r.mes, "Incidentes": r.total} for r in result])
    finally:
        session.close()
