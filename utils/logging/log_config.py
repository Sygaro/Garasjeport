# log_config.py
import os
from config.config_paths import CONFIG_LOGGING_PATH
import json

_default_config = {
    "log_directory": "logs",
    "max_file_size_mb": 10,
    "rotation_days": 14,
    "retention_days": 90,
    "timestamp_format": "%Y-%m-%d %H:%M:%S",
    "log_settings": {
        "default": {
            "enabled": True,
            "level": "INFO",
            "format": "plain",
            "output": ["file"]
        }
    }
}

def load_logging_config():
    try:
        with open(CONFIG_LOGGING_PATH, 'r') as f:
            config = json.load(f)
        return config
    except (FileNotFoundError, json.JSONDecodeError):
        return _default_config

