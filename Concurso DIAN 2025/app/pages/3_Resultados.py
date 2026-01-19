import streamlit as st
import sys
import os

# Add parent dir to path to import utils
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir) # app
sys.path.append(parent_dir)

from utils import setup_page
from db.session import SessionLocal
from db.models import Question

setup_page()

st.header("📊 Resultados del Último Simulacro")

if "last_results" not in st.session_state:
    st.info("No hay resultados recientes.")
    st.stop()

data = st.session_state["last_results"]
total = data["total"]
correct = data["correct"]
score = (correct / total) * 100

st.metric("Puntaje Global", f"{score:.1f}%", f"{correct}/{total} Correctas")

st.divider()

st.subheader("Detalle de Respuestas")

db = SessionLocal()
q_ids = data["q_ids"]
answers = st.session_state.get("answers", {})

for qid in q_ids:
    q = db.query(Question).get(qid)
    user_ans = answers.get(qid, "N/A")
    is_right = (user_ans == q.correct_key)
    
    icon = "✅" if is_right else "❌"
    
    with st.expander(f"{icon} {q.stem[:60]}..."):
        st.write(f"**Pregunta Completa:** {q.stem}")
        # Get option texts
        opts = q.options_json if q.options_json else {}
        user_text = opts.get(user_ans, "")
        correct_text = opts.get(q.correct_key, "")

        st.write(f"**Tu respuesta:** {user_ans}. {user_text}")
        st.write(f"**Correcta:** {q.correct_key}. {correct_text}")
        
        if not is_right:
            st.error(f"Explicación: {q.rationale}")
        else:
            st.success("¡Bien hecho!")
            
        st.caption(f"Tema: {q.topic} | Competencia: {q.competency}")

db.close()
