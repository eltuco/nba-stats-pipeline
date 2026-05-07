import os
import requests
from dotenv import load_dotenv
import time
from src.logger import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from requests.exceptions import HTTPError


load_dotenv()

# Récupération de la clé API depuis les variables d'environnement
API_KEY = os.getenv("BALLDONTLIE_API_KEY")

# Création d'un client API pour interagir avec l'API balldontlie
BASE_URL = "https://api.balldontlie.io"
HEADERS = {
    "Authorization": API_KEY
}
# Création d'un temps d'attente pour respecter le rate limit de l'API (5 appels/minute)
## Paramètres pour le rate limit
_last_call_time = 0
_min_interval = 60 / 5  # 5 calls/minute = 1 appel toutes les 12 secondes

def _rate_limit():
    """Attend si nécessaire pour respecter le rate limit."""
    global _last_call_time  # ← Je vais MODIFIER la variable globale
    
    elapsed = time.time() - _last_call_time  # Temps écoulé depuis le dernier appel
    
    if elapsed < _min_interval:  # Si pas assez de temps écoulé (< 12s)
        wait = _min_interval - elapsed  # Calculer combien attendre
        logger.debug(f"Rate limit : attente de {wait:.1f}s...")
        time.sleep(wait)  # Pause forcée
    
    _last_call_time = time.time()  # ← Mise à jour du timestamp pour le prochain appel

def _is_rate_limit_error(exception) -> bool:
    """Retourne True si l'erreur est un 429 ou 500."""
    return isinstance(exception, HTTPError) and exception.response.status_code in [429, 500]


@retry(
    retry=retry_if_exception_type(HTTPError),
    wait=wait_exponential(multiplier=2, min=12, max=60),
    stop=stop_after_attempt(5),
    reraise=True
)
# Structuration d'une réponse typique de l'API:
# response = requests.get(f"{BASE_URL}/endpoint", headers=api_key, params=paramètres du endpoint)   

# Fonctions pour interagir avec l'API

# @retry :
# retry_if_exception_type(HTTPError) → réessaie uniquement sur les erreurs HTTP
# wait_exponential(multiplier=2, min=12, max=60) → attend 12s, puis 24s, puis 48s, max 60s
# stop_after_attempt(5) → abandonne après 5 tentatives
# reraise=True → si toutes les tentatives échouent, lève quand même l'erreur

@retry(
    retry=retry_if_exception_type(HTTPError),
    wait=wait_exponential(multiplier=2, min=12, max=60),
    stop=stop_after_attempt(5),
    reraise=True
)
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
    _rate_limit()

    params = {"per_page": per_page, "page": page}
    if search:
        params["search"] = search
   
    response = requests.get(
        f"{BASE_URL}/v1/players", 
        headers=HEADERS, 
        params=params
    )
    response.raise_for_status()
    logger.debug(f"get_players: {response.url} - Status: {response.status_code}")
    return response.json()

@retry(
    retry=retry_if_exception_type(HTTPError),
    wait=wait_exponential(multiplier=2, min=12, max=60),
    stop=stop_after_attempt(5),
    reraise=True
)
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
    logger.debug(f"get_teams: {response.url} - Status: {response.status_code}")
    return response.json()

@retry(
    retry=retry_if_exception_type(HTTPError),
    wait=wait_exponential(multiplier=2, min=12, max=60),
    stop=stop_after_attempt(5),
    reraise=True
)
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
    logger.debug(f"get_games: {response.url} - Status: {response.status_code}")
    return response.json()