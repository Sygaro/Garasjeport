import json
import os
from config import config_paths as paths
from config import config_paths as paths


def _load_json_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Finner ikke konfigurasjonsfil: {path}")
    with open(path, "r") as f:
        return json.load(f)

def load_config(path=None):
    """
    Laster og returnerer konfigurasjonsdata fra gitt sti.
    Hvis ingen sti oppgis, brukes config_logging.json som standard.
    """
    if path is None:
        path = paths.CONFIG_LOGGING_PATH

    with open(path, "r") as f:
        return json.load(f)
    config_gpio = _load_json_file(paths.CONFIG_GPIO_PATH)
    config_system = _load_json_file(paths.CONFIG_SYSTEM_PATH)
    return config_gpio, config_system

def load_auth_config():
    return _load_json_file(paths.CONFIG_AUTH_PATH)

def load_portlogic_config():
    path = paths.CONFIG_PORTLOGIC_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Portlogikk-konfig ikke funnet: {path}")
    with open(path, "r") as f:
        config = json.load(f)

    required_keys = [
        "relay_activation_timeout",
        "default_open_time",
        "default_close_time",
        "max_time_factor",
        "timing_history_length"
    ]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Mangler '{key}' i portlogikk-konfig")

    return config


def load_logging_config():
    config = _load_json_file(paths.CONFIG_LOGGING_PATH)

    required_keys = [
        "log_directory", "max_file_size_kb", "rotation_days",
        "retention_days", "log_levels", "enabled_logs"
    ]
    for key in required_keys:
        if key not in config:
            raise KeyError(f"Mangler konfigurasjonsnøkkel i logging: '{key}'")

    return config
