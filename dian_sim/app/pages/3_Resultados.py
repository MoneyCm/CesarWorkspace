import streamlit as st
import os, sys, datetime

# Add root to python path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# The instruction implies adding this block, but it already exists.
# If `import pandas as pd` was intended to be added, it would go here.
# For now, I will assume the instruction was to ensure the existing block is present.

from db.session import SessionLocal
from db.models import Question
from ui_utils import load_css, render_header, metric_card
from core.pdf_utils import generate_exam_pdf

st.set_page_config(page_title="Resultados | DIAN Sim", page_icon="📊", layout="wide")
load_css()
render_header(title="Resultados del Simulacro", subtitle="Análisis de tu desempeño reciente")
# v2.5.1 - Fix PDF Binary

if "last_results" not in st.session_state:
    st.info("No hay resultados recientes para mostrar.")
    with st.container():
         if st.button("⬅️ Volver al Inicio"):
             st.switch_page("app.py")
    st.stop()

data = st.session_state["last_results"]

# --- v2.5 CELEBRATION LOGIC ---
if data.get("new_achievements"):
    st.balloons()
    for ach in data["new_achievements"]:
        st.success(f"🏆 ¡LOGRO DESBLOQUEADO: **{ach}**!")

if data.get("rank_up"):
    st.snow()
    st.warning(f"👑 ¡ASCENSO DE RANGO! Ahora eres: **{data['rank_up']}**")
total = data["total"]
correct = data["correct"]
score = (correct / total) * 100

# Metric Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Puntaje Global", f"{score:.1f}%", f"{correct} de {total}")
with col2:
    metric_card("Puntos Ganados", f"+{data.get('points_earned', 0)}", "¡Buen trabajo!")
with col3:
    metric_card("Racha Actual", f"{data.get('new_streak', 0)}🔥", "Días seguidos")
with col4:
    metric_card("Tiempo", "N/A", "Minutos") # Pendiente cálculo exacto si se desea


st.divider()

# --- v2.5 PDF DOWNLOAD BUTTON ---
st.subheader("📄 Reporte de Desempeño")
db = SessionLocal()
q_ids = data["q_ids"]
answers = st.session_state.get("answers", {})

details = []
for qid in q_ids:
    q = db.query(Question).get(qid)
    details.append({
        "stem": q.stem,
        "user_ans": answers.get(qid, "N/A"),
        "correct_key": q.correct_key,
        "rationale": q.rationale
    })

try:
    pdf_bytes = generate_exam_pdf(data, details)
    st.download_button(
        label="📥 Descargar Reporte en PDF",
        data=pdf_bytes,
        file_name=f"Resultado_Simulacro_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
except Exception as e:
    st.error(f"Error generando PDF: {e}")

st.divider()

st.subheader("📝 Detalle de Respuestas")

db = SessionLocal()
q_ids = data["q_ids"]
answers = st.session_state.get("answers", {})

for i, qid in enumerate(q_ids):
    q = db.query(Question).get(qid)
    user_ans = answers.get(qid, "N/A")
    is_right = (user_ans == q.correct_key)
    
    icon = "✅" if is_right else "❌"
    color_class = "color: #4CAF50" if is_right else "color: #D90000"
    
    with st.expander(f"{icon} Pregunta {i+1}: {q.topic}"):
        st.markdown(f"<div class='dian-card' style='border:none; padding:0;'>", unsafe_allow_html=True)
        st.markdown(f"**Enunciado:** {q.stem}")
        
        col_ans1, col_ans2 = st.columns(2)
        
        # Get option texts
        opts = q.options_json if q.options_json else {}
        user_text = opts.get(user_ans, "Sin responder")
        correct_text = opts.get(q.correct_key, "")

        with col_ans1:
            st.markdown(f"**Tu respuesta:** <span style='{color_class}; font-weight:bold;'>{user_ans}) {user_text}</span>", unsafe_allow_html=True)
        with col_ans2:
            st.markdown(f"**Correcta:** <span style='color: #4CAF50; font-weight:bold;'>{q.correct_key}) {correct_text}</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        if not is_right:
            st.info(f"💡 **Explicación:** {q.rationale}")
        else:
            st.caption(f"💡 **Explicación:** {q.rationale}")
            
        st.caption(f"ID: {q.question_id} | Competencia: {q.competency}")
        st.markdown("</div>", unsafe_allow_html=True)

db.close()

if st.button("🏠 Inicio", type="primary"):
    st.switch_page("app.py")
