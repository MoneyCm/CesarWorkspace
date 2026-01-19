import streamlit as st
import time
from db.session import SessionLocal
from db.models import Question, Attempt, Skill
import datetime
from core.adaptive import calculate_mastery_update, update_priority

st.set_page_config(layout="wide")

if "exam_mode" not in st.session_state or not st.session_state["exam_mode"]:
    st.warning("No hay un examen activo. Ve a 'Nuevo Simulacro'.")
    st.stop()

q_ids = st.session_state["exam_questions"]
current_idx = st.session_state["current_idx"]
total_q = len(q_ids)

db = SessionLocal()
current_q_id = q_ids[current_idx]
question = db.query(Question).filter(Question.question_id == current_q_id).first()

# Progress
progress = (current_idx / total_q)
st.progress(progress, text=f"Pregunta {current_idx + 1} de {total_q}")

# Display Question
st.subheader(f"Tema: {question.topic}")
st.markdown(f"**{question.stem}**")

# Options
options = question.options_json # Dict
opts_keys = list(options.keys())
opts_values = [f"{k}) {v}" for k,v in options.items()]

# Restore previous answer if any
existing_ans = st.session_state["answers"].get(current_q_id)
index_ans = opts_keys.index(existing_ans) if existing_ans else None

selected_val = st.radio("Selecciona una opción:", opts_values, index=index_ans, key=f"q_{current_idx}")

# Navigation
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
    if current_idx > 0:
        if st.button("⬅️ Anterior"):
            st.session_state["current_idx"] -= 1
            st.rerun()

with col3:
    # Save current selection
    if selected_val:
        selected_key = selected_val.split(")")[0] # Extract "A" from "A) Text"
        st.session_state["answers"][current_q_id] = selected_key

    if current_idx < total_q - 1:
        if st.button("Siguiente ➡️"):
            st.session_state["current_idx"] += 1
            st.rerun()
    else:
        if st.button("🏁 Finalizar"):
            # Process Results
            # Save Attempts to DB
            
            for qid in q_ids:
                q_obj = db.query(Question).get(qid)
                key_chosen = st.session_state["answers"].get(qid)
                is_right = (key_chosen == q_obj.correct_key)
                
                # Create Attempt
                att = Attempt(
                    question_id=qid,
                    chosen_key=key_chosen if key_chosen else "NONE",
                    is_correct=is_right,
                    created_at=datetime.datetime.utcnow()
                )
                db.add(att)
                
                # Update Skills
                # Find or Create Skill
                skill = db.query(Skill).filter_by(
                    track=q_obj.track, 
                    competency=q_obj.competency,
                    topic=q_obj.topic
                ).first()
                
                if not skill:
                    skill = Skill(
                        track=q_obj.track, 
                        competency=q_obj.competency,
                        topic=q_obj.topic,
                        mastery_score=0.0,
                        priority_weight=1.0
                    )
                    db.add(skill)
                    db.flush() # get id
                
                skill.mastery_score = calculate_mastery_update(is_right, skill.mastery_score)
                skill.priority_weight = update_priority(skill.priority_weight, is_right)
                skill.last_seen = datetime.datetime.utcnow()
                
            db.commit()
            
            # Reset state and go to results
            st.session_state["exam_mode"] = False
            st.session_state["last_results"] = {
                "total": total_q,
                "correct": sum(1 for qid in q_ids if st.session_state["answers"].get(qid) == db.query(Question).get(qid).correct_key),
                "q_ids": q_ids
            }
            db.close()
            st.success("Examen finalizado. Redirigiendo...")
            time.sleep(1)
            st.switch_page("pages/3_Resultados.py")
