import streamlit as st
import os, sys

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from db.session import SessionLocal
from db.models import Question, Skill
from core.adaptive import select_questions_for_simulation
from ui_utils import load_css, render_header
from core.profiles import PROFILES, get_profile_topics

def get_db():
    return SessionLocal()

# UI Setup
st.set_page_config(page_title="Nuevo Simulacro | DIAN Sim", page_icon="📝", layout="wide")
load_css()
render_header(title="Nuevo Simulacro", subtitle="Configura los parámetros de tu sesión de estudio")

with st.container():
    st.markdown('<div class="dian-card">', unsafe_allow_html=True)
    
    # Tabs for Mode
    tab_manual, tab_profile = st.tabs(["🎛️ Configuración Manual", "👤 Preparación por Cargo"])
    
    # --- MANUAL MODE ---
    with tab_manual:
        with st.form("manual_sim_form"):
            st.markdown("**Configuración de Sesión**")
            num_questions = st.slider("Cantidad de preguntas", 5, 200, 20, key="num_q_manual")
            
            st.markdown("<br>**Filtros Opcionales** (Dejar vacío para incluir todo)", unsafe_allow_html=True)
            
            # Get available options with error handling
            try:
                db_temp = get_db()
                all_tracks = [t[0] for t in db_temp.query(Question.track).distinct().all() if t[0]]
                all_competencies = [t[0] for t in db_temp.query(Question.competency).distinct().all() if t[0]]
                all_topics = [t[0] for t in db_temp.query(Question.topic).distinct().all() if t[0]]
                db_temp.close()
            except Exception as e:
                st.error(f"Error de conexión con la base de datos: {e}")
                st.info("Intenta recargar la página o verifica tu conexión a internet.")
                all_tracks, all_competencies, all_topics = [], [], []

            col1, col2 = st.columns(2)
            with col1:
                track_filter = st.multiselect("Eje (Track)", sorted(all_tracks))
                difficulty_filter = st.multiselect("Dificultad", [1, 2, 3], format_func=lambda x: {1: "🟢 Básico", 2: "🟡 Intermedio", 3: "🔴 Avanzado"}[x])
            with col2:
                competency_filter = st.multiselect("Competencia", sorted(all_competencies))
            
            topic_filter = st.multiselect("Tema Específico", sorted(all_topics))
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                only_situational_manual = st.toggle("Solo preguntas situacionales", value=True, help="Filtra para mostrar solo preguntas que plantean casos prácticos.", key="only_sit_manual")
            with col_t2:
                hardcore_mode = st.toggle("🛡️ Modo Hardcore DIAN", value=False, help="Simula el examen real: mezcla temas, oculta respuestas hasta el final y aplica tiempos estrictos.")
            
            submitted_manual = st.form_submit_button("🚀 Iniciar Simulacro Manual", type="primary")

    # --- PROFILE MODE ---
    with tab_profile:
        st.info("Selecciona el cargo al que aspiras para enfocar el estudio en sus funciones y competencias específicas.")
        
        selected_profile_name = st.selectbox("Seleccionar Cargo / Perfil", list(PROFILES.keys()))
        
        if selected_profile_name:
            profile_data = PROFILES[selected_profile_name]
            st.markdown(f"**Descripción:** {profile_data['description']}")
            
            profile_topics = get_profile_topics(selected_profile_name)
            
            with st.expander("Ver Temas y Competencias del Perfil", expanded=False):
                st.write("**Temas Funcionales:**")
                st.write(", ".join(profile_data["functional_tracks"].get("FUNCIONAL", [])))
                st.write("**Competencias Comportamentales:**")
                st.write(", ".join(profile_data["behavioral_competencies"]))
            
            st.markdown("---")
            col_p1, col_p2 = st.columns([1, 1])
            with col_p1:
                num_questions_profile = st.slider("Cantidad de preguntas", 5, 200, 20, key="num_q_profile")
            with col_p2:
                difficulty_profile = st.multiselect("Nivel de Dificultad", [1, 2, 3], default=[1, 2, 3], format_func=lambda x: {1: "🟢 Básico", 2: "🟡 Intermedio", 3: "🔴 Avanzado"}[x], key="diff_profile")

            # Check availability
            try:
                db_chk = get_db()
                query_chk = db_chk.query(Question).filter(Question.topic.in_(profile_topics))
                if difficulty_profile:
                    query_chk = query_chk.filter(Question.difficulty.in_(difficulty_profile))
                available_count = query_chk.count()
                db_chk.close()
                
                if available_count < 5:
                    st.warning(f"⚠️ Solo hay {available_count} preguntas disponibles para estos temas en tu banco local.")
                    st.markdown("Recomendación: Usa el **Generador IA** para crear preguntas específicas para este cargo.")
                    if st.button("Ir al Generador IA (Preguntas Situacionales)"):
                        st.session_state["ai_default_text"] = profile_data["raw_text"]
                        st.session_state["ai_default_topic"] = selected_profile_name
                        st.session_state["ai_default_diff"] = difficulty_profile[0] if len(difficulty_profile) == 1 else 2
                        st.switch_page("pages/4_Generador_IA.py")
                else:
                    st.success(f"✅ Hay {available_count} preguntas disponibles para este perfil.")
            except Exception as e:
                st.error("⚠️ Error al consultar el banco. Es posible que la base de datos se esté actualizando.")
                available_count = 0
        
        st.markdown("---")
        only_situational = st.toggle("Solo preguntas situacionales (Nuevas)", value=True, help="Filtra para mostrar solo preguntas que plantean casos prácticos generados con el nuevo sistema.")

        if st.button("🚀 Iniciar Simulacro por Perfil", type="primary", disabled=(available_count == 0)):
             submitted_profile = True
        else:
             submitted_profile = False

    st.markdown('</div>', unsafe_allow_html=True)

