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

NOMBRES_EQUIPOS = {
    "FC Barcelona": "Barcelona",
    "Athletic Club": "Athletic Club",
    "Atlético de Madrid": "Atletico Madrid",
    "RC Celta de Vigo": "Celta Vigo",
    "RCD Espanyol": "Espanyol",
    "RCD Espanyol de Barcelona": "Espanyol",
    "Getafe CF": "Getafe",
    "Girona FC": "Girona",
    "UD Las Palmas": "Las Palmas",
    "CD Leganés": "Leganes",
    "RCD Mallorca": "Mallorca",
    "CA Osasuna": "Osasuna",
    "Rayo Vallecano": "Rayo Vallecano",
    "Real Betis Balompié": "Real Betis",
    "Real Madrid CF": "Real Madrid",
    "Real Sociedad": "Real Sociedad",
    "Sevilla FC": "Sevilla",
    "Valencia CF": "Valencia",
    "Real Valladolid CF": "Valladolid",
    "Villarreal CF": "Villarreal",
    "Deportivo Alavés": "Alaves",
    "Sporting de Gijón": "Sporting Gijon",
    "Real Sporting de Gijón": "Sporting Gijon",
    "Granada CF": "Granada CF",
    "SD Eibar": "Eibar",
    "Málaga CF": "Malaga",
    "UD Almería": "Almeria",
    "Levante UD": "Levante",
    "Cádiz CF": "Cadiz",
    "Elche CF": "Elche",
    "RC Deportivo de La Coruña": "Deportivo La Coruna",
    "Real Club Deportivo de La Coruña": "Deportivo La Coruna",
    "Real Racing Club": "Racing Santander",
    "SD Huesca": "Huesca",
    "Real Zaragoza": "Zaragoza",
    "Córdoba CF": "Cordoba",
    "Hércules CF": "Hercules",
    "Real Murcia CF": "Murcia",
    "Xerez CD": "Xerez",
    "Recreativo de Huelva": "Recreativo",
    "CD Numancia": "Numancia",
    "CE Sabadell FC": "Sabadell",
    "SD Ponferradina": "Ponferradina",
    "Real Oviedo": "Oviedo",
    "CD Tenerife": "Tenerife",
    "Albacete BP": "Albacete",
    "Burgos CF": "Burgos",
    "Racing Club Ferrol": "Racing Ferrol",
    "UD Eldense": "Eldense",
    "FC Cartagena": "FC Cartagena",
    "CD Mirandés": "Mirandes",
    "Rayo Vallecano de Madrid": "Rayo Vallecano",
    "UD Logroñés": "Logrono",
    "CD Castellón": "Castellón",
    "UD Logroñés": "Logrono",
    "CD Lugo": "Lugo",
    "AD Alcorcón": "Alcorcon",
    "Gimnàstic de Tarragona": "Nastic",
    "CF Fuenlabrada": "Fuenlabrada",
    "SD Amorebieta": "Amorebieta",
    "Cultural Leonesa": "Cultural Leonesa",
    "CD Badajoz": "Badajoz",
}

