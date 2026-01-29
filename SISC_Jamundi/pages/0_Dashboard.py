import streamlit as st
import pandas as pd
import plotly.express as px
from db.database import get_kpis, get_monthly_stats

st.set_page_config(page_title="Dashboard | SISC Jamundí", page_icon="📊", layout="wide")

st.title("📊 Indicadores de Seguridad (KPIs)")
st.markdown("Análisis avanzado de la situación de convivencia y seguridad en Jamundí.")

# Filtros de fecha
col_f1, col_f2 = st.columns(2)
with col_f1:
    start_date = st.date_input("Fecha Inicio", value=pd.to_datetime("2024-01-01"))
with col_f2:
    end_date = st.date_input("Fecha Fin")

# Obtener datos
try:
    data = get_kpis(start_date, end_date)
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    # Fallback to dummy data if DB fails
    data = {"total": 0, "homicidios": 0, "tasa": 0.0}

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Incidentes", data["total"], help="Total de eventos registrados en el periodo")
with col2:
    st.metric("Total Homicidios", data["homicidios"], delta_color="inverse")
with col3:
    st.metric("Tasa Homicidios", f"{data['tasa']}", "per 100k hab", delta_color="inverse")

st.divider()

# Charts
st.subheader("📈 Evolución Temporal")
try:
    chart_data = get_monthly_stats(start_date, end_date)
    
    if not chart_data.empty:
        fig = px.line(chart_data, x='Mes', y='Incidentes', title="Tendencia Mensual de Delitos en Jamundí",
                     markers=True, line_shape="spline", color_discrete_sequence=["#1e3a8a"])
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para generar la tendencia temporal en este periodo.")
except Exception as e:
    st.error(f"Error generando gráfico: {e}")
