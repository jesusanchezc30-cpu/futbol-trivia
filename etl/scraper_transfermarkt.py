import requests
import os
import time
import random
import psycopg2
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

BASE_URL = "https://www.transfermarkt.es"

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def get_jugadores_equipo_tm(url_equipo, nombre_equipo):
    response = requests.get(url_equipo, headers=HEADERS)
    soup = BeautifulSoup(response.content, "lxml")

    jugadores = []
    filas = soup.select("table.items tbody tr.odd, table.items tbody tr.even")

    for fila in filas:
        try:
            nombre = fila.select_one("td.hauptlink a")
            posicion = fila.select_one("td.posrela table tr:nth-child(2) td")
            valor = fila.select_one("td.rechts.hauptlink a")
            nacionalidad = fila.select_one("td.zentriert img.flaggenrahmen")
            fecha_nac = fila.select_one("td.zentriert:nth-child(3)")

            if not nombre:
                continue

            jugador = {
                "nombre": nombre.text.strip(),
                "posicion": posicion.text.strip() if posicion else None,
                "valor_mercado": valor.text.strip() if valor else None,
                "nacionalidad": nacionalidad["title"] if nacionalidad else None,
                "fecha_nacimiento": fecha_nac.text.strip() if fecha_nac else None,
                "equipo": nombre_equipo,
                "url_perfil": BASE_URL + nombre["href"] if nombre else None
            }
            jugadores.append(jugador)
            print(f"  ✓ {jugador['nombre']} - {jugador['valor_mercado']}")

        except Exception:
            continue

    return jugadores

def get_equipos_laliga_tm():
    url = f"{BASE_URL}/laliga/startseite/wettbewerb/ES1"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "lxml")

    equipos = []
    filas = soup.select("table.items tbody tr")

    for fila in filas:
        try:
            nombre = fila.select_one("td.hauptlink a")
            if not nombre:
                continue
            equipos.append({
                "nombre": nombre.text.strip(),
                "url": BASE_URL + nombre["href"]
            })
        except Exception:
            continue

    return equipos

def cargar_jugadores_tm():
    print("Obteniendo equipos de LaLiga desde Transfermarkt...\n")
    equipos = get_equipos_laliga_tm()

    conn = conectar_db()
    cursor = conn.cursor()

    for equipo in equipos:
        print(f"\n{equipo['nombre']}:")
        jugadores = get_jugadores_equipo_tm(equipo["url"], equipo["nombre"])

        cursor.execute("SELECT id FROM equipos WHERE nombre ILIKE %s", (equipo["nombre"],))
        resultado = cursor.fetchone()
        equipo_bd_id = resultado[0] if resultado else None

        for jugador in jugadores:
            cursor.execute("""
                INSERT INTO jugadores (nombre, posicion, nacionalidad, valor_mercado, url_perfil, equipo_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                jugador["nombre"],
                jugador["posicion"],
                jugador["nacionalidad"],
                jugador["valor_mercado"],
                jugador["url_perfil"],
                equipo_bd_id
            ))

        conn.commit()
        print(f"✓ {len(jugadores)} jugadores guardados")
        time.sleep(random.uniform(2, 4))

    cursor.close()
    conn.close()
    print("\nCarga completada.")

if __name__ == "__main__":
    cargar_jugadores_tm()