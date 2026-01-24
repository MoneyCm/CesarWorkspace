import streamlit as st
import pandas as pd
import os
import sys
import uuid
import datetime
import io

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from db.session import SessionLocal
from db.models import Question
from core.dedupe import compute_hash, find_duplicates
from core.import_utils import validate_import_df
from ui_utils import load_css, render_header

st.set_page_config(page_title="Banco Preguntas | DIAN Sim", page_icon="📂", layout="wide")
load_css()
render_header(title="SISC de Preguntas (Pro)", subtitle="Gestión avanzada, carga masiva y control de calidad")

# --- INITIALIZATION ---
if "bulk_selection" not in st.session_state:
    st.session_state["bulk_selection"] = set()
if "page_num" not in st.session_state:
    st.session_state["page_num"] = 1

def reset_selection():
    st.session_state["bulk_selection"] = set()

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.markdown("### 🛠️ Herramientas Pro")
    if st.button("🗑️ Limpiar Selección"):
        reset_selection()
        st.rerun()
    
    st.divider()
    st.caption("Paginación")
    cols_page = st.columns(2)
    if cols_page[0].button("⬅️ Ant."):
        st.session_state["page_num"] = max(1, st.session_state["page_num"] - 1)
        st.rerun()
    if cols_page[1].button("Sig. ➡️"):
        st.session_state["page_num"] += 1
        st.rerun()

action = st.radio("Acción", ["Explorar / Bulk", "Carga Masiva (Excel/CSV)", "Crear Manualmente"], horizontal=True)
st.divider()

db = SessionLocal()

if action == "Explorar / Bulk":
    # FILTERS
    col_filters = st.columns([2, 1, 1, 1])
    with col_filters[0]:
        search = st.text_input("🔍 Buscar en enunciado o justificación...")
    with col_filters[1]:
        track_f = st.selectbox("Eje", ["Todos", "FUNCIONAL", "COMPORTAMENTAL", "INTEGRIDAD"])
    with col_filters[2]:
        diff_f = st.multiselect("Dificultad", [1, 2, 3], format_func=lambda x: {1: "🟢 Básico", 2: "🟡 Intermedio", 3: "🔴 Avanzado"}[x])
    with col_filters[3]:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.session_state["bulk_selection"]:
            if st.button(f"🗑️ Borrar Seleccionados ({len(st.session_state['bulk_selection'])})", type="primary", use_container_width=True):
                try:
                    for qid in st.session_state["bulk_selection"]:
                        q_to_del = db.query(Question).get(qid)
                        if q_to_del:
                            db.delete(q_to_del)
                    db.commit()
                    reset_selection()
                    st.success("Preguntas eliminadas masivamente.")
                    st.rerun()
                except Exception as e:
                    db.rollback()
                    st.error(f"Error en borrado masivo: {e}")

    # QUERY
    query = db.query(Question)
    if search:
        query = query.filter(Question.stem.ilike(f"%{search}%") | Question.rationale.ilike(f"%{search}%"))
    if track_f != "Todos":
        query = query.filter(Question.track == track_f)
    if diff_f:
        query = query.filter(Question.difficulty.in_(diff_f))
    
    # Pagination Logic
    PAGE_SIZE = 20
    offset = (st.session_state["page_num"] - 1) * PAGE_SIZE
    total_count = query.count()
    questions = query.offset(offset).limit(PAGE_SIZE).all()
    
    st.info(f"📚 Mostrando **{len(questions)}** de **{total_count}** preguntas (Página {st.session_state['page_num']}).")
    
    if not questions:
        st.warning("No hay preguntas que coincidan con la búsqueda.")
    else:
        # SELECT ALL CHECKBOX
        select_all = st.checkbox("Seleccionar todas las visibles")
        if select_all:
            for q in questions:
                st.session_state["bulk_selection"].add(q.question_id)
        
        for q in questions:
            diff_tags = {1: "🟢", 2: "🟡", 3: "🔴"}
            is_selected = q.question_id in st.session_state["bulk_selection"]
            
            # Use small columns for the selection logic
            col_sel, col_exp = st.columns([0.05, 0.95])
            
            with col_sel:
                if st.checkbox("", value=is_selected, key=f"sel_{q.question_id}"):
                    st.session_state["bulk_selection"].add(q.question_id)
                else:
                    st.session_state["bulk_selection"].discard(q.question_id)
            
            with col_exp:
                display_title = f"{diff_tags.get(q.difficulty, '⚪')} [{q.track or 'SIN EJE'}] {q.stem[:80]}..."
                with st.expander(display_title):
                    st.markdown(f"**Enunciado:**\n{q.stem}")
                    ops = q.options_json if q.options_json else {}
                    if ops:
                        cols_ops = st.columns(2)
                        for i, (key, val) in enumerate(ops.items()):
                            cols_ops[i % 2].markdown(f"**{key})** {val}")
                    
                    st.markdown(f"**Respuesta Correcta:** :green[{q.correct_key}]")
                    if q.rationale:
                        st.caption(f"Justificación: {q.rationale}")
                    
                    st.divider()
                    if st.button("🗑️ Eliminar esta pregunta", key=f"del_single_{q.question_id}", type="secondary"):
                        db.delete(q)
                        db.commit()
                        st.rerun()

