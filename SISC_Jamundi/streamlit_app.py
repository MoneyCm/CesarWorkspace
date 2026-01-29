import streamlit as st
import os
import sys
from datetime import date

# Añadir el directorio raíz al path para importar db
sys.path.append(os.getcwd())
from db.database import get_kpis

# Page config
st.set_page_config(
    page_title="SISC Jamundí | Observatorio de Seguridad",
    page_icon="🛡️",
    layout="wide",
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .dian-header {
        color: #1e3a8a;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="dian-header">🛡️ SISC Jamundí: Observatorio de Seguridad</h1>', unsafe_allow_html=True)
    
    st.sidebar.title("Navegación")
    st.sidebar.info("Bienvenido al Sistema de Información para la Seguridad y la Convivencia.")
    
    # Obtener KPIs reales
    current_year = date.today().year
    kpis = get_kpis(start_date=date(current_year, 1, 1))
    
    # Dashboard summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"Total Eventos {current_year}", kpis["total"])
    with col2:
        st.metric("Tasa Homicidios", kpis["tasa"], help="Proyectada por cada 100.000 habitantes")
    with col3:
        st.metric("Hurto Personas", kpis["hurtos"])
    with col4:
        st.metric("Homicidios", kpis["homicidios"])

    st.divider()
    
    st.subheader("📊 Tendencia de Seguridad")
    st.info("Aquí se mostrará el análisis temporal de los delitos en Jamundí.")
    
    st.write("Seleccione una opción en el menú de la izquierda para comenzar.")

if __name__ == "__main__":
    main()
