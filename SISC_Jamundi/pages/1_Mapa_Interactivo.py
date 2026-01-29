import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from db.database import get_events_geojson
import json

st.set_page_config(page_title="Mapa Interactivo | SISC", page_icon="📍", layout="wide")

st.title("📍 Mapa de Calor y Eventos")
st.markdown("Visualización geográfica de los incidentes en el municipio basada en la base de datos central.")

# Filtros en el sidebar
st.sidebar.header("Filtros de Mapa")
start_date = st.sidebar.date_input("Fecha Inicio", value=pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("Fecha Fin")

# Obtener GeoJSON real
try:
    geojson_data = get_events_geojson(start_date, end_date)
    
    if geojson_data and geojson_data.get("features"):
        st.sidebar.success(f"Cargados {len(geojson_data['features'])} eventos.")
    else:
        st.sidebar.warning("No hay eventos con coordenadas para este periodo.")
        geojson_data = None
except Exception as e:
    st.error(f"Error cargando mapa: {e}")
    geojson_data = None

# Crear el mapa base (Jamundí)
m = folium.Map(location=[3.2625, -76.5411], zoom_start=13, tiles="cartodbpositron")

# Agregar datos si existen
if geojson_data:
    folium.GeoJson(
        geojson_data,
        name="Eventos Jamundí",
        tooltip=folium.GeoJsonTooltip(fields=["category", "barrio", "fecha_hecho"], aliases=["Delito:", "Barrio:", "Fecha:"]),
        popup=folium.GeoJsonPopup(fields=["category", "barrio"]),
        marker=folium.CircleMarker(radius=5, color="red", fill=True, fill_opacity=0.6)
    ).add_to(m)

st_folium(m, width=1200, height=600)
