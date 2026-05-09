# loader.py
import duckdb
import os
from dotenv import load_dotenv

# import des méthodes internes
from src.logger import logger
from src.models import Player, Team, Game

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la connexion à DuckDB
## appel de la variable d'environnement DUCKDB_PATH ou utilisation d'un chemin par défaut
DUCKDB_PATH = os.getenv("DUCKDB_PATH", "data/nba.duckdb")

def get_connection() -> duckdb.DuckDBPyConnection:
    """Retourne une connexion à la base DuckDB."""
    # Assure que le dossier existe avant de se connecter
    os.makedirs(os.path.dirname(DUCKDB_PATH), exist_ok=True)
    return duckdb.connect(DUCKDB_PATH)

def init_tables() -> None:
    """Crée les tables si elles n'existent pas.
    - teams: id, full_name, abbreviation, conference, division, city, name
    - players: id, first_name, last_name, position, height, weight, team_id
    - games: id, date, season, status, home_team_id, visitor_team"""
    conn = get_connection()
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            full_name VARCHAR,
            abbreviation VARCHAR,
            conference VARCHAR,
            division VARCHAR,
            city VARCHAR,
            name VARCHAR
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            first_name VARCHAR,
            last_name VARCHAR,
            position VARCHAR,
            height VARCHAR,
            weight VARCHAR,
            team_id INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            date VARCHAR,
            season INTEGER,
            status VARCHAR,
            home_team_id INTEGER,
            visitor_team_id INTEGER,
            home_team_score INTEGER,
            visitor_team_score INTEGER
        )
    """)

    conn.close()
    logger.info("Tables initialisées avec succès")


def insert_teams(teams: list[Team]) -> None:
    """Insère une liste d'équipes dans DuckDB (ignore les doublons)."""
    conn = get_connection()

    for team in teams:
        conn.execute("""
            INSERT OR IGNORE INTO teams VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            team.id, team.full_name, team.abbreviation,
            team.conference, team.division, team.city, team.name
        ])

    conn.close()
    logger.info(f"{len(teams)} équipes insérées")


def insert_players(players: list[Player]) -> None:
    """Insère une liste de joueurs dans DuckDB (ignore les doublons)."""
    conn = get_connection()

    for player in players:
        conn.execute("""
            INSERT OR IGNORE INTO players VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            player.id, player.first_name, player.last_name,
            player.position, player.height, player.weight,
            player.team.id if player.team else None
        ])

    conn.close()
    logger.info(f"{len(players)} joueurs insérés")


def insert_games(games: list[Game]) -> None:
    """Insère une liste de matchs dans DuckDB (ignore les doublons)."""
    conn = get_connection()

    for game in games:
        conn.execute("""
            INSERT OR IGNORE INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            game.id, game.date, game.season, game.status,
            game.home_team.id, game.visitor_team.id,
            game.home_team_score, game.visitor_team_score
        ])

    conn.close()
    logger.info(f"{len(games)} matchs insérés")
