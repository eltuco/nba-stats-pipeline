from pydantic import BaseModel # Importation de BaseModel pour la validation des données
from typing import Optional

class Team(BaseModel):
    id: int
    abbreviation: str
    city: str
    conference: str
    division: str
    full_name: str
    name: str

class Player(BaseModel):
    id: int
    first_name: str
    last_name: str
    position: Optional[str] = None
    height: Optional[str] = None
    weight: Optional[str] = None
    team: Optional[Team] = None

    @property # @property pour créer une méthode qui se comporte comme un attribut
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
class Game(BaseModel):
    id: int
    date: str
    home_team: Team
    visitor_team: Team
    home_team_score: int
    visitor_team_score: int
    season: int
    status: str

    @property # @property pour créer une méthode qui se comporte comme un attribut
    def winner(self) -> str:
        if self.home_team_score > self.visitor_team_score:
            return self.home_team.full_name
        elif self.visitor_team_score > self.home_team_score:
            return self.visitor_team.full_name
        return "Draw"
    
    @property # @property pour créer une méthode qui se comporte comme un attribut
    def point_difference(self) -> int:
        return abs(self.home_team_score - self.visitor_team_score)  
    
"""
class PersonneSimple:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

data = {"first_name": "LeBron", "last_name": "James"}

# Ces 2 syntaxes sont équivalentes :
p1 = PersonneSimple(first_name="LeBron", last_name="James")
p2 = PersonneSimple(**data)  # ← Le ** déplie le dict

######

player_dict = {
    "id": 237,
    "first_name": "LeBron",
    "last_name": "James",
    "position": "F",
    "team": {...}
}

# Ces 2 syntaxes fonctionnent :
player1 = Player(id=237, first_name="LeBron", last_name="James", ...)  # Verbeux
player2 = Player(**player_dict)  # ← Élégant et direct
 """