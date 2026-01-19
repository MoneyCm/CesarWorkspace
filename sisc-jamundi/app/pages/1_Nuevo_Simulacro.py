import streamlit as st
from db.session import SessionLocal
from db.models import Question, Skill
from core.adaptive import select_questions_for_simulation

def get_db():
    return SessionLocal()

st.header("📝 Nuevo Simulacro")

with st.form("new_sim_form"):
    num_questions = st.slider("Cantidad de preguntas", 5, 50, 10)
    
    # Filters
    st.caption("Filtros (Dejar vacío para todo)")
    
    # Get available options for filters
    db_temp = get_db()
    all_tracks = [t[0] for t in db_temp.query(Question.track).distinct().all()]
    all_competencies = [t[0] for t in db_temp.query(Question.competency).distinct().all()]
    all_topics = [t[0] for t in db_temp.query(Question.topic).distinct().all()]
    db_temp.close()

    col1, col2 = st.columns(2)
    with col1:
        track_filter = st.multiselect("Eje (Track)", sorted(all_tracks))
    with col2:
        competency_filter = st.multiselect("Competencia", sorted(all_competencies))
    
    topic_filter = st.multiselect("Tema Específico", sorted(all_topics))
    
    submitted = st.form_submit_button("Iniciar Simulacro")

if submitted:
    db = get_db()
    
    # 1. Fetch Candidates
    query = db.query(Question)
    if track_filter:
        query = query.filter(Question.track.in_(track_filter))
    if competency_filter:
        query = query.filter(Question.competency.in_(competency_filter))
    if topic_filter:
        query = query.filter(Question.topic.in_(topic_filter))
    
    all_candidates = query.all()
    
    # 2. Fetch Skills for Adaptive Logic
    skills = db.query(Skill).all()
    skills_map = {(s.track, s.competency, s.topic): s for s in skills}
    
    # 3. Select Questions
    selected = select_questions_for_simulation(all_candidates, skills_map, n=num_questions)
    
    if not selected:
        st.error("No hay preguntas disponibles con estos filtros.")
    else:
        # Initialize Exam Session State
        st.session_state["exam_mode"] = True
        st.session_state["exam_questions"] = [q.question_id for q in selected] # Store IDs
        st.session_state["current_idx"] = 0
        st.session_state["answers"] = {} # {q_id: chosen_key}
        
        st.rerun()

# If logic for exam is running
if st.session_state.get("exam_mode"):
    st.switch_page("pages/2_Ejecucion.py")
