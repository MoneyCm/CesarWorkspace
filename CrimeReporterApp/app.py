
import streamlit as st
import pandas as pd
from io import BytesIO
from report_engine import load_multiple_files, build_report, guess_columns

st.set_page_config(page_title="Reportador de Delitos (Excel)", layout="wide")

st.title("📊 Reportador de Delitos desde Excel")
st.write("Cargue uno o varios archivos .xlsx del SIEDCO/DIJIN o similares y genere reportes en segundos.")

uploaded_files = st.file_uploader("Arrastre aquí sus archivos Excel", type=["xlsx"], accept_multiple_files=True)

with st.expander("⚙️ Opciones de procesamiento", expanded=False):
    municipio_foco = st.text_input("Municipio foco (opcional, p.ej. Jamundí)", value="")
    normalizar_municipio = st.checkbox("Normalizar nombres de municipio (remover '(CT)', tildes, etc.)", value=True)
    fecha_col = st.text_input("Nombre de columna de fecha (si es distinto a 'FECHA HECHO')", value="")

if uploaded_files:
    with st.spinner("Leyendo y limpiando archivos..."):
        dfs, logs = load_multiple_files(uploaded_files, fecha_col_override=fecha_col or None, normalize_city=normalizar_municipio)
    st.success("Archivos cargados.")

    if logs:
        st.subheader("📝 Registro de limpieza")
        for l in logs:
            st.text(l)

    full = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    if full.empty:
        st.warning("No se pudo leer datos válidos. Revise sus archivos.")
        st.stop()

    # Filtros
    st.sidebar.header("Filtros")
    años = sorted(full["AÑO"].dropna().unique())
    año_sel = st.sidebar.multiselect("Año", años, default=años)

    departamentos = sorted(full["DEPARTAMENTO"].dropna().unique())
    dpto_sel = st.sidebar.multiselect("Departamento", departamentos, default=departamentos)

    municipios = sorted(full["MUNICIPIO"].dropna().unique())
    if municipio_foco and municipio_foco not in municipios:
        municipios = [municipio_foco] + municipios
    muni_sel = st.sidebar.multiselect("Municipio", municipios, default=[municipio_foco] if municipio_foco else municipios)

    full_f = full[full["AÑO"].isin(año_sel) & full["DEPARTAMENTO"].isin(dpto_sel) & full["MUNICIPIO"].isin(muni_sel)]

    st.subheader("👁️ Vista previa datos filtrados")
    st.dataframe(full_f.head(100))

    # KPIs
    total = int(full_f["CANTIDAD"].sum())
    eventos = len(full_f)
    muni_unicos = full_f["MUNICIPIO"].nunique()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total casos (CANTIDAD)", f"{total:,}".replace(",", "."))
    col2.metric("Filas de evento", f"{eventos:,}".replace(",", "."))
    col3.metric("Municipios", muni_unicos)

    # Reportes estándar
    st.subheader("📈 Tablas de reporte")
    piv_mes = full_f.pivot_table(index=["DELITO_FUENTE","AÑO","MES"], values="CANTIDAD", aggfunc="sum").reset_index()
    piv_ubc = full_f.pivot_table(index=["DELITO_FUENTE","DEPARTAMENTO","MUNICIPIO"], values="CANTIDAD", aggfunc="sum").reset_index()

    st.markdown("**Por Mes**")
    st.dataframe(piv_mes.head(1000))
    st.markdown("**Por Ubicación**")
    st.dataframe(piv_ubc.head(1000))

    if "GENERO" in full_f.columns:
        st.markdown("**Por Género**")
        piv_gen = full_f.pivot_table(index=["DELITO_FUENTE","GENERO"], values="CANTIDAD", aggfunc="sum").reset_index()
        st.dataframe(piv_gen)

    if "ARMAS MEDIOS" in full_f.columns:
        st.markdown("**Por Armas/Medios**")
        piv_arm = full_f.pivot_table(index=["DELITO_FUENTE","ARMAS MEDIOS"], values="CANTIDAD", aggfunc="sum").reset_index()
        st.dataframe(piv_arm)

    if "DELITOS" in full_f.columns:
        st.markdown("**Por Tipo de Delito (si aplica)**")
        piv_del = full_f.pivot_table(index=["DELITO_FUENTE","DELITOS"], values="CANTIDAD", aggfunc="sum").reset_index()
        st.dataframe(piv_del)

    # Exportar a Excel
    st.subheader("📥 Exportar a Excel")
    xls_bytes = build_report(full_f)
    st.download_button("Descargar Reporte Excel", data=xls_bytes, file_name="Reporte_Delitos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info("Cargue sus archivos .xlsx para empezar.")
