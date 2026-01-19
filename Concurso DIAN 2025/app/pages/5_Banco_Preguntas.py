import streamlit as st
import pandas as pd
from db.session import SessionLocal
from db.models import Question
from core.dedupe import compute_hash, find_duplicates
import uuid
import datetime

st.header("📂 Banco de Preguntas")

action = st.radio("Acción", ["Explorar", "Importar CSV", "Crear Manualmente"])

db = SessionLocal()

if action == "Explorar":
    search = st.text_input("Buscar en enunciado...")
    query = db.query(Question)
    if search:
        query = query.filter(Question.stem.ilike(f"%{search}%"))
    
    questions = query.limit(50).all()
    
    data = []
    for q in questions:
        data.append({
            "ID": str(q.question_id)[:8],
            "Track": q.track,
            "Topic": q.topic,
            "Stem": q.stem[:50] + "..."
        })
    
    st.dataframe(pd.DataFrame(data))

elif action == "Importar CSV":
    st.markdown("Sube un CSV con columnas: `track, competency, topic, stem, options_A, options_B, options_C, options_D, correct_key, rationale`")
    uploaded = st.file_uploader("Archivo questions.csv", type=["csv"])
    
    if uploaded:
        df = pd.read_csv(uploaded)
        st.write(f"Leídas {len(df)} filas.")
        
        if st.button("Procesar Importación"):
            count_ok = 0
            count_dupe = 0
            
            existing_stems = [q.stem for q in db.query(Question.stem).all()]
            
            for index, row in df.iterrows():
                stem = row['stem']
                
                # Check Duplicates
                dupes = find_duplicates(stem, existing_stems)
                if dupes:
                    st.warning(f"Posible duplicado (fila {index}): '{stem}' similar a '{dupes[0][0]}'")
                    count_dupe += 1
                    # In a real app we might ask for confirmation, here we skip or flag
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
                    difficulty=3, # Default
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
        track = st.selectbox("Track", ["FUNCIONAL", "COMPORTAMENTAL", "INTEGRIDAD"])
        topic = st.text_input("Tema")
        stem = st.text_area("Enunciado")
        op_a = st.text_input("Opción A")
        op_b = st.text_input("Opción B")
        op_c = st.text_input("Opción C")
        op_d = st.text_input("Opción D")
        correct = st.selectbox("Correcta", ["A", "B", "C", "D"])
        rationale = st.text_area("Justificación")
        
        if st.form_submit_button("Guardar"):
            h = compute_hash(stem)
            # Check unique hash
            if db.query(Question).filter_by(hash_norm=h).first():
                st.error("¡Pregunta idéntica ya existe!")
            else:
                q = Question(
                    track=track,
                    competency="Manual", # Default
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
                st.success("Pregunta guardada.")

db.close()
