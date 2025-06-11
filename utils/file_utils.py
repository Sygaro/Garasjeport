# file_utils.py
"""
utils/file_utils.py
Felles helper for robust fil-IO (.json og generelt).
"""

import json
import os
from utils.logging.unified_logger import get_logger

logger = get_logger("file_utils", category="system")

def read_json(path):
    """Leser og returnerer et JSON-objekt fra path."""
    logger.debug(f"Leser JSON fra {path}")
    if not os.path.exists(path):
        logger.warning(f"Filen {path} finnes ikke.")
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.debug(f"Lastet inn JSON fra {path}")
            return data
    except Exception as e:
        logger.error(f"Feil ved lesing av {path}: {e}", exc_info=True)
        return None

def write_json(path, data):
    """Skriver data (dict/list) til JSON-fil på path."""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            logger.debug(f"Skrev JSON til {path}")
    except Exception as e:
        logger.error(f"Feil ved skriving til {path}: {e}", exc_info=True)

def file_exists(path):
    """Sjekker om filen finnes."""
    exists = os.path.exists(path)
    logger.debug(f"file_exists({path}) -> {exists}")
    return exists

def remove_file(path):
    """Sletter en fil om den finnes."""
    if os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"Slettet fil {path}")
        except Exception as e:
            logger.error(f"Feil ved sletting av {path}: {e}", exc_info=True)

def ensure_dir_exists(dir_path):
    """Oppretter katalog om den ikke finnes."""
    try:
        os.makedirs(dir_path, exist_ok=True)
        logger.debug(f"Sikret at katalog {dir_path} finnes.")
    except Exception as e:
        logger.error(f"Feil ved opprettelse av katalog {dir_path}: {e}", exc_info=True)
