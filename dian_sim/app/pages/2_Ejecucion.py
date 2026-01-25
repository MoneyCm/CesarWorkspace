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
        eje_results = {} # {"FUNCIONAL": [correct, total], ...}
        
        for qid in q_ids:
            q_obj = db.query(Question).get(qid)
            key_chosen = answers_dict.get(qid, "NONE")
            
            is_right = (key_chosen == q_obj.correct_key)
            if is_right:
                correct_count += 1
                
            # Track by Eje for weighting
            track = q_obj.track or "FUNCIONAL"
            if track not in eje_results:
                eje_results[track] = [0, 0]
            eje_results[track][1] += 1
            if is_right:
                eje_results[track][0] += 1

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
        
        # Breakdown into dict of tuples for update_user_stats
        breakdown = {k: (v[0], v[1]) for k,v in eje_results.items()}
        
        # Update Gamification with official weighting
        stats, points_earned, new_achievements, rank_up, is_passed = update_user_stats(db, datetime.date.today(), correct_count, total_q, eje_breakdown=breakdown)
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
            "is_passed": is_passed,
            "new_achievements": [a.name for a in new_achievements],
            "breakdown": breakdown
        }
        return True
    except Exception as e:
        db.rollback()
        st.error(f"❌ Error al guardar resultados: {e}")
        return False

# --- UI Setup ---
if "exam_start_time" not in st.session_state:
    st.session_state["exam_start_time"] = time.time()
    st.session_state["tutor_explanation"] = None
    st.session_state["last_answer_time"] = time.time()

st.set_page_config(page_title="Simulacro en Curso", page_icon="📝", layout="wide", initial_sidebar_state="collapsed")
load_css()

