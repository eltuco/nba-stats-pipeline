"""
Template générique de client API - Version améliorée
====================================================

Améliorations par rapport à api_client.py :
- Architecture orientée objet (classe)
- Session HTTP réutilisable (connexions persistantes)
- Décorateur mutualisé (pas de répétition)
- Timeouts configurables
- Pagination automatique
- Exceptions personnalisées
- Type hints complets
- Context manager support

Utilisation :
------------
from api_client_template import APIClient

client = APIClient(
    base_url="https://api.example.com",
    api_key="your_key",
    rate_limit=5  # appels par minute
)

# Utilisation simple
data = client.get("/v1/players", params={"search": "Jordan"})

# Récupération paginée automatique
all_data = client.get_all_pages("/v1/players")

# Avec context manager (ferme automatiquement la session)
with APIClient(base_url="...", api_key="...") as client:
    data = client.get("/endpoint")
"""

import os
import time
import requests
from typing import Dict, Any, Optional, Generator, List
from functools import wraps
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from requests.exceptions import HTTPError, RequestException
import logging

load_dotenv()


# ==============================================================================
# Exceptions personnalisées
# ==============================================================================

class APIClientError(Exception):
    """Exception de base pour le client API"""
    pass


class RateLimitError(APIClientError):
    """Erreur de dépassement du rate limit"""
    pass


class AuthenticationError(APIClientError):
    """Erreur d'authentification"""
    pass


class ResourceNotFoundError(APIClientError):
    """Ressource non trouvée (404)"""
    pass


# ==============================================================================
# Client API générique
# ==============================================================================

