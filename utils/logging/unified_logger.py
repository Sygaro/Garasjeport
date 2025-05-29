# utils/logging/unified_logger.py
from utils.logging.logger_manager import get_logger

class UnifiedLogger:
    def __init__(self, context="default"):
        self.context = context
        self.loggers = {
            "status": get_logger("status"),
            "error": get_logger("error"),
            "activity": get_logger("activity"),
            "timing": get_logger("timing"),
            "sensor": get_logger("env")  # miljøsensor
        }

    def log(self, category, message, level="info"):
        logger = self.loggers.get(category)
        if not logger:
            return

        formatted = f"{self.context}: {message}"
        if level == "debug":
            logger.debug(formatted)
        elif level == "warning":
            logger.warning(formatted)
        elif level == "error":
            logger.error(formatted)
        elif level == "critical":
            logger.critical(formatted)
        else:
            logger.info(formatted)

    def log_status(self, message):
        self.log("status", message)

    def log_error(self, message):
        self.log("error", message, level="error")

    def log_action(self, port, action, source="api", result="success"):
        msg = f"Aksjon: {action}, kilde: {source}, resultat: {result}"
        self.log("activity", f"port:{port}: {msg}")

    def log_timing(self, timing_data):
        self.log("timing", timing_data)

    def log_env_data(self, sensor, data):
        msg = f"{sensor}: {data}"
        self.log("sensor", msg)

    def debug(self, message):
        self.log("status", message, level="debug")
