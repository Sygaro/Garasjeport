# Fil: utils/logging/log_config_loader.py

import json
import logging
from config import config_paths as paths
from config.log_levels import LOG_LEVELS



_logging_config_cache = None


def load_logging_config():
    global _logging_config_cache
    if _logging_config_cache is None:
        with open(paths.CONFIG_LOGGING_PATH, "r") as f:
            config = json.load(f)

        required_top_keys = [
            "max_file_size_mb",
            "max_backups_files",
            "timestamp_format",
            "log_settings"
        ]

        for key in required_top_keys:
            if key not in config:
                raise KeyError(f"Mangler konfigurasjonsnøkkel i logging: '{key}'")

        _logging_config_cache = config

    return _logging_config_cache


def get_log_levels():
    """
    Returnerer et mapping av kategorier til faktiske logging-nivåer (ints).
    Henter nivå-strenger fra logging.json og mapper disse mot LOG_LEVELS.
    """
    config = load_logging_config()
    level_map = {}
    for category, settings in config.get("log_settings", {}).items():
        level_name = settings.get("file_level", "INFO")
        level = LOG_LEVELS.get(level_name.upper(), logging.INFO)
        level_map[category] = level
    return level_map


def get_effective_config(category: str) -> dict:
    config = load_logging_config()
    global_defaults = {
        "timestamp_format": config.get("timestamp_format", "%Y-%m-%d %H:%M:%S"),
        "max_file_size_mb": config.get("max_file_size_mb", 10),
        "max_backups_files": config.get("max_backups_files", 5),
        "log_directory": "logs"
    }
    category_config = config.get("log_settings", {}).get(category, {})

    # Slå sammen defaults og kategori
    merged = {
        **global_defaults,
        **category_config
    }

    # Gi sensibel fallback for navn
    if "filename" not in merged:
        merged["filename"] = f"{category}.log"
        logger.debug("Ingen filnavn spesifisert, bruker standard: %s", merged["filename"])

    return merged
