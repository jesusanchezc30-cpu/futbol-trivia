import psycopg2
import os
import json
import random
from dotenv import load_dotenv

load_dotenv()

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def generar_pregunta_maximo_goleador_liga():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.temporada
        FROM partidos p
        WHERE p.temporada IS NOT NULL
        GROUP BY p.temporada
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    temporada = resultado[0]

    cursor.execute("""
        SELECT e.jugador_nombre, COUNT(*) as goles
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.jugador_nombre IS NOT NULL
        AND p.temporada = %s
        GROUP BY e.jugador_nombre
        ORDER BY goles DESC
        LIMIT 1
    """, (temporada,))
    resultado = cursor.fetchone()
    if not resultado:
        return None
    jugador, goles = resultado

    cursor.execute("""
        SELECT e.jugador_nombre, COUNT(*) as goles
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.jugador_nombre IS NOT NULL
        AND p.temporada = %s
        AND e.jugador_nombre != %s
        GROUP BY e.jugador_nombre
        HAVING COUNT(*) >= 8
        ORDER BY RANDOM() LIMIT 3
    """, (temporada, jugador))
    incorrectos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectos) < 3:
        return None

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [jugador]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Quién fue el máximo goleador de LaLiga en la temporada {nombre_temporada}? ({goles} goles)",
        "respuesta_correcta": jugador,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_goleador_equipo():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.equipo_nombre, p.temporada
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.equipo_nombre IS NOT NULL
        AND p.temporada IS NOT NULL
        GROUP BY e.equipo_nombre, p.temporada
        HAVING COUNT(*) >= 20
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    equipo, temporada = resultado

    cursor.execute("""
        SELECT e.jugador_nombre, COUNT(*) as goles
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.equipo_nombre = %s
        AND p.temporada = %s
        AND e.jugador_nombre IS NOT NULL
        GROUP BY e.jugador_nombre
        ORDER BY goles DESC
        LIMIT 1
    """, (equipo, temporada))
    resultado = cursor.fetchone()
    if not resultado:
        return None
    jugador, goles = resultado

    cursor.execute("""
        SELECT e.jugador_nombre
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.equipo_nombre = %s
        AND p.temporada = %s
        AND e.jugador_nombre != %s
        AND e.jugador_nombre IS NOT NULL
        GROUP BY e.jugador_nombre
        HAVING COUNT(*) >= 2
        ORDER BY RANDOM() LIMIT 3
    """, (equipo, temporada, jugador))
    incorrectos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectos) < 3:
        return None

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [jugador]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Quién fue el máximo goleador del {equipo} en la temporada {nombre_temporada}? ({goles} goles)",
        "respuesta_correcta": jugador,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_mas_goles_equipo():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.temporada
        FROM partidos p
        WHERE p.temporada IS NOT NULL
        GROUP BY p.temporada
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    temporada = resultado[0]

    cursor.execute("""
        SELECT eq.nombre,
            SUM(CASE WHEN p.equipo_local_id = eq.id THEN p.goles_local
                     ELSE p.goles_visitante END) as goles
        FROM partidos p
        JOIN equipos eq ON eq.id = p.equipo_local_id OR eq.id = p.equipo_visitante_id
        WHERE p.temporada = %s
        GROUP BY eq.nombre
        HAVING COUNT(*) >= 30
        ORDER BY goles DESC
        LIMIT 4
    """, (temporada,))
    equipos = cursor.fetchall()

    cursor.close()
    conn.close()

    if len(equipos) < 4:
        return None

    equipo_correcto = equipos[0][0]
    goles_correctos = equipos[0][1]
    incorrectos = [e[0] for e in equipos[1:]]

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [equipo_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Qué equipo marcó más goles en LaLiga en la temporada {nombre_temporada}? ({goles_correctos} goles)",
        "respuesta_correcta": equipo_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_menos_goles_recibidos():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.temporada
        FROM partidos p
        WHERE p.temporada IS NOT NULL
        GROUP BY p.temporada
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    temporada = resultado[0]

    cursor.execute("""
        SELECT eq.nombre,
            SUM(CASE WHEN p.equipo_local_id = eq.id THEN p.goles_visitante
                     ELSE p.goles_local END) as goles_recibidos
        FROM partidos p
        JOIN equipos eq ON eq.id = p.equipo_local_id OR eq.id = p.equipo_visitante_id
        WHERE p.temporada = %s
        GROUP BY eq.nombre
        HAVING COUNT(*) >= 30
        ORDER BY goles_recibidos ASC
        LIMIT 4
    """, (temporada,))
    equipos = cursor.fetchall()

    cursor.close()
    conn.close()

    if len(equipos) < 4:
        return None

    equipo_correcto = equipos[0][0]
    goles_correctos = equipos[0][1]
    incorrectos = [e[0] for e in equipos[1:]]

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [equipo_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Qué equipo recibió menos goles en LaLiga en la temporada {nombre_temporada}? ({goles_correctos} goles)",
        "respuesta_correcta": equipo_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_mas_tarjetas_rojas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.temporada
        FROM partidos p
        WHERE p.temporada IS NOT NULL
        GROUP BY p.temporada
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    temporada = resultado[0]

    cursor.execute("""
        SELECT e.equipo_nombre, COUNT(*) as rojas
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'tarjeta_roja'
        AND p.temporada = %s
        AND e.equipo_nombre IS NOT NULL
        GROUP BY e.equipo_nombre
        ORDER BY rojas DESC
        LIMIT 4
    """, (temporada,))
    equipos = cursor.fetchall()

    cursor.close()
    conn.close()

    if len(equipos) < 4:
        return None

    equipo_correcto = equipos[0][0]
    rojas_correctas = equipos[0][1]
    incorrectos = [e[0] for e in equipos[1:]]

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [equipo_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Qué equipo recibió más tarjetas rojas en LaLiga en la temporada {nombre_temporada}? ({rojas_correctas} rojas)",
        "respuesta_correcta": equipo_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_comparacion_goleadores():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.temporada
        FROM partidos p
        WHERE p.temporada IS NOT NULL
        GROUP BY p.temporada
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    temporada = resultado[0]

    cursor.execute("""
        SELECT e.jugador_nombre, COUNT(*) as goles
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.jugador_nombre IS NOT NULL
        AND p.temporada = %s
        GROUP BY e.jugador_nombre
        HAVING COUNT(*) >= 8
        ORDER BY RANDOM() LIMIT 2
    """, (temporada,))
    jugadores = cursor.fetchall()
    cursor.close()
    conn.close()

    if len(jugadores) < 2:
        return None

    jugador1, goles1 = jugadores[0]
    jugador2, goles2 = jugadores[1]

    if goles1 == goles2:
        return None

    if goles1 > goles2:
        correcto, goles_correcto = jugador1, goles1
        incorrecto, goles_incorrecto = jugador2, goles2
    else:
        correcto, goles_correcto = jugador2, goles2
        incorrecto, goles_incorrecto = jugador1, goles1

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    return {
        "tipo": "trivia",
        "enunciado": f"En la temporada {nombre_temporada}, ¿quién marcó más goles en LaLiga, {correcto} o {incorrecto}?",
        "respuesta_correcta": correcto,
        "opciones": json.dumps([correcto, incorrecto]),
        "dificultad": 2
    }

def generar_pregunta_mas_goles_propio():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.temporada
        FROM partidos p
        WHERE p.temporada IS NOT NULL
        GROUP BY p.temporada
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None
    temporada = resultado[0]

    cursor.execute("""
        SELECT e.equipo_nombre, COUNT(*) as propios
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol_propio'
        AND p.temporada = %s
        AND e.equipo_nombre IS NOT NULL
        GROUP BY e.equipo_nombre
        ORDER BY propios DESC
        LIMIT 4
    """, (temporada,))
    equipos = cursor.fetchall()

    cursor.close()
    conn.close()

    if len(equipos) < 4:
        return None

    equipo_correcto = equipos[0][0]
    propios_correctos = equipos[0][1]
    incorrectos = [e[0] for e in equipos[1:]]

    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [equipo_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Qué equipo marcó más goles en propia puerta en la temporada {nombre_temporada}? ({propios_correctos} goles)",
        "respuesta_correcta": equipo_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 3
    }

def generar_pregunta_pistas_jugador():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.jugador_nombre, e.equipo_nombre, COUNT(*) as goles, p.temporada
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.jugador_nombre IS NOT NULL
        AND e.equipo_nombre IS NOT NULL
        AND p.temporada IS NOT NULL
        GROUP BY e.jugador_nombre, e.equipo_nombre, p.temporada
        HAVING COUNT(*) >= 10
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    if not resultado:
        return None

    jugador, equipo, goles, temporada = resultado
    anio_fin = int(temporada) + 1
    nombre_temporada = f"{str(temporada)[2:]}/{str(anio_fin)[2:]}"

    pistas = [
        f"Jugó en el {equipo}",
        f"Marcó {goles} goles en la temporada {nombre_temporada}",
        f"Jugó en LaLiga",
    ]

    return {
        "tipo": "adivina_jugador",
        "enunciado": "¿Quién es este jugador?",
        "respuesta_correcta": jugador,
        "opciones": None,
        "pistas": json.dumps(pistas),
        "dificultad": 2
    }

def insertar_pregunta(pregunta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO preguntas (tipo, enunciado, respuesta_correcta, opciones, pistas, dificultad)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (enunciado) DO NOTHING
    """, (
        pregunta["tipo"],
        pregunta["enunciado"],
        pregunta["respuesta_correcta"],
        pregunta.get("opciones"),
        pregunta.get("pistas"),
        pregunta.get("dificultad", 1)
    ))
    conn.commit()
    cursor.close()
    conn.close()

def generar_banco_preguntas(n=100):
    generadores = [
        generar_pregunta_maximo_goleador_liga,
        generar_pregunta_goleador_equipo,
        generar_pregunta_mas_goles_equipo,
        generar_pregunta_menos_goles_recibidos,
        generar_pregunta_mas_tarjetas_rojas,
        generar_pregunta_comparacion_goleadores,
        generar_pregunta_mas_goles_propio,
        generar_pregunta_pistas_jugador,
    ]

    generadas = 0
    intentos = 0

    while generadas < n and intentos < n * 3:
        generador = random.choice(generadores)
        pregunta = generador()
        if pregunta:
            insertar_pregunta(pregunta)
            generadas += 1
            print(f"✓ [{pregunta['tipo']}] {pregunta['enunciado']}")
        intentos += 1

    print(f"\nTotal preguntas generadas: {generadas}")

if __name__ == "__main__":
    print("Generando banco de preguntas...\n")
    generar_banco_preguntas(500)