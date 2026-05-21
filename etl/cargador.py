import psycopg2
import os
from dotenv import load_dotenv
from extractor import get_equipos_laliga, get_equipos_segunda

load_dotenv()

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def cargar_equipos():
    equipos = get_equipos_laliga()
    conn = conectar_db()
    cursor = conn.cursor()

    insertados = 0
    for equipo in equipos:
        cursor.execute("""
            INSERT INTO equipos (nombre, nombre_corto, ciudad, estadio, escudo_url, liga, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            equipo["nombre"],
            equipo["nombre_corto"],
            equipo["ciudad"],
            equipo["estadio"],
            equipo["escudo_url"],
            "LaLiga",
            "Primera División"
        ))
        insertados += 1
        print(f"✓ Insertado: {equipo['nombre']}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nTotal insertados: {insertados}")

def cargar_equipos_segunda():
    equipos = get_equipos_segunda()
    conn = conectar_db()
    cursor = conn.cursor()

    insertados = 0
    for equipo in equipos:
        cursor.execute("""
            INSERT INTO equipos (nombre, nombre_corto, ciudad, estadio, escudo_url, liga, categoria)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            equipo["nombre"],
            equipo["nombre_corto"],
            equipo["ciudad"],
            equipo["estadio"],
            equipo["escudo_url"],
            "LaLiga 2",
            "Segunda División"
        ))
        insertados += 1
        print(f"✓ Insertado: {equipo['nombre']}")

    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nTotal insertados: {insertados}")

def cargar_jugadores():
    conn = conectar_db()
    cursor = conn.cursor()

    # Obtenemos los IDs de la API para cada equipo
    from extractor import get_ids_equipos_laliga, get_jugadores_equipo
    equipos_api = get_ids_equipos_laliga()

    for equipo_api_id, equipo_nombre in equipos_api:
        # Buscamos el id del equipo en nuestra base de datos
        cursor.execute("SELECT id FROM equipos WHERE nombre = %s", (equipo_nombre,))
        resultado = cursor.fetchone()
        if not resultado:
            print(f"✗ Equipo no encontrado en BD: {equipo_nombre}")
            continue

        equipo_bd_id = resultado[0]
        jugadores = get_jugadores_equipo(equipo_api_id, equipo_nombre)

        for jugador in jugadores:
            cursor.execute("""
                INSERT INTO jugadores (nombre, nombre_corto, fecha_nacimiento, nacionalidad, posicion, foto_url, equipo_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                jugador["nombre"],
                jugador["nombre_corto"],
                jugador["fecha_nacimiento"],
                jugador["nacionalidad"],
                jugador["posicion"],
                jugador["foto_url"],
                equipo_bd_id
            ))

    conn.commit()
    cursor.close()
    conn.close()
    print("\nJugadores cargados correctamente")

if __name__ == "__main__":
    print("Cargando equipos de Primera División...")
    cargar_equipos()
    print("\nCargando equipos de Segunda División...")
    cargar_equipos_segunda()
    print("\nCargando jugadores de LaLiga...")
    cargar_jugadores()
