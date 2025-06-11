# config_helpers.py
"""
utils/config_helpers.py
Robust lading og validering av config-filer via config_paths.
"""

from config import config_paths as paths
from utils.file_utils import read_json, write_json
from utils.logging.unified_logger import get_logger

logger = get_logger("config_helpers", category="system")

def load_config(attr):
    """Laster konfigurasjonsfil basert på attributtnavn i config_paths."""
    config_path = getattr(paths, attr, None)
    if not config_path:
        logger.error(f"Fant ikke config-path for {attr}")
        raise FileNotFoundError(f"Fant ikke config-path for {attr}")
    config = read_json(config_path)
    if config is None:
        logger.error(f"Kunne ikke lese config-fil: {config_path}")
        raise FileNotFoundError(f"Kunne ikke lese config-fil: {config_path}")
    logger.debug(f"Lastet config fra {config_path}")
    return config

def safe_save_config(attr, data):
    """Skriver config på trygg måte via path-attr."""
    config_path = getattr(paths, attr, None)
    if not config_path:
        logger.error(f"Fant ikke config-path for {attr}")
        return
    write_json(config_path, data)
    logger.info(f"Oppdatert config-fil {config_path}")

def get_config_value(config, key, default=None):
    """Trygg uthenting av verdi fra config."""
    value = config.get(key, default)
    logger.debug(f"Henter {key} fra config: {value}")
    return value
