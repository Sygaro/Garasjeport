import json
import os
from config import config_paths as paths
from utils.log_utils import log_event
from utils.config_loader import load_logging_config

# Last inn loggkonfig
logging_config = load_logging_config()
enabled_logs = logging_config["enabled_logs"]
log_levels = logging_config["log_levels"]

class GarageLogger:
    """
    Kombinert logger som støtter strukturert og tekstbasert logging.
    - Respekterer config_logging.json
    - Skriver til config_paths.*_LOG
    - Fleksibel støtte for JSON-format
    """
    def __init__(self, use_json=False):
        self.use_json = use_json

    def _is_enabled(self, log_type: str) -> bool:
        return enabled_logs.get(log_type, False)

    def _write(self, path: str, log_type: str, msg):
        if not self._is_enabled(log_type):
            return
        if self.use_json and isinstance(msg, dict):
            log_event(path, json.dumps(msg))
        else:
            log_event(path, msg)

    def log_action(self, port, action, source="api", result="success"):
        log_type = "activity"
        msg = {
            "port": port,
            "action": action,
            "source": source,
            "result": result
        } if self.use_json else f"{port} {action} via {source} = {result}"
        self._write(paths.ACTIVITY_LOG, log_type, msg)

    def log_status_change(self, port, new_status):
        log_type = "status"
        msg = {
            "port": port,
            "status": new_status
        } if self.use_json else f"{port} → {new_status}"
        self._write(paths.STATUS_LOG, log_type, msg)

    def log_error(self, port, message):
        log_type = "errors"
        msg = {
            "port": port,
            "error": message
        } if self.use_json else f"{port} | ERROR: {message}"
        self._write(paths.ERROR_LOG, log_type, msg)

    def log_timing(self, port, direction, duration):
        log_type = "timing"
        msg = {
            "port": port,
            "direction": direction,
            "duration_sec": round(duration, 2)
        } if self.use_json else f"{port} {direction}: {duration:.2f}s"
        self._write(paths.TIMING_LOG, log_type, msg)

    def log_all(self, log_type: str, msg):
        """
        Logg til valgfri type (f.eks. 'debug')
        """
        if not self._is_enabled(log_type):
            return
        filename = os.path.join(logging_config["log_directory"], f"{log_type}.log")
        self._write(filename, log_type, msg)

    def log_timing_detailed(self, port, direction, total, relay_time, motion_time):
        msg = f"{port} | {direction} | total: {total:.2f}s | relay→sensor1: {relay_time:.2f}s | sensor1→sensor2: {motion_time:.2f}s"
        self._write(paths.TIMING_LOG, "timing", msg)

    def log_port_stuck(self, port, cause, source):
        msg = f"{port} | bevegelse avbrutt | årsak: {cause} | kilde: {source}"
        self._write(paths.STATUS_LOG, "status", msg)
        self._write(paths.ERROR_LOG, "error", msg)
