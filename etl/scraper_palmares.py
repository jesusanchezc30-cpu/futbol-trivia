import requests
import os
import psycopg2
import time
import random
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9"
}

BASE_URL = "https://www.transfermarkt.es"

URLS_EQUIPOS = {
    "Real Madrid": "/real-madrid/erfolge/verein/418",
    "Barcelona": "/fc-barcelona/erfolge/verein/131",
    "Atletico Madrid": "/atletico-de-madrid/erfolge/verein/13",
    "Athletic Club": "/athletic-bilbao/erfolge/verein/621",
    "Valencia": "/fc-valencia/erfolge/verein/1049",
    "Villarreal": "/villarreal-cf/erfolge/verein/1050",
    "Las Palmas": "/ud-las-palmas/erfolge/verein/472",
    "Sevilla": "/fc-sevilla/erfolge/verein/368",
    "Leganes": "/cd-leganes/erfolge/verein/1244",
    "Celta Vigo": "/rc-celta-de-vigo/erfolge/verein/940",
    "Espanyol": "/rcd-espanyol-barcelona/erfolge/verein/714",
    "Alaves": "/deportivo-alaves/erfolge/verein/1108",
    "Real Betis": "/real-betis-balompie/erfolge/verein/150",
    "Getafe": "/getafe-cf/erfolge/verein/3709",
    "Girona": "/girona-fc/erfolge/verein/12321",
    "Real Sociedad": "/real-sociedad/erfolge/verein/681",
    "Valladolid": "/real-valladolid/erfolge/verein/366",
    "Osasuna": "/ca-osasuna/erfolge/verein/331",
    "Rayo Vallecano": "/rayo-vallecano/erfolge/verein/367",
    "Mallorca": "/rcd-mallorca/erfolge/verein/237",
}

PALABRAS_INCLUIDAS = [
    "campeón", "winner", "ganador", "copa"
]

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def cargar_palmares():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palmares (
            id SERIAL PRIMARY KEY,
            equipo_id INTEGER REFERENCES equipos(id),
            competicion VARCHAR(200),
            logro TEXT,
            creado_en TIMESTAMP DEFAULT NOW()
        )
    """)
    conn.commit()

    for nombre, url_path in URLS_EQUIPOS.items():
        cursor.execute("SELECT id FROM equipos WHERE nombre = %s", (nombre,))
        resultado = cursor.fetchone()
        if not resultado:
            print(f"✗ Equipo no encontrado en BD: {nombre}")
            continue

        equipo_id = resultado[0]
        url = BASE_URL + url_path
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.content, "lxml")

        palmares = []
        filas = soup.select("table tbody tr")
        for fila in filas:
            temporada = fila.select_one("td.zentriert")
            titulo = fila.select_one("td.no-border-links")
            if not temporada or not titulo or not titulo.text.strip():
                continue
            texto = titulo.text.strip().lower()
            if not any(incluida in texto for incluida in PALABRAS_INCLUIDAS):
                continue
            palmares.append({
                "competicion": titulo.text.strip(),
                "logro": temporada.text.strip()
            })

        print(f"✓ {len(palmares)} títulos de {nombre}")

        for titulo in palmares:
            cursor.execute("""
                INSERT INTO palmares (equipo_id, competicion, logro)
                VALUES (%s, %s, %s)
            """, (equipo_id, titulo["competicion"], titulo["logro"]))

        conn.commit()
        time.sleep(random.uniform(2, 4))

    cursor.close()
    conn.close()
    print("\nPalmarés cargado correctamente.")

if __name__ == "__main__":
    print("Extrayendo palmarés de equipos...\n")
    cargar_palmares()