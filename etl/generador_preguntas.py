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
    """¿De qué nacionalidad es X jugador?"""
    conn = conectar_db()
    cursor = conn.cursor()

    # Jugador correcto
    cursor.execute("""
        SELECT j.nombre, j.nacionalidad FROM jugadores j
        WHERE j.nacionalidad IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    jugador = cursor.fetchone()
    if not jugador:
        return None

    nombre, nacionalidad_correcta = jugador

    # 3 nacionalidades incorrectas
    cursor.execute("""
        SELECT DISTINCT nacionalidad FROM jugadores
        WHERE nacionalidad != %s AND nacionalidad IS NOT NULL
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
    """¿En qué equipo juega X jugador?"""
    conn = conectar_db()
    cursor = conn.cursor()

    # Jugador correcto
    cursor.execute("""
        SELECT j.nombre, e.nombre FROM jugadores j
        JOIN equipos e ON j.equipo_id = e.id
        ORDER BY RANDOM() LIMIT 1
    """)
    resultado = cursor.fetchone()
    if not resultado:
        return None

    jugador_nombre, equipo_correcto = resultado

    # 3 equipos incorrectos
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

def generar_pistas_jugador():
    """Genera preguntas de adivina el jugador con pistas progresivas"""
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
    """Genera n preguntas y las guarda en la base de datos"""
    generadores = [
        generar_pregunta_nacionalidad,
        generar_pregunta_equipo,
        generar_pistas_jugador
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