# status_helpers.py
"""
utils/status_helpers.py
Statusfil-hjelpere for atomisk og robust statuslagring/henting.
"""

import os
from utils.file_utils import read_json, write_json
from config import config_paths as paths
from utils.logging.unified_logger import get_logger

logger = get_logger("status_helpers", category="system", source="status_helpers")

def write_status_file(name, data):
    """Skriver status til navngitt statusfil i status-katalogen."""
    dir_path = getattr(paths, "STATUS_DIR", None)
    if not dir_path:
        logger.error("Mangler STATUS_DIR i config_paths.py")
        return
    file_path = os.path.join(dir_path, f"{name}.json")
    write_json(file_path, data)
    logger.info(f"Skrev status til {file_path}")

def read_status_file(name):
    """Leser status fra navngitt statusfil."""
    dir_path = getattr(paths, "STATUS_DIR", None)
    if not dir_path:
        logger.error("Mangler STATUS_DIR i config_paths.py")
        return None
    file_path = os.path.join(dir_path, f"{name}.json")
    status = read_json(file_path)
    logger.debug(f"Leste status fra {file_path}: {status}")
    return status
