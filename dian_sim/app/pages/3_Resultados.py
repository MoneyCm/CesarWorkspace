import streamlit as st
from db.session import SessionLocal
from db.models import Question
from ui_utils import load_css, render_header, metric_card

st.set_page_config(page_title="Resultados | DIAN Sim", page_icon="📊", layout="wide")
load_css()
render_header(title="Resultados del Simulacro", subtitle="Análisis de tu desempeño reciente")

if "last_results" not in st.session_state:
    st.info("No hay resultados recientes para mostrar.")
    with st.container():
         if st.button("⬅️ Volver al Inicio"):
             st.switch_page("app.py")
    st.stop()

data = st.session_state["last_results"]
total = data["total"]
correct = data["correct"]
score = (correct / total) * 100

# Metric Card
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    metric_card("Puntaje Global", f"{score:.1f}%", f"{correct} de {total} respuestas correctas")

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
