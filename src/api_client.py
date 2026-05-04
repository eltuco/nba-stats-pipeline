import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

# Récupération de la clé API depuis les variables d'environnement
API_KEY = os.getenv("BALLDONTLIE_API_KEY")

# Création d'un client API pour interagir avec l'API balldontlie
BASE_URL = "https://api.balldontlie.io"
HEADERS = {
    "Authorization": API_KEY
}


# Timestamp du dernier appel
_last_call_time = 0
_min_interval = 60 / 5  # 5 calls/minute = 1 appel toutes les 12 secondes

def _rate_limit():
    """Attend si nécessaire pour respecter le rate limit."""
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < _min_interval:
        wait = _min_interval - elapsed
        print(f"Rate limit : attente de {wait:.1f}s...")
        time.sleep(wait)
    _last_call_time = time.time()

# Structuration d'une réponse typique de l'API:
# response = requests.get(f"{BASE_URL}/endpoint", headers=api_key, params=paramètres du endpoint)   

# Fonctions pour interagir avec l'API
def get_players(search: str=None, per_page: int=25, page: int=1)-> dict:
    """
    Récupère une liste de joueurs NBA avec une option de recherche par nom.
    Args:
        search (str, optional): Terme de recherche pour filtrer les joueurs. Défaut: None.
        per_page (int, optional): Nombre de résultats par page. Défaut: 25.
        page (int, optional): Numéro de la page à récupérer. Défaut: 1.
    Returns:
        dict: Un dictionnaire contenant les données des joueurs récupérés.
    """
    params = {"per_page": per_page, "page": page}
    if search:
        params["search"] = search
    _rate_limit()
    response = requests.get(
        f"{BASE_URL}/v1/players", 
        headers=HEADERS, 
        params=params)
    response.raise_for_status()
    return response.json()


def get_teams() -> dict:
    """
    Récupère la liste de toutes les équipes NBA.
    Returns:
        Dictionnaire contenant les données de l'API
    """
    _rate_limit()
    response = requests.get(
        f"{BASE_URL}/v1/teams",
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

def get_games(date: str = None, season: int = None, per_page: int = 10) -> dict:
    """
    Récupère les matchs NBA par date ou par saison.

    Args:
        date: Date au format YYYY-MM-DD (optionnel)
        season: Année de la saison ex: 2024 (optionnel)
        per_page: Nombre de résultats par page

    Returns:
        Dictionnaire contenant les données de l'API
    """
    _rate_limit()

    params = {"per_page": per_page}
    if date:
        params["dates[]"] = date
    if season:
        params["seasons[]"] = season

    response = requests.get(
        f"{BASE_URL}/nba/v1/games",
        headers=HEADERS,
        params=params
    )
    response.raise_for_status()
    return response.json()