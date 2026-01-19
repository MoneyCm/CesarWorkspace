import os
import hashlib
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://observatorio:observatorio@localhost:5432/observatorio")
INPUT_DIR = os.getenv("INPUT_DIR", "./data_input")

engine = create_engine(DATABASE_URL)

NORMALIZACION_DELITOS = {
    "Homicidio Intencional": "Homicidio",
    "HOMICIDIO": "Homicidio",
    "Hurtos a Personas": "Hurto a Personas",
    "Hurto Personas": "Hurto a Personas",
    "VIF": "Violencia Intrafamiliar",
    "Violencia intrafamiliar": "Violencia Intrafamiliar",
}

def hash_row(row: dict) -> str:
    keys = ["fecha", "delito", "barrio", "zona", "lat", "lon"]
    raw = "|".join(str(row.get(k, "")).strip() for k in keys)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def normalize_delito(valor: str) -> str:
    if not isinstance(valor, str):
        return "Sin Clasificar"
    return NORMALIZACION_DELITOS.get(valor.strip(), valor.strip())

def parse_fecha(x):
    if pd.isna(x):
        return None
    if isinstance(x, (pd.Timestamp, datetime)):
        return x.date()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(x), fmt).date()
        except Exception:
            continue
    return None

def run():
    os.makedirs(INPUT_DIR, exist_ok=True)
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".xlsx",".xls",".csv"))]
    if not files:
        print("No se encontraron archivos en", INPUT_DIR)
        return

    with engine.begin() as conn:
        # Ensure schema exists (PostGIS extension handled by app)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS crimes (
                id SERIAL PRIMARY KEY,
                source VARCHAR(50),
                incident_id VARCHAR(128),
                hash_id VARCHAR(64) NOT NULL,
                fecha DATE NOT NULL,
                hora TIME NULL,
                delito VARCHAR(120) NOT NULL,
                subdelito VARCHAR(120),
                municipio VARCHAR(120) DEFAULT 'Jamundí',
                zona VARCHAR(20),
                barrio VARCHAR(160),
                corregimiento VARCHAR(160),
                genero_victima VARCHAR(20),
                edad_victima INT,
                arma VARCHAR(80),
                modalidad VARCHAR(120),
                cantidad INT DEFAULT 1,
                lat DOUBLE PRECISION,
                lon DOUBLE PRECISION,
                geom geography(Point,4326),
                extras JSONB,
                created_at TIMESTAMP DEFAULT now(),
                updated_at TIMESTAMP DEFAULT now()
            );
        """))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_crimes_hash_id ON crimes(hash_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_crimes_fecha_delito ON crimes(fecha, delito)"))

    total_insertados = 0
    for fname in files:
        path = os.path.join(INPUT_DIR, fname)
        if fname.lower().endswith(".csv"):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        # Intentar mapear columnas comunes
        cols = {c.lower().strip(): c for c in df.columns}
        get = lambda *names: next((cols[n] for n in names if n in cols), None)

        fecha_col = get("fecha","date","dia","día")
        hora_col = get("hora","time")
        delito_col = get("delito","tipo_delito","categoria","categoría")
        subdelito_col = get("subdelito","subtipo","sub_categoria")
        barrio_col = get("barrio","barrio/corregimiento","sector")
        zona_col = get("zona","urbano_rural","area","área")
        lat_col = get("lat","latitud")
        lon_col = get("lon","longitud","lng")

        rows = []
        for _, r in df.iterrows():
            fecha = parse_fecha(r[fecha_col]) if fecha_col else None
            if not fecha:
                continue
            delito = normalize_delito(str(r[delito_col])) if delito_col else "Sin Clasificar"
            subdelito = str(r[subdelito_col]).strip() if subdelito_col else None
            barrio = str(r[barrio_col]).strip() if barrio_col else None
            zona = str(r[zona_col]).strip().lower() if zona_col else None
            lat = float(r[lat_col]) if lat_col and pd.notna(r[lat_col]) else None
            lon = float(r[lon_col]) if lon_col and pd.notna(r[lon_col]) else None

            row = {
                "source": "Carga Excel",
                "incident_id": None,
                "fecha": fecha,
                "hora": str(r[hora_col]) if hora_col and pd.notna(r[hora_col]) else None,
                "delito": delito,
                "subdelito": subdelito,
                "municipio": "Jamundí",
                "zona": zona,
                "barrio": barrio,
                "corregimiento": None,
                "genero_victima": None,
                "edad_victima": None,
                "arma": None,
                "modalidad": None,
                "cantidad": 1,
                "lat": lat,
                "lon": lon,
                "extras": None
            }
            row["hash_id"] = hash_row(row)
            rows.append(row)

        if not rows:
            print(f"{fname}: sin filas válidas")
            continue

        # Insert with upsert by hash_id
        insert_sql = text("""
            INSERT INTO crimes (source, incident_id, hash_id, fecha, hora, delito, subdelito, municipio, zona, barrio, corregimiento,
                                genero_victima, edad_victima, arma, modalidad, cantidad, lat, lon, geom, extras)
            VALUES (:source, :incident_id, :hash_id, :fecha, NULLIF(:hora,'' )::time, :delito, :subdelito, :municipio, :zona, :barrio, :corregimiento,
                    :genero_victima, :edad_victima, :arma, :modalidad, :cantidad, :lat, :lon,
                    CASE WHEN :lat IS NOT NULL AND :lon IS NOT NULL
                         THEN ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography ELSE NULL END,
                    :extras)
            ON CONFLICT (hash_id) DO NOTHING
        """ )
        with engine.begin() as conn:
            for chunk_start in range(0, len(rows), 500):
                chunk = rows[chunk_start:chunk_start+500]
                conn.execute(insert_sql, chunk)
                total_insertados += len(chunk)
        print(f"{fname}: procesadas {len(rows)} filas")

    print("Total insertados (incluye ignorados por conflicto):", total_insertados)

if __name__ == "__main__":
    run()