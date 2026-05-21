import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY")
BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}

def get_equipos_laliga():
    """Obtiene todos los equipos de LaLiga temporada 2024"""
    url = f"{BASE_URL}/teams"
    params = {
        "league": 140,  # 140 es el ID de LaLiga en API-Football
        "season": 2024
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if "response" not in data:
        print("Error en la API:", data)
        return []

    equipos = []
    for item in data["response"]:
        equipo = {
            "nombre": item["team"]["name"],
            "nombre_corto": item["team"]["code"],
            "ciudad": item["venue"]["city"],
            "estadio": item["venue"]["name"],
            "escudo_url": item["team"]["logo"]
        }
        equipos.append(equipo)
        print(f"✓ {equipo['nombre']} - {equipo['ciudad']}")

    return equipos

if __name__ == "__main__":
    print("Extrayendo equipos de LaLiga...")
    equipos = get_equipos_laliga()
    print(f"\nTotal equipos encontrados: {len(equipos)}")


def get_equipos_segunda():
    """Obtiene todos los equipos de Segunda División temporada 2024"""
    url = f"{BASE_URL}/teams"
    params = {
        "league": 141,  # 141 es el ID de LaLiga 2 en API-Football
        "season": 2024
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if "response" not in data:
        print("Error en la API:", data)
        return []

    equipos = []
    for item in data["response"]:
        equipo = {
            "nombre": item["team"]["name"],
            "nombre_corto": item["team"]["code"],
            "ciudad": item["venue"]["city"],
            "estadio": item["venue"]["name"],
            "escudo_url": item["team"]["logo"]
        }
        equipos.append(equipo)
        print(f"✓ {equipo['nombre']} - {equipo['ciudad']}")

    return equipos

def get_jugadores_equipo(equipo_id_api, equipo_nombre):
    """Obtiene los jugadores de un equipo"""
    url = f"{BASE_URL}/players"
    params = {
        "team": equipo_id_api,
        "season": 2024
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if "response" not in data:
        print(f"Error obteniendo jugadores de {equipo_nombre}:", data)
        return []

    jugadores = []
    for item in data["response"]:
        jugador = {
            "nombre": item["player"]["name"],
            "nombre_corto": item["player"]["firstname"],
            "fecha_nacimiento": item["player"]["birth"]["date"],
            "nacionalidad": item["player"]["nationality"],
            "posicion": item["statistics"][0]["games"]["position"] if item["statistics"] else None,
            "foto_url": item["player"]["photo"]
        }
        jugadores.append(jugador)

    print(f"✓ {len(jugadores)} jugadores de {equipo_nombre}")
    return jugadores

def get_ids_equipos_laliga():
    """Obtiene los IDs de la API para cada equipo de LaLiga"""
    endpoint = f"{BASE_URL}/teams"
    params = {"league": 140, "season": 2024}
    response = requests.get(endpoint, headers=HEADERS, params=params)
    data = response.json()
    return [(item["team"]["id"], item["team"]["name"]) for item in data["response"]]