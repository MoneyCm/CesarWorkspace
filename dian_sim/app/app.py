import streamlit as st
import sys
import os

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal
from ui_utils import load_css, render_header

st.set_page_config(
    page_title="DIAN Sim - Simulador Oficial",
    page_icon="🇨🇴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Global CSS
load_css()

# Render Custom Header
render_header()

st.markdown("""
<div class="dian-card">
    <h2 style="color: var(--dian-red); margin-bottom: 20px;">Bienvenido al Simulador de Mérito</h2>
    <p style="font-size: 1.1rem; margin-bottom: 15px;">
        Esta herramienta te permite entrenar para las pruebas de selección de la DIAN utilizando un motor adaptativo que detecta y refuerza tus áreas débiles.
    </p>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px;">
        <div class="dian-card" style="background: rgba(255,255,255,0.03);">
            <h3>🧠 Entrenamiento Adaptativo</h3>
            <p style="color: #ccc;">El sistema aprende de tus errores y te presenta preguntas desafiantes para optimizar tu tiempo de estudio.</p>
        </div>
        <div class="dian-card" style="background: rgba(255,255,255,0.03);">
            <h3>📂 Banco Gestión Local</h3>
            <p style="color: #ccc;">Sube tus propias preguntas o genera nuevas con IA. Todo se guarda localmente en tu equipo.</p>
        </div>
        <div class="dian-card" style="background: rgba(255,255,255,0.03);">
            <h3>📊 Analíticas Detalladas</h3>
            <p style="color: #ccc;">Monitorea tu progreso por Eje (Funcional, Comportamental) y temas específicos en tiempo real.</p>
        </div>
    </div>
</div>

<div style="text-align: center; margin-top: 40px; color: #666;">
    Selecciona <b>"Nuevo Simulacro"</b> en el menú lateral para comenzar.
</div>
""", unsafe_allow_html=True)

# Initialize session state for generic use
if "user_session" not in st.session_state:
    st.session_state["user_session"] = str(os.urandom(8))
