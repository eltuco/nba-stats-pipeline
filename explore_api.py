# explore_api.py
# import des fonctions de l'API client pour tester les appels API

from src.api_client import get_players, get_games, get_teams

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