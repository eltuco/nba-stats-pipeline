import logging

# Configuration du logger

def setup_logger() -> logging.Logger:
    """Configure et retourne le logger du projet."""
    logger = logging.getLogger("nba_pipeline")
    logger.setLevel(logging.DEBUG)

    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Handler fichier
    file_handler = logging.FileHandler("logs/nba_pipeline.log")
    file_handler.setLevel(logging.INFO)  # Moins verbeux dans le fichier

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    # Application du format aux handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Ajout des handlers au logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
