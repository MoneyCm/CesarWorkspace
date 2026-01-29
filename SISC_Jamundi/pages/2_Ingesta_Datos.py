import streamlit as st
import pandas as pd
from db.database import save_events
import io
import requests

st.set_page_config(page_title="Ingesta de Datos SEM 48 | SISC", page_icon="📥", layout="wide")

st.title("📥 Ingesta de Datos (Formato SEM 48)")
st.markdown("""
Esta herramienta está optimizada para el formato **SEM 48** (47 columnas). 
Puede cargar un archivo local o importar directamente desde una hoja de Google Sheets publicada.
""")

tab1, tab2 = st.tabs(["📄 Cargar Archivo Local", "🌐 Google Sheets"])

with tab1:
    uploaded_file = st.file_uploader("Seleccione un archivo (XLSX, CSV)", type=["xlsx", "csv"], key="local")
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success(f"✅ Archivo '{uploaded_file.name}' cargado con {len(df)} registros.")
            st.write("### Vista previa de los datos")
            st.dataframe(df.head(5))
            if st.button("🚀 Procesar e Insertar en Base de Datos Local", type="primary", key="btn_local"):
                with st.spinner("Procesando 47 columnas de información..."):
                    report = save_events(df)
                    
                    # Mostrar mapeo inteligente
                    if report.get("mappings"):
                        with st.expander("📍 Ver Mapeo Inteligente Detectado"):
                            st.info("El sistema ha identificado automáticamente las siguientes columnas:")
                            mapping_data = [{"Atributo Sistema": k, "Columna en Excel": v} for k, v in report["mappings"].items()]
                            st.table(pd.DataFrame(mapping_data))

                    if report["success"] > 0:
                        st.success(f"¡Éxito! Se insertaron {report['success']} registros correctamente.")
                        st.balloons()
                    if report["errors"]:
                        with st.expander("⚠️ Ver errores detallados"):
                            for err in report["errors"]:
                                st.error(err)
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.info("Para importar desde Google Sheets, la hoja debe estar 'Publicada en la Web' como CSV.")
    sheet_url = st.text_input("Pegue la URL 'Publicar en la web' (formato CSV):")
    
    if st.button("🔍 Previsualizar Datos de Google", key="btn_preview"):
        if sheet_url:
            try:
                # Convertir URL de edición a exportación CSV si es necesario
                if "/edit" in sheet_url:
                    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                    sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                
                response = requests.get(sheet_url)
                df_google = pd.read_csv(io.StringIO(response.text))
                st.session_state["df_google"] = df_google
                st.success(f"Conexión exitosa. Se encontraron {len(df_google)} registros.")
                st.dataframe(df_google.head(5))
            except Exception as e:
                st.error(f"No se pudo conectar con Google Sheets. Verifique la URL y los permisos. Error: {e}")

    if "df_google" in st.session_state:
        if st.button("📥 Importar todo desde Google Sheets a Base de Datos Local", key="btn_google_import"):
            with st.spinner("Sincronizando con Base de Datos Local..."):
                report = save_events(st.session_state["df_google"])
                
                # Mostrar mapeo inteligente
                if report.get("mappings"):
                    with st.expander("📍 Ver Mapeo Inteligente Detectado"):
                        st.info("El sistema ha identificado automáticamente las siguientes columnas:")
                        mapping_data = [{"Atributo Sistema": k, "Columna en Google Sheets": v} for k, v in report["mappings"].items()]
                        st.table(pd.DataFrame(mapping_data))

                if report["success"] > 0:
                    st.success(f"¡Importación masiva completada! {report['success']} registros agregados.")
                    st.balloons()
