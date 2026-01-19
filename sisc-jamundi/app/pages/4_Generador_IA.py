import streamlit as st
import os
from db.session import SessionLocal
from db.models import Question
from core.generators.llm import LLMGenerator
from core.dedupe import compute_hash

import pypdf
import io

st.set_page_config(layout="wide")
st.header("🤖 Generador de Preguntas con IA")

st.markdown("""
Aquí puedes usar inteligencia artificial para crear preguntas a partir de tus propios documentos.
**Nota:** Necesitas una API Key de OpenAI o Google Gemini.
""")

with st.expander("Configuración de API Key", expanded=True):
    provider = st.selectbox("Proveedor", ["OpenAI", "Gemini"])
    api_key_env = os.getenv(f"{provider.upper()}_API_KEY")
    api_key = st.text_input(f"API Key {provider}", value=api_key_env if api_key_env else "", type="password")
    
    st.info("No guardamos tu llave. Se usa solo para esta sesión.")

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Origen del Contenido")
    
    tab_text, tab_file = st.tabs(["📋 Pegar Texto", "📂 Subir Archivo"])
    
    source_text = ""
    
    with tab_text:
        pasted_text = st.text_area("Pega aquí el artículo o ley:", height=300)
        if pasted_text:
            source_text = pasted_text
            
    with tab_file:
        uploaded_file = st.file_uploader("Sube un documento (PDF, TXT)", type=["pdf", "txt"])
        if uploaded_file:
            try:
                if uploaded_file.type == "application/pdf":
                    reader = pypdf.PdfReader(uploaded_file)
                    extracted = []
                    for page in reader.pages:
                        extracted.append(page.extract_text())
                    source_text = "\n".join(extracted)
                    st.success(f"PDF cargado: {len(reader.pages)} páginas leídas.")
                else:
                    # TXT
                    source_text = uploaded_file.read().decode("utf-8")
                    st.success("Archivo de texto cargado.")
            except Exception as e:
                st.error(f"Error leyendo archivo: {e}")

    st.caption(f"Caracteres detectados: {len(source_text)}")
    
    custom_topic = st.text_input("Etiqueta / Tema para estas preguntas (Ej: Gestor II)", value="Gestor II")
    
    num_q = st.slider("Cantidad de preguntas a generar", 1, 10, 3)
    
    generate_btn = st.button("✨ Generar Preguntas", disabled=(not source_text or not api_key))

if generate_btn:
    with st.spinner("Analizando texto y creando preguntas... (Esto puede tardar unos segundos)"):
        try:
            generator = LLMGenerator(provider, api_key)
            results = generator.generate_from_text(source_text, num_q)
            
            # Apply Custom Topic Override
            if results and custom_topic.strip():
                for q in results:
                    q['topic'] = custom_topic.strip()
            
            st.session_state["generated_questions"] = results
            
            if not results:
                st.error("No se pudieron generar preguntas. Revisa tu API Key o el formato del texto.")
            else:
                st.success(f"¡{len(results)} preguntas generadas!")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Create DB Session
db = SessionLocal()

with col2:
    st.subheader("2. Revisar y Guardar")
    if "generated_questions" in st.session_state and st.session_state["generated_questions"]:
        candidates = st.session_state["generated_questions"]
        
        indices_to_save = []
        
        for i, q in enumerate(candidates):
            with st.container(border=True):
                st.write(f"**P{i+1}: {q['stem']}**")
                st.caption(f"{q['track']} | {q['topic']}")
                
                # Show Options
                ops = q.get('options_json', {})
                if ops:
                    for k, v in ops.items():
                        st.text(f"{k}) {v}")
                
                st.info(f"Respuesta Correcta: {q['correct_key']}")
                
                if q.get('rationale'):
                    st.caption(f"**Justificación:** {q['rationale']}")
                
                # Check Duplicates
                exists = db.query(Question).filter_by(hash_norm=q['hash_norm']).first()
                if exists:
                    st.warning("⚠️ Pregunta muy similar ya existe en el banco.")
                else:
                    if st.checkbox("Guardar esta pregunta", key=f"save_{i}", value=True):
                        indices_to_save.append(i)
        
        if st.button("💾 Guardar Seleccionadas en Banco"):
            saved_count = 0
            for i in indices_to_save:
                data = candidates[i]
                # Re-check existence just in case
                if not db.query(Question).filter_by(hash_norm=data['hash_norm']).first():
                    new_q = Question(**data)
                    db.add(new_q)
                    saved_count += 1
            
            db.commit()
            st.balloons()
            st.success(f"Se guardaron {saved_count} preguntas nuevas.")
            # Clear session
            del st.session_state["generated_questions"]
            st.rerun()
            
    else:
        st.info("Las preguntas generadas aparecerán aquí para tu revisión.")

db.close()