# --- FOCUS MODE CSS ---
st.markdown("""
<style>
    /* Hide top header and sidebar decoration */
    [data-testid="stHeader"] { visibility: hidden; }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    
    /* Center content more aggressively for focus */
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

# --- v2.0 NEW: Chronometer / Timer ---
if "total_time_limit" not in st.session_state:
    # GOA Rule: 2.5 minutes per situational question
    st.session_state["total_time_limit"] = 150 * total_q 

# Calculate real-time remaining
elapsed = time.time() - st.session_state.get("exam_start_time", time.time())
time_left = max(0, int(st.session_state["total_time_limit"] - elapsed))

# Hardcore Mode Check
is_hardcore = st.session_state.get("hardcore_mode", False)

# Progress Area
with st.container():
    col_prog1, col_prog2 = st.columns([3, 1])
    with col_prog1:
        progress = (current_idx / total_q)
        label = "🚨 MODO REALISTA (HARDCORE)" if is_hardcore else f"Progreso: {int(progress*100)}%"
        st.progress(progress, text=label)
    with col_prog2:
        # --- JS DYNAMIC CHRONOMETER ---
        color = "#D90000" if time_left < (total_q * 20) else "#ffa500"
        
        st.markdown(f"""
        <div class="floating-timer" id="timer-container" style='
            position: fixed;
            top: 80px;
            right: 20px;
            background: white;
            padding: 10px 20px;
            border-radius: 12px;
            border: 2px solid {color};
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 9999;
            text-align: center;
            min-width: 120px;
        '>
            <span style='font-size:0.7rem; color:#666; font-weight: bold; text-transform: uppercase;'>Tiempo Restante</span><br>
            <div id="countdown" style='font-size:1.8rem; font-weight:800; color:{color}; font-family: monospace;'>
                {time_left // 60}:{time_left % 60:02d}
            </div>
        </div>

        <style>
            @media (max-width: 768px) {{
                .floating-timer {{
                    top: 10px !important;
                    right: 10px !important;
                    padding: 5px 10px !important;
                    min-width: 80px !important;
                }}
                #countdown {{
                    font-size: 1.2rem !important;
                }}
                .floating-timer span {{
                    font-size: 0.5rem !important;
                }}
            }}
        </style>

        <script>
        (function() {{
            var timeLeft = {time_left};
            var display = document.getElementById('countdown');
            var parent = document.getElementById('timer-container');
            
            var timer = setInterval(function() {{
                if (timeLeft <= 0) {{
                    clearInterval(timer);
                    display.innerHTML = "0:00";
                    display.style.color = "red";
                    parent.style.borderColor = "red";
                    
                    // --- AUTO SUBMIT TRIGGER ---
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {{
                        if (buttons[i].innerText.includes('TRIGGER_TIMEOUT')) {{
                            buttons[i].click();
                            break;
                        }}
                    }}
                    return;
                }}
                
                timeLeft--;
                var mins = Math.floor(timeLeft / 60);
                var secs = timeLeft % 60;
                display.innerHTML = mins + ":" + (secs < 10 ? "0" : "") + secs;
                
                if (timeLeft < 60) {{
                    display.style.color = "#D90000";
                    parent.style.borderColor = "#D90000";
                    if (timeLeft % 2 == 0) {{
                        parent.style.boxShadow = "0 0 15px rgba(217,0,0,0.4)";
                    }} else {{
                        parent.style.boxShadow = "0 4px 15px rgba(0,0,0,0.2)";
                    }}
                }}
            }}, 1000);
        }})();
        </script>
        """, unsafe_allow_html=True)

if time_left <= 0:
    st.error("⏳ ¡TIEMPO AGOTADO! Finaliza el examen para guardar tus resultados.")


# Question Card
st.markdown('<div class="dian-card">', unsafe_allow_html=True)
st.caption(f"Eje: {question.track} | Macro: {question.macro_dominio or 'General'}")
st.markdown(f"### {question.topic}")

# Format situational questions
stem_text = question.stem
if "SITUACIÓN:" in stem_text and "PREGUNTA:" in stem_text:
    try:
        parts = stem_text.split("PREGUNTA:")
        sit_part = parts[0].replace("SITUACIÓN:", "").strip()
        q_part = parts[1].strip()
        
        st.markdown(f"""
        <div style="background: rgba(230, 0, 0, 0.03); border-left: 6px solid var(--dian-red); padding: 24px; border-radius: 4px 20px 20px 4px; margin-bottom: 24px; backdrop-filter: blur(5px);">
            <div style="color: var(--dian-red); text-transform: uppercase; font-size: 0.75rem; font-weight: 800; letter-spacing: 0.1em; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span style="background: var(--dian-red); width: 8px; height: 8px; border-radius: 50%;"></span>
                Caso / Situación Laboral
            </div>
            <div style="font-size: 1.1rem; line-height: 1.7; color: #334155;">{sit_part}</div>
        </div>
        <div class='question-stem'>{q_part}</div>
        """, unsafe_allow_html=True)
    except:
        st.markdown(f"<div class='question-stem'>{stem_text}</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<div class='question-stem'>{stem_text}</div>", unsafe_allow_html=True)

# Options
options = question.options_json 
opts_keys = list(options.keys())
opts_values = [f"{k}) {v}" for k,v in options.items()]

# Restore previous answer if any
existing_ans = st.session_state["answers"].get(current_q_id)
index_ans = opts_keys.index(existing_ans) if existing_ans else None

selected_val = st.radio("Selecciona la mejor respuesta:", opts_values, index=index_ans, key=f"q_{current_idx}")

st.markdown('</div>', unsafe_allow_html=True) # End Card

# Navigation Buttons
col1, col2, col3 = st.columns([1, 4, 1])

with col1:
        if st.button("⬅️ Anterior", use_container_width=True):
            st.session_state["current_idx"] = max(0, st.session_state["current_idx"] - 1)
            st.session_state["tutor_explanation"] = None # Clear tutor on change
            st.rerun()

with col2:
    # --- v2.0 NEW: IA Tutor Button ---
    if not is_hardcore:
        if st.button("🤖 Tutor IA (Socrático)", use_container_width=True, help="El tutor te guiará para encontrar la respuesta sin regalártela."):
            with st.spinner("Analizando..."):
                try:
                    # Get provider and key from secrets (Cloud) or env (Local)
                    import os
                    provider = st.secrets.get("DEFAULT_PROVIDER", os.getenv("DEFAULT_PROVIDER", "gemini")).lower()
                    api_key = st.secrets.get(f"{provider.upper()}_API_KEY", os.getenv(f"{provider.upper()}_API_KEY"))
                    
                    if api_key:
                        from core.generators.llm import LLMGenerator
                        gen = LLMGenerator(provider, api_key)
                        # Use the new explain_question method
                        q_data = {
                            "stem": question.stem,
                            "options_json": question.options_json,
                            "correct_key": question.correct_key,
                            "rationale": question.rationale
                        }
                        st.session_state["tutor_explanation"] = gen.explain_question(q_data)
                    else:
                        st.warning("⚠️ API Key no configurada.")
                except Exception as e:
                    st.error(f"Error del Tutor: {e}")

    if st.session_state.get("tutor_explanation"):
        st.info(st.session_state["tutor_explanation"])


with col3:
    # Speed Alert Logic
    current_time = time.time()
    time_spent = current_time - st.session_state.get("last_answer_time", current_time)
    
    # Save current selection
    if selected_val:
        selected_key = selected_val.split(")")[0] # Extract "A" from "A) Text"
        st.session_state["answers"][current_q_id] = selected_key

    if current_idx < total_q - 1:
        if st.button("Siguiente ➡️", type="primary", use_container_width=True):
            if time_spent < 45 and not is_hardcore: # Warning if too fast
                st.toast("⚠️ Estás respondiendo muy rápido. El análisis situacional requiere más tiempo.", icon="⏱️")
            st.session_state["current_idx"] += 1
            st.session_state["last_answer_time"] = time.time()
            st.session_state["tutor_explanation"] = None
            st.rerun()
    else:
        finish_label = "🏁 Finalizar" if time_left > 0 else "⌛ Resultados"
        if st.button(finish_label, type="primary", use_container_width=True, key="finish_btn_manual"):
            if finalize_exam(db, q_ids, st.session_state["answers"]):
                db.close()
                st.balloons()
                time.sleep(1)
                st.switch_page("pages/3_Resultados.py")

# --- v2.2: Hidden Auto-Submit Handler ---
# This button is clicked by JS when time hits 0
if st.button("TRIGGER_TIMEOUT", key="timeout_trigger", help="Internal"):
    if finalize_exam(db, q_ids, st.session_state["answers"]):
        db.close()
        st.switch_page("pages/3_Resultados.py")

# Hide the timeout trigger button via CSS
st.markdown("""
<style>
    div[data-testid="stButton"] button:has(div:contains("TRIGGER_TIMEOUT")) {
        display: none !important;
    }
    /* Fallback for some browsers */
    button[key="timeout_trigger"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

db.close()
