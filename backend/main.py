from fastapi import FastAPI, HTTPException
import psycopg2
import os
import json
from dotenv import load_dotenv

load_dotenv("../etl/.env")

app = FastAPI(title="Futbol Trivia API")

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.get("/")
def inicio():
    return {"mensaje": "Futbol Trivia API funcionando"}

@app.get("/preguntas")
def get_preguntas(tipo: str = None, limite: int = 10):
    """Devuelve preguntas aleatorias, opcionalmente filtradas por tipo"""
    conn = conectar_db()
    cursor = conn.cursor()

    if tipo:
        cursor.execute("""
            SELECT id, tipo, enunciado, respuesta_correcta, opciones, pistas, dificultad
            FROM preguntas
            WHERE tipo = %s AND activa = TRUE
            ORDER BY RANDOM() LIMIT %s
        """, (tipo, limite))
    else:
        cursor.execute("""
            SELECT id, tipo, enunciado, respuesta_correcta, opciones, pistas, dificultad
            FROM preguntas
            WHERE activa = TRUE
            ORDER BY RANDOM() LIMIT %s
        """, (limite,))

    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    preguntas = []
    for fila in filas:
        preguntas.append({
            "id": fila[0],
            "tipo": fila[1],
            "enunciado": fila[2],
            "respuesta_correcta": fila[3],
            "opciones": fila[4] if fila[4] else None,
            "pistas": fila[5] if fila[5] else None,
            "dificultad": fila[6]
        })

    return preguntas

@app.get("/preguntas/{id}")
def get_pregunta(id: int):
    """Devuelve una pregunta por su ID"""
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tipo, enunciado, respuesta_correcta, opciones, pistas, dificultad
        FROM preguntas WHERE id = %s
    """, (id,))
    fila = cursor.fetchone()
    cursor.close()
    conn.close()

    if not fila:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")

    return {
        "id": fila[0],
        "tipo": fila[1],
        "enunciado": fila[2],
        "respuesta_correcta": fila[3],
        "opciones": fila[4] if fila[4] else None,
        "pistas": fila[5] if fila[5] else None,
        "dificultad": fila[6]
    }

@app.get("/equipos")
def get_equipos(categoria: str = None):
    """Devuelve todos los equipos, opcionalmente filtrados por categoría"""
    conn = conectar_db()
    cursor = conn.cursor()

    if categoria:
        cursor.execute("""
            SELECT id, nombre, ciudad, estadio, escudo_url, liga, categoria
            FROM equipos WHERE categoria = %s AND activo = TRUE
        """, (categoria,))
    else:
        cursor.execute("""
            SELECT id, nombre, ciudad, estadio, escudo_url, liga, categoria
            FROM equipos WHERE activo = TRUE
        """)

    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"id": f[0], "nombre": f[1], "ciudad": f[2], "estadio": f[3],
             "escudo_url": f[4], "liga": f[5], "categoria": f[6]} for f in filas]

@app.get("/jugadores")
def get_jugadores(equipo_id: int = None, limite: int = 20):
    """Devuelve jugadores, opcionalmente filtrados por equipo"""
    conn = conectar_db()
    cursor = conn.cursor()

    if equipo_id:
        cursor.execute("""
            SELECT j.id, j.nombre, j.posicion, j.nacionalidad, j.valor_mercado, j.foto_url, e.nombre
            FROM jugadores j JOIN equipos e ON j.equipo_id = e.id
            WHERE j.equipo_id = %s AND j.activo = TRUE
        """, (equipo_id,))
    else:
        cursor.execute("""
            SELECT j.id, j.nombre, j.posicion, j.nacionalidad, j.valor_mercado, j.foto_url, e.nombre
            FROM jugadores j JOIN equipos e ON j.equipo_id = e.id
            WHERE j.activo = TRUE LIMIT %s
        """, (limite,))

    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"id": f[0], "nombre": f[1], "posicion": f[2], "nacionalidad": f[3],
             "valor_mercado": f[4], "foto_url": f[5], "equipo": f[6]} for f in filas]