class APIClient:
    """
    Client API générique avec rate limiting, retry automatique et pagination.
    
    Attributes:
        base_url: URL de base de l'API
        api_key: Clé d'authentification
        rate_limit: Nombre maximum d'appels par minute
        timeout: Timeout par défaut en secondes
        max_retries: Nombre maximum de tentatives en cas d'erreur
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        rate_limit: int = 60,
        timeout: int = 30,
        max_retries: int = 5,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialise le client API.
        
        Args:
            base_url: URL de base de l'API (ex: "https://api.example.com")
            api_key: Clé d'authentification
            rate_limit: Nombre d'appels autorisés par minute (défaut: 60)
            timeout: Timeout en secondes pour chaque requête (défaut: 30)
            max_retries: Nombre de tentatives en cas d'erreur (défaut: 5)
            logger: Logger personnalisé (optionnel)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Rate limiting
        self._rate_limit = rate_limit
        self._min_interval = 60.0 / rate_limit  # Secondes entre chaque appel
        self._last_call_time = 0.0
        
        # Session HTTP réutilisable (connexions persistantes = plus rapide)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": api_key,
            "User-Agent": "APIClient/1.0"
        })
        
        # Logger
        self.logger = logger or logging.getLogger(__name__)
    
    def __enter__(self):
        """Support du context manager (with statement)"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ferme la session proprement"""
        self.close()
    
    def close(self):
        """Ferme la session HTTP"""
        self.session.close()
    
    # ==========================================================================
    # Rate limiting
    # ==========================================================================
    
    def _wait_for_rate_limit(self):
        """Attend si nécessaire pour respecter le rate limit."""
        elapsed = time.time() - self._last_call_time
        
        if elapsed < self._min_interval:
            wait_time = self._min_interval - elapsed
            self.logger.debug(f"Rate limit: attente de {wait_time:.2f}s")
            time.sleep(wait_time)
        
        self._last_call_time = time.time()
    
    # ==========================================================================
    # Décorateur pour retry automatique (mutualisé)
    # ==========================================================================
    
    def _with_retry(self, func):
        """
        Décorateur qui ajoute le retry automatique à une méthode.
        
        Stratégie:
        - Retry uniquement sur HTTPError et RequestException
        - Attente exponentielle: 12s → 24s → 48s → 60s (max)
        - Maximum 5 tentatives
        - Relève l'exception si toutes les tentatives échouent
        """
        @wraps(func)
        @retry(
            retry=retry_if_exception_type((HTTPError, RequestException)),
            wait=wait_exponential(multiplier=2, min=12, max=60),
            stop=stop_after_attempt(self.max_retries),
            reraise=True
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    # ==========================================================================
    # Gestion des erreurs HTTP
    # ==========================================================================
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Gère la réponse HTTP et lève des exceptions appropriées.
        
        Args:
            response: Objet Response de requests
            
        Returns:
            Dictionnaire JSON de la réponse
            
        Raises:
            AuthenticationError: Si erreur 401/403
            ResourceNotFoundError: Si erreur 404
            RateLimitError: Si erreur 429
            APIClientError: Pour toute autre erreur HTTP
        """
        try:
            response.raise_for_status()
        except HTTPError as e:
            status_code = response.status_code
            
            # Erreurs spécifiques avec messages clairs
            if status_code == 401:
                raise AuthenticationError(f"Authentification invalide: {response.text}")
            elif status_code == 403:
                raise AuthenticationError(f"Accès interdit: {response.text}")
            elif status_code == 404:
                raise ResourceNotFoundError(f"Ressource non trouvée: {response.url}")
            elif status_code == 429:
                raise RateLimitError(f"Rate limit dépassé: {response.text}")
            else:
                raise APIClientError(f"Erreur HTTP {status_code}: {response.text}") from e
        
        self.logger.debug(f"✓ {response.request.method} {response.url} - {response.status_code}")
        return response.json()
    
    # ==========================================================================
    # Méthodes HTTP de base
    # ==========================================================================
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Effectue une requête GET.
        
        Args:
            endpoint: Chemin de l'endpoint (ex: "/v1/players")
            params: Paramètres de requête (optionnel)
            timeout: Timeout personnalisé (optionnel)
            **kwargs: Arguments supplémentaires pour requests
            
        Returns:
            Dictionnaire JSON de la réponse
        """
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        
        # Le retry est appliqué automatiquement via _with_retry
        @self._with_retry
        def _do_request():
            response = self.session.get(
                url,
                params=params,
                timeout=timeout,
                **kwargs
            )
            return self._handle_response(response)
        
        return _do_request()
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Effectue une requête POST.
        
        Args:
            endpoint: Chemin de l'endpoint
            data: Données form-encoded (optionnel)
            json: Données JSON (optionnel)
            timeout: Timeout personnalisé (optionnel)
            **kwargs: Arguments supplémentaires pour requests
            
        Returns:
            Dictionnaire JSON de la réponse
        """
        self._wait_for_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        
        @self._with_retry
        def _do_request():
            response = self.session.post(
                url,
                data=data,
                json=json,
                timeout=timeout,
                **kwargs
            )
            return self._handle_response(response)
        
        return _do_request()
    
    # ==========================================================================
    # Pagination automatique
    # ==========================================================================
    
    def get_paginated(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        per_page: int = 100,
        max_pages: Optional[int] = None,
        page_param: str = "page",
        per_page_param: str = "per_page"
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Générateur qui récupère automatiquement toutes les pages.
        
        Args:
            endpoint: Chemin de l'endpoint
            params: Paramètres de base
            per_page: Nombre de résultats par page
            max_pages: Nombre maximum de pages à récupérer (None = toutes)
            page_param: Nom du paramètre de pagination (défaut: "page")
            per_page_param: Nom du paramètre de taille (défaut: "per_page")
            
        Yields:
            Chaque page de résultats sous forme de dictionnaire
            
        Example:
            >>> for page in client.get_paginated("/v1/players"):
            ...     for player in page["data"]:
            ...         print(player["name"])
        """
        params = params or {}
        params[per_page_param] = per_page
        
        page = 1
        while True:
            # Limite de pages atteinte
            if max_pages and page > max_pages:
                break
            
            params[page_param] = page
            data = self.get(endpoint, params=params)
            
            yield data
            
            # Pas de données ou dernière page atteinte
            # (adapter selon la structure de réponse de votre API)
            if not data.get("data") or len(data.get("data", [])) < per_page:
                break
            
            page += 1
    
    def get_all_pages(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Récupère toutes les pages et retourne une liste consolidée.
        
        Args:
            endpoint: Chemin de l'endpoint
            params: Paramètres de requête
            **kwargs: Arguments pour get_paginated
            
        Returns:
            Liste de tous les éléments récupérés
            
        Example:
            >>> all_players = client.get_all_pages("/v1/players")
            >>> print(f"Total: {len(all_players)} joueurs")
        """
        all_items = []
        for page in self.get_paginated(endpoint, params=params, **kwargs):
            # Adapter selon la structure de votre API
            items = page.get("data", [])
            all_items.extend(items)
            
            self.logger.info(f"Récupéré {len(items)} éléments (total: {len(all_items)})")
        
        return all_items


# ==============================================================================
# Exemple d'implémentation spécifique : NBA API Client
# ==============================================================================

class NBAClient(APIClient):
    """
    Client spécifique pour l'API NBA (hérite du template générique).
    
    Example:
        >>> client = NBAClient()
        >>> players = client.get_players(search="LeBron")
        >>> teams = client.get_all_teams()
    """
    
    def __init__(self, api_key: Optional[str] = None, rate_limit: int = 5):
        """
        Initialise le client NBA.
        
        Args:
            api_key: Clé API (si None, cherche dans BALLDONTLIE_API_KEY)
            rate_limit: Appels par minute (API NBA = 5 max)
        """
        api_key = api_key or os.getenv("BALLDONTLIE_API_KEY")
        if not api_key:
            raise ValueError("API key manquante (env: BALLDONTLIE_API_KEY)")
        
        super().__init__(
            base_url="https://api.balldontlie.io",
            api_key=api_key,
            rate_limit=rate_limit,
            timeout=30,
            max_retries=5
        )
    
    # Méthodes spécifiques à l'API NBA (interface simplifiée)
    
    def get_players(
        self,
        search: Optional[str] = None,
        per_page: int = 25,
        page: int = 1
    ) -> Dict[str, Any]:
        """Récupère une liste de joueurs NBA."""
        params = {"per_page": per_page, "page": page}
        if search:
            params["search"] = search
        
        return self.get("/v1/players", params=params)
    
    def get_all_players(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Récupère TOUS les joueurs (toutes pages confondues)."""
        params = {}
        if search:
            params["search"] = search
        
        return self.get_all_pages("/v1/players", params=params)
    
    def get_teams(self) -> Dict[str, Any]:
        """Récupère toutes les équipes NBA."""
        return self.get("/v1/teams")
    
    def get_games(
        self,
        date: Optional[str] = None,
        season: Optional[int] = None,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """
        Récupère les matchs NBA.
        
        Args:
            date: Date au format YYYY-MM-DD
            season: Année de la saison (ex: 2024)
            per_page: Nombre de résultats par page
        """
        params = {"per_page": per_page}
        if date:
            params["dates[]"] = date
        if season:
            params["seasons[]"] = season
        
        return self.get("/v1/games", params=params)


# ==============================================================================
# Exemples d'utilisation
# ==============================================================================

if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    
    # Exemple 1: Client générique
    print("=== Client API générique ===")
    client = APIClient(
        base_url="https://api.example.com",
        api_key="your_key",
        rate_limit=60
    )
    
    # Avec context manager (recommandé)
    with APIClient(base_url="...", api_key="...") as client:
        data = client.get("/endpoint")
    
    # Exemple 2: Client NBA spécifique
    print("\n=== Client NBA ===")
    nba_client = NBAClient()
    
    # Recherche simple
    lebron = nba_client.get_players(search="LeBron")
    print(f"Résultats: {lebron['meta']['total_count']} joueurs")
    
    # Récupération paginée automatique
    all_players = nba_client.get_all_players()
    print(f"Total joueurs: {len(all_players)}")
    
    # Fermeture propre
    nba_client.close()
