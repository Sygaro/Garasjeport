import logging
from utils.logger_factory import get_logger as _get_internal_logger

class GarageLogger:
    def __init__(self, context="default"):
        self.status_logger = _get_internal_logger(f"{context}_status", category="status")
        self.error_logger = _get_internal_logger(f"{context}_error", category="error")
        self.activity_logger = _get_internal_logger(f"{context}_activity", category="activity")
        self.timing_logger = _get_internal_logger(f"{context}_timing", category="timing")
        self.sensor_logger = _get_internal_logger(f"{context}_sensor", category="sensor")

    def log_status(self, context, message):
        self.status_logger.info(f"{context}: {message}")

    def log_error(self, context, message):
        self.error_logger.error(f"{context}: {message}")

    def log_action(self, port, action, source="api", result="success"):
        msg = f"Aksjon: {action}, kilde: {source}, resultat: {result}"
        self.activity_logger.info(f"port:{port}: {msg}")

    def log_timing(self, context, timing_data):
        self.timing_logger.info(f"{context}: {timing_data}")

    def log_sensor_data(self, context, message):
        self.sensor_logger.info(f"{context}: {message}")

    def log_debug(self, context, message):
        self.status_logger.debug(f"{context}: {message}")
        if self.sensor_logger.getEffectiveLevel() <= logging.DEBUG:
            print(f"[DEBUG] {context}: {message}")

    def get_recent_logs(self, log_type="activity", limit=50):
        import os
        from config import config_paths

        log_map = {
            "status": config_paths.STATUS_LOG,
            "error": config_paths.ERROR_LOG,
            "activity": config_paths.ACTIVITY_LOG,
            "timing": config_paths.TIMING_LOG,
            "sensor": config_paths.SENSOR_LOG_PATH
        }

        path = log_map.get(log_type, config_paths.ACTIVITY_LOG)
        if not os.path.exists(path):
            return []

        with open(path, "r") as f:
            lines = f.readlines()
            return [line.strip() for line in lines[-limit:]]

    def log_status_change(self, port, message):
        """
        Logger statusendringer fra sensorer med 'info'-nivå.
        """
        context = f"{port}"
        self._log("info", context, f"[STATUS] {message}")


    def _log(self, level, context, message):
        """
        Intern metode for å logge med ønsket nivå og format.
        Logger kun hvis nivået er tillatt basert på config_logger.json.
        """
        if not hasattr(self, "allowed_levels"):
            self.allowed_levels = {"info", "debug", "error", "warning"}  # fallback
        if level not in self.allowed_levels:
            return

        formatted = f"[{level.upper()}] [{context}] {message}"

        if level == "debug":
            print(formatted)
        elif level == "info":
            print(formatted)
        elif level == "warning":
            print(formatted)
        elif level == "error":
            print(formatted)
        # Kan utvides til logging til fil osv.


# Felles inngangspunkt brukt overalt i systemet
_logger_instances = {}

def get_logger(context="default"):
    if context not in _logger_instances:
        _logger_instances[context] = GarageLogger(context)
    return _logger_instances[context]