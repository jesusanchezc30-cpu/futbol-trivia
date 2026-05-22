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

def generar_pregunta_nacionalidad():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.nombre, j.nacionalidad FROM jugadores j
        WHERE j.nacionalidad IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    jugador = cursor.fetchone()
    if not jugador:
        return None

    nombre, nacionalidad_correcta = jugador

    cursor.execute("""
        SELECT nacionalidad FROM jugadores
        WHERE nacionalidad != %s AND nacionalidad IS NOT NULL
        GROUP BY nacionalidad
        ORDER BY RANDOM() LIMIT 3
    """, (nacionalidad_correcta,))
    incorrectas = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectas) < 3:
        return None

    opciones = incorrectas + [nacionalidad_correcta]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿De qué nacionalidad es {nombre}?",
        "respuesta_correcta": nacionalidad_correcta,
        "opciones": json.dumps(opciones),
        "dificultad": 1
    }

def generar_pregunta_equipo():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.nombre, e.nombre FROM jugadores j
        JOIN equipos e ON j.equipo_id = e.id
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None

    jugador_nombre, equipo_correcto = resultado

    cursor.execute("""
        SELECT nombre FROM equipos
        WHERE nombre != %s
        ORDER BY RANDOM() LIMIT 3
    """, (equipo_correcto,))
    incorrectos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectos) < 3:
        return None

    opciones = incorrectos + [equipo_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿En qué equipo juega {jugador_nombre}?",
        "respuesta_correcta": equipo_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 1
    }

def generar_pregunta_valor_mercado():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.nombre, j.valor_mercado, e.nombre FROM jugadores j
        JOIN equipos e ON j.equipo_id = e.id
        WHERE j.valor_mercado IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None

    jugador_nombre, valor_correcto, equipo = resultado

    cursor.execute("""
        SELECT valor_mercado FROM jugadores
        WHERE valor_mercado != %s AND valor_mercado IS NOT NULL
        GROUP BY valor_mercado
        ORDER BY RANDOM() LIMIT 3
    """, (valor_correcto,))
    incorrectos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectos) < 3:
        return None

    opciones = incorrectos + [valor_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Cuál es el valor de mercado de {jugador_nombre} ({equipo})?",
        "respuesta_correcta": valor_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pistas_jugador():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT j.nombre, j.nacionalidad, j.posicion, j.fecha_nacimiento, e.nombre
        FROM jugadores j
        JOIN equipos e ON j.equipo_id = e.id
        WHERE j.nacionalidad IS NOT NULL AND j.posicion IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    if not resultado:
        return None

    nombre, nacionalidad, posicion, fecha_nac, equipo = resultado

    edad = None
    if fecha_nac:
        from datetime import date
        hoy = date.today()
        edad = hoy.year - fecha_nac.year

    pistas = []
    if posicion:
        pistas.append(f"Juega de {posicion}")
    if nacionalidad:
        pistas.append(f"Es de nacionalidad {nacionalidad}")
    if edad:
        pistas.append(f"Tiene {edad} años")
    if equipo:
        pistas.append(f"Juega en el {equipo}")

    return {
        "tipo": "adivina_jugador",
        "enunciado": "¿Quién es este jugador?",
        "respuesta_correcta": nombre,
        "opciones": None,
        "pistas": json.dumps(pistas),
        "dificultad": 2
    }

def generar_pregunta_maximo_goleador():
    """¿Quién fue el máximo goleador de X equipo en X temporada?"""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.jugador_nombre, COUNT(*) as goles, eq.nombre as equipo, p.temporada
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        JOIN equipos eq ON eq.nombre = e.equipo_nombre
        WHERE e.tipo = 'gol'
        AND e.jugador_nombre IS NOT NULL
        AND p.temporada IS NOT NULL
        GROUP BY e.jugador_nombre, eq.nombre, p.temporada
        HAVING COUNT(*) >= 5
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None

    jugador, goles, equipo, temporada = resultado

    cursor.execute("""
        SELECT e.jugador_nombre
        FROM eventos_partido e
        JOIN partidos p ON e.partido_id = p.id
        WHERE e.tipo = 'gol'
        AND e.equipo_nombre = %s
        AND p.temporada = %s
        AND e.jugador_nombre != %s
        GROUP BY e.jugador_nombre
        ORDER BY RANDOM() LIMIT 3
    """, (equipo, temporada, jugador))
    incorrectos = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectos) < 3:
        return None

    anio_inicio = int(temporada)
    anio_fin = anio_inicio + 1
    nombre_temporada = f"{str(anio_inicio)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [jugador]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Quién marcó más goles en el {equipo} en la temporada {nombre_temporada}? ({goles} goles)",
        "respuesta_correcta": jugador,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_mas_tarjetas():
    """¿Qué equipo tuvo más tarjetas rojas en X temporada?"""
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

    anio_inicio = int(temporada)
    anio_fin = anio_inicio + 1
    nombre_temporada = f"{str(anio_inicio)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [equipo_correcto]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Qué equipo recibió más tarjetas rojas en la temporada {nombre_temporada}? ({rojas_correctas} rojas)",
        "respuesta_correcta": equipo_correcto,
        "opciones": json.dumps(opciones),
        "dificultad": 2
    }

