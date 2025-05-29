from utils.logging.unified_logger import get_logger
# ==========================================
# Filnavn: config_manager.py
# Modulbasert konfigurasjonsbehandling
# ==========================================

import os
import json
from datetime import datetime
import shutil

CONFIG_DIR = "config"
BACKUP_DIR = "backups"
CHANGE_LOG = os.path.join(CONFIG_DIR, "config_change.log")

CONFIG_MODULES = {
    "gpio": "config_gpio.json",
    "system": "config_system.json",
    "logging": "config_logging.json"
}

DEFAULTS = {
    "gpio": {
        "relay_pins": {"port1": 17, "port2": 27},
        "sensor_pins": {
            "port1": {"open": 22, "closed": 23},
            "port2": {"open": 24, "closed": 25}
        }
    },
    "system": {
        "polling_interval_ms": 100,
        "calibration": {
            "port1": {"open_time": 10},
            "port2": {"open_time": 10}
        }
    },
    "logging": {
        "log_rotation_days": 7,
        "log_archive_retention_days": 30
    }
}


class ConfigManager:
    def __init__(self):
        self.config = {}
        self._ensure_structure()
        self.load_all()

    def _ensure_structure(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)

        for key, filename in CONFIG_MODULES.items():
            path = os.path.join(CONFIG_DIR, filename)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    json.dump(DEFAULTS[key], f, indent=2)

    def load_all(self):
        self.config.clear()
        for key, filename in CONFIG_MODULES.items():
            with open(os.path.join(CONFIG_DIR, filename)) as f:
                self.config[key] = json.load(f)

    def get_all(self):
        return self.config

    def get_module(self, key):
        return self.config.get(key, {})

    def update_module(self, key, new_data, user="system", source="unknown"):
        filename = CONFIG_MODULES.get(key)
        if not filename:
            raise ValueError(f"Ugyldig konfig-nøkkel: {key}")

        path = os.path.join(CONFIG_DIR, filename)
        old_data = self.config.get(key, {})

        # Lag backup
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        shutil.copy(path, os.path.join(BACKUP_DIR, f"{key}_{ts}.json"))

        # Lagre ny data
        with open(path, 'w') as f:
            json.dump(new_data, f, indent=2)

        # Logg endringer
        self._log_changes(key, old_data, new_data, user, source)

        # Oppdater cache
        self.config[key] = new_data

    def _log_changes(self, module, old, new, user, source):
        changes = []
        for k in new:
            old_val = old.get(k)
            new_val = new[k]
            if old_val != new_val:
                changes.append(f"{k}: {old_val} → {new_val}")

        if changes:
            with open(CHANGE_LOG, "a") as log:
                log.write(f"{datetime.now()} | {user} via {source} | {module} updated | {', '.join(changes)}\n")
