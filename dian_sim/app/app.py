import streamlit as st
import sys
import os

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from db.models import UserStats
from ui_utils import load_css, render_header
try:
    from core.rank_system import get_rank_info
except ImportError:
    # Manual path fallback
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from core.rank_system import get_rank_info
except Exception as e:
    st.error(f"Error cargando el sistema de rangos: {e}")
    def get_rank_info(pts): return {"name": "Error", "color": "gray", "icon": "❓"}, None

st.set_page_config(
    page_title="DIAN Sim - Simulador Oficial",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- v2.0 NEW: Sidebar Gamification Info ---
db_s = SessionLocal()
try:
    stats_s = db_s.query(UserStats).first()
    if stats_s:
        rank, next_rank = get_rank_info(stats_s.total_points)
        
        # Calculate progress to next rank
        if next_rank:
            total_needed = next_rank["threshold"] - rank["threshold"]
            current_progress = stats_s.total_points - rank["threshold"]
            pct = min(100, int((current_progress / total_needed) * 100))
        else:
            pct = 100
            
        st.sidebar.markdown(f"""
<div class="dian-card" style='padding: 20px; text-align: center; margin-bottom: 10px; border-top: 3px solid {rank["color"]};'>
    <div style='font-size: 0.7rem; color: var(--text-muted); font-weight: 800; text-transform: uppercase; letter-spacing: 2px;'>Rango Actual</div>
    <div style='font-size: 2.5rem; margin: 5px 0;'>{rank["icon"]}</div>
    <div style='font-size: 1.1rem; font-weight: 800; color: {rank["color"]}; margin-bottom: 5px;'>{rank["name"]}</div>
    <div style='background: rgba(0,0,0,0.05); height: 8px; border-radius: 4px; margin: 10px 0; overflow: hidden;'>
        <div style='background: {rank["color"]}; width: {pct}%; height: 100%; transition: width 0.5s ease;'></div>
    </div>
    <div style='font-size: 0.7rem; color: var(--text-muted);'>
        {stats_s.total_points} / {next_rank["threshold"] if next_rank else "MAX"} PTS
    </div>
    <hr style="margin: 15px 0; opacity: 0.1;">
    <div style="display: flex; justify-content: space-around;">
        <div style="text-align: center;">
            <div style="font-size: 1.2rem;">🔥</div>
            <div style="font-size: 0.8rem; font-weight: 700;">{stats_s.current_streak}</div>
            <div style="font-size: 0.6rem; color: var(--text-muted);">RACHA</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 1.2rem;">🏆</div>
            <div style="font-size: 0.8rem; font-weight: 700;">{stats_s.max_streak}</div>
            <div style="font-size: 0.6rem; color: var(--text-muted);">MÁXIMA</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
except Exception as e:
    st.sidebar.warning("⚠️ Error cargando estadísticas. Cierra la terminal y vuelve a ejecutar run_app.bat.")
db_s.close()


# Inject Global CSS
load_css()

# Render Custom Header
render_header()

# Introduction Card
st.markdown('<div class="dian-card">', unsafe_allow_html=True)
st.markdown('<div class="dian-card-header">Bienvenido al Ecosistema de Estudio</div>', unsafe_allow_html=True)
st.markdown('<h1 style="margin-top: 0;">Impulsa tu Carrera en la DIAN</h1>', unsafe_allow_html=True)
st.markdown('<p style="font-size: 1.15rem; color: var(--text-muted); line-height: 1.6;">Prepárate con la herramienta de simulación más avanzada, diseñada para adaptarse a tu ritmo y fortalecer tus competencias legales.</p>', unsafe_allow_html=True)

# Grid of features
st.markdown("""
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 30px; margin-top: 50px; margin-bottom: 20px;">
    <div style="background: rgba(255,255,255,0.4); border: 1px solid rgba(255,255,255,0.8); border-radius: 20px; padding: 25px; transition: all 0.3s ease;">
        <div style="font-size: 2.5rem; margin-bottom: 15px;">🧠</div>
        <h4 style="margin-bottom: 10px;">Entrenamiento Adaptativo</h4>
        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.5;">Algoritmos inteligentes que priorizan tus áreas de mejora para un estudio guiado.</p>
    </div>
    <div style="background: rgba(255,255,255,0.4); border: 1px solid rgba(255,255,255,0.8); border-radius: 20px; padding: 25px; transition: all 0.3s ease;">
        <div style="font-size: 2.5rem; margin-bottom: 15px;">🤖</div>
        <h4 style="margin-bottom: 10px;">Tutoría IA Socrática</h4>
        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.5;">Domina la lógica legal detrás de cada situación con nuestro experto virtual.</p>
    </div>
    <div style="background: rgba(255,255,255,0.4); border: 1px solid rgba(255,255,255,0.8); border-radius: 20px; padding: 25px; transition: all 0.3s ease;">
        <div style="font-size: 2.5rem; margin-bottom: 15px;">📊</div>
        <h4 style="margin-bottom: 10px;">Analítica Visual</h4>
        <p style="font-size: 0.95rem; color: var(--text-muted); line-height: 1.5;">Monitorea tu crecimiento con radares de competencia y métricas de racha.</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 40px; color: var(--text-muted);">
    Selecciona <b>"Nuevo Simulacro"</b> en el menú lateral para comenzar tu sesión.
</div>
""", unsafe_allow_html=True)

# Initialize session state for generic use
if "user_session" not in st.session_state:
    st.session_state["user_session"] = str(os.urandom(8))
