# ==========================================
# Filnavn: garage_logger.py
# Modul for logging av garasjeport-aktivitet
# Logger: hendelser, statusendringer, feil, tid
# ==========================================

import os
import logging
import shutil
import json
from datetime import datetime
from config.config_paths import LOG_DIR, CONFIG_DIR

LOG_FILES = ["activity.log", "status.log", "errors.log", "timing.log"]
ARCHIVE_DIR = os.path.join(LOG_DIR, "archived")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config_logging.json")


def ensure_log_environment():
    """Oppretter logs/-mappe og nødvendige loggfiler ved første kjøring."""
    os.makedirs(LOG_DIR, exist_ok=True)
    for log_file in LOG_FILES:
        full_path = os.path.join(LOG_DIR, log_file)
        if not os.path.exists(full_path):
            with open(full_path, 'w') as f:
                f.write(f"# Opprettet {datetime.now()}\n")


# Kjør én gang ved import
ensure_log_environment()


def _setup_logger(name, filename):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(LOG_DIR, filename))
    formatter = logging.Formatter('%(asctime)s | %(message)s', "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def load_rotation_days():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        return config.get("log_rotation_days", 7)
    except:
        return 7


def load_retention_days():
    try:
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        return config.get("log_archive_retention_days", 30)
    except:
        return 30


def should_rotate(path, max_days):
    if not os.path.exists(path):
        return False
    mod_time = datetime.fromtimestamp(os.path.getmtime(path))
    return (datetime.now() - mod_time).days >= max_days


def rotate_file(path):
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    base = os.path.basename(path).replace(".log", "")
    archived = f"{base}_{timestamp}.log"
    shutil.move(path, os.path.join(ARCHIVE_DIR, archived))


def cleanup_archived_logs():
    """Sletter arkiverte loggfiler eldre enn X dager."""
    retention_days = load_retention_days()
    if not os.path.exists(ARCHIVE_DIR):
        return
    for filename in os.listdir(ARCHIVE_DIR):
        file_path = os.path.join(ARCHIVE_DIR, filename)
        if os.path.isfile(file_path):
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if (datetime.now() - mod_time).days >= retention_days:
                os.remove(file_path)


class GarageLogger:
    """
    Logger for garasjesystemet. Skriver til fire loggfiler:
    - activity.log: motorpulser og brukerhandlinger
    - status.log: endringer i portstatus
    - errors.log: sensorfeil eller blokkert bevegelse
    - timing.log: tid brukt ved åpning/lukking
    """

    def __init__(self):
        self.activity_logger = _setup_logger('activity_logger', 'activity.log')
        self.status_logger = _setup_logger('status_logger', 'status.log')
        self.error_logger = _setup_logger('error_logger', 'errors.log')
        self.timing_logger = _setup_logger('timing_logger', 'timing.log')

    def _rotate_if_needed(self, filename):
        path = os.path.join(LOG_DIR, filename)
        if should_rotate(path, load_rotation_days()):
            rotate_file(path)

    def log_action(self, port, action, source='unknown', result='success'):
        msg = f"{port} | action={action} | source={source} | result={result}"
        self._rotate_if_needed("activity.log")
        self.activity_logger.info(msg)

    def log_status_change(self, port, new_status):
        msg = f"{port} | status_changed_to={new_status}"
        self._rotate_if_needed("status.log")
        self.status_logger.info(msg)

        if new_status == 'sensor_error':
            self._rotate_if_needed("errors.log")
            self.error_logger.error(f"{port} | SENSOR ERROR detected")

    def log_timing(self, port, direction, duration):
        msg = f"{port} | {direction} | duration={duration:.2f}s"
        self._rotate_if_needed("timing.log")
        self.timing_logger.info(msg)
