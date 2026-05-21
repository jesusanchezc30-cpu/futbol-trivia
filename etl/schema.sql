-- Equipos de fútbol
CREATE TABLE equipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nombre_corto VARCHAR(50),
    ciudad VARCHAR(100),
    estadio VARCHAR(100),
    escudo_url TEXT,
    liga VARCHAR(50) DEFAULT 'LaLiga',
    categoria VARCHAR(50) DEFAULT 'Primera División',
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Jugadores
CREATE TABLE jugadores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    nombre_corto VARCHAR(100),
    fecha_nacimiento DATE,
    nacionalidad VARCHAR(100),
    posicion VARCHAR(50),
    dorsal INTEGER,
    foto_url TEXT,
    equipo_id INTEGER REFERENCES equipos(id),
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Temporadas
CREATE TABLE temporadas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    anio_inicio INTEGER NOT NULL,
    anio_fin INTEGER NOT NULL
);

-- Competiciones
CREATE TABLE competiciones (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    pais VARCHAR(50) DEFAULT 'España',
    activa BOOLEAN DEFAULT TRUE
);

-- Partidos
CREATE TABLE partidos (
    id SERIAL PRIMARY KEY,
    temporada_id INTEGER REFERENCES temporadas(id),
    equipo_local_id INTEGER REFERENCES equipos(id),
    equipo_visitante_id INTEGER REFERENCES equipos(id),
    goles_local INTEGER,
    goles_visitante INTEGER,
    fecha DATE,
    jornada INTEGER,
    competicion VARCHAR(50) DEFAULT 'LaLiga'
);

-- Oncenas titulares históricas
CREATE TABLE oncenas (
    id SERIAL PRIMARY KEY,
    equipo_id INTEGER REFERENCES equipos(id),
    temporada_id INTEGER REFERENCES temporadas(id),
    partido_id INTEGER REFERENCES partidos(id),
    jugador_id INTEGER REFERENCES jugadores(id),
    posicion_campo VARCHAR(30)
);

-- Preguntas generadas por el ETL
CREATE TABLE preguntas (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    enunciado TEXT NOT NULL,
    respuesta_correcta TEXT NOT NULL,
    opciones JSONB,
    pistas JSONB,
    dificultad INTEGER DEFAULT 1 CHECK (dificultad BETWEEN 1 AND 3),
    referencia_id INTEGER,
    referencia_tipo VARCHAR(50),
    activa BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    creado_en TIMESTAMP DEFAULT NOW()
);

-- Partidas jugadas
CREATE TABLE partidas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    tipo_juego VARCHAR(50) NOT NULL,
    puntuacion INTEGER DEFAULT 0,
    preguntas_totales INTEGER,
    preguntas_correctas INTEGER,
    tiempo_segundos INTEGER,
    jugada_en TIMESTAMP DEFAULT NOW()
);

-- Ranking global
CREATE TABLE ranking (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuarios(id),
    tipo_juego VARCHAR(50) NOT NULL,
    puntuacion_maxima INTEGER DEFAULT 0,
    partidas_jugadas INTEGER DEFAULT 0,
    actualizado_en TIMESTAMP DEFAULT NOW()
);

-- Datos iniciales de competiciones
INSERT INTO competiciones (nombre, categoria) VALUES
('LaLiga', 'Primera División'),
('LaLiga 2', 'Segunda División'),
('Copa del Rey', 'Copa'),
('Supercopa de España', 'Supercopa');