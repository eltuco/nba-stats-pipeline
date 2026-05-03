import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BALLDONTLIE_API_KEY")
# Remplace cette ligne
BASE_URL = "https://api.balldontlie.io/v1"

HEADERS = {
    "Authorization": API_KEY
}

def get_players(search: str=None, per_page: int=25, page: int=1)-> dict:
    """
    Récupère une liste de joueurs NBA

    Args:
        search (str, optional): Terme de recherche pour filtrer les joueurs. Défaut: None.
        per_page (int, optional): Nombre de résultats par page. éfaut: 25.
        page (int, optional): Numéro de la page à récupérer. Défaut: 1.

    Returns:
        dict: Un dictionnaire contenant les données des joueurs récupérés.
    """
    params = {"per_page": per_page,"page": page}
    if search:
        params["search"] = search
    
    response = requests.get(
        f"{BASE_URL}/players", 
        headers=HEADERS, 
        params=params)
    response.raise_for_status()
    return response.json()

def get_games(season: int, per_page: int = 100) -> dict:
    """
    Récupère les matchs d'une saison NBA.

    Args:
        season: Année de la saison (ex: 2024 pour 2024-2025)
        per_page: Nombre de résultats par page (max 100)

    Returns:
        Dictionnaire contenant les données de l'API
    """
    params = {
        "seasons[]": season,
        "per_page": per_page
    }

    response = requests.get(
        f"{BASE_URL}/games",
        headers=HEADERS,
        params=params
    )
    response.raise_for_status()
    return response.json()


def get_teams() -> dict:
    """
    Récupère la liste de toutes les équipes NBA.

    Returns:
        Dictionnaire contenant les données de l'API
    """
    response = requests.get(
        f"{BASE_URL}/teams",
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()