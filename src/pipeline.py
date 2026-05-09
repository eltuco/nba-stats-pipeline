# pipeline.py
# import des bibliothèques externes
import duckdb
import os
import csv
from datetime import date, timedelta
from dotenv import load_dotenv

#import des modules internes
from src.api_client import get_teams, get_players, get_games
from src.models import Team, Player, Game
from src.loader import init_tables, insert_teams,insert_games
from src.loader import DUCKDB_PATH
from src.logger import logger   

# Chargement des variables d'environnement
load_dotenv()

def load_teams() ->list[Team]:
    """Récupère les données des équipes depuis l'API et les transforme en objets Team."""
    logger.info("Récupération des équipes depuis l'API...")
    data = get_teams()
    teams = [Team(**team) for team in data["data"]]
    insert_teams
    logger.info(f"{len(teams)} équipes récupérées.")
    return teams

def load_recent_games(days: int = 7) -> list[Game]:
    """Récupère les données des matches récents depuis l'API et les transforme en objets Game."""
    logger.info("Récupération des matches récents depuis l'API...")
    # initalisation de la liste des matches
    all_games = []
    for i in range(1, days + 1):
        day = (date.today() - timedelta(days=i)).isoformat()
        data = get_games(date=day)
        if data["data"]:
            games = [Game(**g) for g in data["data"]]
            insert_games(games)
            all_games.extend(games)
            logger.info(f"{day} : {len(games)} matchs insérés")
        else:
            logger.info(f"{day} : aucun match")

    logger.info(f"Total : {len(all_games)} matchs chargés")
    return all_games

def export_team_report() -> str:
    """Génère un rapport CSV du bilan par équipe."""
    logger.info("Génération du rapport CSV...")
    conn = duckdb.connect(DUCKDB_PATH)

    df = conn.execute("""
        WITH results AS (
            SELECT home_team_id as team_id,
                   CASE WHEN home_team_score > visitor_team_score THEN 1 ELSE 0 END as win
            FROM games
            UNION ALL
            SELECT visitor_team_id as team_id,
                   CASE WHEN visitor_team_score > home_team_score THEN 1 ELSE 0 END as win
            FROM games
        ),
        bilan AS (
            SELECT t.full_name,
                   t.conference,
                   COUNT(*) as matchs_joues,
                   SUM(win) as victoires,
                   COUNT(*) - SUM(win) as defaites,
                   ROUND(SUM(win) * 100.0 / COUNT(*), 1) as pct_victoires
            FROM results r
            JOIN teams t ON r.team_id = t.id
            GROUP BY t.full_name, t.conference
        )
        SELECT full_name,
               conference,
               matchs_joues,
               victoires,
               defaites,
               pct_victoires,
               RANK() OVER (PARTITION BY conference ORDER BY victoires DESC) as rang_conference
        FROM bilan
        WHERE conference IN ('East', 'West')
        ORDER BY conference, rang_conference
    """).fetchdf()

    conn.close()

    # Export CSV
    output_path = "data/processed/team_report.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"Rapport exporté : {output_path}")
    return output_path


def run():
    """Point d'entrée principal du pipeline."""
    logger.info("=== Démarrage du pipeline NBA ===")

    # 1. Initialiser la base
    init_tables()

    # 2. Charger les équipes
    load_teams()

    # 3. Charger les matchs récents
    load_recent_games(days=7)

    # 4. Exporter le rapport
    output_path = export_team_report()

    logger.info(f"=== Pipeline terminé — rapport disponible : {output_path} ===")


if __name__ == "__main__":
    run()
