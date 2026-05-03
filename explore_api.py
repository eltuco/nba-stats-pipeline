# explore_api.py
# import des fonctions de l'API client pour tester les appels API

from src.api_client import get_players, get_games, get_teams
from src.models import Player, Team, Game

"""
# Test 1 — Chercher un joueur
print("=== Test 1 : Chercher LeBron James ===")
result = get_players(search="LeBron")
lebron = result["data"][0]
print(f"ID: {lebron['id']} | {lebron['first_name']} {lebron['last_name']} — {lebron['team']['full_name']}")

# Test 2 — Récupérer les équipes
print("\n=== Test 2 : Liste des équipes ===")
teams = get_teams()
for team in teams["data"][:5]:
    print(f"{team['full_name']} ({team['abbreviation']}) — {team['conference']} Conference")

# Test 3 — Récupérer des matchs de la saison 2024
print("\n=== Test 3 : 5 premiers matchs de la saison 2024 ===")
games = get_games(season=2024)
for game in games["data"][:5]:
    print(f"{game['date'][:10]} | {game['home_team']['full_name']} {game['home_team_score']} - {game['visitor_team_score']} {game['visitor_team']['full_name']}")

# Tests 4 
## Test modèle Team
print("\n=== Test 4 : Création d'une instance Team ===") 
team_data = get_teams() 
teams = [Team(**t) for t in team_data["data"]]
print(f"{len(teams)} équipes chargées")
print(f"Première équipe : {teams[0].full_name} ({teams[0].abbreviation}) — {teams[0].conference} Conference")

## Test modèle Player
players_data = get_players(search="LeBron")
players = [Player(**p) for p in players_data["data"]]
lebron = players[0]
print(f"\nJoueur : {lebron.full_name} — {lebron.team.full_name if lebron.team else 'Sans équipe'}")

## Test modèle Game + properties
print("\n=== 5 matchs avec vainqueur et écart ===")
games_data = get_games(season=2024)
games = [Game(**g) for g in games_data["data"][:5]]
for game in games:
    print(f"{game.date[:10]} | Vainqueur: {game.winner} | Écart: {game.point_difference} pts")

"""
# Mock temporaire pour tester les modèles Game sans appeler l'API
team_data = get_teams() 
mock_game = {
    "id": 1,
    "date": "2024-10-22T00:00:00.000Z",
    "season": 2024,
    "status": "Final",
    "home_team": team_data["data"][0],
    "visitor_team": team_data["data"][1],
    "home_team_score": 112,
    "visitor_team_score": 98
}

game = Game(**mock_game)
print(f"{game.date[:10]} | Vainqueur: {game.winner} | Écart: {game.point_difference} pts")