def generar_pregunta_goles_temporada():
    """¿Cuántos goles marcó X equipo en X temporada?"""
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT eq.nombre, p.temporada,
            SUM(CASE WHEN p.equipo_local_id = eq.id THEN p.goles_local
                     ELSE p.goles_visitante END) as goles
        FROM partidos p
        JOIN equipos eq ON eq.id = p.equipo_local_id OR eq.id = p.equipo_visitante_id
        WHERE p.temporada IS NOT NULL
        GROUP BY eq.nombre, p.temporada
        HAVING COUNT(*) >= 30
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None

    equipo, temporada, goles_correctos = resultado

    cursor.execute("""
        SELECT eq.nombre,
            SUM(CASE WHEN p.equipo_local_id = eq.id THEN p.goles_local
                     ELSE p.goles_visitante END) as goles
        FROM partidos p
        JOIN equipos eq ON eq.id = p.equipo_local_id OR eq.id = p.equipo_visitante_id
        WHERE p.temporada = %s AND eq.nombre != %s
        GROUP BY eq.nombre
        HAVING COUNT(*) >= 30
        ORDER BY RANDOM() LIMIT 3
    """, (temporada, equipo))
    incorrectos = [str(row[1]) for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    if len(incorrectos) < 3:
        return None

    anio_inicio = int(temporada)
    anio_fin = anio_inicio + 1
    nombre_temporada = f"{str(anio_inicio)[2:]}/{str(anio_fin)[2:]}"

    opciones = incorrectos + [str(goles_correctos)]
    random.shuffle(opciones)

    return {
        "tipo": "trivia",
        "enunciado": f"¿Cuántos goles marcó el {equipo} en la temporada {nombre_temporada}?",
        "respuesta_correcta": str(goles_correctos),
        "opciones": json.dumps(opciones),
        "dificultad": 3
    }

def insertar_pregunta(pregunta):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO preguntas (tipo, enunciado, respuesta_correcta, opciones, pistas, dificultad)
        VALUES (%s, %s, %s, %s, %s, %s)
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

def generar_banco_preguntas(n=50):
    generadores = [
        generar_pregunta_nacionalidad,
        generar_pregunta_equipo,
        generar_pregunta_valor_mercado,
        generar_pistas_jugador,
        generar_pregunta_maximo_goleador,
        generar_pregunta_mas_tarjetas,
        generar_pregunta_goles_temporada
    ]

    generadas = 0
    intentos = 0

    while generadas < n and intentos < n * 2:
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
    generar_banco_preguntas(50)