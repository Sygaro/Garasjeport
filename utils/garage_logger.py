import os
import json
from datetime import datetime
from config import config_paths as paths
from utils.config_loader import load_config

class GarageLogger:
    def __init__(self, status_log_path=None, error_log_path=None, log_type="text"):
        self.log_type = log_type  # 'text' eller 'json'
        self.config = load_config(paths.CONFIG_LOGGING_PATH)

        self.status_log = status_log_path or paths.STATUS_LOG
        self.error_log = error_log_path or paths.ERROR_LOG
        self.activity_log = paths.ACTIVITY_LOG
        self.timing_log = paths.TIMING_LOG

        self.ensure_log_dirs()

    def ensure_log_dirs(self):
        for path in [self.status_log, self.error_log, self.activity_log, self.timing_log]:
            os.makedirs(os.path.dirname(path), exist_ok=True)

    def _get_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_status(self, context, message):
        self._write_log(self.status_log, {
            "timestamp": self._get_timestamp(),
            "level": "STATUS",
            "context": context,
            "message": message
        })

    def log_error(self, context, message):
        self._write_log(self.error_log, {
            "timestamp": self._get_timestamp(),
            "level": "ERROR",
            "context": context,
            "message": message
        })

    def log_action(self, port, action, source="api", result="success"):
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "INFO",
            "context": f"port:{port}",
            "message": f"Aksjon: {action}, kilde: {source}, resultat: {result}"
        }
        self._write_log(paths.ACTIVITY_LOG, entry)

    def _write_log(self, path, message_dict):
        try:
            msg = (
                f"{message_dict['timestamp']} "
                f"[{message_dict['level']}] "
                f"{message_dict['context']}: "
                f"{message_dict['message']}"
            )
            with open(path, "a") as f:
                f.write(msg + "\n")
        except Exception as e:
            print(f"[Logger Error] Klarte ikke å skrive til logg: {e}")


    def log_timing(self, context, timing_data):
        entry = {
            "timestamp": self._get_timestamp(),
            "level": "TIMING",
            "context": context,
            "message": timing_data
        }
        self._write_log(self.timing_log, entry)

    def log_debug(self, context, message):
        print(f"[DEBUG] {context}: {message}")  # Konsoll-debug