def conectar_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def get_partidos_jornada(jornada, temporada="2024"):
    url = f"{BASE_URL}/laliga/spieltag/wettbewerb/ES1/saison_id/{temporada}/spieltag/{jornada}"
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "lxml")

    partidos = []
    bloques = soup.select("div.box")

    for bloque in bloques:
        fila_principal = bloque.select_one("tr.table-grosse-schrift")
        if not fila_principal:
            continue

        try:
            celdas_equipo = fila_principal.select("td.spieltagsansicht-vereinsname.hide-for-small a[title]")
            nombres_equipos = [e["title"] for e in celdas_equipo if e.get("title") and "jornada" not in e["title"].lower() and "hilo" not in e["title"].lower()]

            if len(nombres_equipos) < 2:
                continue

            equipo_local = nombres_equipos[0]
            equipo_visitante = nombres_equipos[1]

            resultado = bloque.select_one("span.matchresult.finished")
            if not resultado:
                continue

            marcador = resultado.text.strip()
            partes = marcador.split(":")
            if len(partes) != 2:
                continue

            goles_local = int(partes[0].strip())
            goles_visitante = int(partes[1].strip())

            url_informe = bloque.select_one("a.liveLink")
            url_partido = BASE_URL + url_informe["href"] if url_informe else None

            eventos = []
            filas_eventos = bloque.select("tr.spieltagsansicht-aktionen")
            for fila in filas_eventos:
                jugador_tag = fila.select_one("a[href*='/profil/spieler/']")
                tipo_tag = fila.select_one("span[class*='icon-']")

                if not jugador_tag or not tipo_tag:
                    continue

                minuto_tag = fila.select_one("td.zentriert.no-border-links")
                minuto_texto = minuto_tag.text.strip().replace("'", "") if minuto_tag else ""
                if "+" in minuto_texto:
                    partes_min = minuto_texto.split("+")
                    try:
                        minuto = int(partes_min[0]) + int(partes_min[1])
                    except Exception:
                        minuto = None
                else:
                    minuto = int(minuto_texto) if minuto_texto.isdigit() else None

                jugador = jugador_tag.text.strip()
                tipo = "gol"

                clases = " ".join(tipo_tag.get("class", []))
                if "rotekarte" in clases:
                    tipo = "tarjeta_roja"
                elif "gelbekarte" in clases:
                    tipo = "tarjeta_amarilla"
                elif "eigentor" in clases:
                    tipo = "gol_propio"

                celda_local = fila.select_one("td.rechts.no-border-rechts")
                if celda_local and jugador_tag in celda_local.find_all("a"):
                    equipo_evento = equipo_local
                else:
                    equipo_evento = equipo_visitante

                eventos.append({
                    "minuto": minuto,
                    "tipo": tipo,
                    "jugador_nombre": jugador,
                    "equipo_nombre": equipo_evento
                })

            partidos.append({
                "equipo_local": equipo_local,
                "equipo_visitante": equipo_visitante,
                "goles_local": goles_local,
                "goles_visitante": goles_visitante,
                "jornada": jornada,
                "temporada": temporada,
                "url": url_partido,
                "eventos": eventos
            })

        except Exception:
            continue

    print(f"  Jornada {jornada}: {len(partidos)} partidos encontrados")
    return partidos

def obtener_o_crear_equipo(cursor, nombre):
    cursor.execute("SELECT id FROM equipos WHERE nombre ILIKE %s", (nombre,))
    resultado = cursor.fetchone()
    if resultado:
        return resultado[0]

    cursor.execute("""
        INSERT INTO equipos (nombre, liga, categoria)
        VALUES (%s, 'LaLiga', 'Primera División')
        RETURNING id
    """, (nombre,))
    nuevo = cursor.fetchone()
    print(f"  ✓ Equipo nuevo creado: {nombre}")
    return nuevo[0]

def insertar_partido(cursor, partido):
    nombre_local = NOMBRES_EQUIPOS.get(partido["equipo_local"], partido["equipo_local"])
    nombre_visitante = NOMBRES_EQUIPOS.get(partido["equipo_visitante"], partido["equipo_visitante"])

    local_id = obtener_o_crear_equipo(cursor, nombre_local)
    visitante_id = obtener_o_crear_equipo(cursor, nombre_visitante)

    cursor.execute("""
        INSERT INTO partidos (equipo_local_id, equipo_visitante_id, goles_local, goles_visitante, jornada, competicion, temporada)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id
    """, (
        local_id, visitante_id,
        partido["goles_local"], partido["goles_visitante"],
        partido["jornada"], "LaLiga",
        partido["temporada"]
    ))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def cargar_temporada(temporada="2024", jornadas=38):
    conn = conectar_db()
    cursor = conn.cursor()

    print(f"\nCargando temporada {temporada}/{int(temporada)+1}...\n")

    for jornada in range(1, jornadas + 1):
        partidos = get_partidos_jornada(jornada, temporada)

        for partido in partidos:
            partido_id = insertar_partido(cursor, partido)
            if not partido_id:
                continue

            for evento in partido.get("eventos", []):
                equipo_nombre_bd = NOMBRES_EQUIPOS.get(evento["equipo_nombre"], evento["equipo_nombre"])
                cursor.execute("""
                    INSERT INTO eventos_partido (partido_id, minuto, tipo, jugador_nombre, equipo_nombre)
                    VALUES (%s, %s, %s, %s, %s)
                """, (partido_id, evento["minuto"], evento["tipo"], evento["jugador_nombre"], equipo_nombre_bd))

        conn.commit()
        print(f"✓ Jornada {jornada} completada")
        time.sleep(random.uniform(2, 3))

    cursor.close()
    conn.close()
    print(f"Temporada {temporada} cargada correctamente.")

if __name__ == "__main__":
    for temporada in ["2024", "2023", "2022", "2021", "2020", "2019", "2018", "2017", "2016", "2015", "2014", "2013", "2012"]:
        cargar_temporada(temporada, 38)