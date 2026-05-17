# test_loader.py

import pytest
import duckdb
from src.models import Team, Player, Game
from src.loader import insert_teams, insert_players, insert_games


@pytest.fixture
def conn():
    """Connexion DuckDB en mémoire — repart de zéro à chaque test."""
    connection = duckdb.connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture
def initialized_conn(conn):
    """Connexion avec les tables déjà créées."""
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
    return conn


@pytest.fixture
def sample_team():
    return Team(
        id=20,
        full_name="New York Knicks",
        abbreviation="NYK",
        conference="East",
        division="Atlantic",
        city="New York",
        name="Knicks"
    )


@pytest.fixture
def sample_player(sample_team):
    return Player(
        id=73,
        first_name="Jalen",
        last_name="Brunson",
        position="G",
        height="6-2",
        weight="190",
        team=sample_team
    )


@pytest.fixture
def sample_game(sample_team):
    visitor = Team(
        id=2,
        full_name="Philadelphia 76ers",
        abbreviation="PHI",
        conference="East",
        division="Atlantic",
        city="Philadelphia",
        name="76ers"
    )
    return Game(
        id=1,
        date="2026-05-11T00:00:00.000Z",
        season=2025,
        status="Final",
        home_team=sample_team,
        visitor_team=visitor,
        home_team_score=114,
        visitor_team_score=98
    )


# ============================================================
# Tests insert_teams
# ============================================================

def test_insert_teams(initialized_conn, sample_team):
    """Les équipes doivent être insérées correctement."""
    insert_teams([sample_team], conn=initialized_conn)
    result = initialized_conn.execute("SELECT COUNT(*) as nb FROM teams").fetchone()
    assert result[0] == 1

def test_insert_teams_no_duplicates(initialized_conn, sample_team):
    """Insérer deux fois la même équipe ne doit pas créer de doublon."""
    insert_teams([sample_team], conn=initialized_conn)
    insert_teams([sample_team], conn=initialized_conn)
    result = initialized_conn.execute("SELECT COUNT(*) as nb FROM teams").fetchone()
    assert result[0] == 1


# ============================================================
# Tests insert_players
# ============================================================

def test_insert_players(initialized_conn, sample_player):
    """Les joueurs doivent être insérés correctement."""
    insert_players([sample_player], conn=initialized_conn)
    result = initialized_conn.execute("SELECT COUNT(*) as nb FROM players").fetchone()
    assert result[0] == 1

def test_insert_players_no_duplicates(initialized_conn, sample_player):
    """Insérer deux fois le même joueur ne doit pas créer de doublon."""
    insert_players([sample_player], conn=initialized_conn)
    insert_players([sample_player], conn=initialized_conn)
    result = initialized_conn.execute("SELECT COUNT(*) as nb FROM players").fetchone()
    assert result[0] == 1


# ============================================================
# Tests insert_games
# ============================================================

def test_insert_games(initialized_conn, sample_game):
    """Les matchs doivent être insérés correctement."""
    insert_games([sample_game], conn=initialized_conn)
    result = initialized_conn.execute("SELECT COUNT(*) as nb FROM games").fetchone()
    assert result[0] == 1

def test_insert_games_no_duplicates(initialized_conn, sample_game):
    """Insérer deux fois le même match ne doit pas créer de doublon."""
    insert_games([sample_game], conn=initialized_conn)
    insert_games([sample_game], conn=initialized_conn)
    result = initialized_conn.execute("SELECT COUNT(*) as nb FROM games").fetchone()
    assert result[0] == 1