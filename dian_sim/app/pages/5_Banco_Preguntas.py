import streamlit as st
import pandas as pd
import os
import sys
import uuid
import datetime

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from db.session import SessionLocal
from db.models import Question
from core.dedupe import compute_hash, find_duplicates
from ui_utils import load_css, render_header

st.set_page_config(page_title="Banco Preguntas | DIAN Sim", page_icon="📂", layout="wide")
load_css()
render_header(title="Gestión de Preguntas", subtitle="Explora, importa y crea contenido manualmente")

# Marcador de Versión para forzar refresco
st.sidebar.caption("Versión: 1.2.5 (Fix-Delete)")
if st.sidebar.button("🔄 Forzar Recarga de Datos"):
    st.rerun()

action = st.radio("Acción", ["Explorar", "Importar CSV", "Crear Manualmente"], horizontal=True)
st.divider()

db = SessionLocal()

if action == "Explorar":
    search = st.text_input("🔍 Buscar en enunciado...")
    query = db.query(Question)
    if search:
        query = query.filter(Question.stem.ilike(f"%{search}%"))
    
    questions = query.all()
    
    st.info(f"📚 Se encontraron **{len(questions)}** preguntas en el banco.")
    
    if not questions:
        st.warning("No hay preguntas que coincidan con la búsqueda.")
    else:
        for q in questions:
            # Título resumido para el expander
            display_title = f"[{q.track or 'SIN EJE'}] {q.stem[:80]}..."
            
            with st.expander(display_title):
                st.markdown(f"**Enunciado:**\n{q.stem}")
                
                # Mostrar Opciones si existen
                ops = q.options_json if q.options_json else {}
                if ops:
                    st.markdown("**Opciones:**")
                    cols = st.columns(2)
                    for i, (key, val) in enumerate(ops.items()):
                        # Check if val is dict or string (fix potential data issues)
                        val_str = val if isinstance(val, str) else str(val)
                        cols[i % 2].markdown(f"**{key})** {val_str}")
                
                st.markdown(f"**Respuesta Correcta:** :green[{q.correct_key}]")
                
                if q.rationale:
                    with st.container(border=True):
                        st.caption("Justificación")
                        st.write(q.rationale)
                
                st.divider()
                
                # Barra de acciones (Eliminar)
                col_info, col_del = st.columns([0.8, 0.2])
                with col_info:
                    st.caption(f"Tema: {q.topic or 'General'} | ID: {q.question_id}")
                
                with col_del:
                    with st.popover("🗑️ Eliminar", use_container_width=True):
                        st.error("¿Estás seguro?")
                        if st.button("Confirmar Borrado", key=f"del_{q.question_id}", type="primary", use_container_width=True):
                            try:
                                # Get a fresh instance from the session to delete
                                item_to_del = db.query(Question).filter_by(question_id=q.question_id).first()
                                if item_to_del:
                                    db.delete(item_to_del)
                                    db.commit()
                                    st.toast("Pregunta eliminada", icon="🗑️")
                                    st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error(f"Error: {e}")

elif action == "Importar CSV":
    st.info("Sube un CSV con columnas: `track, competency, topic, stem, options_A, options_B, options_C, options_D, correct_key, rationale`")
    uploaded = st.file_uploader("Archivo questions.csv", type=["csv"])
    
    if uploaded:
        df = pd.read_csv(uploaded)
        st.success(f"Leídas {len(df)} filas.")
        
        with st.expander("Previsualizar Datos"):
            st.dataframe(df.head())
        
        if st.button("Procesar Importación", type="primary"):
            count_ok = 0
            count_dupe = 0
            
            existing_stems = [q.stem for q in db.query(Question.stem).all()]
            
            progress_bar = st.progress(0)
            
            for index, row in df.iterrows():
                progress_bar.progress((index + 1) / len(df))
                stem = row['stem']
                
                # Check Duplicates
                dupes = find_duplicates(stem, existing_stems)
                if dupes:
                    st.warning(f"Posible duplicado (fila {index}): '{stem}' similar a '{dupes[0][0]}'")
                    count_dupe += 1
                    continue
                
                ops = {
                    "A": row['options_A'],
                    "B": row['options_B'],
                    "C": row['options_C'],
                    "D": row['options_D']
                }
                
                q = Question(
                    question_id=str(uuid.uuid4()),
                    track=row['track'],
                    competency=row['competency'],
                    topic=row['topic'],
                    difficulty=3,
                    stem=stem,
                    options_json=ops,
                    correct_key=row['correct_key'],
                    rationale=row.get('rationale', ''),
                    created_at=datetime.datetime.utcnow(),
                    hash_norm=compute_hash(stem)
                )
                db.add(q)
                count_ok += 1
                
            db.commit()
            st.success(f"Importados: {count_ok}. Saltados (Duplicados): {count_dupe}")

elif action == "Crear Manualmente":
    with st.form("manual_create"):
        st.subheader("Nueva Pregunta")
        col1, col2 = st.columns(2)
        with col1:
            track = st.selectbox("Track / Eje", ["FUNCIONAL", "COMPORTAMENTAL", "INTEGRIDAD"])
            topic = st.text_input("Tema")
        with col2:
            stem = st.text_area("Enunciado de la Pregunta")
            
        st.markdown("---")
        st.markdown("**Opciones de Respuesta**")
        c1, c2 = st.columns(2)
        with c1:
            op_a = st.text_input("Opción A")
            op_b = st.text_input("Opción B")
        with c2:
            op_c = st.text_input("Opción C")
            op_d = st.text_input("Opción D")
            
        col_correct, col_rationale = st.columns([1, 2])
        with col_correct:
            correct = st.selectbox("Respuesta Correcta", ["A", "B", "C", "D"])
        with col_rationale:
            rationale = st.text_area("Justificación / Explicación")
        
        if st.form_submit_button("Guardar Pregunta", type="primary"):
            h = compute_hash(stem)
            # Check unique hash
            if db.query(Question).filter_by(hash_norm=h).first():
                st.error("¡Pregunta idéntica ya existe!")
            else:
                q = Question(
                    question_id=str(uuid.uuid4()),
                    track=track,
                    competency="Manual",
                    topic=topic,
                    stem=stem,
                    difficulty=3,
                    options_json={"A": op_a, "B": op_b, "C": op_c, "D": op_d},
                    correct_key=correct,
                    rationale=rationale,
                    hash_norm=h
                )
                db.add(q)
                db.commit()
                st.success("Pregunta guardada exitosamente.")

db.close()
