import streamlit as st
import time
from db.session import SessionLocal
from db.models import Question, Attempt, Skill
import datetime
from core.adaptive import calculate_mastery_update, update_priority
from core.gamification import update_user_stats
from core.rank_system import get_rank_info
from core.generators.llm import LLMGenerator
from ui_utils import load_css, render_header

# --- v2.2: Exam Termination Function ---
def finalize_exam(db, q_ids, answers_dict):
    """Processes all answers and saves to DB."""
    try:
        correct_count = 0
        total_q = len(q_ids)
        
        for qid in q_ids:
            q_obj = db.query(Question).get(qid)
            key_chosen = answers_dict.get(qid, "NONE")
            
            is_right = (key_chosen == q_obj.correct_key)
            if is_right:
                correct_count += 1
                
            # Create Attempt
            att = Attempt(
                question_id=qid,
                chosen_key=key_chosen,
                is_correct=is_right,
                created_at=datetime.datetime.utcnow()
            )
            db.add(att)
            
            # Update Skills
            skill = db.query(Skill).filter_by(track=q_obj.track, competency=q_obj.competency, topic=q_obj.topic).first()
            if not skill:
                skill = Skill(track=q_obj.track, competency=q_obj.competency, topic=q_obj.topic, mastery_score=0.0, priority_weight=1.0)
                db.add(skill)
                db.flush()
            
            skill.mastery_score = calculate_mastery_update(is_right, skill.mastery_score)
            skill.priority_weight = update_priority(skill.priority_weight, is_right)
            skill.last_seen = datetime.datetime.utcnow()
        
        # Update Gamification
        stats, points_earned, new_achievements, rank_up = update_user_stats(db, datetime.date.today(), correct_count, total_q)
        db.commit()
        
        # Store results for next page
        st.session_state["exam_mode"] = False
        st.session_state["last_results"] = {
            "total": total_q,
            "correct": correct_count,
            "score": (correct_count / total_q) * 100 if total_q > 0 else 0,
            "q_ids": q_ids,
            "points_earned": points_earned,
            "new_streak": stats.current_streak,
            "rank_up": rank_up,
            "new_achievements": [a.name for a in new_achievements]
        }
        return True
    except Exception as e:
        db.rollback()
        st.error(f"❌ Error al guardar resultados: {e}")
        return False

# --- v2.1 NEW: Automatic Timer Setup ---
if "exam_start_time" not in st.session_state:
    st.session_state["exam_start_time"] = time.time()
    st.session_state["tutor_explanation"] = None

st.set_page_config(page_title="Simulacro en Curso", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")
load_css()

# --- FOCUS MODE CSS ---
st.markdown("""
<style>
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .main .block-container {
        max-width: 850px !important;
        padding-top: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

render_header(title="Simulacro en Curso")

if "exam_mode" not in st.session_state or not st.session_state["exam_mode"]:
    st.warning("No hay un examen activo. Ve a 'Nuevo Simulacro'.")
    st.stop()

q_ids = st.session_state["exam_questions"]
current_idx = st.session_state["current_idx"]
total_q = len(q_ids)

db = SessionLocal()
current_q_id = q_ids[current_idx]
question = db.query(Question).filter(Question.question_id == current_q_id).first()

if "total_time_limit" not in st.session_state:
    st.session_state["total_time_limit"] = 60 * total_q 

elapsed = time.time() - st.session_state.get("exam_start_time", time.time())
time_left = max(0, int(st.session_state["total_time_limit"] - elapsed))

with st.container():
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        progress = (current_idx / total_q)
        st.progress(progress, text=f"Progreso: {int(progress*100)}%")
    with col_prog2:
        color = "#D90000" if time_left < (total_q * 10) else "#ffa500"
        st.markdown(f"""
        <div class="floating-timer" id="timer-container" style='position: fixed; top: 80px; right: 20px; background: white; padding: 10px 20px; border-radius: 12px; border: 2px solid {color}; box-shadow: 0 4px 15px rgba(0,0,0,0.2); z-index: 9999; text-align: center; min-width: 120px; transition: all 0.3s ease;'>
            <span style='font-size:0.7rem; color:#666; font-weight: bold; text-transform: uppercase;'>Tiempo Restante</span><br>
            <div id="countdown" style='font-size:1.8rem; font-weight:800; color:{color}; font-family: monospace;'>{time_left // 60}:{time_left % 60:02d}</div>
        </div>
        """, unsafe_allow_html=True)

if time_left <= 0:
    st.error("⏳ ¡TIEMPO AGOTADO! Finaliza el examen para guardar tus resultados.")

st.markdown('<div class="dian-card">', unsafe_allow_html=True)
st.caption(f"Eje: {question.track} | Competencia: {question.competency}")
st.markdown(f"### {question.topic}")

stem_text = question.stem
if "SITUACIÓN:" in stem_text and "PREGUNTA:" in stem_text:
    parts = stem_text.split("PREGUNTA:")
    st.markdown(f"<div style='background: rgba(230, 0, 0, 0.03); border-left: 6px solid var(--dian-red); padding: 24px; border-radius: 4px 20px 20px 4px; margin-bottom: 24px; backdrop-filter: blur(5px);'>{parts[0]}</div><div class='question-stem'>{parts[1]}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='question-stem'>{stem_text}</div>", unsafe_allow_html=True)

options = question.options_json 
opts_keys = list(options.keys())
opts_values = [f"{k}) {v}" for k,v in options.items()]
existing_ans = st.session_state["answers"].get(current_q_id)
index_ans = opts_keys.index(existing_ans) if existing_ans else None
selected_val = st.radio("Selecciona tu respuesta:", opts_values, index=index_ans, key=f"q_{current_idx}")
st.markdown('</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 4, 1])
with col1:
        if st.button("⬅️ Anterior", use_container_width=True):
            st.session_state["current_idx"] -= 1
            st.session_state["tutor_explanation"] = None 
            st.rerun()
with col2:
    if st.button("🤖 Tutor IA", use_container_width=True):
        st.info("El tutor está analizando...") # Simplificado para el ejemplo
with col3:
    if selected_val:
        st.session_state["answers"][current_q_id] = selected_val.split(")")[0]
    if current_idx < total_q - 1:
        if st.button("Siguiente ➡️", type="primary", use_container_width=True):
            st.session_state["current_idx"] += 1
            st.rerun()
    else:
        finish_label = "🏁 Finalizar" if time_left > 0 else "⌛ Ver Resultados"
        if st.button(finish_label, type="primary", use_container_width=True):
            if finalize_exam(db, q_ids, st.session_state["answers"]):
                db.close()
                st.switch_page("pages/3_Resultados.py")

db.close()
