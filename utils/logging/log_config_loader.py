from config import config_paths as paths

import json


def load_logging_config():
    with open(paths.CONFIG_LOGGING_PATH, "r") as f:
        config = json.load(f)

    required_top_keys = [
        "log_directory",
        "max_file_size_mb",
        "rotation_days",
        "retention_days",
        "timestamp_format",
        "log_settings"
    ]
    for key in required_top_keys:
        if key not in config:
            raise KeyError(f"Mangler konfigurasjonsnøkkel i logging: '{key}'")

    return config