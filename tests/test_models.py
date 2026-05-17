# test_models.py
import pytest
from pydantic import ValidationError
from src.models import Team, Game, Player

# ============================================================
# Fixtures — données de test réutilisables
# ============================================================
@pytest.fixture
def team_data():
    return {
        "id": 20,
        "full_name": "New York Knicks",
        "abbreviation": "NYK",
        "city": "New York",
        "conference": "East",
        "division": "Atlantic",
        "name": "Knicks"
    }

@pytest.fixture
def player_data():
    return {
        "id": 73,
        "first_name": "Jalen",
        "last_name": "Brunson",
        "position": "G",
        "height": "6-2",
        "weight": "190",
        "team": {
            "id": 20,
            "full_name": "New York Knicks",
            "abbreviation": "NYK",
            "conference": "East",
            "division": "Atlantic",
            "city": "New York",
            "name": "Knicks"
        }
    }
@pytest.fixture
def game_data(team_data):
    visitor = {
        "id": 2,
        "full_name": "Philadelphia 76ers",
        "abbreviation": "PHI",
        "conference": "East",
        "division": "Atlantic",
        "city": "Philadelphia",
        "name": "76ers"
    }
    return {
        "id": 1,
        "date": "2026-05-11T00:00:00.000Z",
        "season": 2025,
        "status": "Final",
        "home_team": team_data,
        "visitor_team": visitor,
        "home_team_score": 114,
        "visitor_team_score": 98
    }

# ============================================================
# Tests Team
# ============================================================

def test_team_valid(team_data):
    """Un team valide doit être créé sans erreur."""
    team = Team(**team_data)
    assert team.id == 20
    assert team.full_name == "New York Knicks"
    assert team.abbreviation == "NYK"

def test_team_missing_field(team_data):
    """Un champ obligatoire manquant doit lever une ValidationError."""
    del team_data["full_name"]
    with pytest.raises(ValidationError):
        Team(**team_data)

def test_team_wrong_type(team_data):
    """Un mauvais type doit lever une ValidationError."""
    team_data["id"] = "pas_un_entier"
    with pytest.raises(ValidationError):
        Team(**team_data)


# ============================================================
# Tests Player
# ============================================================

def test_player_valid(player_data):
    """Un joueur valide doit être créé sans erreur."""
    player = Player(**player_data)
    assert player.full_name == "Jalen Brunson"
    assert player.team.full_name == "New York Knicks"

def test_player_optional_fields():
    """Un joueur sans champs optionnels doit être valide."""
    player = Player(id=1, first_name="Jalen", last_name="Brunson")
    assert player.position is None
    assert player.team is None

def test_player_full_name(player_data):
    """La property full_name doit concatener prénom et nom."""
    player = Player(**player_data)
    assert player.full_name == "Jalen Brunson"


# ============================================================
# Tests Game
# ============================================================

def test_game_valid(game_data):
    """Un match valide doit être créé sans erreur."""
    game = Game(**game_data)
    assert game.id == 1
    assert game.season == 2025

def test_game_winner_home(game_data):
    """Le vainqueur doit être l'équipe à domicile si son score est plus élevé."""
    game = Game(**game_data)
    assert game.winner is not None
    assert game.winner.full_name == "New York Knicks"
    assert game.winner.id == 20

def test_game_winner_visitor(game_data):
    """Le vainqueur doit être l'équipe visiteuse si son score est plus élevé."""
    game_data["home_team_score"] = 98
    game_data["visitor_team_score"] = 114
    game = Game(**game_data)
    assert game.winner is not None
    assert game.winner.full_name == "Philadelphia 76ers"
    assert game.winner.id == 2

def test_game_draw(game_data):
    """Un match nul doit retourner None."""
    game_data["home_team_score"] = 100
    game_data["visitor_team_score"] = 100
    game = Game(**game_data)
    assert game.winner is None

def test_game_point_difference(game_data):
    """L'écart de points doit être correct."""
    game = Game(**game_data)
    assert game.point_difference == 16