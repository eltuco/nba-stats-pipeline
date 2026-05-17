# Importation de la librairie Pydantic qui permet de valider les données 
# en définissant des modèles de données (classes) avec des types spécifiques.

from pydantic import BaseModel 
from typing import Optional
from datetime import date as date_type
from pydantic import field_validator
from pydantic.config import ConfigDict

class Team(BaseModel):
    model_config = ConfigDict(
        frozen=True,  # Immuable (team ne change pas après création)
        str_strip_whitespace=True,  # Nettoie les espaces
        validate_assignment=True  # Valide même après création
    )
    id: int
    abbreviation: str
    city: str
    conference: str
    division: str
    full_name: str
    name: str

class Player(BaseModel):
    """
    Représente un joueur NBA.
    
    Attributes:
        id: Identifiant unique du joueur
        first_name: Prénom
        last_name: Nom de famille
        position: Position (G, F, C) ou None
        team: Équipe actuelle ou None (free agent)
    """
    id: int
    first_name: str
    last_name: str
    position: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    team: Optional[Team] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None

    @property # @property pour créer une méthode qui se comporte comme un attribut
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
class Game(BaseModel):
    id: int
    date: date_type  # Validation automatique + méthodes datetime
    home_team: Team
    visitor_team: Team
    home_team_score: int
    visitor_team_score: int
    season: int
    status: str

    @property # @property pour créer une méthode qui se comporte comme un attribut
    def winner(self) -> Optional[Team]:
        """Retourne l'équipe gagnante ou None en cas d'égalité."""
        if self.home_team_score > self.visitor_team_score:
            return self.home_team
        elif self.visitor_team_score > self.home_team_score:
            return self.visitor_team
        return None  # Ou lever une exception si impossible
    
    @property # @property pour créer une méthode qui se comporte comme un attribut
    def point_difference(self) -> int:
        return abs(self.home_team_score - self.visitor_team_score)  
    
    @field_validator('home_team_score', 'visitor_team_score')
    def score_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Le score ne peut pas être négatif')
        return v

    @property
    def is_overtime(self) -> bool:
        """Détecte si le match est allé en prolongation."""
        # Note: Cette détection est approximative car l'API ne fournit pas
        # directement cette information. Un match NBA typique a un score
        # total entre 180-230 points. Au-delà, c'est probablement overtime.
        total_score = self.home_team_score + self.visitor_team_score
        return total_score > 230
        
    @property
    def margin_of_victory(self) -> int:
        """Marge de victoire (peut être négative)."""
        return self.home_team_score - self.visitor_team_score