elif action == "Carga Masiva (Excel/CSV)":
    st.info("Sube un archivo `.xlsx` o `.csv`. Columnas requeridas: `track, competency, topic, stem, options_A, options_B, options_C, options_D, correct_key, rationale` (opcional)")
    
    # --- TEMPLATE DOWNLOAD ---
    template_data = {
        'track': ['FUNCIONAL', 'COMPORTAMENTAL', 'INTEGRIDAD'],
        'competency': ['Gestión Tributaria', 'Orientación al Logro', 'Ética'],
        'topic': ['IVA', 'Trabajo en Equipo', 'Valores'],
        'stem': ['SITUACIÓN: Un contribuyente... PREGUNTA: ¿Qué hacer?', 'SITUACIÓN: Caso de equipo...', 'SITUACIÓN: Dilema ético...'],
        'options_A': ['Opción 1', 'Valor 1', 'Acción 1'],
        'options_B': ['Opción 2', 'Valor 2', 'Acción 2'],
        'options_C': ['Opción 3', 'Valor 3', 'Acción 3'],
        'options_D': ['Opción 4', 'Valor 4', 'Acción 4'],
        'correct_key': ['A', 'B', 'C'],
        'rationale': ['Explicación A', 'Explicación B', 'Explicación C'],
        'difficulty': [2, 1, 3]
    }
    df_template = pd.DataFrame(template_data)
    towrite = io.BytesIO()
    with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Descargar Plantilla Excel (.xlsx)",
        data=towrite.getvalue(),
        file_name="Plantilla_Preguntas_DIAN.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.divider()
    
    uploaded = st.file_uploader("Archivo de preguntas", type=["csv", "xlsx"])
    
    if uploaded:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            
            st.success(f"Archivo leído: {len(df)} filas detectadas.")
            
            # VALIDATION
            is_valid, err_list = validate_import_df(df)
            
            if not is_valid:
                st.error("📉 El archivo tiene errores de estructura o datos:")
                for err in err_list[:15]: # Limit display
                    st.write(f"- {err}")
                if len(err_list) > 15:
                    st.write(f"... y {len(err_list)-15} errores más.")
                st.stop()
            else:
                st.success("✅ Estructura validada correctamente.")
                with st.expander("Previsualizar datos"):
                    st.dataframe(df.head())
                
                if st.button("🚀 Procesar e Importar", type="primary"):
                    count_ok = 0
                    count_dupe = 0
                    
                    existing_hashes = [q.hash_norm for q in db.query(Question.hash_norm).all()]
                    
                    progress = st.progress(0)
                    for index, row in df.iterrows():
                        progress.progress((index + 1) / len(df))
                        stem = str(row['stem'])
                        h = compute_hash(stem)
                        
                        if h in existing_hashes:
                            count_dupe += 1
                            continue
                            
                        ops = {
                            "A": str(row['options_A']),
                            "B": str(row['options_B']),
                            "C": str(row['options_C']),
                            "D": str(row['options_D'])
                        }
                        
                        # Safe difficulty conversion
                        raw_diff = row.get('difficulty', 2)
                        try:
                            difficulty = int(float(raw_diff)) if not pd.isna(raw_diff) else 2
                        except (ValueError, TypeError):
                            difficulty = 2
                            
                        q = Question(
                            question_id=str(uuid.uuid4()),
                            track=str(row['track']).upper(),
                            competency=str(row.get('competency', 'General')),
                            topic=str(row.get('topic', 'General')),
                            difficulty=difficulty,
                            stem=stem,
                            options_json=ops,
                            correct_key=str(row['correct_key']).strip().upper(),
                            rationale=str(row.get('rationale', '')),
                            hash_norm=h
                        )
                        db.add(q)
                        count_ok += 1
                        existing_hashes.append(h) # Update local cache for batch
                    
                    db.commit()
                    st.balloons()
                    st.success(f"¡Importación Finalizada! Nuevas: {count_ok} | Duplicadas omitidas: {count_dupe}")

        except Exception as e:
            st.error(f"Error procesando el archivo: {e}")

elif action == "Crear Manualmente":
    with st.form("manual_create"):
        st.subheader("Nueva Pregunta")
        col1, col2 = st.columns(2)
        with col1:
            track = st.selectbox("Track / Eje", ["FUNCIONAL", "COMPORTAMENTAL", "INTEGRIDAD"])
            topic = st.text_input("Tema")
        with col2:
            stem = st.text_area("Enunciado de la Pregunta")
            difficulty = st.select_slider("Dificultad", options=[1, 2, 3], format_func=lambda x: {1: "Básico", 2: "Intermedio", 3: "Avanzado"}[x], value=2)
            
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
            if db.query(Question).filter_by(hash_norm=h).first():
                st.error("¡Pregunta idéntica ya existe!")
            else:
                q = Question(
                    question_id=str(uuid.uuid4()),
                    track=track,
                    competency="Manual",
                    topic=topic,
                    stem=stem,
                    difficulty=difficulty,
                    options_json={"A": op_a, "B": op_b, "C": op_c, "D": op_d},
                    correct_key=correct,
                    rationale=rationale,
                    hash_norm=h
                )
                db.add(q)
                db.commit()
                st.success("Pregunta guardada exitosamente.")

db.close()
