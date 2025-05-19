# utils/garage_logger.py

import os
import logging
import shutil
import json
from datetime import datetime, timedelta
from config.config_paths import LOG_DIR, CONFIG_LOGGING_PATH, ARCHIVE_DIR

class GarageLogger:
    """
    Logger for garasjesystemet. Skriver til fire loggfiler:
    - activity.log: motorpulser og brukerhandlinger
    - status.log: endringer i portstatus
    - errors.log: sensorfeil eller uventede tilstander
    - timing.log: tid brukt ved åpning/lukking
    """

    def __init__(self):
        self._ensure_log_environment()
        self.rotation_days = self._load_rotation_days()
        self.retention_days = self._load_retention_days()

        self.activity_logger = self._setup_logger('activity_logger', 'activity.log')
        self.status_logger = self._setup_logger('status_logger', 'status.log')
        self.error_logger = self._setup_logger('error_logger', 'errors.log')
        self.timing_logger = self._setup_logger('timing_logger', 'timing.log')

    def _ensure_log_environment(self):
        """Oppretter logg- og arkivmapper samt nødvendige filer."""
        os.makedirs(LOG_DIR, exist_ok=True)
        os.makedirs(ARCHIVE_DIR, exist_ok=True)

        for name in ["activity.log", "status.log", "errors.log", "timing.log"]:
            path = os.path.join(LOG_DIR, name)
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write(f"# Opprettet {datetime.now()}\n")

    def _setup_logger(self, name, filename):
        """Oppretter logger med ønsket formattering."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        path = os.path.join(LOG_DIR, filename)
        handler = logging.FileHandler(path)
        formatter = logging.Formatter('%(asctime)s | %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
        return logger

    def _load_rotation_days(self):
        try:
            with open(CONFIG_LOGGING_PATH) as f:
                config = json.load(f)
            return config.get("log_rotation_days", 7)
        except:
            return 7

    def _load_retention_days(self):
        try:
            with open(CONFIG_LOGGING_PATH) as f:
                config = json.load(f)
            return config.get("log_archive_retention_days", 30)
        except:
            return 30

    def _rotate_if_needed(self, filepath):
        """Roterer loggfiler etter X dager."""
        if not os.path.exists(filepath):
            return
        mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        if (datetime.now() - mod_time).days >= self.rotation_days:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            base = os.path.basename(filepath).replace(".log", "")
            archived = f"{base}_{timestamp}.log"
            shutil.move(filepath, os.path.join(ARCHIVE_DIR, archived))

    def cleanup_archived_logs(self):
        """Sletter arkiverte loggfiler eldre enn Y dager."""
        for filename in os.listdir(ARCHIVE_DIR):
            file_path = os.path.join(ARCHIVE_DIR, filename)
            if os.path.isfile(file_path):
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if (datetime.now() - mod_time).days >= self.retention_days:
                    os.remove(file_path)

    # === Logging API ===

    def log_action(self, port, action, source='system', result='success'):
        """
        Logger en bruker- eller systemhandling.
        Eksempel: port1 | action=open | source=api | result=success
        """
        self._rotate_if_needed(os.path.join(LOG_DIR, "activity.log"))
        msg = f"{port} | action={action} | source={source} | result={result}"
        self.activity_logger.info(msg)

    def log_status_change(self, port, new_status):
        """
        Logger en endring i portstatus.
        Eksempel: port2 | status_changed_to=closed
        """
        self._rotate_if_needed(os.path.join(LOG_DIR, "status.log"))
        msg = f"{port} | status_changed_to={new_status}"
        self.status_logger.info(msg)

    def log_error(self, port, message):
        """
        Logger en feil for porten.
        Eksempel: port1 | SENSOR ERROR detected
        """
        self._rotate_if_needed(os.path.join(LOG_DIR, "errors.log"))
        msg = f"{port} | {message}"
        self.error_logger.error(msg)

    def log_timing(self, port, direction, duration):
        """
        Logger hvor lang tid det tok å åpne/lukke port.
        Eksempel: port1 | open | duration=4.15s
        """
        self._rotate_if_needed(os.path.join(LOG_DIR, "timing.log"))
        msg = f"{port} | {direction} | duration={duration:.2f}s"
        self.timing_logger.info(msg)
