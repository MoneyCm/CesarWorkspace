import streamlit as st
import sys
import os

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.session import SessionLocal

st.set_page_config(
    page_title="DIAN Sim",
    page_icon="🇨🇴",
    layout="wide"
)

st.title("🇨🇴 Simulator - Concurso DIAN")

st.markdown("""
Bienvenido al simulador de entrenamiento para la DIAN.

**Características:**
- 🧠 **Entrenamiento Adaptativo**: El sistema prioriza tus debilidades.
- 📂 **Banco de Preguntas**: Gestión local y deduplicación.
- 📊 **Analíticas**: Revisa tu progreso por competencias.

Selecciona una opción en el menú lateral para comenzar.
""")

# Initialize session state for generic use
if "user_session" not in st.session_state:
    st.session_state["user_session"] = str(os.urandom(8))
