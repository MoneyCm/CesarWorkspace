-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;

-- Users
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT now()
);

-- Fuentes
CREATE TABLE IF NOT EXISTS fuentes (
  id SERIAL PRIMARY KEY,
  nombre TEXT NOT NULL,
  responsable TEXT,
  canal TEXT,
  periodicidad TEXT,
  campos JSONB,
  created_at TIMESTAMP DEFAULT now()
);

-- Ingest logs
CREATE TABLE IF NOT EXISTS ingest_logs (
  id SERIAL PRIMARY KEY,
  fuente_id INTEGER REFERENCES fuentes(id),
  filename TEXT,
  uploaded_by TEXT,
  uploaded_at TIMESTAMP DEFAULT now(),
  registros INTEGER,
  errores INTEGER,
  sha256 TEXT
);

-- Eventos (microdatos)
CREATE TABLE IF NOT EXISTS eventos (
  id SERIAL PRIMARY KEY,
  fecha_hecho DATE,
  hora TIME,
  tipo_evento TEXT,
  modalidad TEXT,
  barrio TEXT,
  fuente_id INTEGER REFERENCES fuentes(id),
  victima_sexo TEXT,
  victima_edad INTEGER,
  victima_pseudo TEXT,
  arma TEXT,
  geom geometry(POINT,4326)
);
