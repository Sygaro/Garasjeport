# ==========================================
# Filnavn: bootstrap.py
# Initierer loggmappene, loggfiler, config og backups
# ==========================================

import os
import json
from datetime import datetime

LOG_DIR = "logs"
LOG_FILES = ["activity.log", "status.log", "errors.log", "timing.log"]
CONFIG_PATH = "config.json"
BACKUP_DIR = "backups"

def ensure_logs():
    """Oppretter logs/-mappe og nødvendige loggfiler."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    for log_file in LOG_FILES:
        full_path = os.path.join(LOG_DIR, log_file)
        if not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                f.write(f"# Opprettet {datetime.now()}\n")

def ensure_config():
    """Oppretter tom config.json hvis den mangler."""
    if not os.path.exists(CONFIG_PATH):
        default = {
            "polling_interval_ms": 100,
            "relay_pins": {
                "port1": 17,
                "port2": 27
            },
            "sensor_pins": {
                "port1": {"open": 22, "closed": 23},
                "port2": {"open": 24, "closed": 25}
            },
            "calibration": {
                "port1": {"open_time": 10},
                "port2": {"open_time": 10}
            }
        }
        with open(CONFIG_PATH, 'w') as f:
            json.dump(default, f, indent=2)

def ensure_backups():
    """Oppretter backups/-mappe hvis den mangler."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

def init_environment():
    """Kalles én gang ved oppstart av systemet."""
    ensure_logs()
    ensure_config()
    ensure_backups()
