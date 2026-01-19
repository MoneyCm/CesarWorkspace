-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Crimes table (SQL mirror of SQLAlchemy model)
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
CREATE UNIQUE INDEX IF NOT EXISTS uq_crimes_hash_id ON crimes(hash_id);
CREATE INDEX IF NOT EXISTS idx_crimes_fecha_delito ON crimes(fecha, delito);