-- Extensiones Geoespaciales y UUID
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Seguridad y Usuarios
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

INSERT INTO roles (name, description) VALUES 
('Admin SISC', 'Control total del sistema'),
('Analista Observatorio', 'Generación de reportes y analítica'),
('Cargador de datos', 'Solo ingesta de archivos'),
('Consulta interna', 'Visualización de tableros protegidos'),
('Público', 'Acceso a datos agregados abiertos');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT REFERENCES roles(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Usuario admin por defecto (password: admin123) - Obviamente esto se cambia en producción
-- Hash generado de ejemplo para desarrollo
INSERT INTO users (username, email, password_hash, role_id) 
VALUES ('admin', 'admin@jamundi.gov.co', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6L6s57RwRXWux.72', 1);

-- 2. Fuentes y Convenios
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    acronym VARCHAR(20) UNIQUE,
    description TEXT,
    contact_person VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO sources (name, acronym, description) VALUES 
('Policía Nacional - SIEDCO', 'SIEDCO', 'Sistema Estadístico Delictivo'),
('Fiscalía General - SPOA', 'SPOA', 'Sistema de Información de la Fiscalía'),
('Instituto Medicina Legal', 'INMLCF', 'Datos de necropsias y lesiones'),
('Secretaría de Salud Jamundí', 'SALUD', 'Registros de atención y RUAF');

-- 3. Geografía (Límites de Jamundí)
CREATE TABLE territories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- BARRIO, VEREDA, COMUNA, CORREGIMIENTO
    code VARCHAR(20),
    geom GEOMETRY(GEOMETRY, 4326)
);

-- 4. Tipologías
CREATE TABLE event_types (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(100),
    is_delicto BOOLEAN DEFAULT TRUE
);

INSERT INTO event_types (category, subcategory) VALUES 
('HOMICIDIO', 'DOLOSO'),
('HOMICIDIO', 'CULPOSO (ACCIDENTE TRANSITO)'),
('HURTO', 'A PERSONAS'),
('HURTO', 'A RESIDENCIAS'),
('HURTO', 'A COMERCIO'),
('LESIONES PERSONALES', 'EN RIÑA'),
('VIOLENCIA INTRAFAMILIAR', 'GENERAL');

-- 5. Eventos (Formato SEM 48)
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Jurisdicción y Ubicación
    juris_depto VARCHAR(100),
    municipio VARCHAR(100),
    barrio VARCHAR(100),
    zona VARCHAR(50),
    juris_distrito VARCHAR(100),
    juris_estacion VARCHAR(100),
    juris_cai VARCHAR(100),
    juris_dependencia VARCHAR(100),
    clase_sitio VARCHAR(100),
    
    -- Hecho
    hechos_id INT,
    descripcion_conducta VARCHAR(255),
    modalidad VARCHAR(100),
    armas_medios VARCHAR(100),
    fecha_hecho DATE NOT NULL,
    hora_hecho TIME NOT NULL,
    anio INT,
    mes VARCHAR(20),
    nro_semana INT,
    semana_hecho VARCHAR(50),
    dia_semana VARCHAR(20),
    intervalos_hora VARCHAR(50),
    hora24 INT,
    turno VARCHAR(20),
    
    -- Persona/Víctima
    genero VARCHAR(20),
    edad VARCHAR(20),
    agrupa_edad_persona VARCHAR(50),
    grupos_vulnerables_persona VARCHAR(100),
    pais_persona VARCHAR(50),
    tipo_identificacion VARCHAR(50),
    profesiones VARCHAR(100),
    grado_instruccion_persona VARCHAR(100),
    cargo_persona VARCHAR(100),
    clase_empleado_descripcion VARCHAR(100),
    
    -- Caracterización y SPOA
    causas_lesion_muerte_persona VARCHAR(255),
    spoa_caracterizacion TEXT,
    spoa_caracterizacion_id VARCHAR(50),
    spoa_motivacion VARCHAR(255),
    conductas_especiales VARCHAR(100),
    medio_conocimiento VARCHAR(100),
    
    -- Administrativos
    nro_fuente_hecho INT,
    unidad_apoya VARCHAR(100),
    razon_social VARCHAR(100),
    nivel_gestion_estatal VARCHAR(100),
    count_2024 INT,
    count_2025 INT,
    
    -- Relacionales / Legacy
    event_type_id INT REFERENCES event_types(id),
    estado VARCHAR(50) DEFAULT 'Abierto',
    descripcion_adicional TEXT,
    location_geom GEOMETRY(POINT, 4326),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices Espaciales
CREATE INDEX idx_events_geom ON events USING GIST (location_geom);
CREATE INDEX idx_territories_geom ON territories USING GIST (geom);
CREATE INDEX idx_events_date ON events (occurrence_date);
