import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os
from dotenv import load_dotenv

# Charger les variables d'environnement (LOG_LEVEL, etc.)
load_dotenv(dotenv_path="config/.env")

# Dictionnaire pour conserver les loggers déjà créés
_LOGGERS = {}

def _init_base_logger():
    """Initialise la configuration de base pour tous les loggers."""
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configuration globale depuis .env
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    max_bytes = int(os.getenv("LOG_MAX_SIZE_MB", 5)) * 1024 * 1024
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))

    return {
        "level": level,
        "max_bytes": max_bytes,
        "backup_count": backup_count,
        "log_dir": log_dir,
    }

def get_logger(name: str) -> logging.Logger:
    """
    Récupère (ou crée) un logger configuré globalement.

    Args:
        name (str): Nom du logger (ex: "SOCKS5", "TLS_SERVER").
    """
    if name in _LOGGERS:
        return _LOGGERS[name]

    config = _init_base_logger()

    logger = logging.getLogger(name)
    logger.setLevel(config["level"])

    if not logger.hasHandlers():
        # Format uniforme
        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler fichier (rotation auto)
        log_file = config["log_dir"] / f"{name.lower()}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=config["max_bytes"],
            backupCount=config["backup_count"],
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _LOGGERS[name] = logger
    return logger