# LOGIC HANDLER
final_query_filters = {}
run_sim = False

if submitted_manual:
    run_sim = True
    final_query_filters = {
        "tracks": track_filter,
        "competencies": competency_filter,
        "topics": topic_filter,
        "difficulties": difficulty_filter,
        "only_situational": only_situational_manual,
        "hardcore": hardcore_mode
    }

if submitted_profile and selected_profile_name:
    run_sim = True
    # For profile, we filter strictly by the topics defined in the profile
    # Or broad filter by track? Better specific topics + competencies
    profile_topics = get_profile_topics(selected_profile_name)
    final_query_filters = {
        "topics": profile_topics,
        "difficulties": difficulty_profile,
        "only_situational": only_situational
    }
    num_questions = num_questions_profile

if run_sim:
    try:
        db = get_db()
        
        # 1. Fetch Candidates
        query = db.query(Question)
        
        if final_query_filters.get("tracks"):
            query = query.filter(Question.track.in_(final_query_filters["tracks"]))
        if final_query_filters.get("competencies"):
            query = query.filter(Question.competency.in_(final_query_filters["competencies"]))
        if final_query_filters.get("topics"):
            query = query.filter(Question.topic.in_(final_query_filters["topics"]))
        if final_query_filters.get("difficulties"):
            query = query.filter(Question.difficulty.in_(final_query_filters["difficulties"]))
        if final_query_filters.get("only_situational"):
            query = query.filter(Question.stem.ilike("%SITUACIÓN%"))
        
        all_candidates = query.all()
        
        # 2. Fetch Skills for Adaptive Logic
        skills = db.query(Skill).all()
        skills_map = {(s.track, s.competency, s.topic): s for s in skills}
        
        # 3. Select Questions
        selected = select_questions_for_simulation(all_candidates, skills_map, n=num_questions)
        
        if not selected:
            st.error("No hay preguntas disponibles con estos criterios.")
        else:
            # Initialize Exam Session State
            st.session_state["exam_mode"] = True
            st.session_state["exam_questions"] = [q.question_id for q in selected] # Store IDs
            st.session_state["current_idx"] = 0
            st.session_state["answers"] = {} # {q_id: chosen_key}
            st.session_state["hardcore_mode"] = final_query_filters.get("hardcore", False)
            
            st.switch_page("pages/2_Ejecucion.py")
    except Exception as e:
        st.error(f"⚠️ Error al preparar el simulacro: {e}")
        st.info("Es posible que la base de datos se esté sincronizando con el nuevo Protocolo 2667. Intenta de nuevo en unos segundos.")

# If logic for exam is running (legacy check, but kept for safety)
if st.session_state.get("exam_mode"):
    st.switch_page("pages/2_Ejecucion.py")
