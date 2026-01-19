
import pandas as pd
import io
import unicodedata
import re

def _strip_accents(text):
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    return text

def _normalize_city(name):
    if not isinstance(name, str):
        return name
    name = _strip_accents(name)
    name = re.sub(r"\s*\(CT\)\s*", "", name, flags=re.IGNORECASE)
    name = name.replace("Bogota D.C.", "Bogotá D.C.")
    return name.strip()

def guess_columns(df):
    cols = [str(c).strip().upper() for c in df.columns]
    return cols

def _find_header_row(df_raw):
    for i in range(min(len(df_raw), 200)):
        row_vals = set(str(x).strip().upper() for x in df_raw.iloc[i].tolist())
        if "DEPARTAMENTO" in row_vals and "MUNICIPIO" in row_vals:
            return i
    return None

def load_one(file, fecha_col_override=None, normalize_city=True):
    df_raw = pd.read_excel(file, header=None)
    header_row = _find_header_row(df_raw)
    if header_row is None:
        raise ValueError("No se encontró la fila de encabezado (no aparecen 'DEPARTAMENTO' y 'MUNICIPIO').")
    df = pd.read_excel(file, header=header_row)
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Fecha
    fecha_col = fecha_col_override.upper() if fecha_col_override else ("FECHA HECHO" if "FECHA HECHO" in df.columns else None)
    if not fecha_col:
        raise ValueError("No se encontró columna de fecha. Configure el nombre en opciones.")
    # Pandas >=2 ya no requiere infer_datetime_format; modo estricto por defecto
    df["FECHA"] = pd.to_datetime(df[fecha_col], errors="coerce", dayfirst=True)

    # Básicos
    if "CANTIDAD" not in df.columns:
        # si no existe, asumir 1 por fila
        df["CANTIDAD"] = 1

    required = ["DEPARTAMENTO","MUNICIPIO"]
    for r in required:
        if r not in df.columns:
            raise ValueError(f"Falta columna requerida: {r}")

    if normalize_city:
        df["MUNICIPIO"] = df["MUNICIPIO"].map(_normalize_city)

    df["AÑO"] = df["FECHA"].dt.year
    df["MES"] = df["FECHA"].dt.month

    # nombre de fuente con base en título si existe
    try:
        filename = getattr(file, "name", "Archivo")
    except Exception:
        filename = "Archivo"
    delito_fuente = filename.split("_")[0].split(".")[0]
    df["DELITO_FUENTE"] = delito_fuente

    # ordenar columnas
    first_cols = [c for c in ["DELITO_FUENTE","AÑO","MES","DEPARTAMENTO","MUNICIPIO","FECHA","CANTIDAD"] if c in df.columns]
    other_cols = [c for c in df.columns if c not in first_cols]
    df = df[first_cols + other_cols]

    return df

def load_multiple_files(files, fecha_col_override=None, normalize_city=True):
    dfs = []
    logs = []
    for f in files:
        try:
            df = load_one(f, fecha_col_override=fecha_col_override, normalize_city=normalize_city)
            dfs.append(df)
            logs.append(f"OK: {getattr(f, 'name', 'archivo')} -> {len(df)} filas")
        except Exception as e:
            logs.append(f"ERROR: {getattr(f, 'name', 'archivo')} -> {e}")
    return dfs, logs

def build_report(df):
    # genera un Excel con pestañas útiles
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Datos_Filtrados", index=False)

        piv_mes = df.pivot_table(index=["DELITO_FUENTE","AÑO","MES"], values="CANTIDAD", aggfunc="sum").reset_index()
        piv_mes.to_excel(writer, sheet_name="Por_Mes", index=False)

        piv_ubc = df.pivot_table(index=["DELITO_FUENTE","DEPARTAMENTO","MUNICIPIO"], values="CANTIDAD", aggfunc="sum").reset_index()
        piv_ubc.to_excel(writer, sheet_name="Por_Ubicacion", index=False)

        if "GENERO" in df.columns:
            piv_gen = df.pivot_table(index=["DELITO_FUENTE","GENERO"], values="CANTIDAD", aggfunc="sum").reset_index()
            piv_gen.to_excel(writer, sheet_name="Por_Genero", index=False)

        if "ARMAS MEDIOS" in df.columns:
            piv_arm = df.pivot_table(index=["DELITO_FUENTE","ARMAS MEDIOS"], values="CANTIDAD", aggfunc="sum").reset_index()
            piv_arm.to_excel(writer, sheet_name="Por_Arma", index=False)

        if "DELITOS" in df.columns:
            piv_del = df.pivot_table(index=["DELITO_FUENTE","DELITOS"], values="CANTIDAD", aggfunc="sum").reset_index()
            piv_del.to_excel(writer, sheet_name="Por_Delito", index=False)

    output.seek(0)
    return output.getvalue()
