# log_config.py
import os
from config.config_paths import CONFIG_LOGGING_PATH
from utils.logging.unified_logger import get_logger

import json

logger = get_logger(name="log_config", category="system")


_default_config = {
    "log_directory": "logs",
    "max_file_size_mb": 10,
    "rotation_days": 14,
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
    "log_settings": {
        "default": {
            "file_enabled": true,
            "file_level": "DEBUG",
            "console_enabled": true,
            "console_level": "DEBUG",
            "format": "plain",
            "output": ["file"]
        }
    }
}

def load_logging_config():
    logger.debug("Laster loggkonfigurasjon fra: %s", CONFIG_LOGGING_PATH)
    try:
        with open(CONFIG_LOGGING_PATH, 'r') as f:
            config = json.load(f)
            logger.info("Loggkonfigurasjon lastet: %s", config)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        logger.warning("Kunne ikke laste loggkonfigurasjon, bruker standardverdier.")
        logger.debug("Bruker standard loggkonfigurasjon: %s", _default_config)
        # Hvis filen ikke finnes eller er ugyldig, returner standardverdier
        return _default_config

